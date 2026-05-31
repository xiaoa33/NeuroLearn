from fastapi import APIRouter

from ..schemas.state import StateReportRequest, StateReportResponse, StateHistoryResponse

router = APIRouter(prefix="/api/state", tags=["state"])


@router.post("/report", response_model=StateReportResponse)
async def report_state(body: StateReportRequest):
    pass


@router.get("/history", response_model=StateHistoryResponse)
async def get_state_history():
    pass