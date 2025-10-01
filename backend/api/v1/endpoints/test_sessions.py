from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
import uuid

from core.database.connection import get_db
from core.database.models import TestSession, User

router = APIRouter()

class TestSessionCreate(BaseModel):
    user_id: str
    session_type: str  # baseline, monthly, weekly, daily, follow_up

class TestSessionUpdate(BaseModel):
    status: Optional[str] = None
    overall_score: Optional[float] = None
    overall_risk_level: Optional[str] = None
    next_recommended_date: Optional[date] = None

class TestSessionResponse(BaseModel):
    id: str
    user_id: str
    session_type: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    overall_score: Optional[float]
    overall_risk_level: Optional[str]
    next_recommended_date: Optional[date]
    
    class Config:
        from_attributes = True

@router.post("/", response_model=TestSessionResponse)
async def create_test_session(session_data: TestSessionCreate, db: Session = Depends(get_db)):
    """
    Create a new test session
    """
    # Verify user exists
    user = db.query(User).filter(User.id == str(session_data.user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_session = TestSession(
        id=str(uuid.uuid4()),
        user_id=str(session_data.user_id),
        session_type=session_data.session_type,
        status="in_progress",
        started_at=datetime.utcnow()
    )
    
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    
    return new_session

@router.get("/{session_id}", response_model=TestSessionResponse)
async def get_test_session(session_id: str, db: Session = Depends(get_db)):
    """
    Get test session details
    """
    session = db.query(TestSession).filter(TestSession.id == str(session_id)).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session

@router.get("/user/{user_id}", response_model=List[TestSessionResponse])
async def get_user_sessions(user_id: str, db: Session = Depends(get_db)):
    """
    Get all sessions for a user
    """
    sessions = db.query(TestSession).filter(TestSession.user_id == str(user_id)).order_by(TestSession.started_at.desc()).all()
    return sessions

@router.put("/{session_id}", response_model=TestSessionResponse)
async def update_test_session(session_id: str, session_data: TestSessionUpdate, db: Session = Depends(get_db)):
    """
    Update test session
    """
    session = db.query(TestSession).filter(TestSession.id == str(session_id)).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Update fields
    for field, value in session_data.dict(exclude_unset=True).items():
        setattr(session, field, value)
    
    if session_data.status == "completed":
        session.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(session)
    
    return session
