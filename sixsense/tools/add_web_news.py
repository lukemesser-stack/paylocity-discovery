# Load web news triggers (data/web_news_*.json) into a built dashboard file: a.web_news = {on, items}.
# Usage: python3 tools/add_web_news.py data/web_news_X.json out.html   (owner-added items already on the account are kept)
import json, sys, datetime
src, out = sys.argv[1], sys.argv[2]
news = {k: v for k, v in json.load(open(src)).items() if not k.startswith('_')}
O = open(out, encoding='utf-8').read(); k = 'const EMBEDDED_DATA = '; i = O.index(k) + len(k); j = O.index(';\n', i)
d = json.loads(O[i:j]); now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')
for name, items in news.items():
    if name not in d: print('not found:', name); continue
    keep = [x for x in ((d[name].get('web_news') or {}).get('items') or []) if x.get('added_by') == 'owner']
    seen = {x.get('url') for x in keep}
    d[name]['web_news'] = {'on': now, 'items': keep + [x for x in items if x.get('url') not in seen]}
    print(f'{name}: {len(items)} item(s)')
open(out, 'w', encoding='utf-8').write(O[:i] + json.dumps(d, ensure_ascii=False) + O[j:])
