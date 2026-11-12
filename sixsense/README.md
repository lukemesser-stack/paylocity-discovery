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
**Layout (v2):** four compact view cards (Call today · This week · Heating up · All accounts) with live counts, a search bar, a **Filters** panel (tier, signals, stage, fit, last active; active filters show as removable tags) and a sort menu. Each account is a three-line row: name, up to two badges, a signal strip (6s · ZI · BF · Web, filled when that source has something current) and the score; the strongest reasons to call with the last 6sense activity date on the right; who to call and the next step. Why now in the side panel is a bulleted list. ZoomInfo links and headings use the ZoomInfo logo, and the Benefits section uses the BenefitFlow logo (small PNGs embedded in the template as `ZI_LOGO` / `BF_LOGO`). Clicking a row opens a side panel (full screen on a phone) with tabs **Call prep** (suggested opener, notes, why now, who to call, past-sales mark), **Signals**, **Company** and **History**, plus ‹ › to move through the list (j / k, Esc to close). ✓ Worked in the panel moves on to the next account. The suggested opener is built from rules and the account's signals, with no AI. Owner tools (imports, ZoomInfo / BenefitFlow refreshes, JSON backup) sit in the **⚙ Owner** menu, which the SDR doesn't see. One font throughout; colour is used for urgency (tier, next step) and the page-visit key.
A preview build sets `const PREVIEW = true` (banner, no sharing, "See it as your SDR" switch).

- There's no fixed "top 6" block: the stat cards and filters pick what the list shows, ranked by score.
- **Stat cards are filters**: clicking a card shows only its accounts in the table (click again to clear). The filter row under All accounts has buttons for A · Call today, B · This week, C · Nurture, D · Monitor, Heating up, Past sales, Trigger events and Competitor. Active 7 days, Renewing soon, ZoomInfo confirmed and ZoomInfo intent are cards only (set with `noChip` in `CARDS`).
  - Buttons can be combined. Tiers add together (A + B = everything to call this week), and the other buttons narrow the list (B · This week + Heating up = this-week accounts that are heating up).
- **Search** (press `/`) covers company, keywords, pages visited and your notes. You can also filter by tier, stage, fit and **last active** (any time, last 7 / 30 / 60 / 90 days, or quiet 90+ days, counted from the last day 6sense saw activity). The last-active filter combines with the other filters and doesn't change the score.
- **✓ Worked**: marks an account as contacted today. It drops off the list for 7 days (there's no Hide worked button; searching for it still finds it), and comes back early (tagged *new since worked*) if 6sense records new activity.
- **Notes** per account, saved in the browser and included in 💾 Save JSON. The Python script keeps `worked_on` and `notes` too.
- **Add emails / JSON**: drop 6sense alert `.msg` files (or a JSON update) anywhere on the page. Emails already loaded are skipped: an email counts as a duplicate only when every account in it already has that day's activity. Outlook gives every alert the same file name, so names alone aren't used. Nothing is merged until you click Apply.
- **⬇ Call list CSV** exports the rows you're currently looking at.
- **🗑 Remove account** (owner and editors only, in the account detail under "Not your account?"): two clicks hide an account that isn't yours, for you and your SDR. It's stored as `removed_at` and kept in the data, so later 6sense emails about it merge into it and stay hidden (the import log lists them under "Kept hidden"), and ZoomInfo and BenefitFlow skip it. **Removed accounts (N)** at the bottom of the page lists them with **↩ Restore** (sets `restored_at`). Read-only viewers never see the button or the list. The Python script keeps both fields and leaves removed accounts off the CSV and the printed ranking; they're still scored, so Python and JS stay the same.
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

## Previous sales process (owner, manual)
- In an account's detail, **☆ Mark as past sales process** sets `past_process: true` and `past_process_on`. Write the details in the regular **Notes** box.
- The account then shows a **★ Past deal** badge, a "★ Past sales process: see notes" line in Why now, and a Past sales filter. The CSV has a Past sales process column.
- The old separate sales-history box is gone. Any text it held (`history_note`) is moved into Notes as "Sales history: …" the first time the page or the Python script reads it, so nothing is lost.

## Cost
- The page's buttons, email auto-refresh and LinkedIn links run in the browser against ZoomInfo directly. They use **no AI tokens** and only free ZoomInfo calls (search, plus enrichment of companies already under management).
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
| ZoomInfo + BenefitFlow boost (mock, not live yet) | up to +20 | Weekly-digest buying signals (competitor 8, site visit 8, payroll/benefits/HR research 6, other research 4, new leader 5, M&A 4, hiring surge 3; full for 7 days, half to 14, quarter to 30; leaders/M&A/hiring last longer), ZoomInfo HR intent 80+ in 30 days +3, BenefitFlow renewal ≤90 days +5 / ≤180 +3, broker or carrier change in 6 months +3 |

Tiers: **A ≥65 Call today · B ≥45 This week · C ≥28 Nurture · D Monitor**. An account with no activity for 60+ days is capped at C. (Mock, not live yet:) a new ZoomInfo digest buying signal in the last 14 days keeps an account in This week at least, and turns a P3/P4 next step into "Follow up on ZoomInfo signal".

Change the weights, competitor list, page patterns and aliases in the config block at the top of the script.
