// Nexus Social — app.js

const POSTS = [
  { id:1, user:'Riya Kapoor', initials:'RK', color:'#ff4d6d', time:'2h ago', location:'Hyderabad',
    text:'Golden hour in Hyderabad hits different. The city never stops surprising you. Grateful for every sunset that reminds me to slow down.',
    tags:['#Hyderabad','#GoldenHour','#CityLife'], likes:2400, comments:186, badge:'Creator',
    aiNote:'Caption scored 94% engagement · Best post time: 7 PM' },
  { id:2, user:'Arjun Sharma', initials:'AS', color:'#7c3aed', time:'4h ago', location:'Tech Community',
    text:'Just wrapped the Agentic Premier League hackathon — built a fully working AI wellness app in 3 hours using Gemini + Firebase + Vertex AI. The future of agentic AI is here.',
    tags:['#GeminiAI','#Hackathon','#GoogleCloud','#AgenticAI'], likes:847, comments:93, badge:null, aiNote:null },
  { id:3, user:'Priya Mehta', initials:'PM', color:'#0d9488', time:'6h ago', location:'GDG Hyderabad',
    text:'The developer community in Hyderabad is thriving. 200+ developers showed up for the Agentic Premier League. This is what building the future looks like.',
    tags:['#GDGHyderabad','#DevCommunity','#HyderabadTech'], likes:1200, comments:74, badge:'GDG Lead', aiNote:'High community resonance detected' }
];

const state = {
  posts: JSON.parse(localStorage.getItem('nexus_posts')||'[]'),
  liked: JSON.parse(localStorage.getItem('nexus_liked')||'[]')
};

document.addEventListener('DOMContentLoaded', () => {
  const isCloudRun = true; // Python backend handles API key
  if (isCloudRun || hasApiKey()) { showApp(); } else { document.getElementById('apiModal').style.display='flex'; }
  document.getElementById('saveApiKey').addEventListener('click', handleSaveKey);
  document.getElementById('apiKeyInput').addEventListener('keydown', e => { if(e.key==='Enter') handleSaveKey(); });
  document.querySelectorAll('#styleChips .chip').forEach(c => c.addEventListener('click', () => {
    document.querySelectorAll('#styleChips .chip').forEach(x=>x.classList.remove('active')); c.classList.add('active');
  }));
  document.querySelectorAll('#platformChips .chip').forEach(c => c.addEventListener('click', () => {
    document.querySelectorAll('#platformChips .chip').forEach(x=>x.classList.remove('active')); c.classList.add('active');
  }));
});

async function handleSaveKey() {
  const key = document.getElementById('apiKeyInput').value.trim();
  const err = document.getElementById('modalError');
  const btn = document.getElementById('saveApiKey');
  if (!key || !key.startsWith('AIza')) { err.textContent='Valid key starts with AIza...'; err.style.display='block'; return; }
  btn.textContent='Verifying...'; btn.disabled=true;
  saveApiKey(key);
  try { await callGemini('Say hi in 3 words'); showApp(); }
  catch(e) { clearApiKey(); err.textContent=e.message; err.style.display='block'; btn.textContent='Activate Nexus AI'; btn.disabled=false; }
}

function showApp() {
  document.getElementById('apiModal').style.display='none';
  document.getElementById('mainApp').style.display='block';
  renderPosts();
}

function resetApiKey() {
  clearApiKey();
  document.getElementById('mainApp').style.display='none';
  document.getElementById('apiModal').style.display='flex';
  document.getElementById('apiKeyInput').value='';
  document.getElementById('modalError').style.display='none';
  const btn=document.getElementById('saveApiKey'); btn.textContent='Activate Nexus AI'; btn.disabled=false;
}

function switchTab(name, el) {
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active'));
  document.getElementById('tab-'+name).classList.add('active');
  el.classList.add('active');
}

function fmt(n) { return n>=1000?(n/1000).toFixed(1)+'k':String(n); }

function renderPosts() {
  const c = document.getElementById('postsContainer');
  const all = [...POSTS, ...state.posts.slice().reverse()];
  c.innerHTML = all.map(p => {
    const lk = state.liked.includes(p.id);
    return `<div class="post-card" id="post-${p.id}">
      <div class="post-header">
        <div class="post-av" style="background:${p.color}">${p.initials}</div>
        <div class="post-meta">
          <div class="post-name">${p.user}${p.badge?`<span class="creator-badge">${p.badge}</span>`:''}</div>
          <div class="post-time">${p.time}${p.location?' · '+p.location:''}</div>
        </div>
      </div>
      <div class="post-body">
        <div class="post-text">${p.text}</div>
        <div class="post-tags">${(p.tags||[]).map(t=>`<span class="tag">${t}</span>`).join('')}</div>
      </div>
      ${p.aiNote?`<div class="ai-note"><span class="ai-icon">✦</span><span>${p.aiNote}</span></div>`:''}
      <div class="post-actions">
        <button class="action-btn ${lk?'liked':''}" onclick="toggleLike(${p.id},this)">
          <svg width="15" height="15" viewBox="0 0 16 16" fill="${lk?'#ff4d6d':'none'}" stroke="${lk?'#ff4d6d':'currentColor'}" stroke-width="1.5"><path d="M8 13s-6-3.5-6-7a4 4 0 018 0 4 4 0 018 0c0 3.5-6 7-6 7z"/></svg>
          <span class="lc">${fmt(p.likes+(lk?1:0))}</span>
        </button>
        <button class="action-btn">
          <svg width="15" height="15" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M13 3H3a1 1 0 00-1 1v7a1 1 0 001 1h2l3 2 3-2h2a1 1 0 001-1V4a1 1 0 00-1-1z"/></svg>
          ${fmt(p.comments)}
        </button>
        <button class="action-btn" onclick="quickSentiment(this,'${p.text.replace(/'/g,"&apos;").replace(/\n/g,' ')}')">
          <svg width="15" height="15" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="8" cy="8" r="6"/><path d="M5.5 9.5s1 1.5 2.5 1.5 2.5-1.5 2.5-1.5M6 6.5h.5M9.5 6.5h.5"/></svg>
          Sentiment
        </button>
      </div>
    </div>`;
  }).join('');
}

function toggleLike(id, btn) {
  const i = state.liked.indexOf(id);
  const on = i===-1;
  if(on) state.liked.push(id); else state.liked.splice(i,1);
  localStorage.setItem('nexus_liked', JSON.stringify(state.liked));
  const svg=btn.querySelector('svg'), cnt=btn.querySelector('.lc');
  const p=[...POSTS,...state.posts].find(x=>x.id===id);
  svg.setAttribute('fill',on?'#ff4d6d':'none'); svg.setAttribute('stroke',on?'#ff4d6d':'currentColor');
  btn.classList.toggle('liked',on);
  cnt.textContent = fmt((p?p.likes:0)+(on?1:0));
}

async function aiSuggestHashtags() {
  const text=document.getElementById('composeText').value.trim();
  const el=document.getElementById('hashtagSuggestions');
  if(!text){showToast('Type something first!','warn');return;}
  el.style.display='block'; el.innerHTML='<div class="loading-msg">Gemini thinking...</div>';
  try {
    const r=await geminiSuggestHashtags(text);
    const tags=r.split(',').map(t=>t.trim()).filter(Boolean);
    el.innerHTML=`<div class="ht-label">✦ Gemini suggests</div><div class="ht-tags">${tags.map(t=>`<span class="ht-tag" onclick="insertTag('${t}')">${t}</span>`).join('')}</div>`;
  } catch(e){el.innerHTML=`<div class="err-msg">${e.message}</div>`;}
}

function insertTag(t) {
  const ta=document.getElementById('composeText');
  ta.value=(ta.value+' '+t).trim();
}

async function moderateCompose() {
  const text=document.getElementById('composeText').value.trim();
  const el=document.getElementById('safetyResult');
  if(!text){showToast('Write something first!','warn');return;}
  el.style.display='block'; el.innerHTML='<div class="loading-msg">Content Shield scanning...</div>';
  try {
    const r=await geminiModerateContent(text);
    const c=r.verdict==='safe'?'#0d9488':r.verdict==='warning'?'#d97706':'#e11d48';
    const ic=r.verdict==='safe'?'✓':r.verdict==='warning'?'⚠':'✕';
    el.innerHTML=`<div class="safety-badge" style="border-color:${c};color:${c}">${ic} ${r.verdict.toUpperCase()} (${r.score}/100)</div><div class="safety-text">${r.summary}</div>`;
  } catch(e){el.innerHTML=`<div class="err-msg">${e.message}</div>`;}
}

function publishPost() {
  const text=document.getElementById('composeText').value.trim();
  if(!text){showToast('Write something first!','warn');return;}
  const tags=(text.match(/#\w+/g)||[]);
  const np={id:Date.now(),user:'Techie',initials:'TK',color:'#7c3aed',time:'Just now',location:'Hyderabad',
    text:text.replace(/#\w+/g,'').trim(),tags,likes:0,comments:0,badge:null,aiNote:null};
  state.posts.push(np);
  localStorage.setItem('nexus_posts',JSON.stringify(state.posts));
  document.getElementById('composeText').value='';
  document.getElementById('hashtagSuggestions').style.display='none';
  document.getElementById('safetyResult').style.display='none';
  renderPosts(); showToast('Posted!','success');
}

async function generateCaptions() {
  const desc=document.getElementById('captionPrompt').value.trim();
  const style=document.querySelector('#styleChips .chip.active')?.dataset.val||'Inspirational';
  const platform=document.querySelector('#platformChips .chip.active')?.dataset.val||'LinkedIn';
  const btn=document.getElementById('genCaptionBtn'), out=document.getElementById('captionOutput');
  if(!desc){showToast('Describe your post first!','warn');return;}
  btn.disabled=true; btn.textContent='Generating...';
  out.innerHTML='<div class="loading-msg">Gemini crafting your captions...</div>';
  try {
    const r=await geminiGenerateCaptions({description:desc,style,platform});
    const caps=r.split(/\n\s*\n/).filter(c=>c.trim()&&/^\d\./.test(c.trim()));
    out.innerHTML=`<div class="caps-label">✦ ${style} captions for ${platform}</div>`+
      (caps.length?caps.map((c,i)=>{
        const txt=c.replace(/^\d\.\s*/,'');
        const tags=(txt.match(/#\w+/g)||[]).join(' ');
        const body=txt.replace(/#\w+/g,'').trim();
        return `<div class="cap-card" onclick="copyCaption(this,'${txt.replace(/'/g,"\\'")}')">
          <div class="cap-num">Option ${i+1}</div>
          <div class="cap-body">${body}</div>
          ${tags?`<div class="cap-tags">${tags}</div>`:''}
          <div class="cap-copy">Click to copy</div>
        </div>`;
      }).join('') : `<div class="cap-raw">${r}</div>`);
  } catch(e){out.innerHTML=`<div class="err-msg">${e.message}</div>`;}
  finally{btn.disabled=false;btn.textContent='Generate 3 captions with Gemini ✦';}
}

function copyCaption(el,text) {
  navigator.clipboard.writeText(text).catch(()=>{});
  document.getElementById('composeText').value=text;
  const cc=el.querySelector('.cap-copy'); if(cc){cc.textContent='✓ Copied!'; setTimeout(()=>{cc.textContent='Click to copy';},2000);}
  showToast('Caption copied to compose!','success');
}

async function moderateContent() {
  const text=document.getElementById('moderateInput').value.trim();
  const btn=document.getElementById('moderateBtn'), out=document.getElementById('moderateOutput');
  if(!text){showToast('Paste content first!','warn');return;}
  btn.disabled=true; btn.textContent='Analysing...';
  out.innerHTML='<div class="loading-msg">Content Shield scanning...</div>';
  try {
    const r=await geminiModerateContent(text);
    const cols={safe:'#0d9488',warning:'#d97706',unsafe:'#e11d48'};
    const ics={safe:'✓',warning:'⚠',unsafe:'✕'};
    const c=cols[r.verdict]||'#888', ic=ics[r.verdict]||'?';
    const bars=Object.entries(r.categories||{}).map(([k,v])=>`
      <div class="cat-row"><span class="cat-lbl">${k.replace(/_/g,' ')}</span>
      <div class="cat-bar-w"><div class="cat-bar" style="width:${v}%;background:${v>60?'#e11d48':v>30?'#d97706':'#0d9488'}"></div></div>
      <span class="cat-val">${v}</span></div>`).join('');
    out.innerHTML=`
      <div class="verdict" style="border-color:${c}">
        <div class="verdict-ic" style="background:${c}">${ic}</div>
        <div><div class="verdict-ttl" style="color:${c}">${r.verdict.toUpperCase()} — ${r.score}/100</div>
        <div class="verdict-txt">${r.summary}</div></div>
      </div>
      ${bars?`<div class="cat-grid">${bars}</div>`:''}
      <div class="recommend">${r.recommendation}</div>`;
  } catch(e){out.innerHTML=`<div class="err-msg">${e.message}</div>`;}
  finally{btn.disabled=false;btn.textContent='Analyse with Content Shield ✦';}
}

async function analyseSentiment() {
  const text=document.getElementById('sentimentInput').value.trim();
  const btn=document.getElementById('sentimentBtn'), out=document.getElementById('sentimentOutput');
  if(!text){showToast('Enter some text!','warn');return;}
  btn.disabled=true; btn.textContent='Analysing...';
  out.innerHTML='<div class="loading-msg">Gemini analysing...</div>';
  try {
    const r=await geminiAnalyseSentiment(text);
    const oc={positive:'#0d9488',negative:'#e11d48',neutral:'#888',mixed:'#d97706'}[r.overall]||'#888';
    const pct=((Math.max(-100,Math.min(100,r.score))+100)/200)*100;
    const emo=Object.entries(r.emotions||{}).map(([k,v])=>`
      <div class="emo-row"><span class="emo-lbl">${k}</span>
      <div class="emo-bar-w"><div class="emo-bar" style="width:${v}%"></div></div>
      <span class="emo-val">${v}%</span></div>`).join('');
    const phrases=(r.key_phrases||[]).map(p=>`<span class="kp">${p}</span>`).join('');
    out.innerHTML=`
      <div class="sent-header" style="border-color:${oc}">
        <div class="sent-overall" style="color:${oc}">${(r.overall||'').toUpperCase()}</div>
        <div class="sent-tone">Tone: ${r.tone||'—'}</div>
        <div class="score-bar"><span class="score-lbl">Negative</span>
          <div class="score-track"><div class="score-fill" style="width:${pct}%;background:${oc}"></div></div>
          <span class="score-lbl">Positive</span></div>
      </div>
      ${emo?`<div class="emo-section"><div class="sec-ttl">Emotions</div>${emo}</div>`:''}
      ${phrases?`<div class="phrases-section"><div class="sec-ttl">Key phrases</div><div class="phrases">${phrases}</div></div>`:''}
      ${r.insight?`<div class="insight-box"><div class="insight-lbl">✦ Gemini insight</div><div class="insight-txt">${r.insight}</div></div>`:''}`;
  } catch(e){out.innerHTML=`<div class="err-msg">${e.message}</div>`;}
  finally{btn.disabled=false;btn.textContent='Analyse sentiment with Gemini ✦';}
}

async function quickSentiment(btn,text) {
  const orig=btn.innerHTML; btn.disabled=true; btn.textContent='...';
  try { const r=await geminiQuickSentiment(text); showToast(r,'info',4000); }
  catch(e){showToast(e.message,'warn');}
  finally{btn.disabled=false;btn.innerHTML=orig;}
}

async function askTrend() {
  const q=document.getElementById('trendInput').value.trim();
  const out=document.getElementById('trendOutput');
  if(!q){showToast('Ask something first!','warn');return;}
  out.innerHTML='<div class="loading-msg">Gemini researching...</div>';
  try {
    const r=await geminiAskTrend(q);
    out.innerHTML=`<div class="trend-ans"><div class="trend-ans-lbl">✦ Gemini says</div><div class="trend-ans-txt">${r.replace(/\n/g,'<br>')}</div></div>`;
  } catch(e){out.innerHTML=`<div class="err-msg">${e.message}</div>`;}
}

function showToast(msg,type='info',dur=3000) {
  const c=document.getElementById('toastContainer');
  const t=document.createElement('div');
  t.className=`toast toast-${type}`; t.textContent=msg;
  c.appendChild(t);
  setTimeout(()=>{t.style.opacity='0';setTimeout(()=>t.remove(),400);},dur);
}
