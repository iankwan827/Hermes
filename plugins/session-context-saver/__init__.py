"""
session-context-saver — Saves last 100 messages of an expired session to a JSON file.

When a session expires (idle timeout or daily reset), this plugin reads
the last 100 messages from the session database and saves them to
~/.hermes/last_session_messages.json. The next session can read this
file to restore context from the previous conversation.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

LAST_SESSION_FILE = Path.home() / ".hermes" / "last_session_messages.json"
MAX_MESSAGES = 100


def _get_db_path() -> Path:
    """Get the state.db path for the current profile."""
    from hermes_constants import get_hermes_home
    return get_hermes_home() / "state.db"


def _save_session_messages(session_id: str) -> bool:
    """Read last MAX_MESSAGES from session and save to JSON file."""
    try:
        db_path = _get_db_path()
        if not db_path.exists() or db_path.stat().st_size == 0:
            logger.debug("state.db not found or empty, skipping context save")
            return False

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Get session metadata
        cursor.execute(
            "SELECT id, source, started_at, ended_at, title FROM sessions WHERE id = ?",
            (session_id,),
        )
        session_row = cursor.fetchone()
        if not session_row:
            conn.close()
            return False

        # Get last N messages (excluding tool results for readability)
        cursor.execute(
            """SELECT role, content, tool_call_id, tool_calls, tool_name, timestamp
               FROM messages
               WHERE session_id = ?
                 AND role IN ('user', 'assistant')
                 AND content IS NOT NULL
                 AND content != ''
               ORDER BY timestamp DESC
               LIMIT ?""",
            (session_id, MAX_MESSAGES),
        )
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return False

        # Reverse to chronological order
        rows.reverse()

        messages = []
        for role, content, tool_call_id, tool_calls, tool_name, timestamp in rows:
            msg = {"role": role, "content": content, "timestamp": timestamp}
            messages.append(msg)

        data = {
            "session_id": session_row[0],
            "source": session_row[1],
            "started_at": session_row[2],
            "ended_at": session_row[3],
            "title": session_row[4],
            "message_count": len(messages),
            "messages": messages,
        }

        LAST_SESSION_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))
        logger.info(
            "Saved %d messages from session %s to %s",
            len(messages), session_id, LAST_SESSION_FILE,
        )
        return True

    except Exception as e:
        logger.error("Failed to save session context: %s", e)
        return False


def register(ctx: Any) -> None:
    """Register the on_session_finalize hook."""

    def on_session_finalize(**kwargs: Any) -> None:
        reason = kwargs.get("reason", "")
        session_id = kwargs.get("session_id", "")

        # Only save on session expiry (idle timeout or daily reset)
        if reason != "session_expired":
            return

        if not session_id:
            return

        logger.info(
            "Session %s expired (reason=%s), saving last %d messages",
            session_id, reason, MAX_MESSAGES,
        )
        _save_session_messages(session_id)

    ctx.register_hook("on_session_finalize", on_session_finalize)
