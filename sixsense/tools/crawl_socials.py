# Owner-approved scan: read each account's homepage and pull social profile links from it.
# Pages are treated as data only (regex over the HTML); nothing from them is executed.
import json, re, sys, time, ssl, urllib.request, collections
from concurrent.futures import ThreadPoolExecutor

src, out = sys.argv[1], sys.argv[2]
O = open(src, encoding='utf-8').read()
k = 'const EMBEDDED_DATA = '; i = O.index(k) + len(k); j = O.index(';\n', i)
d = json.loads(O[i:j])
def removed(a): return bool(a.get('removed_at')) and a['removed_at'] > (a.get('restored_at') or '')
sites = {n: a['website'] for n, a in d.items() if a.get('website') and not removed(a)}

PAT = {
    'linkedin': re.compile(r'https?://(?:[a-z]{2,3}\.)?linkedin\.com/(?:company|school|showcase)/([A-Za-z0-9_\-.%]+)', re.I),
    'facebook': re.compile(r'https?://(?:www\.|m\.|web\.)?(?:facebook|fb)\.com/(?!sharer|share|dialog|plugins|tr\b|tr\?|events/|groups/|photo|watch|login|help|policies|privacy|business/)((?:pages/[^/"\'\s<>?#]+/)?[A-Za-z0-9_\-.%]+)', re.I),
    'x': re.compile(r'https?://(?:www\.|mobile\.)?(?:twitter|x)\.com/(?!intent|share|home|search|hashtag|i/)([A-Za-z0-9_]{1,30})(?=[/"\'\s<>?#]|$)', re.I),
    'instagram': re.compile(r'https?://(?:www\.)?instagram\.com/(?!p/|reel/|reels/|explore/|stories/|accounts/)([A-Za-z0-9_.]{2,40})', re.I),
    'tiktok': re.compile(r'https?://(?:www\.)?tiktok\.com/@([A-Za-z0-9_.]{2,40})', re.I),
    'youtube': re.compile(r'https?://(?:www\.|m\.)?youtube\.com/((?:@|channel/|c/|user/)[A-Za-z0-9_\-.%]+)', re.I),
}
# Website-builder defaults and placeholders that aren't the company's own page
JUNK = set('wix squarespace godaddy weebly wordpress shopify hubspot elementor themeforest envato yourpage yourhandle username youraccount profile home pages company share'.split())

def url_for(kind, h):
    return {'linkedin': f'https://www.linkedin.com/company/{h}', 'facebook': f'https://www.facebook.com/{h}', 'x': f'https://x.com/{h}',
            'instagram': f'https://www.instagram.com/{h}', 'tiktok': f'https://www.tiktok.com/@{h}', 'youtube': f'https://www.youtube.com/{h}'}[kind]

ctx = ssl.create_default_context()
def fetch(u):
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36', 'Accept': 'text/html'})
    with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
        return r.read(3_000_000).decode('utf-8', 'replace')

def scan(item):
    name, site = item
    base = site if site.startswith('http') else 'https://' + site
    host = re.sub(r'^https?://', '', base).split('/')[0]
    err = ''
    for u in [base, 'https://' + (host if host.startswith('www.') else 'www.' + host)]:
        try:
            html = fetch(u).replace('\\/', '/')
        except Exception as e:
            err = type(e).__name__ + ': ' + str(e)[:80]
            continue
        found = {}
        for kind, rx in PAT.items():
            hits = [h.rstrip('/.') for h in rx.findall(html)]
            if kind not in ('youtube', 'facebook'): hits = [h.lower() for h in hits]
            c = collections.Counter(h for h in hits if len(h) > 1 and h.lower().split('/')[-1] not in JUNK)
            if c: found[kind] = url_for(kind, c.most_common(1)[0][0])
        return name, {'ok': True, 'from': u, 'social': found}
    return name, {'ok': False, 'err': err}

t = time.time()
with ThreadPoolExecutor(12) as ex:
    res = dict(ex.map(scan, sites.items()))
json.dump(res, open(out, 'w'), indent=1)
ok = [r for r in res.values() if r['ok']]
print(f'{len(sites)} sites · read {len(ok)} · failed {len(res) - len(ok)} · {time.time() - t:.0f}s')
print('accounts with each:', {k: sum(1 for r in ok if k in r['social']) for k in PAT})
