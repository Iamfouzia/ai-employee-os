"""
Phase 3a: Short-Term Memory (Redis)
--------------------------------------
Holds the ACTIVE conversation/session state - things that matter only
while a task is in progress. e.g. "the plan we're currently executing",
"which step we're on", "what the user said 2 messages ago".

Everything here is scoped by session_id and expires automatically (TTL) -
this is NOT where permanent customer history lives (that's long_term.py).
"""

import json
import redis
from app.nlu.schemas import TaskPlan

DEFAULT_TTL_SECONDS = 60 * 60 * 6  # 6 hours - a session shouldn't outlive a workday

_r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


def save_session_state(session_id: str, state: dict, ttl: int = DEFAULT_TTL_SECONDS) -> None:
    """Persist the current graph state (raw_input, task_plan, results, etc.) for a session."""
    serializable = dict(state)
    if isinstance(serializable.get("task_plan"), TaskPlan):
        serializable["task_plan"] = serializable["task_plan"].model_dump()
    _r.set(f"session:{session_id}", json.dumps(serializable), ex=ttl)


def load_session_state(session_id: str) -> dict | None:
    """Get back whatever state was last saved for this session, or None if expired/missing."""
    raw = _r.get(f"session:{session_id}")
    if raw is None:
        return None
    return json.loads(raw)


def append_conversation_turn(session_id: str, role: str, content: str, ttl: int = DEFAULT_TTL_SECONDS) -> None:
    """Keep a rolling log of the conversation for this session (for context memory)."""
    key = f"conversation:{session_id}"
    _r.rpush(key, json.dumps({"role": role, "content": content}))
    _r.expire(key, ttl)


def get_conversation_history(session_id: str) -> list[dict]:
    """Return the full conversation turn list for this session."""
    key = f"conversation:{session_id}"
    raw_turns = _r.lrange(key, 0, -1)
    return [json.loads(t) for t in raw_turns]


def clear_session(session_id: str) -> None:
    """Wipe a session's state and conversation history (e.g. task fully completed)."""
    _r.delete(f"session:{session_id}", f"conversation:{session_id}")


if __name__ == "__main__":
    sid = "test-session-1"
    append_conversation_turn(sid, "user", "Send a quotation to John for 25 laptops")
    append_conversation_turn(sid, "assistant", "Quotation sent, tracking reply.")
    save_session_state(sid, {"raw_input": "Send a quotation to John for 25 laptops", "current_step_index": 1})

    print("History:", get_conversation_history(sid))
    print("State:", load_session_state(sid))