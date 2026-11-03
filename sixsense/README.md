# 6sense "Target Now" scorer

`optimize_sixsense.py` cleans your accumulated 6sense JSON and ranks every account by **who to call now**.

## Daily use

1. Add new 6sense Outlook alerts to the JSON, the same way you do today (parser or dashboard drag-and-drop).
2. Run:
   ```bash
   python3 optimize_sixsense.py 6SENSE_Update_File.json
   ```
3. Open `6SENSE_Update_File_dashboard.html` (it's rebuilt on every run with the fresh data). Work the **Call today** cards first, then tier B.
   The same ranking is also in `6SENSE_Update_File_target_now.csv` and printed in the terminal.

## Dashboard (`dashboard_template.html`)
- **Call today** cards: the top tier-A accounts, each with a next step and why it ranks there.
- **Stat cards are filters**: Call today, This week, Heating up, Active 7 days, Competitor research.
- **Search** (press `/`) covers company, keywords, pages visited and your notes. You can also filter by tier, stage and fit.
- **✓ Worked**: marks an account as contacted today. It drops off the list for 7 days, and comes back early (tagged *new since worked*) if 6sense records new activity.
- **Notes** per account, saved in the browser and included in 💾 Save JSON. The Python script keeps `worked_on` and `notes` too.
- **Add emails / JSON**: drop 6sense alert `.msg` files (or a JSON update) anywhere on the page. Emails already loaded are skipped, matched by file name and by activity date. Nothing is merged until you click Apply.
- **⬇ Call list CSV** exports the rows you're currently looking at.
- Scores are recalculated against today's date every time you open the page, so the file never goes stale. Add `?today=YYYY-MM-DD` to the URL to see the ranking as of another day.

## Sharing with your SDR
The run also writes `6SENSE_Update_File_share.html`. That's the same dashboard, published as a claude.ai page.
- The owner (and anyone you add as an Editor) can click **Worked**, write notes and import emails. Each change saves the page itself, and everyone with the link sees it.
- Anyone else with the link gets a read-only copy: the same ranking, reasons, pages and notes, plus the CSV export.
- To push a fresh JSON run, ask Claude to republish `_share.html` to the same link, or just drop the JSON on the shared page.

## ZoomInfo intent (Call today + This week only)
Each account can carry a `zi` block: `{company_id, name, location, employees, pulled_on, intent: [{topic, category, score, audience, date}], skipped?, note?}`.
- It's pulled through the ZoomInfo connector. Match accounts by website with `search_companies` (free), then call `enrich_company_signals` with `signalTypes: ["INTENT"]`, which is free for companies already under management.
- Accounts not under management are skipped and marked `skipped`, so no credits are spent without asking.
- The dashboard shows a "ZoomInfo:" line under Why now and a ZoomInfo section in the account detail. Accounts get a **✓ Confirmed** badge (and a filter card) when a ZoomInfo topic matches a 6sense keyword, Bombora surge topic or page visit on the same theme.
- ZoomInfo doesn't change the score.
- **Refresh from the page (owner only):** on the shared claude.ai page, **↻ ZoomInfo** in the header refreshes all Call today and This week accounts. Each account's ZoomInfo section has its own **↻ Refresh ZoomInfo intent** button.
  - The page calls the owner's ZoomInfo connector (`mcp` capability: `search_companies` and `enrich_company_signals`). It checks management status first, which is free.
  - Refresh-all only pulls free accounts. On a single account that would cost credits, the button asks for a second click.
  - Results are saved to the page, so read-only viewers see them without needing ZoomInfo themselves.
- **Automatic on import:** when the owner applies new 6sense emails, every account from those emails that now ranks Call today or This week gets its ZoomInfo intent refreshed before the page saves.
  - Only free accounts are pulled, and at most once a day per account.
  - If ZoomInfo fails, the email data still saves and the import log shows the reason.

## Trigger events (ZoomInfo)
`zi.scoops` (`[{date, summary, types, link}]`) and `zi.new_leaders` (`[{name, title, person_id, window_days}]`) feed a **🔔 Trigger** badge, the top of Why now, a Trigger events filter card and a detail section.
- **Leadership change:** ZoomInfo Scoops of type Executive Move, New Hire, Promotion, Management Move or Left Company, from the last 120 days.
- **New leader:** a free `search_contacts` by `positionStartDateMin`, run twice (180 days, then 90 days) for CEO/President/COO, CFO/Controller/Finance, HR/People/Talent/Benefits and Payroll titles. Practice titles like "Financial Services" are excluded. It returns names and titles only, with no contact details.
- **Vendor clue:** the host of a Scoop's job-post link, e.g. `recruitingbypaycor.com`, means they likely use Paycor.
- **Hiring surge:** shown in the account detail only.
- Each new leader's **name is a link** (with a blue **in** badge) that searches LinkedIn for their name plus the company name, in Why now, the Call today cards and the account detail. There's no ZoomInfo credit or API call. An exact profile URL would come from `enrich_contacts` with `externalUrls`, which costs about 1 ZoomInfo credit per person, so it isn't built in.

## Who to call (ZoomInfo)
`zi.people` (`[{name, title, person_id, accuracy}]`) comes from a free `search_contacts` on HR, payroll, finance and executive titles, run with no start-date filter and sorted by accuracy.
- The dashboard picks up to 3 buyers per account: the best **HR** leader, then **Payroll**, then **Finance** (CFO, Controller or VP Finance). An **Executive** fills in when one of those is missing. Non-buyer titles (Inventory Controller, "Financial Services" practice roles, assistants) are skipped, and new leaders rank first within their role.
- They appear as 👤 under the company name in the table, as "Call:" on the Call today cards, and in a "Who to call" section in the account detail. Each name is a LinkedIn search link.
- Every person shows ZoomInfo's **accuracy score** (70–99). Under 80 is dimmed with a "check LinkedIn first" hint.
- The ZoomInfo refresh buttons and email auto-refresh re-run this search. Activity tracking stays in Salesforce.

## Previous sales process (owner, manual)
- In an account's detail, **☆ Mark as past sales process** sets `past_process: true` and `past_process_on`. A **Sales history** box (`history_note`) appears for details to pass to the SDR.
- The account then shows a **★ Past deal** badge (the note shows on hover), a "★ Past sales process: …" line in Why now, and a filter card. Search covers the note, and the CSV has two columns for it.
- Read-only viewers see the note but can't edit it. Removing the mark keeps the note, so re-marking brings it back. The Python script preserves these fields.

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

Tiers: **A ≥65 Call today · B ≥45 This week · C ≥28 Nurture · D Monitor**. An account with no activity for 60+ days is capped at C.

Change the weights, competitor list, page patterns and aliases in the config block at the top of the script.
