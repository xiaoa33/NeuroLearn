from fastapi import APIRouter, HTTPException
from datetime import datetime

from ..schemas.session import SessionStartResponse, SessionEndRequest, SessionEndResponse

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

# 添加路径
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "p2_knowledge"))
from p2_knowledge.db_service import create_session, end_session as db_end_session
from p2_knowledge.db_service import SessionLocal
from p2_knowledge.models.session import LearningSession


@router.post("/start", response_model=SessionStartResponse)
async def start_session_route():
    """
    开始一个新的学习会话
    
    Returns:
        会话ID和开始时间
    """
    session_id = create_session()
    if session_id == -1:
        raise HTTPException(status_code=500, detail="创建会话失败")
    
    # 获取会话信息
    db = SessionLocal()
    try:
        session = db.query(LearningSession).filter(LearningSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=500, detail="创建会话失败")
        
        return SessionStartResponse(
            session_id=session.id,
            started_at=session.started_at
        )
    finally:
        db.close()


@router.post("/{session_id}/end", response_model=SessionEndResponse)
async def end_session_route(session_id: int, body: SessionEndRequest):
    """
    结束学习会话
    
    Args:
        session_id: 会话ID
        body: 会话结束信息
    
    Returns:
        会话结束信息和时长
    """
    success = db_end_session(
        session_id=session_id,
        final_state=body.final_state,
        sam_valence=body.sam_valence,
        sam_arousal=body.sam_arousal,
        cards_reviewed=body.cards_reviewed,
        questions_answered=body.questions_answered
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    # 获取会话信息
    db = SessionLocal()
    try:
        session = db.query(LearningSession).filter(LearningSession.id == session_id).first()
        if not session or not session.ended_at:
            raise HTTPException(status_code=500, detail="结束会话失败")
        
        # 计算时长
        duration = (session.ended_at - session.started_at).total_seconds() / 60
        
        return SessionEndResponse(
            session_id=session.id,
            ended_at=session.ended_at,
            duration_minutes=round(duration, 2)
        )
    finally:
        db.close()
