# 6sense "Target Now" scorer

`optimize_sixsense.py` cleans your accumulated 6sense JSON and ranks every account by **who to call now**.

## Daily use

1. Add new 6sense Outlook alerts to the JSON, the same way you do today (parser or dashboard drag-and-drop).
2. Run:
   ```bash
   python3 optimize_sixsense.py 6SENSE_Update_File.json
   ```
3. Open `6SENSE_Update_File_dashboard.html` (it's rebuilt on every run with the fresh data). Click the **Call today** stat card first, then **This week**.
   The same ranking is also in `6SENSE_Update_File_target_now.csv` and printed in the terminal.

## Dashboard (`dashboard_template.html`)
**Layout (v2):** four compact view cards (Call today · This week · Heating up · All accounts) with live counts, a search bar, a **Filters** panel (tier, signals, stage, fit, last active; active filters show as removable tags) and a sort menu, where company size sorts either way (**Size, largest first** / **Size, smallest first**, added 2026-11-13; accounts with no employee count go last in both). **Each account card** (updated 2026-11-12: no reason line, since the score carries the urgency; up to four badges, dropping 6QA, Check fit, sources and Past deal first so renewals and triggers always show; employee count under the name) has: the company name, which **opens their website** in a new tab (clicking anywhere else on the card opens the side panel), up to two badges and the score; the reason to call with the last 6sense activity date; and a row of **social buttons** (LinkedIn, Facebook, X, Instagram, TikTok, shown only when we have the link) with the **payroll vendor as its logo** on the right (ADP, Paycom, Paycor, Paychex, UKG, isolved, Rippling, ProLiant and Dayforce logos are embedded as `VENDOR_LOGOS`; other vendors show a 💼 name chip). Vendor sources: ZoomInfo tech stack, job-post sites and BenefitFlow filings first; the owner's **territory list** (`vendor_list`, the Salesforce "Current Provider" column, loaded 2026-11-12 for 145 accounts) fills in only when none of those found a vendor. A **Payroll vendor** pull-down in the Company tab (owner only; `vendor_manual`, `vendor_manual_on`) overrides every source when you learn the vendor on a call; **Not set** goes back to the automatic sources. An **Employees** box under it (owner and editors; `emp_manual`, `emp_manual_on`, added 2026-11-13) overrides ZoomInfo's head count, which often counts only one location; the card, size sort and size filter use it, and clearing the box goes back to ZoomInfo. The score does not use employee count, so Python and JS still match. **Hickory Foods** (Jacksonville, FL; ZoomInfo ID 1148931335) was added by hand on 2026-11-13 (`added_manually_on`) from a free ZoomInfo profile (under management), with 400 employees set by the owner (ZoomInfo says 13); it has no 6sense signals yet, so it scores 0 until alerts or ZoomInfo intent come in. The SDR sees the result but not the pull-down. "missing", "Other", "Unknown" and "New Business" are ignored, and "Paylocity" on a *Lost Client* row is skipped. `VENDOR_CANON` maps spellings (Ceridian → Dayforce, UltiPro → UKG…). Who to call, the next step and ✓ Worked are in the side panel only. Social links come from ZoomInfo `socialMediaUrls` (free in the same `enrich_companies` call for managed companies), with the prospect list's LinkedIn as a fallback; **↻ ZoomInfo: social links** in the ⚙ Owner menu backfills them for accounts that don't have them yet (managed companies only, no credits). Links are picked in this order: **added by you** (`social_manual`), **the company's own website** (`web_social`, from a scan of each homepage's links), **ZoomInfo** (`zi.firmo.social`), then the prospect list's LinkedIn. YouTube is a sixth button. The **Company** tab has a **Social pages** section listing each platform with its source: you can paste a link (**Add**) or hide a wrong one (✕, stored as `'-'`), and missing platforms get a faint **Find on…** web-search link (free, no API) for you and the SDR. Why now in the side panel is a bulleted list. ZoomInfo links and headings use the ZoomInfo logo, and the Benefits section uses the BenefitFlow logo (`ZI_LOGO` / `BF_LOGO`). Clicking a row opens a side panel (full screen on a phone) with tabs **Call prep** (notes, why now, who to call, past-sales mark, suggested openers), **Signals**, **Company** and **History**, plus ‹ › to move through the list (j / k, Esc to close). With the panel open, clicking another card switches the panel to that company (2026-11-13: the dimmed background no longer catches the click); clicking empty background, ✕ or Esc closes it. ✓ Worked in the panel moves on to the next account. Owner tools (imports, ZoomInfo / BenefitFlow refreshes, JSON backup) sit in the **⚙ Owner** menu, which the SDR doesn't see. One font throughout; colour is used for urgency (tier, next step) and the page-visit key.
A preview build sets `const PREVIEW = true` (banner, no sharing, "See it as your SDR" switch).

- There's no fixed "top 6" block: the stat cards and filters pick what the list shows, ranked by score.
- **Stat cards are filters**: clicking a card shows only its accounts in the table (click again to clear). The filter row under All accounts has buttons for A · Call today, B · This week, C · Nurture, D · Monitor, Heating up, Past sales, Trigger events and Competitor. Active 7 days, Renewing soon, ZoomInfo confirmed and ZoomInfo intent are cards only (set with `noChip` in `CARDS`).
  - Buttons can be combined. Tiers add together (A + B = everything to call this week), and the other buttons narrow the list (B · This week + Heating up = this-week accounts that are heating up).
- **Company size:** a **Sort: Company size** option (largest first) and a size filter in Filters (1–49, 50–199, 200–499, 500–999, 1,000+ employees, from ZoomInfo).
- **Side panel tabs** are Company, Signals, Call prep, History, and it opens on Company. Recent news in Signals has a 📰.
- **Search** (press `/`) covers company, keywords, pages visited and your notes. You can also filter by tier, stage, fit and **last active** (any time, last 7 / 30 / 60 / 90 days, or quiet 90+ days, counted from the last day 6sense saw activity). The last-active filter combines with the other filters and doesn't change the score.
- **✓ Worked**: marks an account as contacted today. It drops off the list for 7 days (there's no Hide worked button; searching for it still finds it), and comes back early (tagged *new since worked*) if 6sense records new activity.
- **Why now in Call prep** is kept short: recent activity, triggers, renewals, page visits, competitor and ZoomInfo intent, and news. ZoomInfo digest lines, the payroll vendor, 6QA and Bombora surge are left out there (they're in the Signals and Company tabs). A possible-Paylocity-client warning is always kept and names its source.
- **Notes** per account: one **AE notes** box at the top of Call prep (field `notes`), with an "updated" date (`notes_on`). The owner writes it; the SDR reads it. It's in 💾 Save JSON and the CSV, and the Python script keeps it. (An SDR notes box was tried and removed on 2026-11-12: personal Claude plans can't give the SDR editor access. The code still keeps any `sdr_notes` field, and an Editor who isn't the owner gets only ✓ Worked, never the owner tools, via `user.isOwner()`.)
- **🎯 Top 50** (owner): **☆ Add to Top 50** in the account panel marks an account for extra ABM effort (`top50`, `top50_on`). It shows a 🎯 Top 50 badge first on the account row and in the panel for everyone, and adds a **Top 50** filter button. Click again to remove it. It doesn't change the score.
- **⬆ Import** (header, next to ⚙ Owner; owner only; moved out of the Owner menu 2026-11-13): drop **ZoomInfo weekly digest** and **ZoomInfo breaking alert** emails here too (`.msg`, `.eml` or `.txt`). The page spots a digest by its "Target account" blocks, files it under the email's send date (from the email headers; today if it can't read one), matches each company to a dashboard account by website and then by name, and adds one dated `zid` entry per account (same parser rules as `tools/blend_book_digests.py`). The log lists the matches, the number of buying signals and any companies not on the dashboard (skipped) before you click ✓ Apply. Dropping the same week again is caught. Applying refreshes ZoomInfo and BenefitFlow for those accounts, like a 6sense import.
- **Add emails / JSON**: drop 6sense alert `.msg` files (or a JSON update) anywhere on the page. Emails already loaded are skipped: an email counts as a duplicate only when every account in it already has that day's activity. Outlook gives every alert the same file name, so names alone aren't used. Nothing is merged until you click Apply.
- **⬇ Call list CSV** exports the rows you're currently looking at.
- **Clear "Not in my book" / "Dup?"** (owner and editors only): click either badge (it shows a ×) to clear it for you and your SDR. It's saved as `book_ok_on` (the date) and `dup_ok` (the duplicate names you cleared), so later imports and Python runs don't bring it back. A new possible duplicate shows the badge again. Clearing "Not in my book" also takes the account out of the Not in my book count. Neither changes the score. Read-only viewers see the badges as plain labels.
- **🗑 Remove account** (owner and editors only, in the account detail under "Not your account?"): two clicks hide an account that isn't yours, for you and your SDR. It's stored as `removed_at` and kept in the data, so later 6sense emails about it merge into it and stay hidden (the import log lists them under "Kept hidden"), and ZoomInfo and BenefitFlow skip it. **Removed accounts (N)** at the bottom of the page lists them with **↩ Restore** (sets `restored_at`). **🗑 Clear this list** (two clicks) deletes removed accounts for good: their data is dropped and only a marker is kept (name, website, aliases, ZoomInfo ID, `removed_at`, `purged_on`), so later emails about them still stay hidden. They no longer appear in the list. The 35 accounts removed by 2026-11-12 were cleared this way. Read-only viewers never see the button or the list. The Python script keeps both fields and leaves removed accounts off the CSV and the printed ranking; they're still scored, so Python and JS stay the same.
- **On a phone**, each account is a card (score, company, Why now, next step, ✓ Worked), the stat cards and filter buttons sit in rows you swipe sideways, and an opened account is one column. Text uses one font and three sizes, and iPhone text enlarging is turned off.
- **Account detail order** (same on every screen; on wide screens it reads down the columns): Notes, Previous sales process, Company snapshot, Pages visited, Intent keywords, ZoomInfo intent, Trigger events, Recent news, Who to call (then known contacts), BenefitFlow benefits, Bombora surge topics, then Score breakdown, Last 13 weeks, duplicates and Remove account. Change it in `DETAIL_ORDER` in the template.
- The card layout is used up to 1000px wide (phones and tablets). On wider screens the table's long cells wrap, so Next step and ✓ Worked stay on screen; the Stage / Fit column hides below 1200px.
- **Pages visited colors** (explained under the list in each account): **red** = asked for us (demo, contact, pricing or quote page, the strongest buying signal), **gold** = came from an ad or campaign page (`/lp/`, `/learn-more`, `/demo/`), **teal** = general browsing. The same groups drive the Pages points in the score.
- **Score breakdown** shows one chip per factor (e.g. `Recency 20/25`). Darker green means closer to full points, white means none. A plain line underneath lists full, partial and missing factors. It only displays the score; it doesn't change it.
- Scores are recalculated against today's date every time you open the page, so the file never goes stale. Add `?today=YYYY-MM-DD` to the URL to see the ranking as of another day.

## Handing a blank copy to a peer
`peer_kit/Target_Now_Peer_Kit.zip` holds `Target_Now_Starter.html` (the dashboard with no accounts), `Target_Now_Setup_Guide.docx` (formatted setup guide) and `READ_ME_FIRST.txt` (plain-text copy). The peer connects ZoomInfo and BenefitFlow in their own Claude, opens Claude Code, attaches the starter and pastes the prompt from the readme. That publishes their own private copy, using their own connectors. Opened as a plain file, the starter shows the same steps with a Copy prompt button. On an empty dashboard a getting-started panel explains the first steps.
**Only rebuild the peer kit when the owner asks for it.** Dashboard changes don't update it automatically. To rebuild the starter: `echo '{}' > Target_Now.json && python3 optimize_sixsense.py Target_Now.json`, then copy `Target_Now_share.html` to `peer_kit/Target_Now_Starter.html` and re-zip.

## Sharing with your SDR
The run also writes `6SENSE_Update_File_share.html`. That's the same dashboard, published as a claude.ai page.
- The owner (and anyone you add as an Editor) can click **Worked**, write notes and import emails. Each change saves the page itself, and everyone with the link sees it.
- Anyone else with the link gets a read-only copy: the same ranking, reasons, pages and notes, plus the CSV export.
- To push a fresh JSON run, ask Claude to republish `_share.html` to the same link, or just drop the JSON on the shared page.

## ZoomInfo intent (Call today, This week and Heating up)
Each account can carry a `zi` block: `{company_id, name, location, employees, pulled_on, intent: [{topic, category, score, audience, date}], skipped?, note?}`.
- It's pulled through the ZoomInfo connector. Match accounts by website with `search_companies` (free), then call `enrich_company_signals` with `signalTypes: ["INTENT"]`, which is free for companies already under management.
- Accounts not under management are skipped and marked `skipped`, so no credits are spent without asking.
- The dashboard shows a "ZoomInfo:" line under Why now and a ZoomInfo section in the account detail. Accounts get a **✓ Confirmed** badge (and a filter card) when a ZoomInfo topic matches a 6sense keyword, Bombora surge topic or page visit on the same theme.
- ZoomInfo doesn't change the score.
- **Open in ZoomInfo:** accounts with a ZoomInfo company id get a **ZoomInfo ↗** link under the company name and an **Open in ZoomInfo ↗** button in the ZoomInfo section. It opens `app.zoominfo.com/#/apps/profile/company/<id>/overview` in a new tab. It's only a link: no ZoomInfo call or credits from the page, and the viewer must be signed in to ZoomInfo. Accounts get an id the first time a ZoomInfo refresh matches them.
- **Refresh from the page (owner only):** on the shared claude.ai page, **↻ ZoomInfo** in the header refreshes all Call today, This week and Heating up accounts. Each account's ZoomInfo section has its own **↻ Refresh ZoomInfo intent** button.
  - The page calls the owner's ZoomInfo connector (`mcp` capability: `search_companies` and `enrich_company_signals`). It checks management status first, which is free.
  - Refresh-all only pulls free accounts. On a single account that would cost credits, the button asks for a second click.
  - Results are saved to the page, so read-only viewers see them without needing ZoomInfo themselves.
- **Automatic on import:** when the owner applies new 6sense emails, every account in those emails gets its ZoomInfo data refreshed before the page saves, whatever its tier (highest score first).
  - Each import also catches up up to 40 other accounts (any tier, highest score first) whose ZoomInfo pull is more than 7 days old, so intent stays inside the 60-day window.
- **Daily auto-refresh** (owner only, free, no AI): the first time you open the page each day, it refreshes ZoomInfo (intent, news, Scoops, new leaders, contacts, snapshot) for every Call today, This week, Heating up and **Top 50** account not already pulled that day, 20 at a time, Top 50 first. Accounts that would cost credits are skipped. The header shows progress; keep the page open for a minute or two. It saves once at the end and won't run again that day (`ziDailyAuto`). The SDR's view never runs it.
- **Why still load the ZoomInfo digest emails:** about half the digest's buying signals can't come from the live connector: **named people visiting our website** and **named people researching a topic**. The connector's intent is company-level only and it has no website-visitor tool. Everything else in the digest (company intent, competitors, new leaders, M&A, hiring, funding) the live refresh also gets.
- **↻ ZoomInfo: all** (owner only, in the header) runs the same free refresh on every account not pulled in the last 7 days, whatever its tier, 20 accounts at a time with a pause between steps. Keep the page open; it saves once at the end. If ZoomInfo stops it (e.g. a rate limit), what was pulled is kept and clicking again continues. Accounts ZoomInfo can't match by website are retried after 30 days (`zi_checked_on`); accounts not under management are skipped and re-checked weekly (`zi.checked_on`).
- **ZoomInfo intent** stat card and filter button: every account with HR-related ZoomInfo intent in the last 60 days, any tier. Use it to find accounts that are quiet in 6sense but researching in ZoomInfo.
  - Only free accounts are pulled, and at most once a day per account.
  - If ZoomInfo fails, the email data still saves and the import log shows the reason.

## Trigger events (ZoomInfo)
`zi.scoops` (`[{date, summary, types, link}]`) and `zi.new_leaders` (`[{name, title, person_id, window_days}]`) feed a **🔔 Trigger** badge, the top of Why now, a Trigger events filter card and a detail section.
- **Leadership change:** ZoomInfo Scoops of type Executive Move, New Hire, Promotion, Management Move or Left Company, from the last 120 days.
- **New leader:** a free `search_contacts` by `positionStartDateMin`, run twice (180 days, then 90 days) for CEO/President/COO, CFO/Controller/Finance, HR/People/Talent/Benefits and Payroll titles. Practice titles like "Financial Services" are excluded. It returns names and titles only, with no contact details.
- **Vendor clue:** the host of a Scoop's job-post link, e.g. `recruitingbypaycor.com`, means they likely use Paycor.
- **Hiring surge:** shown in the account detail only.
- Each new leader's **name is a link** (with a blue **in** badge) that searches LinkedIn for their name plus the company name, in Why now and the account detail. There's no ZoomInfo credit or API call. An exact profile URL would come from `enrich_contacts` with `externalUrls`, which costs about 1 ZoomInfo credit per person, so it isn't built in.

## Who to call (ZoomInfo)
`zi.people` (`[{name, title, person_id, accuracy}]`) comes from a free `search_contacts` on HR, payroll, finance and executive titles, run with no start-date filter and sorted by accuracy.
- The dashboard picks up to 3 buyers per account: the best **HR** leader, then **Payroll**, then **Finance** (CFO, Controller or VP Finance). An **Executive** fills in when one of those is missing. Non-buyer titles (Inventory Controller, "Financial Services" practice roles, assistants) are skipped, and new leaders rank first within their role.
- They appear as 👤 under the company name in the table and in a "Who to call" section in the account detail. Each name is a LinkedIn search link.
- Every person shows ZoomInfo's **accuracy score** (70–99). Under 80 is dimmed with a "check LinkedIn first" hint.
- The ZoomInfo refresh buttons and email auto-refresh re-run this search. Activity tracking stays in Salesforce.

## Company snapshot, payroll vendor and news (ZoomInfo)
- **Snapshot** (`zi.firmo`) comes from `enrich_companies`, which is free for companies under management. It covers industry, employees, revenue range, HQ, locations, founding year, type and a one-line description. It shows as a line under the company name plus a Company snapshot section in the detail view.
- **Payroll vendor** (`zi.payroll_tech.vendors`) comes from free `search_companies` calls filtered by ZoomInfo tech-product ids (`PAYROLL_TECH` in the template) for ADP, Paychex, Paycor, UKG, Paycom, Paylocity, isolved and Dayforce. Vendor clues from job-post links are added too. It shows as a 💼 chip and a "Payroll: …" Why now line marked "confirm in Salesforce". A Paylocity hit shows a "may already be a client" warning.
- **News** (`zi.news`) comes from `enrich_company_signals` NEWS in the same call as intent. Only items from the last 12 months that mention the company by name are kept. The latest item from the last 60 days goes in Why now, and up to 4 items with links in the detail view. Acquisition news becomes a 🔔 Acquisition trigger.
- **Careers** (in the snapshot, or on its own when there's no snapshot): a **Latest job post** link when ZoomInfo has an Open Position Scoop with a link (it's often the company's job board, e.g. recruitingbypaycor.com), plus a **Find careers page** web-search link built from the company name and website. Both are free: no ZoomInfo call, no credits.
- All three are refreshed by the ZoomInfo buttons and email auto-refresh. They don't change the score.

## BenefitFlow: benefits renewal, broker and contacts
Each account can carry a `bf` block (`employer_id, broker, broker_years, carrier, funding, renewal, eligible, plan_types, peo, secondary_broker, signals, people, revealed, pulled_on`).
- **Where it comes from:** the owner's BenefitFlow connector. Per account, the page runs one free `search_employers` by website (falling back to the company name) with partners and signals, then one free `search_contacts` for HR, Benefits, Finance and Executive people. `enrich_companies` is not used (it spends enrichment credits).
- **Benefits section** in the account detail: renewal date (red when 90 days or less away), broker and years with them, other firms on the filings (e.g. ADP), carrier, insured vs. self-funded, benefit-eligible employees, plan lines, PEO, BenefitFlow intent, and BenefitFlow signals.
- **Triggers:** renewal within 90 days, broker change, carrier switch and M&A become 🔔 triggers. Renewal also gets a 📅 badge, a **Renewing soon** card and a **Renewing ≤ 90 days** filter button. Renewals 3–6 months out show as a plain Why now line.
- **Payroll vendor:** a PEO or payroll firm on the benefit filings (ADP, Paychex, Insperity…) is added to the 💼 Payroll chip.
- **Who to call** merges ZoomInfo and BenefitFlow people by name and labels the source. BenefitFlow names link to their exact LinkedIn profile. Extra contacts sit under "N more HR, finance and exec contacts".
- **Get email/phone** (owner only): the first click is a free price check; if BenefitFlow charges (1 contact credit per person), the button turns yellow and a second click reveals. Contacts your team already unlocked are free and reveal on the first click. Revealed email and phone are saved to the page, so the SDR sees them.
- **Refresh:** **↻ BenefitFlow** in the header (Call today, This week and Heating up accounts not pulled today), a per-account **↻ Refresh BenefitFlow** button, and automatically when emails are imported: every account in the new emails, whatever its tier (once a day), plus a catch-up of every Call today, This week and Heating up account that has no BenefitFlow data or hasn't been checked in 30 days (up to 60 accounts per import, highest score first). Calls are spaced about 1.3 s apart to stay under BenefitFlow's 50-calls-a-minute limit (two calls per account). Daily limit: 500 calls per user.
- **Open in BenefitFlow:** the BenefitFlow logo on the Benefits heading opens `benefit-flow.com/search/employer/<employer_id>` (set by `BF_URL_TEMPLATE`). It's only a link; the viewer must be signed in to BenefitFlow. The ZoomInfo logo on the Company snapshot and ZoomInfo intent headings does the same for ZoomInfo.
- BenefitFlow doesn't change the score.

## Suggested openers (Call prep)
Built by rules from the account's own data, with no AI (`openerPlan` in the template). Up to three openers, each with a Copy button:
- **Latest event:** leads with the newest real event and its details. Events, strongest first: new HR, payroll, finance or exec leaders; M&A; funding; leadership news; expansion or earnings news headlines (quoted); named open roles; hiring pushes; BenefitFlow growth or funding signals. Events are from the last 60–120 days; acquisitions count for 12 months and add "On top of the acquisition…". If the person being called is the new leader, it opens with congrats.
- **Industry:** state, size and industry from the ZoomInfo snapshot.
- **Competitor:** what teams on their payroll vendor usually say (or, when they've only researched one, a "what are you running today?" question).
- The middle sentence turns their research into a plain pain (`OP_TOPIC_PAIN`, e.g. COBRA → "COBRA and benefits continuation"). It never says we saw them researching, and **page visits are never mentioned**. Finance leaders and finance hires get a payroll-cost angle.
- The closing question uses their current payroll vendor when known (`OP_VENDORS`).
- **Talking points, newest first** sit underneath with dates and source links. These include the events, intent and competitor research (marked "don't mention"), the payroll vendor, and the BenefitFlow renewal as an optional "If useful" line.
- Openers don't change the score.
- **✨ AI openers (owner only, the one exception to "no AI tokens"):** on Call today and Top 50 accounts, a **✨ AI openers** button beside "Suggested openers" asks Claude (quick model) for three openers. It uses the **owner's** Claude account: an AI call always spends the account of whoever clicks, so only the owner gets the button. The result is saved to the page (`ai_openers: {on, at, items:[{angle, text}]}`), so the SDR sees it without a Claude account. It's capped at 15 a day per browser (`AI_DAILY_CAP`), and each call is about 600 tokens in and 250 out. Claude gets the same facts as the rule-built openers (`aiPrompt`), never notes, with the same never-mention rules. The first click asks you to allow Claude for the page. The rule-built openers stay underneath.

## Previous sales process (owner, manual)
- In an account's detail, **☆ Mark as past sales process** sets `past_process: true` and `past_process_on`. Write the details in the regular **Notes** box.
- The account then shows a **★ Past deal** badge, a "★ Past sales process: see notes" line in Why now, and a Past sales filter. The CSV has a Past sales process column.
- The old separate sales-history box is gone. Any text it held (`history_note`) is moved into Notes as "Sales history: …" the first time the page or the Python script reads it, so nothing is lost.

## Cost
- The page's buttons, email auto-refresh and LinkedIn links run in the browser against ZoomInfo directly. Apart from the owner-only ✨ AI openers button, they use **no AI tokens** and only free ZoomInfo calls (search, plus enrichment of companies already under management).
- Asking Claude in chat to refresh or republish does use tokens. Use the page buttons for day-to-day work, and start a fresh session for dashboard changes.
- Refresh buttons and email auto-refresh pull Scoops in the same free call as intent, then run the leader search. Triggers don't change the score.

The scoring rules are written twice, once in the script and once in the template. If you change one, change the other.

Re-running is safe: the output is the same each time, and a `.bak` copy of the previous file is kept. The JSON is still a flat `{company: account}` dict, so the dashboard keeps working.

## What it fixes on each run
- Merges known duplicate companies (`ALIASES`) and flags likely ones (`possible_duplicate_of`).
- Gives every record the same fields. For records without dates, `activity_date` and `_latest_date` are filled in from their activity history.
- Removes empty `source_files` entries. These made the dashboard's duplicate-upload check misfire.
- Fixes contact names that had part of the job title stuck to them (e.g. "Natalie Vazquez Account" / "Manager").
- Rebuilds `competitor_keywords` from all keywords, without regard to upper/lower case.
- Sorts accounts best-first, with the `priority` block at the top of each.

## Score (0-100)
| Factor | Pts | Why |
|---|---|---|
| Recency of last activity | 25 | Intent goes cold within weeks |
| Momentum (active days in last 30, and whether that's rising) | 15 | Repeated activity matters more than one spike |
| Buying stage | 20 | Purchase > Decision > Consideration > Awareness > Target |
| Profile fit | 15 | Strong > Moderate > Weak |
| High-intent pages | 15 | demo/contact > ad landing pages > any visit |
| Signal volume (log-scaled) | 5 | |
| Competitor research | 5 | Shows they're shopping, so there's a chance to displace a competitor |
| Known contact / form fill | +2 | |
| On our site (added 2026-11-14) | +4 / +2 | A visit to our own website in the last 7 days (+4) or 30 days (+2). Off-site keyword research doesn't count here, so a direct visit scores a little higher. Shown as **On our site** in the score breakdown. |
| ZoomInfo + BenefitFlow boost | up to +20 | Weekly-digest buying signals (competitor 8, site visit 8, payroll/benefits/HR research 6, other research 4, new leader 5, M&A 4, hiring surge 3; full for 7 days, half to 14, quarter to 30; leaders/M&A/hiring last longer), ZoomInfo HR intent 80+ in 30 days +3, BenefitFlow renewal ≤90 days +5 / ≤180 +3, broker or carrier change in 6 months +3 |

Tiers: **A ≥65 Call today · B ≥45 This week · C ≥28 Nurture · D Monitor**. An account with no activity for 60+ days is capped at C. A new ZoomInfo digest buying signal in the last 14 days keeps an account in This week at least, and turns a P3/P4 next step into "Follow up on ZoomInfo signal".

Change the weights, competitor list, page patterns and aliases in the config block at the top of the script.

## Working notes for the next session

**Live dashboard:** https://claude.ai/artifact/Us82tGvEWGgk8eCeUpbDkX. It's owned by Luke and shared view-only with the SDR. The page saves itself, so **always re-read it before publishing** and build from its data. Publish without `capabilities`, so its current permissions stay (ZoomInfo: search_companies, enrich_company_signals, search_contacts, enrich_companies; BenefitFlow: search_employers, search_contacts, get_contact; artifact, downloads, user, sample). `sample` (✨ AI openers) was added on 2026-11-12; if you ever pass `capabilities`, restate all of them.

**State on 2026-11-12:**
- 293 records: 258 active accounts, plus 35 removed accounts deleted for good on 2026-11-12 (only hidden markers remain).
- Seven ZoomInfo weekly digests (9/29–11/10) are loaded in `zid`. The 9/29, 10/6 and 10/13 emails were added through the page's importer after fixing it to skip blank lines between a company name and its "Target account" heading.
- The blended score is live (6sense base plus up to +20 for ZoomInfo/BenefitFlow, and a floor that keeps a fresh digest signal in This week).
- The scorecard section was removed at the owner's request.

**Tools (`tools/`):**
- `blend_book_digests.py WORKDIR` merges a new prospect-list export and/or new digest `.msg` files into the live data. It's safe to re-run: the same digest week is never loaded twice, and live notes, Worked marks, removals and revealed contacts are never overwritten. Its docstring describes the folder layout.
- `inject.py TEMPLATE LIVE.html OUT.html` rebuilds the page from the template using the live page's data.
- `parity.js DIR` checks that Python and JS scores match. Before running it, run `optimize_sixsense.py` on the data in `DIR/py/T.json`.
- `crawl_socials.py LIVE_OR_OUT.html OUT.json` reads every account's homepage and pulls social profile links from it (regex only, 12 at a time, ~40 s for 250 sites). It needs open network access, so the cloud environment has to be switched to unrestricted while it runs, then back to limited. `add_web_social.py PAGE.html OUT.json` writes the results into a built page as `web_social` (it drops known junk links). First run 2026-11-12: 210 of 252 sites read, 177 accounts got links.
- `add_vendor_list.py PAGE.html MATCH.json` writes territory-list providers into a built page as `vendor_list` (name matching is done first; ambiguous matches are left out).
- `prodtest.js DIR` loads `DIR/prod.wrap.html` as the owner (desktop) and as the SDR (phone).

**Not done yet:**
1. An owner-menu import for an updated prospect list (ZoomInfo digests can now be dropped on the page), so updates no longer need a session.
2. A combined "Update ZoomInfo + BenefitFlow" button, with BenefitFlow paced at about 100 accounts a day.
3. Merging duplicates by website / ZoomInfo ID when emails are imported, plus an owner-only "Merge into…" button. Duplicates still showing: Hillpointe LLC (same company as the removed Hillpointe), Dipasqua Enterprises, Inc. = Di Pasqua Enterprises, and Flextrude Aluminum Shapes = Flextrude. The list rows for Flextrude and Zonal point to UK companies.
4. Ask the 6sense admin to limit the Hot Accounts alert to CRM-owned accounts.

## 2026-11-13: HR tech, BenefitFlow intent, Company tab order

- **Company tab order:** Company snapshot, then **Benefits (BenefitFlow)**, then Payroll vendor, Employees, Social pages (`DRAWER_TABS.company.parts`).
- **HR tech rows in the snapshot** (`zi.hr_tech`: `hrms`, `hr_other`, `ats`, `on`), under Payroll / HR: **HR system**, **Other HR software**, **Applicant tracking**, the same categories as the Technologies tab in ZoomInfo. Filled by **↻ ZoomInfo: HR tech** in the ⚙ Owner menu. The connector can't list one company's technologies, so the page (1) looks up every product in each category with ZoomInfo `lookup` (`fieldName: tech-products`, `parentCategory: Human Resources`, `category: <name>`, which ZoomInfo requires; 364 products in HR systems; the product list is cached in this browser for 30 days), then (2) asks `search_companies` which of our companies use them, 25 products × 50 companies a search, splitting hits in half until each is one product. All free. Accounts are re-checked after 30 days (`HR_TECH_STALE_DAYS`). Each category is saved as soon as it finishes (`zi.hr_tech.done[<key>]`), so a run that stops part-way keeps what it found and the next click picks up the rest. The three rows always show in the snapshot ("Not checked yet" until the button has run). The button never quits silently: a click while another ZoomInfo refresh is running, a missing lookup permission or a lost connection each say so in the status line. A first live run on 11/13/2026 saved nothing because the earlier version saved only after all three categories finished. `lookup` was added to the page's ZoomInfo permissions for this. Checked against the live connector on 11/13/2026: the lookup answer is `{"tech-products":[{data:[{id, attributes:{name}}]}]}`, and a search of InterMed (49285305) with Paycom's id (23448) matched, as ZoomInfo's Technologies tab shows. If ZoomInfo returns no product list, the button says so and changes nothing.
- **🔥 BF Active / BF Intensive badge** on the card when BenefitFlow's `compositeIntentScore` is Active or Intensive (`bfIntentStrong`). Light stays in the Benefits section only. Badge only: the score is unchanged, so Python and JS still match. BenefitFlow's intent *topics* are not exposed by its connector, only the level.
- **↻ BenefitFlow: all accounts** (⚙ Owner): every account not checked in 30 days, hottest first, up to 200 a click (`BF_ALL_MAX`, about 400 of BenefitFlow's 500 calls a day); the status line says how many are left. Free name searches only; BenefitFlow `enrich_companies` (which uses enrichment credits) is not used.

## 2026-11-13: Web news triggers (Signals tab)

- **🔎 In the news · web search** sits under Trigger events on the Signals tab (`s-web`). Up to 3 items per account (`WEB_NEWS_MAX`), newest first; undated items ("recent") sort after dated ones. Each shows the date, a kind (Leadership change, New location, Growth, Award, Acquisition, Funding, Hiring, Partnership, Other), what happened and a source link.
- Data: `a.web_news = { on, items: [{ date, kind, text, url, src, added_by? }] }`. Newer `on` wins on merge (JS `mergeAccount`, Python `merge_into`). The score does not use it, so Python and JS still match.
- **Where the news comes from:** the page cannot search the web and makes no AI calls for this. Claude runs the web searches in a session and saves them to `data/web_news_<date>.json`, then `tools/add_web_news.py <json> <built html>` loads them (owner-added items are kept). Only items dated within about 12 months are kept, each with its link; accounts searched with nothing recent get `[]` and show "No news found yet" with the checked date.
- **Owner and editors** can add an item by hand (`+ Add a news item`: date, kind, text, link) or remove one (✕). The SDR sees the list only.
- First batch (11/13/2026): the 9 Call today accounts. CAMPUS USA's three items came from the owner's own research chat (CEO succession 10/6/2026, $4B assets, Leesburg branch 10/9/2025); Coastal (TCS acquisition closed 1/14/2026), Frontline Performance Group (Shiji CheckMax integration, July 2026), Entec (Plastics News 2026 honoree), Park Square Homes (Highfield at Twisted Oaks), Quality Labor Management (2026 ClearlyRated award). InterMed, Orthomerica and Ocala Eye: nothing dated recent enough (InterMed's PE deal was January 2023, its CEO hire May 2024).

### News refresh queue (added 2026-11-13)

- **↻ Request news refresh** (owner and editors) in each account's In the news block sets `web_news.requested_on` (and `req_changed`, so the request survives a merge); **Cancel** removes it.
- **⚙ Owner → 🔎 In the news: refresh queue (N)** shows the queue (`newsQueue()`): accounts with an open request, plus **Call today** accounts never searched or not searched in 14 days (`NEWS_STALE_DAYS`). So every account that moves into Call today after a 6sense or ZoomInfo import joins the queue on its own. **Copy request** puts a ready-to-paste line for a Claude session on the clipboard.
- The page itself never searches the web (no web access, and no AI use for this). A Claude session runs the searches: `python3 tools/news_queue.py <live.html>` prints the same queue, the findings go in `data/web_news_<date>.json`, and `tools/add_web_news.py` loads them (which clears the requests, since `on` is then newer).
- Second batch (11/13/2026): 40 Top 50 accounts, saved in `data/web_news_2026-11-13_top50.json`; 23 had dated, linked news. 49 accounts have now been searched, and 29 have news.


## 2026-11-13: ZoomInfo breaking alerts, ⬆ Import in the header, 🎨 Look menu

- **ZoomInfo breaking alerts** (the one-event "🚨" emails) load through ⬆ Import like digests. Three kinds are read: **Key Contact Visit** (a named person on our site, with the pages), **Executive Leadership Change** (new leader, plus the email, mobile, LinkedIn and "Insights" lines ZoomInfo includes) and **Competitive Threat** (competitor research). Other alert kinds are skipped with a log line naming them.
- Each alert becomes one `zid` entry: `{date, cat: 'Breaking alert · <kind>', src: 'alert', items: [{window: 'Breaking alert', text, kind, person?: {name, title, email, phone, linkedin}, pages?, notes?, competitor?, size?}]}`. The `text` is worded exactly like the weekly digest line ("<name>, <title>, has visited a webpage", "<name>, <title>, has joined the company.", "Competitive Alert: Actively researched competitor - <vendor>"), so the existing digest scoring applies unchanged and a later digest repeating it is marked "(repeat)". Python and JS scores still match (`parity.js`: 294 accounts, 0 differences with the five test alerts loaded).
- Date: the email's send date (internet headers, else the Outlook property table via `msgSentDate`; most saved alerts have no headers). Matching: logo domain, then name, then the name squeezed together against company names and website names ("Visit Orlando" → VisitOrlando / visitorlando.com). Alerts for companies not on the dashboard are skipped and listed.
- Duplicates: keyed by date + line (`zidKey` in JS, `zid_key` in Python), so an alert and a digest on the same day are both kept, and dropping the same alert twice is caught. Digest checks ignore alert entries.
- Signals tab: the section is now **ZoomInfo digests & alerts**; alerts show ⚡, the contact details (as selectable text, LinkedIn as a link), pages visited and insights.
- Effect of the first five test alerts (11/13 data, not loaded on the live page yet): Visit Orlando 30 → 38 (This week, new VP People & Culture visit), Fleet Landing 40 → 45 (CFO hire now a digest-style signal), Ocala Eye 67 → 65 (the alert dates the visit to 10/27, a week before the digest showed it), FPG and Dan Newlin unchanged.
- **🎨 Look** (header, everyone including read-only viewers): Light / Dark / Auto (follows the device or claude.ai theme) and Green / Blue / Purple / Charcoal. Saved per browser in `localStorage` (`tn_look`), applied before the page paints; nothing is saved to the page and other viewers are unaffected. Implemented as CSS token overrides on `<html data-tn-dark data-tn-accent>`; with neither set the page looks exactly as before. Hard-coded greens were moved to tokens (`--spark-1`, `--chip-1`, `--brand-line`, …) with their old values.

## 2026-11-13: Peer kit rebuilt

- `peer_kit/` was rebuilt on request for a new AE starting from a blank slate: `Target_Now_Starter.html` (current dashboard, no accounts), a new `Target_Now_Setup_Guide.docx` written for a first-time user (setup, daily routine, page tour, imports incl. ZoomInfo 🚨 alerts, score, credits, backups, troubleshooting, and a standing-instructions block for asking Claude to change the dashboard or run the In the news refresh), `READ_ME_FIRST.txt`, zipped as `Target_Now_Peer_Kit.zip`.
- The starter's built-in setup prompt (`SETUP_PROMPT`) now passes `"sample":{}` (✨ AI openers) and ZoomInfo `lookup` (HR tech), matching the live dashboard. The getting-started steps point to **⬆ Import**. These only show on an empty dashboard, so the live page is unaffected.
- Checked: none of the owner's 294 account names appear in the starter; it loads with no errors both as a plain file (setup steps + Copy prompt) and as a fresh owner page.

## 2026-11-14: Website visits score a little higher

- New score part **On our site** (`web` in the breakdown, max 4): +4 when someone was on our website in the last 7 days, +2 within 30 days, from the page-visit dates in the 6sense emails. Keyword research elsewhere earns nothing here. Same in Python (`score`) and JS (`score`); `parity.js`: 294 accounts, 0 differences.
- Only 5 accounts had a site visit in the last 30 days on 11/14, so the change is small: Frontline Performance Group 85→89, InterMed 76→80 (now above Entec Polymers 77), Ocala Eye 67→69, Real Life Christian Church 59→61, Park Place Behavioral Health Care 43→45 (Nurture → This week).
- Background (6sense's own docs): their intent score predicts an opportunity in the next 90 days from web visits, keyword research on their B2B network, third-party intent and CRM/marketing activity; weights aren't published. Buying stage is their summary of all of it. Discussed but not done yet: fading demo/contact/pricing visits after 90 days, counting keyword-only days for less, weighting 6sense stage more, adding Airbase to the competitor list.
