# paylocity-discovery
## 6sense dashboard

- `sixsense_dashboard_v3.html` — self-contained buyer-intent dashboard (open directly in a browser). Ships with the latest data embedded.
- `6SENSE_Update_File.json` — cumulative 6sense data export, cleaned (duplicate company-name variants merged, dates normalized).

To refresh the dashboard, drag a new `6SENSE_Update_File.json` (or individual `.msg` emails) onto the upload zone at the bottom. JSON update files merge as snapshots — re-loading the same file never double-counts — and progress auto-saves to browser storage.
