const runButton=document.querySelector('#run');
const progress=document.querySelector('#progress');
const result=document.querySelector('#result');
const verdict=document.querySelector('#verdict');
const runs=document.querySelector('#runs');
const marker=document.querySelector('#marker');
const limitations=document.querySelector('#limitations');
const safe=s=>String(s??'Unavailable').replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
const short=s=>s?s.slice(0,12)+'…':'Unavailable';

fetch('/health').then(r=>r.json()).then(h=>{
  const i=h.integrations||{};
  document.querySelector('#services').textContent=i.daytona_configured&&i.neo4j_configured?'Services configured':'Setup incomplete';
}).catch(()=>document.querySelector('#services').textContent='Services unavailable');

const copy={
  COMPUTATIONALLY_OBSERVABLE:['good','Computationally observable','Exact synthetic marker recovered under tested computational conditions.'],
  NOT_TECHNICALLY_COMPARABLE:['bad','Not technically comparable','Changed pipeline completed but did not recover exact synthetic marker. No biological conclusion follows.'],
  NO_CONCLUSION:['neutral','No conclusion','Challenge could not be completed or verified.']
};

function render(data){
  const known=Object.hasOwn(copy,data.verdict)?data.verdict:'NO_CONCLUSION';
  const [tone,title,description]=copy[known];
  verdict.className='verdict '+tone;
  verdict.innerHTML=`<p class="label">Neo4j verdict</p><h2>${title}</h2><p>${description}</p>`;
  if(data.variant){marker.innerHTML=`<p class="label">Known synthetic challenge</p><div><strong>${safe(data.variant.gene)}-${safe(data.variant.type)}</strong><span>Position ${safe(data.variant.position)} · ${safe(data.variant.length_bp)} bp · VAF ${safe(Math.round(data.variant.test_vaf*100))}%</span><code>${safe(data.variant.sequence)}</code></div>`;marker.classList.remove('hidden')}else marker.classList.add('hidden');
  runs.innerHTML=(data.runs||[]).map(r=>`<article class="run-card"><header><h3>${safe(r.profile)}</h3><span class="state">${safe(r.status)}</span></header><dl><div><dt>Exact recovery</dt><dd>${r.exact_recovery===true?'Yes':r.exact_recovery===false?'No':'Unavailable'}</dd></div><div><dt>Sandbox</dt><dd>${safe(short(r.sandbox_id))}</dd></div><div><dt>Caller</dt><dd>${safe(r.caller)} ${safe(r.caller_version)}</dd></div><div><dt>Configuration</dt><dd>${safe(short(r.config_sha256))}</dd></div><div><dt>Position</dt><dd>${safe(r.detected_position)}</dd></div><div><dt>Length</dt><dd>${r.detected_length_bp==null?'Unavailable':safe(r.detected_length_bp)+' bp'}</dd></div></dl></article>`).join('');
  if((data.limitations||[]).length){limitations.innerHTML=`<p class="label">Limitations</p><ul>${data.limitations.map(x=>`<li>${safe(x)}</li>`).join('')}</ul>`;limitations.classList.remove('hidden')}else limitations.classList.add('hidden');
  result.classList.remove('hidden');
}

runButton.addEventListener('click',async()=>{
  runButton.disabled=true;result.classList.add('hidden');progress.textContent='Awaiting verified Daytona execution and Neo4j verdict…';
  const controller=new AbortController();const timer=setTimeout(()=>controller.abort(),360000);
  try{
    const response=await fetch('/api/v1/cases/AML-DEMO-001/handoff-tests',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({fixture_id:'FLT3-ITD-DEMO-001',profiles:['compatible','changed']}),signal:controller.signal});
    if(!response.ok)throw new Error('Challenge service returned '+response.status);
    render(await response.json());progress.textContent='Verified run complete.';
  }catch(error){render({verdict:'NO_CONCLUSION',runs:[]});progress.textContent=error.name==='AbortError'?'Challenge timed out.':'Execution incomplete: '+error.message;}
  finally{clearTimeout(timer);runButton.disabled=false;}
});
