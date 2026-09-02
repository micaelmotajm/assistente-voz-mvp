from pydantic import BaseModel, Field
from typing import Optional, Literal

Priority = Literal["low", "medium", "high"]
TaskStatus = Literal["pending", "done", "cancelled"]

class TaskCreate(BaseModel):
    title: str
    due_at: Optional[str] = None
    priority: Priority = "medium"
    notes: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    due_at: Optional[str] = None
    priority: Optional[Priority] = None
    status: Optional[TaskStatus] = None
    notes: Optional[str] = None

class EventCreate(BaseModel):
    title: str
    start_at: str
    duration_minutes: int = Field(default=60, ge=1, le=1440)
    participants: Optional[str] = None
    notes: Optional[str] = None

class InterpretRequest(BaseModel):
    text: str

class InterpretResponse(BaseModel):
    intent: str
    title: str
    due_at: Optional[str] = None
    start_at: Optional[str] = None
    duration_minutes: int = 60
    priority: Priority = "medium"
    participants: Optional[str] = None
    notes: Optional[str] = None
    confidence: float = 0.0

class MeetingBriefRequest(BaseModel):
    transcript: str

class StudyPlanRequest(BaseModel):
    subject: str
    goal: str
    minutes_per_day: int = Field(default=60, ge=10, le=480)
    days_per_week: int = Field(default=5, ge=1, le=7)
