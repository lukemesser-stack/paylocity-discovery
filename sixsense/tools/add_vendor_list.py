# Writes the owner's territory-list "Current Provider" into matched accounts as vendor_list.
import json,sys
f,mf=sys.argv[1],sys.argv[2]
O=open(f,encoding='utf-8').read();k='const EMBEDDED_DATA = ';i=O.index(k)+len(k);j=O.index(';\n',i);d=json.loads(O[i:j])
m=json.load(open(mf))
REJECT={'Orange City Arts','The City of Sanford','Bridges of Canada'}
SKIP={'missing','other','unknown','new business'}
set_,skipped=[],[]
for n,rows in m.items():
    if n in REJECT or n not in d: continue
    rows=[r for r in rows if not (r['Account Stage']=='Lost Client' and r['Current Provider']=='Paylocity')]
    vals={r['Current Provider'] for r in rows if str(r['Current Provider']).strip().lower() not in SKIP}
    if 'Paylocity' in vals: vals={'Paylocity'}
    if len(vals)!=1: skipped.append((n,sorted(vals))); continue
    d[n]['vendor_list']=vals.pop(); d[n]['vendor_list_on']='2026-11-12'; set_.append(n)
open(f,'w',encoding='utf-8').write(O[:i]+json.dumps(d,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')+O[j:])
print('vendor_list set on',len(set_),'| skipped (conflict or nothing usable):',[x for x in skipped if x[1]])
