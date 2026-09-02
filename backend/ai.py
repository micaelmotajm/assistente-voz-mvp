"""
Camada de inteligência.

O contrato é estável para que o parser local possa ser trocado por um LLM
sem alterar a API. Em produção, implemente um provider seguro aqui.
"""

import re
from datetime import datetime, timedelta
from dateutil import parser as dateparser

WEEKDAYS = {
    "segunda": 0, "terça": 1, "terca": 1, "quarta": 2,
    "quinta": 3, "sexta": 4, "sábado": 5, "sabado": 5, "domingo": 6
}

def _date_from_text(text):
    now = datetime.now()
    low = text.lower()
    if "amanhã" in low or "amanha" in low:
        return (now + timedelta(days=1)).date()
    if "hoje" in low:
        return now.date()
    for name, weekday in WEEKDAYS.items():
        if name in low:
            days = (weekday - now.weekday()) % 7
            days = 7 if days == 0 else days
            return (now + timedelta(days=days)).date()
    return None

def _time_from_text(text):
    patterns = [
        r"\b(?:às|as|a)\s*(\d{1,2})(?:[:h](\d{2}))?\b",
        r"\b(\d{1,2})h(?:\s*(\d{2}))?\b",
    ]
    for pattern in patterns:
        m = re.search(pattern, text.lower())
        if m:
            hour = int(m.group(1))
            minute = int(m.group(2) or 0)
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return hour, minute
    return None

def _duration(text):
    low = text.lower()

    # Prioridade 1: duração explícita, introduzida por "por"/"durante"
    # (ex.: "por 1 hora", "durante 30 minutos") — evita confundir com o horário.
    m = re.search(r"(?:por|durante)\s+(\d+)\s*(hora|horas|min|minutos|h)\b", low)

    # Prioridade 2: "X minutos/horas de duração"
    if not m:
        m = re.search(r"(\d+)\s*(hora|horas|min|minutos)\s+de\s+dura[cç][aã]o", low)

    # Prioridade 3 (fallback): primeiro número+unidade que não pareça ser
    # um horário do tipo "às 9h" / "as 9h".
    if not m:
        for candidate in re.finditer(r"(\d+)\s*(hora|horas|min|minutos|h)\b", low):
            prefix = low[max(0, candidate.start() - 4):candidate.start()]
            if "às" in prefix or re.search(r"\bas\s*$", prefix):
                continue
            m = candidate
            break

    if not m:
        return 60
    value = int(m.group(1))
    return value * 60 if m.group(2).startswith("hora") or m.group(2) == "h" else value

def interpret(text):
    low = text.lower()
    date = _date_from_text(text)
    time = _time_from_text(text)
    due_at = start_at = None

    if date and time:
        dt = datetime.combine(date, datetime.min.time()).replace(
            hour=time[0], minute=time[1]
        )
        start_at = dt.isoformat(timespec="minutes")

    intent = "task"
    if any(k in low for k in ["reunião", "reuniao", "encontro", "call", "meeting"]):
        intent = "event"
    elif any(k in low for k in ["estudar", "estudo", "aprender", "revisar"]):
        intent = "study"

    if intent == "task" and start_at:
        due_at = start_at

    title = text.strip()
    participants = None
    m = re.search(r"(?:com|com o|com a)\s+([A-ZÁÉÍÓÚÃÕÂÊÔÇ][\wÁÉÍÓÚÃÕÂÊÔÇ]*(?:\s+[A-ZÁÉÍÓÚÃÕÂÊÔÇ][\wÁÉÍÓÚÃÕÂÊÔÇ]*)?)", text)
    if m and intent == "event":
        participants = m.group(1)

    priority = "high" if any(k in low for k in ["urgente", "prioridade alta", "importante"]) else "medium"
    if any(k in low for k in ["algum dia", "quando puder"]):
        priority = "low"

    return {
        "intent": intent,
        "title": title,
        "due_at": due_at,
        "start_at": start_at,
        "duration_minutes": _duration(text),
        "priority": priority,
        "participants": participants,
        "notes": None,
        "confidence": 0.82 if (date or time or intent != "task") else 0.58,
    }

def meeting_brief(transcript):
    lines = [x.strip("-• \t") for x in transcript.splitlines() if x.strip()]
    decisions, actions, points = [], [], []
    for line in lines:
        low = line.lower()
        if any(k in low for k in ["decidimos", "decisão", "decidido", "vamos"]):
            decisions.append(line)
        if any(k in low for k in ["tarefa", "preciso", "deve", "ficou para", "responsável"]):
            actions.append(line)
        points.append(line)

    return {
        "summary": " ".join(points[:5])[:1200],
        "key_points": points[:10],
        "decisions": decisions[:10],
        "actions": actions[:10],
        "next_step": actions[0] if actions else "Definir a próxima ação da reunião."
    }

def study_plan(subject, goal, minutes_per_day, days_per_week):
    methods = [
        "Revisão ativa: tente explicar o conteúdo sem consultar material.",
        "Prática deliberada: resolva exercícios/problemas progressivos.",
        "Revisão espaçada: retome conteúdos anteriores antes do novo tópico.",
        "Projeto prático: aplique o conteúdo em uma pequena entrega.",
    ]
    days = []
    for i in range(days_per_week):
        days.append({
            "day": i + 1,
            "minutes": minutes_per_day,
            "method": methods[i % len(methods)],
            "activity": f"{'Teoria + exercícios' if i % 2 == 0 else 'Revisão + prática'} de {subject}."
        })
    return {
        "subject": subject,
        "goal": goal,
        "weekly_minutes": minutes_per_day * days_per_week,
        "days": days
    }
