#!/usr/bin/env python3
"""
Clean, de-duplicate and score the 6sense accounts JSON so you know who to call today.

Usage (run it every time you add new 6sense email alerts to the JSON):

    python3 optimize_sixsense.py 6SENSE_Update_File.json
    python3 optimize_sixsense.py 6SENSE_Update_File.json --top 25 --today 2026-11-02

Writes, next to the input file:
    <name>.json  (overwritten in place, a .bak copy is kept) - same shape the dashboard expects,
                 plus a `priority` block on every account, sorted best-first
    <name>_target_now.csv - ranked call list, opens in Excel

Standard library only. The output stays a flat {company: account} dict, so the existing
6sense dashboard and its drag-and-drop merge keep working.
"""
import argparse
import csv
import json
import math
import re
import shutil
import sys
from datetime import date, datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration: edit these as you learn more about your accounts
# ---------------------------------------------------------------------------

# Alternate names 6sense uses for the same company -> the name to keep.
# Applied on every run, so a new alert under an alias is folded in automatically.
ALIASES = {
    "National Realty Of Brevard, Inc.": "National Realty Of Brevard",
    "COLORVISION INC": "Colorvision",
    "World Hotels": "WorldHotels",
    "Mitsukoshi, Inc.": "Mitsukoshi",
    "Silver Springs Bottled Water Co Inc": "Silver Springs Bottled Water Company",
    "ACCESS | MANAGEMENT ∙ REALTY ∙ MAINTENANCE ∙ LIFESTYLE": "Access Residential Management, LLC",
}

# Look alike but have different websites or names, so they are flagged and not merged.
# Move a pair into ALIASES once you confirm it is the same company.
POSSIBLE_DUPLICATES = [
    ("Di Pasqua Enterprises", "Dipasqua Enterprises, Inc."),   # dipasqua.com vs subwaydipasqua.com
    ("Hillpointe", "Hillpointe LLC"),                          # hillpointe.com vs pointegrand.com
    ("Velovita", "Jeunesse.Global"),                           # both map to velovita.com
    ("Access Residential Management, LLC", "Ahm Rbr Associates, LLC"),  # both accessdifference.com
]

COMPETITORS = ["adp", "workable", "rippling", "expensify", "pluralsight", "beti",
               "paycor", "paychex", "ultimate software", "ukg", "gusto", "bamboohr",
               "workday", "paycom", "isolved", "dayforce", "ceridian", "namely", "trinet"]

# Paylocity pages where someone is raising their hand (strongest web signal there is).
HAND_RAISE_PAGES = ["/request-a-demo", "/contact", "/pricing", "/get-a-quote"]
# Paid-ad / campaign landing pages: real interest, but often one click from an ad.
AD_LANDING_PAGES = ["/lp/", "/learn-more", "/demo/"]

STAGE_POINTS = {"purchase": 20, "decision": 18, "consideration": 13, "awareness": 6, "target": 3}
FIT_POINTS = {"strong": 15, "moderate": 8, "weak": 0}
REACH_POINTS = {"high": 0, "medium": 0, "low": 0}  # reach is about *our* coverage, not their intent

# Words that the .msg parser sometimes glues onto the end of a contact name instead of the title.
TITLE_SPILL = {"account", "senior", "sr.", "sr", "hr", "payroll", "office", "operations", "general",
               "regional", "executive", "assistant", "vice", "chief", "human", "benefits", "finance"}

# ---------------------------------------------------------------------------


def norm_comp(text):
    return text.strip().lower()


def parse_d(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def merge_into(dst, src):
    """Same merge rules the skill/dashboard uses."""
    dst["signal_count"] = dst.get("signal_count", 0) + src.get("signal_count", 0)
    dst["web_visits"] = dst.get("web_visits", 0) + src.get("web_visits", 0)
    if (src.get("_latest_date") or "") > (dst.get("_latest_date") or ""):
        dst["stage"] = src.get("stage", dst.get("stage"))
    for f in ("fit", "reach", "website"):
        if not dst.get(f) and src.get(f):
            dst[f] = src[f]
    for f in ("keywords", "competitor_keywords"):
        dst[f] = sorted(set(dst.get(f, [])) | set(src.get(f, [])), key=str.lower)
    for f in ("dates", "activity_dates", "source_files"):
        dst[f] = sorted(set(dst.get(f, [])) | set(src.get(f, [])))
    seen = {(u.get("decoded"), u.get("date")) for u in dst.get("decoded_urls", [])}
    for u in src.get("decoded_urls", []):
        if (u.get("decoded"), u.get("date")) not in seen:
            dst.setdefault("decoded_urls", []).append(u)
            seen.add((u.get("decoded"), u.get("date")))
    for f in ("contacts", "form_fills", "surge_topics"):
        existing = {json.dumps(x, sort_keys=True) for x in dst.get(f, [])}
        for x in src.get(f, []):
            if json.dumps(x, sort_keys=True) not in existing:
                dst.setdefault(f, []).append(x)
    for f in ("email_date", "activity_date", "_latest_date"):
        if (src.get(f) or "") > (dst.get(f) or ""):
            dst[f] = src[f]
    names = set(dst.get("aliases", [])) | {src["company"]} | set(src.get("aliases", []))
    dst["aliases"] = sorted(names - {dst["company"]})
    if src.get("zi") and (src["zi"].get("pulled_on") or "") >= ((dst.get("zi") or {}).get("pulled_on") or ""):
        dst["zi"] = src["zi"]
    if src.get("bf"):   # BenefitFlow: newest pull wins, revealed contacts are kept from both
        revealed = {**((dst.get("bf") or {}).get("revealed") or {}), **(src["bf"].get("revealed") or {})}
        if (src["bf"].get("pulled_on") or "") >= ((dst.get("bf") or {}).get("pulled_on") or ""):
            dst["bf"] = dict(src["bf"])
        if revealed:
            dst["bf"]["revealed"] = revealed
    if (src.get("six_qa_on") or "") > (dst.get("six_qa_on") or ""):
        dst["six_qa_on"] = src["six_qa_on"]
    if src.get("past_process"):
        dst["past_process"] = True
        dst["past_process_on"] = max(filter(None, [dst.get("past_process_on"), src.get("past_process_on")]), default=None)
    if (src.get("worked_on") or "") > (dst.get("worked_on") or ""):
        dst["worked_on"] = src["worked_on"]
    if src.get("book") and not dst.get("book"):   # on the owner's prospect list
        dst["book"] = src["book"]
    if src.get("book_ok_on") and not dst.get("book_ok_on"):   # owner cleared "Not in my book"
        dst["book_ok_on"] = src["book_ok_on"]
    if src.get("dup_ok"):   # possible duplicates the owner cleared
        dst["dup_ok"] = sorted(set(dst.get("dup_ok", [])) | set(src["dup_ok"]))
    if src.get("zid"):   # ZoomInfo weekly digest entries, one per digest date
        have = {e.get("date") for e in dst.get("zid", [])}
        dst["zid"] = dst.get("zid", []) + [e for e in src["zid"] if e.get("date") not in have]
    if src.get("purged_on"): dst["purged_on"] = src["purged_on"]   # deleted for good: only a marker is kept
    for f in ("removed_at", "restored_at"):   # owner removed / restored the account on the page
        if (src.get(f) or "") > (dst.get(f) or ""):
            dst[f] = src[f]
    if src.get("sdr_notes") and src["sdr_notes"] not in (dst.get("sdr_notes") or ""):   # the SDR's notes box
        dst["sdr_notes"] = "\n".join(filter(None, [dst.get("sdr_notes"), src["sdr_notes"]]))
    if (src.get("ai_openers") or {}).get("at", "") > (dst.get("ai_openers") or {}).get("at", ""):   # owner's saved AI openers
        dst["ai_openers"] = src["ai_openers"]
    if (src.get("social_manual_on") or "") > (dst.get("social_manual_on") or ""):   # social links the owner added or hid
        dst["social_manual"], dst["social_manual_on"] = src.get("social_manual") or {}, src["social_manual_on"]
    if src.get("web_social") and (src["web_social"].get("on") or "") >= ((dst.get("web_social") or {}).get("on") or ""):   # links read from their website
        dst["web_social"] = src["web_social"]
    wn_t = lambda w: max([x for x in ((w or {}).get("on"), (w or {}).get("req_changed")) if x] or [""])
    if src.get("web_news") and wn_t(src["web_news"]) > wn_t(dst.get("web_news")):   # web news triggers (and refresh requests)
        dst["web_news"] = src["web_news"]
    if (src.get("emp_manual_on") or "") > (dst.get("emp_manual_on") or ""):   # head count the owner typed
        dst["emp_manual"], dst["emp_manual_on"] = src.get("emp_manual"), src["emp_manual_on"]
    if (src.get("vendor_manual_on") or "") > (dst.get("vendor_manual_on") or ""):   # vendor the owner picked after a call
        dst["vendor_manual"], dst["vendor_manual_on"] = src.get("vendor_manual"), src["vendor_manual_on"]
    if src.get("vendor_list") and (src.get("vendor_list_on") or "") >= (dst.get("vendor_list_on") or ""):   # owner's current-vendor list
        dst["vendor_list"], dst["vendor_list_on"] = src["vendor_list"], src.get("vendor_list_on")
    if (src.get("top50_on") or "") > (dst.get("top50_on") or ""):   # owner's Top 50 ABM mark
        dst["top50"], dst["top50_on"] = bool(src.get("top50")), src["top50_on"]
    if src.get("notes") and src["notes"] not in (dst.get("notes") or ""):
        dst["notes"] = "\n".join(filter(None, [dst.get("notes"), src["notes"]]))


def fix_contact(c):
    name, title = (c.get("name") or "").split(), (c.get("title") or "").strip()
    moved = []
    while len(name) > 2 and name[-1].lower() in TITLE_SPILL:
        moved.insert(0, name.pop())
    if moved:
        c["name"] = " ".join(name)
        c["title"] = " ".join(moved + ([title] if title else []))
    return c


def clean(account):
    a = account
    # consistent schema for every record
    for f in ("keywords", "competitor_keywords", "decoded_urls", "contacts", "form_fills",
              "dates", "activity_dates", "source_files", "surge_topics"):
        a[f] = a.get(f) or []
    for f in ("signal_count", "web_visits"):
        a[f] = int(a.get(f) or 0)
    for f in ("stage", "fit", "reach", "website"):
        a[f] = (a.get(f) or "").strip()
    # the separate sales-history box is gone: its text moves into notes (once), same as the dashboard
    hist = (a.pop("history_note", None) or "").strip()
    if hist and hist not in (a.get("notes") or ""):
        a["notes"] = (a["notes"].strip() + "\n\nSales history: " + hist) if (a.get("notes") or "").strip() else "Sales history: " + hist

    # 6sense tags qualified accounts with a trailing "6QA" after the name. Keep it as a flag, not part of the name.
    m = re.search(r"\s+6QA$", a["company"], re.I)
    if m:
        a["company"] = a["company"][: m.start()].strip()
        flagged = max(a.get("activity_dates") or a.get("dates") or [""]) or None
        a["six_qa_on"] = max(filter(None, [a.get("six_qa_on"), flagged]), default=None)

    # Empty filenames break the dashboard's "already loaded" check.
    a["source_files"] = sorted({s for s in a["source_files"] if s})
    a["dates"] = sorted(set(a["dates"]))
    a["activity_dates"] = sorted(set(a["activity_dates"]))

    # Records added without an email header had no dates. Fill them from the activity history.
    last = max(a["activity_dates"] + a["dates"], default=None)
    a.setdefault("email_date", None)
    if not a.get("activity_date"):
        a["activity_date"] = max(a["activity_dates"], default=last)
    # always derived from the real dates (the dashboard does the same when merging)
    url_dates = [u.get("date") for u in a["decoded_urls"] if parse_d(u.get("date"))]
    a["_latest_date"] = max(a["dates"] + a["activity_dates"] + url_dates, default=None)

    # Competitor keywords: one consistent list, case-insensitive.
    found = {k for k in a["keywords"] + a["competitor_keywords"] if norm_comp(k) in COMPETITORS}
    a["competitor_keywords"] = sorted(found, key=str.lower)
    a["keywords"] = sorted(set(a["keywords"]), key=str.lower)

    a["decoded_urls"].sort(key=lambda u: u.get("date") or "", reverse=True)
    seen_t, topics = set(), []
    for t in a["surge_topics"]:
        k = (t.get("topic"), t.get("date"))
        if t.get("topic") and k not in seen_t:
            seen_t.add(k); topics.append(t)
    a["surge_topics"] = sorted(topics, key=lambda t: t.get("date") or "", reverse=True)
    a["contacts"] = [fix_contact(c) for c in a["contacts"]]
    return a


def page_path(url):
    return re.sub(r"^https?://[^/]+", "", url or "") or "/"


# ── Signal boost: ZoomInfo + BenefitFlow points on top of the 6sense score. Same rules as the dashboard. ──
BOOST_CAP = 20
DIGEST_POINTS = {"competitor": 8, "visit": 8, "research": 6, "research_other": 4, "leader": 5, "mna": 4, "hiring": 3, "other": 0}
THEMES = [r"\badp\b|automatic data processing|paychex|ukg|ultimate software|paycor|rippling|gusto|payroll|\bhris\b|\bhcm\b|workday|paycom|isolved|dayforce|ceridian|pay on demand",
          r"benefit|\baca\b|affordable care|cobra|safe harbor|enrollment|401k|retirement|\bhra\b|health insurance",
          r"talent|recruit|candidate|applicant|onboarding|on boarding|hiring",
          r"engagement|communication|retention|culture|recognition",
          r"attendance|time clock|timekeeping|\bhours\b|scheduling",
          r"asset",
          r"airbase|corporate card|credit card|expense|spend management"]


def digest_kind(text):
    if re.search(r"competitor - ", text, re.I): return "competitor"
    if re.search(r"visited a webpage", text, re.I): return "visit"
    if re.search(r"(researching|researched intent topics:).*(payroll|benefits|human resources|compensation|\bhr\b|labor)", text, re.I): return "research"
    if re.search(r"researching|researched intent topics", text, re.I): return "research_other"
    if re.search(r"has joined|appointed|promoted", text, re.I): return "leader"
    if re.search(r"mergers & acquisitions|acquir", text, re.I): return "mna"
    if re.search(r"hiring plans", text, re.I): return "hiring"
    return "other"


def digest_fade(kind, age):
    if kind == "leader": return 1 if age <= 30 else 0.5 if age <= 90 else 0
    if kind in ("mna", "hiring"): return 1 if age <= 30 else 0.5 if age <= 60 else 0
    return 1 if age <= 7 else 0.5 if age <= 14 else 0.25 if age <= 30 else 0


def digest_new_act(a, today):
    seen, out = set(), []
    for e in sorted(a.get("zid") or [], key=lambda e: str(e.get("date"))):
        d = parse_d(e.get("date"))
        for it in e.get("items") or []:
            is_new = it.get("window") == "Last 7 days" or it.get("text") not in seen
            seen.add(it.get("text"))
            if is_new and it.get("kind") == "act" and d and d <= today:
                out.append({"text": it.get("text") or "", "age": (today - d).days})
    return out


def next_renewal_days(a, today):
    r = (a.get("bf") or {}).get("renewal")
    if not parse_d(r):
        return None
    y, m, dd = int(r[:4]), int(r[5:7]), int(r[8:10])
    def at(year):   # day overflow rolls into the next month, like the dashboard's date maths
        return date(year, m, 1).toordinal() + dd - 1
    t = today.toordinal()
    d = at(today.year)
    if d < t:
        d = at(today.year + 1)
    return d - t


def signal_boost(a, today):
    best = {}
    for it in digest_new_act(a, today):
        k = digest_kind(it["text"])
        pts = math.floor(DIGEST_POINTS[k] * digest_fade(k, it["age"]))
        if pts > 0 and pts > best.get(k, 0):
            best[k] = pts
    total = sum(best.values())
    for t in (a.get("zi") or {}).get("intent") or []:
        d = parse_d(t.get("date"))
        txt = f"{t.get('topic') or ''} {t.get('category') or ''}"
        if d and d <= today and (today - d).days <= 30 and (t.get("score") or 0) >= 80 and any(re.search(p, txt, re.I) for p in THEMES):
            total += 3
            break
    days = next_renewal_days(a, today)
    if days is not None and days <= 90:
        total += 5
    elif days is not None and days <= 180:
        total += 3
    for x in (a.get("bf") or {}).get("signals") or []:
        d = parse_d(x.get("at"))
        if x.get("type") in ("broker_change", "carrier_switch") and d and d <= today and (today - d).days <= 182:
            total += 3
            break
    return min(BOOST_CAP, total)


def fresh_digest_signal(a, today):
    return any(it["age"] <= 14 for it in digest_new_act(a, today))


def score(a, today):
    """0-100 'call this account now' score. Recency and momentum dominate on purpose:
    6sense signals cool off fast, so a Decision-stage account that went quiet in March
    should rank below a Consideration account that has been on the site all week."""
    days = sorted({d for d in (parse_d(x) for x in a["dates"] + a["activity_dates"]) if d and d <= today})
    last = days[-1] if days else None
    since = (today - last).days if last else 999

    # 1. Recency (25)
    recency = 25 if since <= 7 else 20 if since <= 14 else 14 if since <= 30 else 8 if since <= 60 else 3 if since <= 90 else 0
    # 2. Momentum (15): distinct active days in last 30, plus acceleration vs the 30 before
    d30 = sum(1 for d in days if (today - d).days <= 30)
    d60 = sum(1 for d in days if 30 < (today - d).days <= 60)
    momentum = min(12, d30 * 3) + (3 if d30 > d60 and d30 >= 2 else 0)
    # 3. Buying stage (20) & 4. Profile fit (15)
    stage = STAGE_POINTS.get(a["stage"].lower(), 0)
    fit = FIT_POINTS.get(a["fit"].lower(), 0)
    # 5. High-intent pages (15): demo/contact > ad landing pages > any page; recent counts more
    def pages_matching(patterns, max_age=None):
        return [u for u in a["decoded_urls"]
                if any(p in page_path(u.get("decoded")) for p in patterns)
                and (max_age is None or ((pd := parse_d(u.get("date"))) and (today - pd).days <= max_age))]
    hand, ad = pages_matching(HAND_RAISE_PAGES), pages_matching(AD_LANDING_PAGES)
    hot = hand + ad
    if pages_matching(HAND_RAISE_PAGES, 30):
        pages = 15
    elif hand or pages_matching(AD_LANDING_PAGES, 30):
        pages = 10
    elif ad:
        pages = 6
    else:
        pages = 3 if a["decoded_urls"] else 0
    # 6. Volume (5): log-scaled so one huge account does not swamp everything
    volume = min(5, math.floor(math.log2(1 + a["signal_count"])))
    # 7. Competitor research (5): they are shopping, and probably on a competitor today
    comp = 5 if a["competitor_keywords"] else 0
    # Penalties: we already have a known person to call -> small bump instead
    known = 2 if a["contacts"] or a["form_fills"] else 0

    boost = signal_boost(a, today)
    total = min(100, recency + momentum + stage + fit + pages + volume + comp + known + boost)
    tier = "A - Call today" if total >= 65 else "B - This week" if total >= 45 else "C - Nurture" if total >= 28 else "D - Monitor"
    if since > 60 and tier[0] in "AB":  # gone quiet: good account, wrong moment
        tier = "C - Nurture"
    fresh_zi = fresh_digest_signal(a, today)
    if fresh_zi and tier[0] in "CD":   # a new ZoomInfo buying signal keeps it in This week for 14 days
        tier = "B - This week"
    action = recommended_action(a, since, hand, ad, d30, today)
    if fresh_zi and action[:2] in ("P3", "P4"):
        action = "P2 Follow up on ZoomInfo signal"

    return {
        "score": total,
        "tier": tier,
        "action": action,
        "last_activity": last.isoformat() if last else None,
        "days_since_activity": since if last else None,
        "active_days_30d": d30,
        "active_days_prev_30d": d60,
        "trend": "heating up" if d30 > d60 else "cooling" if d30 < d60 else "steady",
        "hot_pages": sorted({page_path(u.get("decoded")) for u in hot}),
        "breakdown": {"recency": recency, "momentum": momentum, "stage": stage, "fit": fit,
                      "pages": pages, "volume": volume, "competitor": comp, "known_contact": known, "boost": boost},
        "scored_on": today.isoformat(),
    }


def has_kw(a, *words):
    blob = " | ".join(a["keywords"] + [t["topic"] for t in a.get("surge_topics", [])]).lower()
    return any(w in blob for w in words)


def recommended_action(a, since, hand, ad, d30, today):
    """Same priority order as the dashboard's action engine, with a recency gate so a
    'Call today' never fires on an account that has been silent for months."""
    stage, fit = a["stage"].lower(), a["fit"].lower()
    comp = ", ".join(a["competitor_keywords"])
    fresh = since <= 30
    recent = lambda us: any((pd := parse_d(u.get("date"))) and (today - pd).days <= 30 for u in us)
    if recent(hand):
        return "P1 Call today: visited demo/contact page"
    if comp and stage == "decision":
        return f"P1 Close competitor deal ({comp})"
    if comp and stage == "consideration" and since <= 14:
        return f"P1 Displace {comp}"
    if stage in ("decision", "purchase") and fit == "strong" and fresh:
        return "P1 Push to close"
    if stage == "consideration" and d30 >= 3 and since <= 7:
        return "P1 Strike while hot"
    if recent(ad) and fit in ("strong", "moderate"):
        return "P2 Follow up on ad click (landing page)"
    if stage == "consideration" and a["signal_count"] >= 5 and fresh:
        return "P2 Run discovery"
    if has_kw(a, "benefit", "enrollment", "aca", "safe harbor", "401k", "retirement") and fresh:
        return "P2 Benefits pitch"
    if has_kw(a, "hris", "hcm", "migration", "ultimate software", "paycor", "workday") and stage == "consideration":
        return "P2 Migration conversation"
    if stage == "awareness" and a["signal_count"] >= 10 and fresh:
        return "P2 Warm up"
    if has_kw(a, "compensation", "pay transparency", "performance"):
        return "P3 Comp & performance pitch"
    if has_kw(a, "talent", "recruit", "candidate", "on boarding", "onboarding"):
        return "P3 Talent suite angle"
    if has_kw(a, "engagement", "communication", "retention", "culture"):
        return "P3 Engagement pitch"
    if has_kw(a, "airbase", "corporate card", "expense"):
        return "P3 Spend management (Airbase) angle"
    if fit == "strong":
        return "P3 Early nurture"
    return "P4 Monitor"


def is_removed(a):
    """Removed on the dashboard (🗑 Remove account) and not restored since. Still scored and kept, just not listed."""
    return bool(a.get("removed_at")) and a["removed_at"] > (a.get("restored_at") or "")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("json_file")
    ap.add_argument("--today", help="YYYY-MM-DD (default: today)")
    ap.add_argument("--top", type=int, default=20, help="rows to print (default 20)")
    ap.add_argument("--out", help="write here instead of overwriting the input")
    ap.add_argument("--no-dashboard", action="store_true", help="skip building <name>_dashboard.html")
    args = ap.parse_args()

    src = Path(args.json_file)
    today = parse_d(args.today) if args.today else date.today()
    data = json.loads(src.read_text(encoding="utf-8"))

    # junk rows the .msg parser sometimes produces
    data = {k: v for k, v in data.items()
            if not k.lower().startswith(("3 web visits",)) and "known contact" not in k.lower()}

    accounts = {}
    for key, acc in data.items():
        acc = clean(dict(acc, company=acc.get("company") or key))
        canon = ALIASES.get(acc["company"], acc["company"])
        if canon in accounts:
            if acc["company"] == canon:  # canonical arrived after its alias: swap so its name wins
                acc, accounts[canon] = accounts[canon], acc
            merge_into(accounts[canon], acc)
        else:
            if acc["company"] != canon:
                acc["aliases"] = sorted(set(acc.get("aliases", [])) | {acc["company"]})
                acc["company"] = canon
            accounts[canon] = acc

    for a, b in POSSIBLE_DUPLICATES:
        if a in accounts and b in accounts:
            accounts[a].setdefault("possible_duplicate_of", [])
            accounts[b].setdefault("possible_duplicate_of", [])
            if b not in accounts[a]["possible_duplicate_of"]:
                accounts[a]["possible_duplicate_of"].append(b)
            if a not in accounts[b]["possible_duplicate_of"]:
                accounts[b]["possible_duplicate_of"].append(a)

    for acc in accounts.values():
        acc["priority"] = score(acc, today)

    ranked = sorted(accounts.values(), key=lambda a: (-a["priority"]["score"], a["company"].lower()))

    # field order: the things you look at first, then the history
    order = ["company", "priority", "stage", "fit", "reach", "website", "signal_count", "web_visits",
             "competitor_keywords", "keywords", "surge_topics", "zi", "bf", "contacts", "form_fills", "decoded_urls",
             "activity_date", "email_date", "_latest_date", "dates", "activity_dates", "source_files",
             "aliases", "possible_duplicate_of", "six_qa_on", "past_process", "past_process_on", "worked_on", "notes",
             "removed_at", "restored_at"]
    out = {a["company"]: {**{k: a[k] for k in order if k in a}, **{k: v for k, v in a.items() if k not in order}}
           for a in ranked}

    dst = Path(args.out) if args.out else src
    if dst == src:
        shutil.copy2(src, src.with_suffix(".json.bak"))
    dst.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    csv_path = dst.with_name(dst.stem + "_target_now.csv")
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Rank", "Company", "Score", "Tier", "Action", "Stage", "Fit", "Last activity",
                    "Days since", "Active days (30d)", "Trend", "Competitors", "Hot pages", "Top keywords", "Website"])
        for i, a in enumerate([a for a in ranked if not is_removed(a)], 1):
            p = a["priority"]
            w.writerow([i, a["company"], p["score"], p["tier"], p["action"], a["stage"], a["fit"],
                        p["last_activity"], p["days_since_activity"], p["active_days_30d"], p["trend"],
                        "; ".join(a["competitor_keywords"]), "; ".join(p["hot_pages"]),
                        "; ".join(a["keywords"][:6]), a["website"]])

    template = Path(__file__).with_name("dashboard_template.html")
    html_path = None
    if not args.no_dashboard and template.exists():
        html = template.read_text(encoding="utf-8")
        marker = "/*__EMBEDDED_DATA__*/null"
        assert marker in html, "dashboard_template.html is missing the data marker"
        payload = json.dumps(out, ensure_ascii=False).replace("<", "\\u003c")
        stamp = datetime.now().astimezone().isoformat(timespec="seconds")
        page = html.replace(marker, payload, 1).replace("const PUBLISHED_AT = null;", f"const PUBLISHED_AT = {json.dumps(stamp)};", 1)
        # _share.html: the page fragment claude.ai publishes (it adds its own <html>/<head>)
        share_path = dst.with_name(dst.stem + "_share.html")
        share_path.write_text(page, encoding="utf-8")
        # _dashboard.html: the same page wrapped as a normal file you open from disk
        html_path = dst.with_name(dst.stem + "_dashboard.html")
        html_path.write_text('<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n'
                             '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n</head>\n<body>\n'
                             + page + '\n</body>\n</html>\n', encoding="utf-8")

    removed = [a for a in ranked if is_removed(a)]
    ranked = [a for a in ranked if not is_removed(a)]
    tiers = {}
    for a in ranked:
        tiers[a["priority"]["tier"]] = tiers.get(a["priority"]["tier"], 0) + 1
    print(f"{len(data)} rows in -> {len(accounts)} accounts out (scored as of {today})"
          + (f", {len(removed)} removed on the dashboard and not listed" if removed else ""))
    print("  " + " | ".join(f"{t}: {n}" for t, n in sorted(tiers.items())))
    print(f"  wrote {dst}\n  wrote {csv_path}" + (f"\n  wrote {html_path}" if html_path else "") + "\n")
    print(f"{'#':>3} {'Score':>5}  {'Company':<38} {'Stage':<13} {'Fit':<9} {'Last':>10} {'30d':>3}  Action")
    for i, a in enumerate(ranked[: args.top], 1):
        p = a["priority"]
        print(f"{i:>3} {p['score']:>5}  {a['company'][:38]:<38} {a['stage']:<13} {a['fit']:<9} "
              f"{p['last_activity'] or '-':>10} {p['active_days_30d']:>3}  {p['action']}")


if __name__ == "__main__":
    sys.exit(main())
