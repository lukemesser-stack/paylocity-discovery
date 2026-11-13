# Target Now: project instructions (paste into the Target Now project)

You are continuing work on **Target Now**, Luke's 6sense / ZoomInfo / BenefitFlow call-prioritization dashboard.

## Where things are
- **Live dashboard:** https://claude.ai/artifact/Us82tGvEWGgk8eCeUpbDkX (owned by Luke, shared view-only with his SDR).
- **Code:** GitHub `lukemesser-stack/paylocity-discovery`, folder `sixsense/`, branch `main` (new work goes on a new branch, then a pull request into `main`).
- **Read first:** `sixsense/README.md`. It describes every feature, data field and tool.
- Main file: `sixsense/dashboard_template.html`. Scoring: `sixsense/optimize_sixsense.py`. Tools: `sixsense/tools/` (inject.py, prodtest.js, parity.js, add_web_news.py, news_queue.py and others). Saved web news: `sixsense/data/web_news_*.json`.

## Standing rules (Luke's words)
- Before any republish: re-read the live dashboard and build from its data (`tools/inject.py dashboard_template.html <live.html> <out.html>`). Keep its existing permissions (publish without `capabilities` unless a new connector tool is needed). Report any changes Luke made on the page since the last publish.
- Free ZoomInfo and BenefitFlow calls only. Nothing that costs credits without Luke's two-click confirm. (BenefitFlow `enrich_companies` uses enrichment credits: don't use it.)
- No AI-token use in the dashboard. The one exception is the owner-only ✨ AI openers button.
- Activity tracking stays in Salesforce.
- The score must stay the same in Python and JS (check with `tools/parity.js`).
- Only rebuild the peer kit when Luke asks.
- Explain results in plain language.
- Don't change anything until Luke asks.

## Recurring jobs
- **In the news refresh:** Luke pastes a request from ⚙ Owner → 🔎 In the news: refresh queue, or asks for the queue. Read the live page, run `python3 tools/news_queue.py <live.html>`, web-search each account for news from the last 12 months (leadership changes, new locations, acquisitions, awards, growth), keep up to 3 dated items with links per account (`[]` if nothing), save to `data/web_news_<date>.json`, load with `tools/add_web_news.py`, test, publish, commit.
- New **Call today** accounts after a 6sense / ZoomInfo import join that queue on their own.

## How to publish safely
1. Read the live artifact, then save it as live.html.
2. Run `inject.py` and diff the data to see what Luke changed.
3. Run `node tools/prodtest.js <dir>` (owner and SDR views).
4. Publish to the same URL.
5. Add a README note.
6. Commit and push.
