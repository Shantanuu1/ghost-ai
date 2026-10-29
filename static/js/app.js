const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
let cid=null, ctrl=null, calm=localStorage.getItem("calm")==="1";
const NAMES={friendly:"Friendly Ghost",mysterious:"Mysterious Ghost",nightmare:"Nightmare Mode"};
const persona=()=>localStorage.getItem("persona")||"friendly";
async function api(url,method="GET",body,signal){
  let r; try{r=await fetch(url,{method,headers:{"Content-Type":"application/json"},body:body?JSON.stringify(body):undefined,signal});}
  catch(e){if(e.name==="AbortError")throw e;throw new Error("Cannot reach the Ghost AI server. Is app.py still running?");}
  let d={};try{d=await r.json();}catch{}
  if(!r.ok)throw new Error(d.error||"Request failed.");return d;}
function md(t){const e=s=>s.replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));
  return t.split("```").map((p,i)=>i%2?"<pre><code>"+e(p.replace(/^[^\n]*\n/,""))+"</code></pre>":e(p)).join("");}
function show(v){$$(".view").forEach(x=>x.classList.toggle("on",x.id==="v-"+v));$$("#nav button").forEach(b=>b.classList.toggle("on",b.dataset.view===v));
  if(v==="memory")loadMem();if(v==="settings")loadStatus();}
$$("#nav button").forEach(b=>b.onclick=()=>show(b.dataset.view));
function tag(){$("#pTag").textContent="Personality: "+NAMES[persona()];$("#persona").value=persona();}
function err(m){const e=$("#err");e.textContent=m;e.hidden=!m;}
function bubble(role,html,isHtml){$("#welcome")?.remove();const d=document.createElement("div");d.className="m "+role;
  isHtml?d.innerHTML=html:d.textContent=html;$("#log").append(d);$("#log").scrollTop=1e9;return d;}
async function send(text){
  err("");bubble("user",text);const w=bubble("bot",'<span class="dots"><span></span><span></span><span></span></span>',true);
  ctrl=new AbortController();$("#send").disabled=true;$("#stop").hidden=false;
  try{const d=await api("/api/chat","POST",{message:text,conversation_id:cid,personality:persona()},ctrl.signal);
    cid=d.conversation_id;w.innerHTML=md(d.reply);loadConvs();}
  catch(e){w.remove();if(e.name!=="AbortError")err(e.message);else err("Stopped. The model may finish in the background, but the reply was discarded.");}
  $("#send").disabled=false;$("#stop").hidden=true;$("#log").scrollTop=1e9;}
$("#chatForm").onsubmit=e=>{e.preventDefault();const t=$("#msg").value.trim();if(!t)return;$("#msg").value="";send(t);};
$("#msg").onkeydown=e=>{if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();$("#chatForm").requestSubmit();}};
$("#stop").onclick=()=>ctrl?.abort();
$("#awaken").onclick=()=>{$("#msg").focus();send("Hello, Ghost. Introduce yourself briefly.");};
$("#newChat").onclick=()=>{cid=null;$("#log").innerHTML="";err("");show("chat");$("#msg").focus();};
async function loadConvs(){try{const l=await api("/api/conversations");$("#convs").innerHTML="";
  l.forEach(c=>{const d=document.createElement("div"),s=document.createElement("span"),x=document.createElement("i");
    s.textContent=c.title;x.textContent="✕";x.title="Delete";x.setAttribute("role","button");d.append(s,x);
    s.ondblclick=async()=>{const t=prompt("Rename conversation",c.title);if(t&&t.trim()){await api("/api/conversations/"+c.id,"PATCH",{title:t});loadConvs();}};
    s.onclick=()=>openConv(c.id);
    x.onclick=async()=>{if(confirm("Delete this conversation?")){await api("/api/conversations/"+c.id,"DELETE");if(cid===c.id){cid=null;$("#log").innerHTML="";}loadConvs();}};
    $("#convs").append(d);});}catch(e){}}
async function openConv(id){try{const c=await api("/api/conversations/"+id);cid=id;$("#log").innerHTML="";err("");
  c.messages.forEach(m=>m.role==="user"?bubble("user",m.content):bubble("bot",md(m.content),true));show("chat");}catch(e){err(e.message);}}
async function run(btn,out,url,payload){btn.disabled=true;out.innerHTML='<span class="dots"><span></span><span></span><span></span></span>';
  try{const d=await api(url,"POST",payload);out.innerHTML=md(d.reply);return d.reply;}catch(e){out.innerHTML="";out.textContent="⚠ "+e.message;}finally{btn.disabled=false;}}
$("#cGo").onclick=()=>run($("#cGo"),$("#cOut"),"/api/code",{code:$("#cIn").value,mode:$("#cMode").value,language:$("#cLang").value,personality:persona()});
$("#zGo").onclick=()=>run($("#zGo"),$("#zOut"),"/api/summarize",{text:$("#zIn").value,personality:persona()});
let story="";
$("#sSet").onchange=()=>$("#sCustom").hidden=$("#sSet").value!=="custom";
$("#sGo").onclick=async()=>{const s=$("#sSet").value==="custom"?$("#sCustom").value:$("#sSet").value;
  story=await run($("#sGo"),$("#sOut"),"/api/story",{setting:s,type:$("#sType").value,intensity:$("#sInt").value,length:$("#sLen").value})||"";};
$("#sCopy").onclick=()=>story&&navigator.clipboard.writeText(story);
$("#sClear").onclick=()=>{story="";$("#sOut").textContent="";};
$("#sSave").onclick=()=>{if(!story)return;const a=document.createElement("a");a.href=URL.createObjectURL(new Blob([story],{type:"text/plain"}));a.download="ghost-story.txt";a.click();};
async function loadMem(){try{const l=await api("/api/memories");$("#mList").innerHTML=l.length?"":"<li>Nothing saved yet.</li>";
  l.forEach(m=>{const li=document.createElement("li"),s=document.createElement("span"),b=document.createElement("button");s.textContent=m.content;b.textContent="Delete";b.className="ghostbtn";
    b.onclick=async()=>{await api("/api/memories/"+m.id,"DELETE");loadMem();};li.append(s,b);$("#mList").append(li);});}catch(e){$("#mList").textContent=e.message;}}
$("#mAdd").onclick=async()=>{try{await api("/api/memories","POST",{content:$("#mIn").value});$("#mIn").value="";loadMem();}catch(e){alert(e.message);}};
$("#mClear").onclick=async()=>{if(confirm("Forget ALL saved memories?")){await api("/api/memories","DELETE");loadMem();}};
$("#hClear").onclick=async()=>{if(confirm("Delete ALL conversations?")){await api("/api/conversations","DELETE");cid=null;$("#log").innerHTML="";loadConvs();}};
async function loadStatus(){try{const s=await api("/api/status");$("#stat").textContent=!s.online?"not reachable":s.model_ready?"connected, model ready":"connected, model missing";$("#hint").textContent=s.hint;}
  catch(e){$("#stat").textContent="unknown";$("#hint").textContent=e.message;}}
$("#persona").onchange=e=>{localStorage.setItem("persona",e.target.value);tag();};
$("#anim").checked=!calm;$("#anim").onchange=e=>{calm=!e.target.checked;localStorage.setItem("calm",calm?"1":"0");document.body.classList.toggle("calm",calm);};
document.body.classList.toggle("calm",calm);
$$(".cards button").forEach(b=>b.onclick=()=>{const g=b.dataset.go;
  if(g==="chat")$("#msg").focus();else if(g==="code"){$("#cMode").value="debug";show("code");}
  else if(g==="learn"){$("#cMode").value="learn";show("code");}else if(g==="story")show("story");else if(g==="summarize")show("summarize");
  else send("What do you remember about me? List my saved memories.");});
(function stars(){const c=$("#stars"),x=c.getContext("2d");let p=[];
  function size(){c.width=innerWidth;c.height=innerHeight;p=Array.from({length:50},()=>({x:Math.random()*c.width,y:Math.random()*c.height,r:Math.random()*1.5+.3,s:Math.random()*.25+.05}));}
  size();addEventListener("resize",size);
  (function f(){x.clearRect(0,0,c.width,c.height);if(!calm&&!matchMedia("(prefers-reduced-motion:reduce)").matches)p.forEach(a=>{a.y-=a.s;if(a.y<0)a.y=c.height;x.fillStyle="rgba(196,181,253,.6)";x.beginPath();x.arc(a.x,a.y,a.r,0,7);x.fill();});requestAnimationFrame(f);})();})();
tag();loadConvs();
