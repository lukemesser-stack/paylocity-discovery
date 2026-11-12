"""Blend live dashboard data + ZoomInfo prospect export (my book) + weekly ZoomInfo digest emails -> one data JSON.

Usage: python3 blend_book_digests.py WORKDIR
WORKDIR holds:
  live.html            the live dashboard, saved with Artifact read (always re-read first)
  list.xlsx            ZoomInfo company export of the prospect list (optional)
  digests/YYYY-MM-DD.msg  ZoomInfo weekly target-account digest emails, named by send date
  pylib/               pip install --target pylib olefile  (for .msg files)
Writes WORKDIR/blended.json. Then inject it into dashboard_template.html, run optimize_sixsense.py
on it for the Python/JS parity check (parity.js), and publish to the live URL without capabilities.
Same-name, same-ZoomInfo-ID or same-website accounts merge; live data (notes, Worked, removals,
revealed contacts) is never overwritten.
"""
import sys, re, json, html, collections, datetime, openpyxl
TODAY = datetime.date.today().isoformat()
S = sys.argv[1]; sys.path.insert(0, S + '/pylib'); import olefile
dom = lambda u: re.sub(r'^https?://', '', (u or '').lower().strip()).replace('www.', '', 1).split('/')[0]
L = open(S + '/live.html', encoding='utf-8').read(); k = 'const EMBEDDED_DATA = '; i = L.index(k) + len(k)
D = json.loads(L[i:L.index(';\n', i)])
bydom = {dom(a.get('website')): a for a in D.values() if a.get('website')}
byzi = {str((a.get('zi') or {}).get('company_id')): a for a in D.values() if (a.get('zi') or {}).get('company_id')}
# 1) book
import os, glob
P = []
if os.path.exists(S + '/list.xlsx'):
  wb = openpyxl.load_workbook(S + '/list.xlsx', read_only=True, data_only=True); rows = list(wb.worksheets[0].iter_rows(values_only=True))
  hdr = rows[0]; P = [dict(zip(hdr, r)) for r in rows[1:] if any(r)]
def rng(r): return re.sub(r'\$(\d+) mil\. - \$(\d+) mil\.', r'$\1M–$\2M', str(r or '')).replace(' bil.', 'B').replace(' mil.', 'M')
added = matched = 0
for p in P:
    zid = str(p['ZoomInfo Company ID']); w = dom(p['Website'])
    a = byzi.get(zid) or (bydom.get(w) if w else None) or D.get(p['Company Name'])
    firmo = {'industry': p['Primary Industry'] or '', 'sub_industry': p['Primary Sub-Industry'] or '', 'employees': int(p['Employees'] or 0) or None,
             'revenue_range': rng(p['Revenue Range (in USD)']), 'hq': ', '.join(x for x in [p['Company City'], p['Company State']] if x),
             'founded': str(p['Founded Year'] or ''), 'type': p['Ownership Type'] or '', 'locations': int(p['Number of Locations']) if str(p['Number of Locations'] or '').isdigit() else None,
             'about': '', 'on': TODAY, 'src': 'book'}
    book = {'on': TODAY, 'phone': p['Company HQ Phone'] or '', 'linkedin': p['LinkedIn Company Profile URL'] or '', 'parent': p['Entity Name (Ultimate Parent)'] or ''}
    if a:
        matched += 1
        a['book'] = book
        a.setdefault('zi', {})
        if not a['zi'].get('company_id'): a['zi'].update({'company_id': zid, 'name': p['Company Name'], 'intent': a['zi'].get('intent') or []})
        if not a['zi'].get('firmo'): a['zi']['firmo'] = firmo
    else:
        added += 1
        name = p['Company Name']
        D[name] = {'company': name, 'stage': '', 'fit': '', 'reach': '', 'website': ('https://' + w) if w else '', 'signal_count': 0, 'web_visits': 0,
                   'keywords': [], 'competitor_keywords': [], 'decoded_urls': [], 'contacts': [], 'form_fills': [], 'dates': [], 'activity_dates': [],
                   'source_files': [], 'aliases': [], 'possible_duplicate_of': [], 'surge_topics': [],
                   'zi': {'company_id': zid, 'name': name, 'location': firmo['hq'], 'employees': str(firmo['employees'] or ''), 'intent': [], 'firmo': firmo},
                   'book': book}
        bydom[w] = D[name]
# 2) digests
ACT = re.compile(r'researching (payroll|benefits|human resources|recruiting|talent|workforce|compensation)|competitive alert|competitor|has visited a webpage|'
                 r'mergers & acquisitions|\bacquire|researched intent topics: (hr|labor|benefits|payroll|vendors|human)|'
                 r'(chief financial officer|cfo|controller|chief people|human resources|hr director|payroll|benefits)[^.]{0,40}(has joined|appointed|promoted)|'
                 r'hiring plans:.*(human resources|finance|accounting)', re.I)
CONTEXT = re.compile(r'hiring plans|funding|has joined the company|departed the company|appointed|promoted', re.I)
def body(f):
    o = olefile.OleFileIO(f)
    def get(prop):
        for t in ('001F', '001E'):
            n = f'__substg1.0_{prop}{t}'
            if o.exists(n):
                b = o.openstream(n).read(); return b.decode('utf-16-le', 'ignore') if t == '001F' else b.decode('utf-8', 'ignore')
        return ''
    return get('1000'), get('007D')
counts = collections.Counter()
for fp in sorted(glob.glob(S + '/digests/*.msg')):
    date = os.path.basename(fp)[:10]
    raw, _ = body(fp)
    doms = re.findall(r'd_company-not-found\.png/([^>]+?)\.png>', raw)
    t = re.sub(r'<https?://[^>]+>', '', raw); t = re.sub(r'[ \t ]+', ' ', t)
    lines = [l.strip() for l in t.split('\n')]; accs = []; cur = None; win = ''
    for n, s in enumerate(lines):
        if s == 'Target account': cur = {'name': lines[n - 1], 'cat': '', 'items': []}; accs.append(cur); continue
        if cur is None: continue
        if s in ('Now is a good time to reach out', 'Competitive risk', 'Recent signals'): cur['cat'] = s; continue
        if s.startswith('Last ') and s.endswith('days'): win = s; continue
        if not s or s in ('•', 'See Full Update', 'Find Buying Group', '‌') or s.startswith('Contact Us'): continue
        if cur['cat'] and win and not (n + 1 < len(lines) and lines[n + 1] == 'Target account'):
            txt = re.sub(r'\s+([,.])', r'\1', s)
            kind = 'act' if ACT.search(txt) else 'context' if CONTEXT.search(txt) else 'noise'
            cur['items'].append({'window': win, 'text': txt[:240], 'kind': kind})
    for i2, c in enumerate(accs):
        d = doms[i2] if i2 < len(doms) else ''
        a = bydom.get(d)
        if not a: counts['digest account not matched'] += 1; continue
        seen = set(); items = [it for it in c['items'] if not (it['text'] in seen or seen.add(it['text']))]
        if any(e['date'] == date for e in a.get('zid', [])): counts['digest week already loaded'] += 1; continue
        a.setdefault('zid', []).append({'date': date, 'cat': c['cat'], 'items': items})
        counts['digest entries'] += 1
json.dump(D, open(S + '/blended.json', 'w'), ensure_ascii=False)
print('book matched to dashboard:', matched, '| added from book:', added, '| total accounts:', len(D), '|', dict(counts))
print('not in book (live):', sum(1 for a in D.values() if not a.get('book') and not (a.get('removed_at') and a['removed_at'] > (a.get('restored_at') or ''))))
kinds = collections.Counter(it['kind'] for a in D.values() for e in a.get('zid', []) for it in e['items']); print('digest items by kind:', dict(kinds))
for a in D.values():
    for e in a.get('zid', []):
        for it in e['items']:
            if it['kind'] == 'act' and e['date'] == '2026-11-10': print('  ACT 11/10', a['company'], '|', it['text'][:90])
