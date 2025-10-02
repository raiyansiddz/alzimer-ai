from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uuid
import json
from datetime import datetime

from core.database.connection import get_db
from core.database.models import TestResult, CognitiveTestResult, TestSession, User
from core.llm.groq_service import groq_service
from core.llm.prompts.cognitive import get_avlt_prompt, get_mmse_prompt, get_moca_prompt, get_digit_span_prompt

router = APIRouter()

class CognitiveTestSubmit(BaseModel):
    session_id: str
    test_name: str
    test_data: Dict[str, Any]
    response_time: Optional[int] = None

class CognitiveTestResponse(BaseModel):
    id: str
    session_id: str
    test_name: str
    score: Optional[float]
    max_score: Optional[float]
    risk_level: Optional[str]
    analysis_result: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True

@router.post("/submit", response_model=CognitiveTestResponse)
async def submit_cognitive_test(test_data: CognitiveTestSubmit, db: Session = Depends(get_db)):
    """
    Submit cognitive test results and get AI analysis
    """
    # Verify session exists
    session = db.query(TestSession).filter(TestSession.id == str(test_data.session_id)).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get user for context
    user = db.query(User).filter(User.id == session.user_id).first()
    user_context = {
        "age": user.age,
        "education_level": user.education_level,
        "language": user.language,
        "vision_type": user.vision_type
    }
    
    # Get appropriate prompt based on test name
    prompt = ""
    if test_data.test_name == "avlt":
        prompt = get_avlt_prompt(test_data.test_data, user_context)
    elif test_data.test_name == "mmse":
        prompt = get_mmse_prompt(test_data.test_data, user_context)
    elif test_data.test_name == "moca":
        prompt = get_moca_prompt(test_data.test_data, user_context)
    elif test_data.test_name == "digit_span":
        prompt = get_digit_span_prompt(test_data.test_data, user_context)
    else:
        # Generic prompt for other tests
        prompt = f"Analyze this {test_data.test_name} test result and provide assessment."
    
    # Get AI analysis
    try:
        analysis = await groq_service.analyze_test_result(prompt, test_data.test_data)
        analysis_result = analysis["analysis"]
    except Exception as e:
        print(f"AI analysis error: {str(e)}")
        analysis_result = {"error": "Analysis failed", "risk_level": "unknown"}
    
    # Calculate score
    score = test_data.test_data.get("total_score", 0)
    max_score = test_data.test_data.get("max_score", 100)
    risk_level = analysis_result.get("risk_level", "medium")
    
    # Create test result
    test_result = TestResult(
        id=str(uuid.uuid4()),
        session_id=str(test_data.session_id),
        test_name=test_data.test_name,
        test_type="cognitive",
        score=float(score) if score else None,
        max_score=float(max_score) if max_score else None,
        risk_level=risk_level,
        raw_data=test_data.test_data,
        analysis_result=analysis_result,
        created_at=datetime.utcnow()
    )
    
    db.add(test_result)
    
    # Create detailed cognitive result
    cognitive_result = CognitiveTestResult(
        id=str(uuid.uuid4()),
        test_result_id=test_result.id,
        test_name=test_data.test_name,
        score=float(score) if score else None,
        max_score=float(max_score) if max_score else None,
        response_time=test_data.response_time,
        details=test_data.test_data
    )
    
    db.add(cognitive_result)
    db.commit()
    db.refresh(test_result)
    
    # Convert UUIDs to strings for response
    return {
        "id": str(test_result.id),
        "session_id": str(test_result.session_id),
        "test_name": test_result.test_name,
        "score": test_result.score,
        "max_score": test_result.max_score,
        "risk_level": test_result.risk_level,
        "analysis_result": test_result.analysis_result
    }

@router.get("/session/{session_id}", response_model=List[CognitiveTestResponse])
async def get_session_cognitive_tests(session_id: str, db: Session = Depends(get_db)):
    """
    Get all cognitive test results for a session
    """
    results = db.query(TestResult).filter(
        TestResult.session_id == str(session_id),
        TestResult.test_type == "cognitive"
    ).all()
    
    # Convert UUIDs to strings for response
    return [{
        "id": str(result.id),
        "session_id": str(result.session_id),
        "test_name": result.test_name,
        "score": result.score,
        "max_score": result.max_score,
        "risk_level": result.risk_level,
        "analysis_result": result.analysis_result
    } for result in results]
