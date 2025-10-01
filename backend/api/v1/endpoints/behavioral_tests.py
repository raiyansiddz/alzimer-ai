from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uuid
from datetime import datetime

from core.database.connection import get_db
from core.database.models import TestResult, BehavioralTestResult, TestSession

router = APIRouter()

class BehavioralTestSubmit(BaseModel):
    session_id: str
    test_name: str
    response_times: List[int]
    accuracy: float
    test_data: Dict[str, Any]

class BehavioralTestResponse(BaseModel):
    id: str
    session_id: str
    test_name: str
    accuracy: Optional[float]
    efficiency: Optional[float]
    
    class Config:
        from_attributes = True

@router.post("/submit", response_model=BehavioralTestResponse)
async def submit_behavioral_test(test_data: BehavioralTestSubmit, db: Session = Depends(get_db)):
    """
    Submit behavioral test results
    """
    # Verify session exists
    session = db.query(TestSession).filter(TestSession.id == str(test_data.session_id)).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Calculate efficiency (inverse of average response time)
    avg_response_time = sum(test_data.response_times) / len(test_data.response_times) if test_data.response_times else 0
    efficiency = (1000 / avg_response_time) * 100 if avg_response_time > 0 else 0
    
    # Determine risk level based on accuracy and efficiency
    risk_level = "low"
    if test_data.accuracy < 0.6 or efficiency < 50:
        risk_level = "high"
    elif test_data.accuracy < 0.8 or efficiency < 75:
        risk_level = "medium"
    
    # Create test result
    test_result = TestResult(
        id=str(uuid.uuid4()),
        session_id=str(test_data.session_id),
        test_name=test_data.test_name,
        test_type="behavioral",
        score=test_data.accuracy * 100,
        max_score=100.0,
        risk_level=risk_level,
        raw_data=test_data.test_data,
        analysis_result={
            "accuracy": test_data.accuracy,
            "efficiency": efficiency,
            "avg_response_time": avg_response_time
        },
        created_at=datetime.utcnow()
    )
    
    db.add(test_result)
    
    # Create behavioral result
    behavioral_result = BehavioralTestResult(
        id=str(uuid.uuid4()),
        test_result_id=test_result.id,
        test_name=test_data.test_name,
        response_times=test_data.response_times,
        accuracy=test_data.accuracy,
        efficiency=efficiency,
        details=test_data.test_data
    )
    
    db.add(behavioral_result)
    db.commit()
    db.refresh(test_result)
    
    return behavioral_result

@router.get("/session/{session_id}", response_model=List[BehavioralTestResponse])
async def get_session_behavioral_tests(session_id: str, db: Session = Depends(get_db)):
    """
    Get all behavioral test results for a session
    """
    results = db.query(BehavioralTestResult).join(TestResult).filter(
        TestResult.session_id == str(session_id),
        TestResult.test_type == "behavioral"
    ).all()
    
    return results
