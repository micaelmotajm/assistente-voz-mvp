const $ = id => document.getElementById(id);

async function api(path, options={}) {
  const r = await fetch(path, {headers: {"Content-Type":"application/json"}, ...options});
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

async function load() {
  const data = await api("/api/dashboard");
  $("events").innerHTML = data.events.length ? data.events.map(e =>
    `<div class="item"><b>${esc(e.title)}</b><small>${fmt(e.start_at)} · ${e.duration_minutes} min</small>${e.participants ? `<span class="tag">👤 ${esc(e.participants)}</span>` : ""}</div>`
  ).join("") : "<p>Nenhum evento cadastrado.</p>";
  $("tasks").innerHTML = data.tasks.length ? data.tasks.map(t =>
    `<div class="item"><b>${esc(t.title)}</b><small>${t.due_at ? fmt(t.due_at) : "Sem prazo"} · prioridade ${t.priority}</small><button onclick="done(${t.id})">Concluir</button></div>`
  ).join("") : "<p>Nenhuma tarefa pendente.</p>";
}
function esc(s){return String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]))}
function fmt(s){return s ? new Date(s).toLocaleString("pt-BR",{dateStyle:"short",timeStyle:"short"}) : ""}

$("process").onclick = async () => {
  const text = $("input").value.trim();
  if (!text) return;
  const x = await api("/api/interpret",{method:"POST",body:JSON.stringify({text})});
  $("interpretation").innerHTML = `<p><b>Entendi como:</b> ${esc(x.intent)} — ${esc(x.title)}</p>`;
  if (x.intent === "event" && x.start_at) {
    await api("/api/events",{method:"POST",body:JSON.stringify({
      title:x.title,start_at:x.start_at,duration_minutes:x.duration_minutes,
      participants:x.participants,notes:x.notes
    })});
  } else {
    await api("/api/tasks",{method:"POST",body:JSON.stringify({
      title:x.title,due_at:x.due_at,priority:x.priority,notes:x.notes
    })});
  }
  $("input").value="";
  load();
};

async function done(id){await api(`/api/tasks/${id}`,{method:"PATCH",body:JSON.stringify({status:"done"})});load()}
window.done=done;

$("brief").onclick = async () => {
  const x = await api("/api/meetings/brief",{method:"POST",body:JSON.stringify({transcript:$("transcript").value})});
  $("briefing").textContent = JSON.stringify(x,null,2);
};

$("study").onclick = async () => {
  const x = await api("/api/study/plan",{method:"POST",body:JSON.stringify({
    subject:$("subject").value,goal:$("goal").value,
    minutes_per_day:Number($("minutes").value),days_per_week:Number($("days").value)
  })});
  $("studyout").textContent = JSON.stringify(x,null,2);
};

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
if (SpeechRecognition) {
  const rec = new SpeechRecognition();
  rec.lang="pt-BR"; rec.interimResults=true;
  rec.onstart=()=> $("mic").classList.add("listening");
  rec.onend=()=> $("mic").classList.remove("listening");
  rec.onresult=e=> $("input").value=Array.from(e.results).map(r=>r[0].transcript).join("");
  $("mic").onclick=()=>rec.start();
} else {
  $("mic").title="Reconhecimento de voz não disponível neste navegador.";
}

load();
