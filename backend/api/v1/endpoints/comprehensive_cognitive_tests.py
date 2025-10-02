from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import json
import uuid

from core.database.connection import get_db
from core.database.models import User, TestSession, TestResult, CognitiveTestResult
from core.tests.cognitive_test_engine import cognitive_test_engine, UserType
from core.analysis.llm_analysis_engine import llm_analysis_engine
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic Models
class TestSessionCreate(BaseModel):
    user_id: str
    session_type: str = "cognitive_assessment"
    
class AVLTRequest(BaseModel):
    user_id: str
    session_id: str
    trial_number: int = 1

class AVLTResponse(BaseModel):
    user_id: str
    session_id: str
    words_recalled: List[str]
    response_times: List[float]
    trial_number: int

class DigitSpanRequest(BaseModel):
    user_id: str
    session_id: str
    direction: str = "forward"  # forward or backward

class DigitSpanResponse(BaseModel):
    user_id: str
    session_id: str
    sequences_attempted: List[List[int]]
    sequences_correct: List[bool]
    max_span_achieved: int

class MMSERequest(BaseModel):
    user_id: str
    session_id: str

class MMSEResponse(BaseModel):
    user_id: str
    session_id: str
    section_scores: Dict[str, int]
    total_score: int
    completion_time: float
    adaptations_used: List[str]

class SimpleMemoryRequest(BaseModel):
    user_id: str
    session_id: str

class SimpleMemoryResponse(BaseModel):
    user_id: str
    session_id: str
    items_recalled: List[str]
    accuracy_percentage: float
    cues_needed: int

# BLIND USER COGNITIVE TESTS
@router.post("/blind/avlt/start", summary="Start AVLT test for blind users")
async def start_avlt_blind(request: AVLTRequest, db: Session = Depends(get_db)):
    """Start Auditory Verbal Learning Test for blind users"""
    try:
        # Get user information
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Generate test configuration
        test_config = await cognitive_test_engine.run_avlt_test(request.user_id, request.trial_number)
        
        # Create test result entry
        test_result = TestResult(
            id=str(uuid.uuid4()),
            session_id=request.session_id,
            test_name="AVLT",
            test_type="cognitive",
            raw_data=test_config,
            created_at=datetime.utcnow()
        )
        db.add(test_result)
        db.commit()
        
        return {
            "test_result_id": test_result.id,
            "test_config": test_config,
            "status": "started"
        }
    
    except Exception as e:
        logger.error(f"AVLT start failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/blind/avlt/submit", summary="Submit AVLT responses for blind users")
async def submit_avlt_blind(response: AVLTResponse, db: Session = Depends(get_db)):
    """Submit AVLT test responses and get analysis"""
    try:
        # Get user and test result
        user = db.query(User).filter(User.id == response.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        test_result = db.query(TestResult).filter(
            TestResult.session_id == response.session_id,
            TestResult.test_name == "AVLT"
        ).first()
        
        if not test_result:
            raise HTTPException(status_code=404, detail="Test result not found")
        
        # Prepare test data for analysis
        test_data = {
            f"trial_{response.trial_number}_recall": response.words_recalled,
            "response_times": response.response_times,
            "trial_number": response.trial_number,
            "words_presented": test_result.raw_data.get("words_presented", [])
        }
        
        # Get user context
        user_context = {
            "age": user.age,
            "education_level": user.education_level,
            "language": user.language,
            "user_type": "blind"
        }
        
        # Analyze with LLM
        analysis_result = await llm_analysis_engine.analyze_avlt_blind(test_data, user_context)
        
        # Calculate basic score
        words_presented = test_result.raw_data.get("words_presented", [])
        score = len(set(response.words_recalled) & set(words_presented))
        max_score = len(words_presented)
        
        # Update test result
        test_result.score = score
        test_result.max_score = max_score
        test_result.analysis_result = analysis_result
        test_result.risk_level = analysis_result.get("analysis_result", {}).get("risk_level", "medium")
        
        # Create cognitive test result entry
        cognitive_result = CognitiveTestResult(
            id=str(uuid.uuid4()),
            test_result_id=test_result.id,
            test_name="AVLT",
            subtest_name=f"Trial_{response.trial_number}",
            score=score,
            max_score=max_score,
            response_time=sum(response.response_times) if response.response_times else 0,
            errors=max_score - score,
            details={
                "words_recalled": response.words_recalled,
                "response_times": response.response_times,
                "trial_number": response.trial_number
            }
        )
        db.add(cognitive_result)
        db.commit()
        
        return {
            "test_result_id": test_result.id,
            "score": score,
            "max_score": max_score,
            "percentage": (score / max_score * 100) if max_score > 0 else 0,
            "analysis": analysis_result,
            "next_trial": response.trial_number < 5,
            "status": "completed" if response.trial_number >= 5 else "continue"
        }
    
    except Exception as e:
        logger.error(f"AVLT submit failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/blind/digit-span/start", summary="Start Digit Span test for blind users")
async def start_digit_span_blind(request: DigitSpanRequest, db: Session = Depends(get_db)):
    """Start Digit Span Test for blind users"""
    try:
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        test_config = await cognitive_test_engine.run_digit_span_test(request.user_id, request.direction)
        
        test_result = TestResult(
            id=str(uuid.uuid4()),
            session_id=request.session_id,
            test_name="Digit Span",
            test_type="cognitive",
            raw_data=test_config,
            created_at=datetime.utcnow()
        )
        db.add(test_result)
        db.commit()
        
        return {
            "test_result_id": test_result.id,
            "test_config": test_config,
            "status": "started"
        }
    
    except Exception as e:
        logger.error(f"Digit Span start failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/blind/digit-span/submit", summary="Submit Digit Span responses for blind users")
async def submit_digit_span_blind(response: DigitSpanResponse, db: Session = Depends(get_db)):
    """Submit Digit Span test responses and get analysis"""
    try:
        user = db.query(User).filter(User.id == response.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        test_result = db.query(TestResult).filter(
            TestResult.session_id == response.session_id,
            TestResult.test_name == "Digit Span"
        ).first()
        
        if not test_result:
            raise HTTPException(status_code=404, detail="Test result not found")
        
        # Prepare test data for analysis
        test_data = {
            "sequences_attempted": response.sequences_attempted,
            "sequences_correct": response.sequences_correct,
            "max_span_achieved": response.max_span_achieved,
            "forward_span": response.max_span_achieved if "forward" in test_result.raw_data.get("direction", "") else 0,
            "backward_span": response.max_span_achieved if "backward" in test_result.raw_data.get("direction", "") else 0
        }
        
        user_context = {
            "age": user.age,
            "education_level": user.education_level,
            "language": user.language,
            "user_type": "blind"
        }
        
        # Analyze with LLM
        analysis_result = await llm_analysis_engine.analyze_digit_span_blind(test_data, user_context)
        
        # Update test result
        score = sum(response.sequences_correct)
        max_score = len(response.sequences_attempted)
        
        test_result.score = score
        test_result.max_score = max_score
        test_result.analysis_result = analysis_result
        test_result.risk_level = analysis_result.get("analysis_result", {}).get("risk_level", "medium")
        
        db.commit()
        
        return {
            "test_result_id": test_result.id,
            "score": score,
            "max_score": max_score,
            "max_span_achieved": response.max_span_achieved,
            "analysis": analysis_result,
            "status": "completed"
        }
    
    except Exception as e:
        logger.error(f"Digit Span submit failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WEAK VISION USER COGNITIVE TESTS
@router.post("/weak-vision/mmse/start", summary="Start MMSE test for weak vision users")
async def start_mmse_weak_vision(request: MMSERequest, db: Session = Depends(get_db)):
    """Start MMSE Test for weak vision users"""
    try:
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        test_config = await cognitive_test_engine.run_mmse_test(request.user_id)
        
        test_result = TestResult(
            id=str(uuid.uuid4()),
            session_id=request.session_id,
            test_name="MMSE",
            test_type="cognitive",
            raw_data=test_config,
            created_at=datetime.utcnow()
        )
        db.add(test_result)
        db.commit()
        
        return {
            "test_result_id": test_result.id,
            "test_config": test_config,
            "status": "started"
        }
    
    except Exception as e:
        logger.error(f"MMSE start failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/weak-vision/mmse/submit", summary="Submit MMSE responses for weak vision users")
async def submit_mmse_weak_vision(response: MMSEResponse, db: Session = Depends(get_db)):
    """Submit MMSE test responses and get analysis"""
    try:
        user = db.query(User).filter(User.id == response.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        test_result = db.query(TestResult).filter(
            TestResult.session_id == response.session_id,
            TestResult.test_name == "MMSE"
        ).first()
        
        if not test_result:
            raise HTTPException(status_code=404, detail="Test result not found")
        
        # Prepare test data for analysis
        test_data = {
            **response.section_scores,
            "total_score": response.total_score,
            "completion_time": response.completion_time,
            "adaptations_used": response.adaptations_used
        }
        
        user_context = {
            "age": user.age,
            "education_level": user.education_level,
            "language": user.language,
            "user_type": "weak_vision"
        }
        
        # Analyze with LLM
        analysis_result = await llm_analysis_engine.analyze_mmse_weak_vision(test_data, user_context)
        
        # Update test result
        test_result.score = response.total_score
        test_result.max_score = 30
        test_result.analysis_result = analysis_result
        test_result.risk_level = analysis_result.get("analysis_result", {}).get("risk_level", "medium")
        
        db.commit()
        
        return {
            "test_result_id": test_result.id,
            "total_score": response.total_score,
            "max_score": 30,
            "percentage": (response.total_score / 30 * 100),
            "section_scores": response.section_scores,
            "analysis": analysis_result,
            "status": "completed"
        }
    
    except Exception as e:
        logger.error(f"MMSE submit failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# NON-EDUCATED USER COGNITIVE TESTS
@router.post("/non-educated/simple-memory/start", summary="Start Simple Memory test for non-educated users")
async def start_simple_memory_non_educated(request: SimpleMemoryRequest, db: Session = Depends(get_db)):
    """Start Simple Memory Test for non-educated users"""
    try:
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        test_config = await cognitive_test_engine.run_simple_memory_test(request.user_id)
        
        test_result = TestResult(
            id=str(uuid.uuid4()),
            session_id=request.session_id,
            test_name="Simple Memory Test",
            test_type="cognitive",
            raw_data=test_config,
            created_at=datetime.utcnow()
        )
        db.add(test_result)
        db.commit()
        
        return {
            "test_result_id": test_result.id,
            "test_config": test_config,
            "status": "started"
        }
    
    except Exception as e:
        logger.error(f"Simple Memory start failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/non-educated/simple-memory/submit", summary="Submit Simple Memory responses for non-educated users")
async def submit_simple_memory_non_educated(response: SimpleMemoryResponse, db: Session = Depends(get_db)):
    """Submit Simple Memory test responses and get analysis"""
    try:
        user = db.query(User).filter(User.id == response.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        test_result = db.query(TestResult).filter(
            TestResult.session_id == response.session_id,
            TestResult.test_name == "Simple Memory Test"
        ).first()
        
        if not test_result:
            raise HTTPException(status_code=404, detail="Test result not found")
        
        # Prepare test data for analysis
        test_data = {
            "items_presented": test_result.raw_data.get("words", []),
            "items_recalled": response.items_recalled,
            "accuracy_percentage": response.accuracy_percentage,
            "cues_needed": response.cues_needed
        }
        
        user_context = {
            "age": user.age,
            "education_level": user.education_level,
            "language": user.language,
            "user_type": "non_educated",
            "cultural_background": getattr(user, 'cultural_background', 'Unknown')
        }
        
        # Analyze with LLM
        analysis_result = await llm_analysis_engine.analyze_simple_memory_non_educated(test_data, user_context)
        
        # Update test result
        max_score = len(test_result.raw_data.get("words", []))
        score = len(response.items_recalled)
        
        test_result.score = score
        test_result.max_score = max_score
        test_result.analysis_result = analysis_result
        test_result.risk_level = analysis_result.get("analysis_result", {}).get("risk_level", "medium")
        
        db.commit()
        
        return {
            "test_result_id": test_result.id,
            "score": score,
            "max_score": max_score,
            "percentage": response.accuracy_percentage,
            "items_recalled": response.items_recalled,
            "analysis": analysis_result,
            "status": "completed"
        }
    
    except Exception as e:
        logger.error(f"Simple Memory submit failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# EDUCATED USER COGNITIVE TESTS
@router.post("/educated/full-moca/start", summary="Start Full MoCA test for educated users")
async def start_full_moca_educated(request: MMSERequest, db: Session = Depends(get_db)):
    """Start Full MoCA Test for educated users"""
    try:
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        test_config = await cognitive_test_engine.run_full_moca_test(request.user_id)
        
        test_result = TestResult(
            id=str(uuid.uuid4()),
            session_id=request.session_id,
            test_name="Full MoCA",
            test_type="cognitive",
            raw_data=test_config,
            created_at=datetime.utcnow()
        )
        db.add(test_result)
        db.commit()
        
        return {
            "test_result_id": test_result.id,
            "test_config": test_config,
            "status": "started"
        }
    
    except Exception as e:
        logger.error(f"Full MoCA start failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# COMPREHENSIVE ANALYSIS ENDPOINT
@router.post("/analyze-comprehensive", summary="Get comprehensive analysis across all tests")
async def get_comprehensive_analysis(session_id: str, db: Session = Depends(get_db)):
    """Get comprehensive analysis for a test session"""
    try:
        # Get all test results for the session
        test_results = db.query(TestResult).filter(TestResult.session_id == session_id).all()
        
        if not test_results:
            raise HTTPException(status_code=404, detail="No test results found for session")
        
        # Get user information
        session = db.query(TestSession).filter(TestSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Test session not found")
        
        user = db.query(User).filter(User.id == session.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Prepare all test results
        all_results = []
        for result in test_results:
            all_results.append({
                "test_name": result.test_name,
                "test_type": result.test_type,
                "score": result.score,
                "max_score": result.max_score,
                "risk_level": result.risk_level,
                "analysis_result": result.analysis_result,
                "created_at": result.created_at.isoformat() if result.created_at else None
            })
        
        # User context
        user_context = {
            "age": user.age,
            "education_level": user.education_level,
            "vision_type": user.vision_type,
            "user_type": user.vision_type,  # Map vision_type to user_type
            "language": user.language
        }
        
        # Generate comprehensive analysis
        comprehensive_analysis = await llm_analysis_engine.generate_comprehensive_analysis(all_results, user_context)
        
        # Update session with overall results
        overall_score = sum([r["score"] or 0 for r in all_results])
        overall_max = sum([r["max_score"] or 0 for r in all_results])
        overall_percentage = (overall_score / overall_max * 100) if overall_max > 0 else 0
        
        session.overall_score = overall_percentage
        session.overall_risk_level = comprehensive_analysis.get("comprehensive_analysis", {}).get("risk_level", "medium")
        session.completed_at = datetime.utcnow()
        session.status = "completed"
        
        db.commit()
        
        return {
            "session_id": session_id,
            "overall_score": overall_percentage,
            "overall_risk_level": session.overall_risk_level,
            "individual_test_results": all_results,
            "comprehensive_analysis": comprehensive_analysis,
            "user_context": user_context,
            "status": "completed"
        }
    
    except Exception as e:
        logger.error(f"Comprehensive analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))