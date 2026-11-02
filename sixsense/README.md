# 6sense "Target Now" scorer

`optimize_sixsense.py` cleans your accumulated 6sense JSON and ranks every account by **who to call now**.

## Daily use

1. Add new 6sense Outlook alerts to the JSON, the same way you do today (parser or dashboard drag-and-drop).
2. Run:
   ```bash
   python3 optimize_sixsense.py 6SENSE_Update_File.json
   ```
3. Work the call list top-down: Tier A today, Tier B this week. It's in `6SENSE_Update_File_target_now.csv` and also printed in the terminal.

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
