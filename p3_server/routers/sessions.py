from fastapi import APIRouter

from ..schemas.session import SessionStartResponse, SessionEndRequest, SessionEndResponse

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.post("/start", response_model=SessionStartResponse)
async def start_session():
    pass


@router.post("/{session_id}/end", response_model=SessionEndResponse)
async def end_session(session_id: int, body: SessionEndRequest):
    pass