import json,sys,re
f,crawl=sys.argv[1],sys.argv[2]
O=open(f,encoding='utf-8').read();k='const EMBEDDED_DATA = ';i=O.index(k)+len(k);j=O.index(';\n',i);d=json.loads(O[i:j])
r=json.load(open(crawl)); n=0
BAD={'https://www.facebook.com/2008','https://www.facebook.com/profile.php'}
for name,v in r.items():
    if not v.get('ok') or name not in d: continue
    s={}
    for kk,u in v['social'].items():
        u=re.sub(r'(%20)+$','',u)
        if u in BAD or u.endswith('-'): continue
        s[kk]=u
    if s: d[name]['web_social']={**s,'on':'2026-11-12'}; n+=1
raw=json.dumps(d,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
open(f,'w',encoding='utf-8').write(O[:i]+raw+O[j:]); print('accounts with website links:',n)
