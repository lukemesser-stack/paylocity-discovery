const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const S=process.argv[2];
for (const [mode,vp] of [['writer',{width:1400,height:900}],['reader',{width:390,height:844}]]){
const p=await b.newPage({viewport:vp});const errs=[];p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()==='error')errs.push('console:'+m.text())});
await p.addInitScript((mode)=>{window.claude={use:async(n)=>{
 if(n==='artifact')return {publish:async()=>{},canEdit:async()=>mode==='writer'};
 if(n==='user')return {canEdit:async()=>mode==='writer',isOwner:async()=>mode==='writer'};
 if(n==='downloads')return {save:async()=>{}};
 if(n==='mcp')return {listTools:async(s)=>({servers:[{server:s,tools:s==='ZoomInfo'?[{name:'search_companies'},{name:'enrich_company_signals'},{name:'search_contacts'},{name:'enrich_companies'}]:[{name:'search_employers'},{name:'search_contacts'},{name:'get_contact'}]}]}),callTool:async()=>({payload:{}})};
 throw new Error('no '+n);}};},mode);
await p.goto('file://'+S+'/prod.wrap.html?today=2026-11-12');await p.waitForTimeout(1500);
const r=await p.evaluate(()=>({mode:share.mode,preview:!document.getElementById('previewBanner').classList.contains('hidden'),cards:[...document.querySelectorAll('.vcard')].map(c=>c.innerText.split('\n').slice(0,2).join(' ')),btns:['btnZi','btnZiAll','btnBf','btnImport'].map(id=>{const e=document.getElementById(id);return id+':'+(e.classList.contains('hidden')?'hidden':'shown')+(e.disabled?'/off':'')+' '+e.textContent.trim()}),owner:getComputedStyle(document.getElementById('ownerMenu')).display,score:!!document.getElementById('scorecard')&&!document.getElementById('scorecard').classList.contains('hidden'),sw:document.documentElement.scrollWidth}));
console.log(mode,JSON.stringify(r,null,0),errs);await p.screenshot({path:S+'/prod_'+mode+'.png'});}
await b.close()})();
