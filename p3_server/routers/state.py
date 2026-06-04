from fastapi import APIRouter, Query

from ..schemas.state import StateReportRequest, StateReportResponse, StateHistoryResponse
from ..services.state_service import report_state, get_state_history

router = APIRouter(prefix="/api/state", tags=["state"])


@router.post("/report", response_model=StateReportResponse)
async def report_state_route(body: StateReportRequest):
    """
    报告学习状态
    
    Args:
        body: 行为信号、SAM量表和摄像头信号
    
    Returns:
        学习状态、评分和建议
    """
    camera_data = None
    if body.camera:
        camera_data = {
            "attention": body.camera.attention,
            "blink_rate": body.camera.blink_rate
        }
    
    result = report_state(
        behavior={
            "correct_rate": body.behavior.correct_rate,
            "avg_time_zscore": body.behavior.avg_time_zscore,
            "unfocus_count": body.behavior.unfocus_count
        },
        sam={
            "valence": body.sam.valence,
            "arousal": body.sam.arousal
        },
        camera=camera_data,
        session_id=body.session_id
    )
    
    return StateReportResponse(
        state=result["state"],
        score=result["score"],
        weights=result["weights"],
        suggestion_text=result["suggestion_text"]
    )


@router.get("/history", response_model=StateHistoryResponse)
async def get_state_history_route(n_days: int = Query(7, ge=1, le=30, description="天数")):
    """
    获取最近 n 天的状态历史
    
    Args:
        n_days: 天数
    
    Returns:
        状态记录列表
    """
    records = get_state_history(n_days)
    return StateHistoryResponse(records=records)
