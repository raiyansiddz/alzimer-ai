from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date, timedelta
import uuid

from core.database.connection import get_db
from core.database.models import ProgressTracking, TestResult, TestSession, User

router = APIRouter()

class ProgressResponse(BaseModel):
    id: str
    user_id: str
    test_name: str
    date: date
    score: float
    risk_level: str
    change_from_previous: Optional[float]
    trend: Optional[str]
    
    class Config:
        from_attributes = True

class ProgressComparisonResponse(BaseModel):
    test_name: str
    current_score: float
    previous_score: Optional[float]
    change_percentage: Optional[float]
    trend: str
    data_points: List[dict]

@router.get("/user/{user_id}", response_model=List[ProgressResponse])
async def get_user_progress(user_id: str, db: Session = Depends(get_db)):
    """
    Get progress tracking data for a user
    """
    progress = db.query(ProgressTracking).filter(
        ProgressTracking.user_id == str(user_id)
    ).order_by(ProgressTracking.date.desc()).all()
    
    return progress

@router.get("/user/{user_id}/comparison", response_model=List[ProgressComparisonResponse])
async def get_progress_comparison(user_id: str, db: Session = Depends(get_db)):
    """
    Get progress comparison with visualization data
    """
    # Get all test sessions for user
    sessions = db.query(TestSession).filter(
        TestSession.user_id == str(user_id),
        TestSession.status == "completed"
    ).order_by(TestSession.completed_at).all()
    
    if not sessions:
        return []
    
    # Group results by test name
    test_groups = {}
    
    for session in sessions:
        results = db.query(TestResult).filter(
            TestResult.session_id == session.id
        ).all()
        
        for result in results:
            if result.test_name not in test_groups:
                test_groups[result.test_name] = []
            
            test_groups[result.test_name].append({
                "date": session.completed_at.date().isoformat(),
                "score": result.score,
                "risk_level": result.risk_level
            })
    
    # Calculate comparisons
    comparisons = []
    
    for test_name, data_points in test_groups.items():
        if len(data_points) < 2:
            comparisons.append(ProgressComparisonResponse(
                test_name=test_name,
                current_score=data_points[0]["score"] if data_points else 0,
                previous_score=None,
                change_percentage=None,
                trend="insufficient_data",
                data_points=data_points
            ))
            continue
        
        current = data_points[-1]
        previous = data_points[-2]
        
        current_score = current["score"] or 0
        previous_score = previous["score"] or 0
        
        change = current_score - previous_score
        change_percentage = (change / previous_score * 100) if previous_score > 0 else 0
        
        # Determine trend
        if abs(change_percentage) < 5:
            trend = "stable"
        elif change_percentage > 0:
            trend = "improving"
        else:
            trend = "declining"
        
        comparisons.append(ProgressComparisonResponse(
            test_name=test_name,
            current_score=current_score,
            previous_score=previous_score,
            change_percentage=change_percentage,
            trend=trend,
            data_points=data_points
        ))
    
    return comparisons

@router.post("/calculate-next-date/{user_id}")
async def calculate_next_test_date(user_id: str, db: Session = Depends(get_db)):
    """
    Calculate recommended next test date based on risk level
    """
    # Get latest completed session
    latest_session = db.query(TestSession).filter(
        TestSession.user_id == str(user_id),
        TestSession.status == "completed"
    ).order_by(TestSession.completed_at.desc()).first()
    
    if not latest_session:
        return {
            "next_date": (datetime.utcnow() + timedelta(days=30)).date(),
            "frequency": "monthly",
            "reason": "Initial baseline"
        }
    
    # Determine frequency based on risk level
    risk_level = latest_session.overall_risk_level or "medium"
    
    frequency_map = {
        "high": {"days": 7, "frequency": "weekly"},
        "medium": {"days": 30, "frequency": "monthly"},
        "low": {"days": 90, "frequency": "quarterly"}
    }
    
    config = frequency_map.get(risk_level, frequency_map["medium"])
    next_date = datetime.utcnow() + timedelta(days=config["days"])
    
    # Update session with next recommended date
    latest_session.next_recommended_date = next_date.date()
    db.commit()
    
    return {
        "next_date": next_date.date(),
        "frequency": config["frequency"],
        "reason": f"Based on {risk_level} risk level assessment"
    }
