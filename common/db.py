from __future__ import annotations

import json
import sqlite3
import time
from typing import Any, Optional
from common.config import DATABASE_PATH


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DATABASE_PATH), timeout=10.0)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cases (
                id TEXT PRIMARY KEY,
                user_addr TEXT NOT NULL,
                category TEXT NOT NULL,
                company TEXT NOT NULL,
                facts_json TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at REAL NOT NULL,
                deadline_at REAL NOT NULL,
                tier INTEGER NOT NULL DEFAULT 1,
                email_msg_id TEXT,
                tracking_paid INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT NOT NULL,
                ts REAL NOT NULL,
                kind TEXT NOT NULL,
                detail TEXT NOT NULL,
                FOREIGN KEY(case_id) REFERENCES cases(id)
            )
            """
        )
        conn.commit()


def save_case(
    case_id: str,
    user_addr: str,
    category: str,
    company: str,
    facts_json: str,
    status: str = "INTAKE",
    deadline_at: float = 0.0,
    tier: int = 1,
    email_msg_id: str | None = None,
    tracking_paid: int = 0,
) -> None:
    now = time.time()
    if deadline_at <= 0.0:
        deadline_at = now + 120.0  # 2 minutes default

    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO cases (
                id, user_addr, category, company, facts_json, status, created_at, deadline_at, tier, email_msg_id, tracking_paid
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                case_id,
                user_addr,
                category,
                company,
                facts_json,
                status,
                now,
                deadline_at,
                tier,
                email_msg_id,
                tracking_paid,
            ),
        )
        conn.commit()


def update_case_status(
    case_id: str,
    status: str,
    deadline_at: float | None = None,
    tier: int | None = None,
    email_msg_id: str | None = None,
) -> None:
    updates = ["status = ?"]
    params: list[Any] = [status]
    if deadline_at is not None:
        updates.append("deadline_at = ?")
        params.append(deadline_at)
    if tier is not None:
        updates.append("tier = ?")
        params.append(tier)
    if email_msg_id is not None:
        updates.append("email_msg_id = ?")
        params.append(email_msg_id)

    params.append(case_id)
    with get_db_connection() as conn:
        conn.execute(f"UPDATE cases SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()


def mark_tracking_paid(case_id: str) -> None:
    with get_db_connection() as conn:
        conn.execute("UPDATE cases SET tracking_paid = 1 WHERE id = ?", (case_id,))
        conn.commit()


def get_case(case_id: str) -> Optional[dict[str, Any]]:
    with get_db_connection() as conn:
        cur = conn.execute("SELECT * FROM cases WHERE id = ?", (case_id,))
        row = cur.fetchone()
        if row:
            return dict(row)
        return None


def get_active_case_for_user(user_addr: str) -> Optional[dict[str, Any]]:
    with get_db_connection() as conn:
        cur = conn.execute(
            "SELECT * FROM cases WHERE user_addr = ? AND status NOT IN ('CLOSED', 'RESOLVED') ORDER BY created_at DESC LIMIT 1",
            (user_addr,),
        )
        row = cur.fetchone()
        if row:
            return dict(row)
        return None


def list_due_waiting_cases(now_ts: float | None = None) -> list[dict[str, Any]]:
    if now_ts is None:
        now_ts = time.time()
    with get_db_connection() as conn:
        cur = conn.execute(
            "SELECT * FROM cases WHERE status = 'WAITING' AND deadline_at <= ? ORDER BY deadline_at ASC",
            (now_ts,),
        )
        return [dict(row) for row in cur.fetchall()]


def record_event(case_id: str, kind: str, detail: str) -> None:
    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO events (case_id, ts, kind, detail) VALUES (?, ?, ?, ?)",
            (case_id, time.time(), kind, detail),
        )
        conn.commit()


def get_case_events(case_id: str) -> list[dict[str, Any]]:
    with get_db_connection() as conn:
        cur = conn.execute(
            "SELECT * FROM events WHERE case_id = ? ORDER BY ts ASC",
            (case_id,),
        )
        return [dict(row) for row in cur.fetchall()]
