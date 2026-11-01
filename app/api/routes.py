
import uuid

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.agents.executive_assistant import build_graph
from app.memory.short_term import load_session_state, get_conversation_history

router = APIRouter(prefix="/api/assistant", tags=["Executive Assistant"])

_graph = build_graph()


class CommandRequest(BaseModel):
    text: str = Field(..., description="Natural language command, e.g. 'Send a quotation to John for 25 laptops'")
    session_id: str | None = Field(None, description="Reuse an existing session, or omit to start a new one")


class StepResult(BaseModel):
    step_id: int
    outcome: str


class CommandResponse(BaseModel):
    session_id: str
    raw_input: str
    results: list[StepResult]


@router.post("/command", response_model=CommandResponse)
def run_command(payload: CommandRequest):
    """Send a natural-language instruction through the planner -> AI Employees pipeline."""
    session_id = payload.session_id or str(uuid.uuid4())

    try:
        final_state = _graph.invoke({
            "session_id": session_id,
            "raw_input": payload.text,
        })
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Executive Assistant failed to process command: {e}",
        )

    return CommandResponse(
        session_id=session_id,
        raw_input=final_state["raw_input"],
        results=[StepResult(**r) for r in final_state["results"]],
    )


@router.get("/session/{session_id}")
def get_session(session_id: str):
    """Inspect what the assistant currently remembers for a session (state + conversation log)."""
    state = load_session_state(session_id)
    if state is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found or expired")

    return {
        "session_id": session_id,
        "state": state,
        "conversation": get_conversation_history(session_id),
    }