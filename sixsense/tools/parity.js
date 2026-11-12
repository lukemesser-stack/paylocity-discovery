const {chromium}=require('playwright');const fs=require('fs');(async()=>{const b=await chromium.launch();const S=process.argv[2];
const py=JSON.parse(fs.readFileSync(S+'/py/T.json','utf8'));const p=await b.newPage();await p.goto('file://'+S+'/py/T_dashboard.html?today=2026-11-12');await p.waitForTimeout(800);
const js=await p.evaluate(()=>Object.fromEntries(allAccounts().map(a=>[a.company,[a.priority.score,a.priority.tier,a.priority.action]])));
let diff=0;for(const [k,v] of Object.entries(py)){const j=js[k];if(!j||j[0]!==v.priority.score||j[1]!==v.priority.tier||j[2]!==v.priority.action){diff++;if(diff<4)console.log('DIFF',k,j,v.priority.score,v.priority.tier)}}
console.log('compared',Object.keys(py).length,'differences',diff);await b.close()})();
