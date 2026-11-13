import sys,re
tpl, live, out = sys.argv[1:4]
L=open(live,encoding='utf-8').read(); T=open(tpl,encoding='utf-8').read()
s=L.index('<!--6S-START-->'); e=L.rindex('</body></html>'); frag=L[s:e]
k='const EMBEDDED_DATA = '; i=frag.index(k)+len(k); j=frag.index(';\n',i); data=frag[i:j]
k2='const PUBLISHED_AT = '; i2=frag.index(k2)+len(k2); j2=frag.index(';',i2); pub=frag[i2:j2]
assert '/*__EMBEDDED_DATA__*/null' in T and 'const PUBLISHED_AT = null;' in T
page=T.replace('/*__EMBEDDED_DATA__*/null',data,1).replace('const PUBLISHED_AT = null;','const PUBLISHED_AT = '+pub+';',1)
open(out,'w',encoding='utf-8').write(page)
open(out+'.livefrag','w',encoding='utf-8').write(frag)
print(len(data), pub)
