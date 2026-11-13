# Print the "In the news" refresh queue from a saved live dashboard (same rule as newsQueue() in the page):
# accounts with a refresh request newer than their last search, plus Call today (tier A) accounts never searched
# or not searched in 14 days. Usage: python3 tools/news_queue.py live.html [YYYY-MM-DD]
import json, sys, datetime
O = open(sys.argv[1], encoding='utf-8').read(); k = 'const EMBEDDED_DATA = '; i = O.index(k) + len(k)
d = json.loads(O[i:O.index(';\n', i)])
today = datetime.date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else datetime.date.today()
def removed(a): return bool(a.get('removed_at')) and a['removed_at'] > (a.get('restored_at') or '')
out = []
for n, a in d.items():
    if removed(a): continue
    w = a.get('web_news') or {}
    req = bool(w.get('requested_on')) and w['requested_on'] > (w.get('on') or '')
    on = (w.get('on') or '')[:10]
    stale = not on or (today - datetime.date.fromisoformat(on)).days > 14
    if req or (str((a.get('priority') or {}).get('tier', '')).startswith('A') and stale):
        out.append((n, a.get('website') or '', ((a.get('zi') or {}).get('firmo') or {}).get('hq', ''), 'requested' if req else 'call today'))
for row in out: print(' | '.join(row))
print(len(out), 'in queue')
