from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uuid
import json
from datetime import datetime

from core.database.connection import get_db
from core.database.models import TestResult, CognitiveTestResult, TestSession, User
from core.llm.enhanced_groq_service import enhanced_groq_service

router = APIRouter()

class EnhancedCognitiveTestSubmit(BaseModel):
    session_id: str
    test_name: str
    test_type: str  # 'avlt', 'mmse', 'moca', 'digit_span', 'clock_drawing', 'verbal_fluency', 'trail_making'
    test_data: Dict[str, Any]
    response_times: Optional[List[float]] = []
    user_notes: Optional[str] = None

class CognitiveTestBattery(BaseModel):
    session_id: str
    tests: List[EnhancedCognitiveTestSubmit]

class DetailedCognitiveResponse(BaseModel):
    id: str
    session_id: str
    test_name: str
    test_type: str
    score: Optional[float]
    max_score: Optional[float]
    risk_level: Optional[str]
    detailed_analysis: Optional[Dict[str, Any]]
    recommendations: Optional[Dict[str, Any]]
    processing_time: Optional[int]
    confidence_score: Optional[float]
    
    class Config:
        from_attributes = True

@router.post("/enhanced/submit", response_model=DetailedCognitiveResponse)
async def submit_enhanced_cognitive_test(test_data: EnhancedCognitiveTestSubmit, db: Session = Depends(get_db)):
    """
    Submit cognitive test with enhanced AI analysis
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
        "vision_type": user.vision_type,
        "name": user.name
    }
    
    try:
        # Get enhanced AI analysis
        analysis_result = await enhanced_groq_service.analyze_cognitive_test(
            test_data.test_type,
            test_data.test_data,
            user_context
        )
        
        analysis = analysis_result["analysis"]
        
        # Extract key metrics
        overall_score = analysis.get("overall_score", 0)
        risk_level = analysis.get("risk_level", "medium")
        confidence_score = analysis.get("confidence_score", 0)
        
        # Create enhanced test result
        test_result = TestResult(
            id=str(uuid.uuid4()),
            session_id=str(test_data.session_id),
            test_name=test_data.test_name,
            test_type="cognitive",
            score=float(overall_score),
            max_score=100.0,
            risk_level=risk_level,
            raw_data={
                "test_data": test_data.test_data,
                "response_times": test_data.response_times,
                "user_notes": test_data.user_notes
            },
            analysis_result=analysis,
            created_at=datetime.utcnow()
        )
        
        db.add(test_result)
        
        # Create detailed cognitive result
        cognitive_result = CognitiveTestResult(
            id=str(uuid.uuid4()),
            test_result_id=test_result.id,
            test_name=test_data.test_name,
            subtest_name=test_data.test_type,
            score=float(overall_score),
            max_score=100.0,
            response_time=int(sum(test_data.response_times)) if test_data.response_times else None,
            errors=len([t for t in test_data.response_times if t > 10]) if test_data.response_times else 0,
            details={
                "domain_scores": analysis.get("domain_scores", {}),
                "detailed_analysis": analysis.get("detailed_analysis", {}),
                "cultural_considerations": analysis.get("detailed_analysis", {}).get("cultural_considerations", "")
            }
        )
        
        db.add(cognitive_result)
        db.commit()
        db.refresh(test_result)
        
        return DetailedCognitiveResponse(
            id=test_result.id,
            session_id=test_result.session_id,
            test_name=test_result.test_name,
            test_type=test_data.test_type,
            score=test_result.score,
            max_score=test_result.max_score,
            risk_level=test_result.risk_level,
            detailed_analysis=analysis.get("detailed_analysis"),
            recommendations=analysis.get("recommendations"),
            processing_time=analysis_result.get("processing_time"),
            confidence_score=confidence_score
        )
        
    except Exception as e:
        db.rollback()
        print(f"Enhanced cognitive test analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/battery/submit", response_model=List[DetailedCognitiveResponse])
async def submit_cognitive_test_battery(battery: CognitiveTestBattery, db: Session = Depends(get_db)):
    """
    Submit multiple cognitive tests as a battery
    """
    results = []
    
    for test in battery.tests:
        try:
            result = await submit_enhanced_cognitive_test(test, db)
            results.append(result)
        except Exception as e:
            print(f"Error processing test {test.test_name}: {str(e)}")
            continue
    
    return results

@router.get("/tests/available")
async def get_available_tests():
    """
    Get list of available cognitive tests with descriptions
    """
    return {
        "tests": [
            {
                "id": "avlt",
                "name": "Auditory Verbal Learning Test",
                "description": "Measures verbal learning and memory across multiple trials",
                "duration_minutes": 15,
                "domains": ["memory", "learning", "attention"]
            },
            {
                "id": "mmse", 
                "name": "Mini-Mental State Examination",
                "description": "Brief cognitive screening test covering multiple domains",
                "duration_minutes": 10,
                "domains": ["orientation", "memory", "attention", "language", "visuospatial"]
            },
            {
                "id": "moca",
                "name": "Montreal Cognitive Assessment", 
                "description": "Comprehensive cognitive screening with higher sensitivity",
                "duration_minutes": 15,
                "domains": ["visuospatial", "executive", "memory", "attention", "language", "orientation"]
            },
            {
                "id": "digit_span",
                "name": "Digit Span Test",
                "description": "Measures working memory and attention span",
                "duration_minutes": 5,
                "domains": ["working_memory", "attention"]
            },
            {
                "id": "clock_drawing",
                "name": "Clock Drawing Test",
                "description": "Assesses visuospatial abilities and executive function",
                "duration_minutes": 5,
                "domains": ["visuospatial", "executive", "constructional"]
            },
            {
                "id": "verbal_fluency",
                "name": "Verbal Fluency Test",
                "description": "Measures language production and executive function",
                "duration_minutes": 5,
                "domains": ["language", "executive", "semantic_memory"]
            },
            {
                "id": "trail_making",
                "name": "Trail Making Test",
                "description": "Assesses processing speed and cognitive flexibility",
                "duration_minutes": 10,
                "domains": ["processing_speed", "cognitive_flexibility", "attention"]
            }
        ]
    }

@router.get("/session/{session_id}/analysis")
async def get_session_comprehensive_analysis(session_id: str, db: Session = Depends(get_db)):
    """
    Get comprehensive analysis of all cognitive tests in a session
    """
    # Get session
    session = db.query(TestSession).filter(TestSession.id == str(session_id)).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get user
    user = db.query(User).filter(User.id == session.user_id).first()
    
    # Get all cognitive test results
    results = db.query(TestResult).filter(
        TestResult.session_id == str(session_id),
        TestResult.test_type == "cognitive"
    ).all()
    
    if not results:
        raise HTTPException(status_code=404, detail="No cognitive test results found")
    
    # Prepare data for comprehensive analysis
    user_data = {
        "id": user.id,
        "age": user.age,
        "education_level": user.education_level,
        "language": user.language,
        "vision_type": user.vision_type
    }
    
    test_results = []
    for result in results:
        test_results.append({
            "test_name": result.test_name,
            "score": result.score,
            "risk_level": result.risk_level,
            "analysis": result.analysis_result
        })
    
    try:
        # Generate comprehensive recommendations
        recommendations = await enhanced_groq_service.generate_personalized_recommendations(
            user_data, test_results
        )
        
        return {
            "session_id": session_id,
            "user_profile": user_data,
            "test_summary": {
                "total_tests": len(results),
                "average_score": sum(r.score for r in results if r.score) / len(results),
                "risk_levels": [r.risk_level for r in results],
                "completion_date": max(r.created_at for r in results).isoformat()
            },
            "comprehensive_analysis": recommendations["analysis"],
            "processing_info": {
                "processing_time": recommendations.get("processing_time"),
                "model_info": recommendations.get("model_info")
            }
        }
        
    except Exception as e:
        print(f"Comprehensive analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/session/{session_id}/detailed", response_model=List[DetailedCognitiveResponse])
async def get_session_detailed_results(session_id: str, db: Session = Depends(get_db)):
    """
    Get detailed results for all cognitive tests in a session
    """
    results = db.query(TestResult).filter(
        TestResult.session_id == str(session_id),
        TestResult.test_type == "cognitive"
    ).all()
    
    detailed_results = []
    for result in results:
        detailed_results.append(DetailedCognitiveResponse(
            id=result.id,
            session_id=result.session_id,
            test_name=result.test_name,
            test_type=result.raw_data.get("test_type", "unknown"),
            score=result.score,
            max_score=result.max_score,
            risk_level=result.risk_level,
            detailed_analysis=result.analysis_result.get("detailed_analysis"),
            recommendations=result.analysis_result.get("recommendations"),
            processing_time=None,
            confidence_score=result.analysis_result.get("confidence_score")
        ))
    
    return detailed_results