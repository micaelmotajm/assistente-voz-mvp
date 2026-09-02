from datetime import datetime, date
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from db import get_db, init_db
from schemas import (
    TaskCreate, TaskUpdate, EventCreate, InterpretRequest,
    InterpretResponse, MeetingBriefRequest, StudyPlanRequest
)
from ai import interpret, meeting_brief, study_plan

BASE = Path(__file__).resolve().parent.parent
FRONTEND = BASE / "frontend"

app = FastAPI(title="Assistente Voz API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

@app.on_event("startup")
def startup():
    init_db()

def row_dict(row):
    return dict(row) if row else None

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "assistente-voz"}

@app.post("/api/interpret", response_model=InterpretResponse)
def api_interpret(payload: InterpretRequest):
    return interpret(payload.text)

@app.get("/api/tasks")
def list_tasks(status: str | None = None):
    with get_db() as db:
        if status:
            rows = db.execute("SELECT * FROM tasks WHERE status=? ORDER BY due_at", (status,)).fetchall()
        else:
            rows = db.execute("SELECT * FROM tasks ORDER BY due_at").fetchall()
        return [row_dict(r) for r in rows]

@app.post("/api/tasks")
def create_task(payload: TaskCreate):
    with get_db() as db:
        cur = db.execute(
            "INSERT INTO tasks(title,due_at,priority,status,notes,created_at) VALUES(?,?,?,?,?,?)",
            (payload.title, payload.due_at, payload.priority, "pending",
             payload.notes, datetime.now().isoformat(timespec="seconds"))
        )
        return {"id": cur.lastrowid, **payload.model_dump(), "status": "pending"}

@app.patch("/api/tasks/{task_id}")
def update_task(task_id: int, payload: TaskUpdate):
    data = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not data:
        raise HTTPException(400, "Nenhuma alteração enviada.")
    sets = ", ".join(f"{k}=?" for k in data)
    values = list(data.values()) + [task_id]
    with get_db() as db:
        cur = db.execute(f"UPDATE tasks SET {sets} WHERE id=?", values)
        if cur.rowcount == 0:
            raise HTTPException(404, "Tarefa não encontrada.")
        row = db.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
        return row_dict(row)

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int):
    with get_db() as db:
        cur = db.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        if cur.rowcount == 0:
            raise HTTPException(404, "Tarefa não encontrada.")
    return {"deleted": True}

@app.get("/api/events")
def list_events():
    with get_db() as db:
        rows = db.execute("SELECT * FROM events ORDER BY start_at").fetchall()
        return [row_dict(r) for r in rows]

@app.post("/api/events")
def create_event(payload: EventCreate):
    with get_db() as db:
        cur = db.execute(
            "INSERT INTO events(title,start_at,duration_minutes,participants,notes,created_at) VALUES(?,?,?,?,?,?)",
            (payload.title, payload.start_at, payload.duration_minutes,
             payload.participants, payload.notes, datetime.now().isoformat(timespec="seconds"))
        )
        return {"id": cur.lastrowid, **payload.model_dump()}

@app.post("/api/meetings/brief")
def meeting_brief_api(payload: MeetingBriefRequest):
    return meeting_brief(payload.transcript)

@app.post("/api/study/plan")
def study_plan_api(payload: StudyPlanRequest):
    plan = study_plan(payload.subject, payload.goal, payload.minutes_per_day, payload.days_per_week)
    with get_db() as db:
        db.execute(
            "INSERT INTO study_plans(subject,goal,minutes_per_day,days_per_week,method,created_at) VALUES(?,?,?,?,?,?)",
            (payload.subject, payload.goal, payload.minutes_per_day,
             payload.days_per_week, "adaptive", datetime.now().isoformat(timespec="seconds"))
        )
    return plan

@app.get("/api/dashboard")
def dashboard():
    with get_db() as db:
        tasks = db.execute(
            "SELECT * FROM tasks WHERE status='pending' ORDER BY due_at LIMIT 20"
        ).fetchall()
        events = db.execute(
            "SELECT * FROM events ORDER BY start_at LIMIT 20"
        ).fetchall()
        return {"tasks": [row_dict(x) for x in tasks], "events": [row_dict(x) for x in events]}

app.mount("/static", StaticFiles(directory=FRONTEND), name="static")

@app.get("/")
def home():
    return FileResponse(FRONTEND / "index.html")
