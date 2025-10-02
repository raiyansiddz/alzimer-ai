from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import json
import uuid

from core.database.connection import get_db
from core.database.models import User, TestSession, TestResult, BehavioralTestResult
from core.tests.behavioral_test_engine import behavioral_test_engine, UserType
from core.analysis.llm_analysis_engine import llm_analysis_engine
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic Models
class BehavioralTestRequest(BaseModel):
    user_id: str
    session_id: str
    test_type: str
    duration_minutes: Optional[int] = 10

class VoiceResponseData(BaseModel):
    user_id: str
    session_id: str
    response_times: List[float]
    command_accuracy: float
    voice_responses: List[str]
    audio_stimuli_responses: Dict[str, List[float]]

class VisualResponseData(BaseModel):
    user_id: str
    session_id: str
    response_times: List[float]
    accuracy_rate: float
    target_types: List[str]
    error_types: List[str]

class GameEngagementData(BaseModel):
    user_id: str
    session_id: str
    games_completed: List[Dict[str, Any]]
    session_duration: float
    help_requests: int
    retry_attempts: int
    completion_rate: float

class ComplexInteractionData(BaseModel):
    user_id: str
    session_id: str
    tasks_completed: List[Dict[str, Any]]
    completion_times: List[float]
    accuracy_rates: List[float]
    error_patterns: Dict[str, int]
    cognitive_load_indicators: Dict[str, float]

# BLIND USER BEHAVIORAL TESTS
@router.post("/blind/voice-response-monitoring/start", summary="Start Voice Response Monitoring for blind users")
async def start_voice_response_monitoring_blind(request: BehavioralTestRequest, db: Session = Depends(get_db)):
    """Start Voice Response Time Monitoring for blind users"""
    try:
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        test_config = await behavioral_test_engine.run_voice_response_monitoring(
            request.user_id, 
            request.duration_minutes or 10
        )
        
        test_result = TestResult(
            id=str(uuid.uuid4()),
            session_id=request.session_id,
            test_name="Voice Response Time Monitoring",
            test_type="behavioral",
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
        logger.error(f"Voice Response Monitoring start failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/blind/voice-response-monitoring/submit", summary="Submit Voice Response Monitoring data for blind users")
async def submit_voice_response_monitoring_blind(response: VoiceResponseData, db: Session = Depends(get_db)):
    """Submit Voice Response Monitoring data and get analysis"""
    try:
        user = db.query(User).filter(User.id == response.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        test_result = db.query(TestResult).filter(
            TestResult.session_id == response.session_id,
            TestResult.test_name == "Voice Response Time Monitoring"
        ).first()
        
        if not test_result:
            raise HTTPException(status_code=404, detail="Test result not found")
        
        # Create behavioral test result
        avg_response_time = sum(response.response_times) / len(response.response_times) if response.response_times else 0
        
        behavioral_result = BehavioralTestResult(
            id=str(uuid.uuid4()),
            test_result_id=test_result.id,
            test_name="Voice Response Time Monitoring",
            response_times=json.dumps(response.response_times),
            accuracy=response.command_accuracy,
            efficiency=100.0 / avg_response_time if avg_response_time > 0 else 0,
            details={
                "voice_responses": response.voice_responses,
                "audio_stimuli_responses": response.audio_stimuli_responses,
                "average_response_time": avg_response_time,
                "response_variability": _calculate_variability(response.response_times)
            }
        )
        db.add(behavioral_result)
        
        # Prepare analysis data
        behavioral_data = {
            "user_type": "blind",
            "test_type": "voice_response_monitoring",
            "response_times": response.response_times,
            "accuracy_rates": [response.command_accuracy],
            "response_variability": _calculate_variability(response.response_times),
            "error_patterns": {},
            "fatigue_indicators": []
        }
        
        user_context = {
            "age": user.age,
            "education_level": user.education_level,
            "user_type": "blind",
            "adaptations": ["audio_only", "voice_commands"]
        }
        
        # Analyze behavioral patterns
        analysis_result = await _analyze_behavioral_data(behavioral_data, user_context)
        
        # Update main test result
        test_result.score = response.command_accuracy
        test_result.max_score = 100.0
        test_result.analysis_result = analysis_result
        test_result.risk_level = _determine_risk_level(response.command_accuracy, avg_response_time)
        
        db.commit()
        
        return {
            "test_result_id": test_result.id,
            "average_response_time": avg_response_time,
            "command_accuracy": response.command_accuracy,
            "response_variability": _calculate_variability(response.response_times),
            "analysis": analysis_result,
            "status": "completed"
        }
    
    except Exception as e:
        logger.error(f"Voice Response Monitoring submit failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/blind/audio-pattern-recognition/start", summary="Start Audio Pattern Recognition for blind users")
async def start_audio_pattern_recognition_blind(request: BehavioralTestRequest, db: Session = Depends(get_db)):
    """Start Audio Pattern Recognition test for blind users"""
    try:
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        test_config = await behavioral_test_engine.run_audio_pattern_recognition(request.user_id)
        
        test_result = TestResult(
            id=str(uuid.uuid4()),
            session_id=request.session_id,
            test_name="Audio Pattern Recognition",
            test_type="behavioral",
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
        logger.error(f"Audio Pattern Recognition start failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WEAK VISION USER BEHAVIORAL TESTS
@router.post("/weak-vision/visual-response-monitoring/start", summary="Start Visual Response Monitoring for weak vision users")
async def start_visual_response_monitoring_weak_vision(request: BehavioralTestRequest, db: Session = Depends(get_db)):
    """Start Visual Response Time Monitoring for weak vision users"""
    try:
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        test_config = await behavioral_test_engine.run_visual_response_monitoring(request.user_id)
        
        test_result = TestResult(
            id=str(uuid.uuid4()),
            session_id=request.session_id,
            test_name="Visual Response Time Monitoring",
            test_type="behavioral",
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
        logger.error(f"Visual Response Monitoring start failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/weak-vision/visual-response-monitoring/submit", summary="Submit Visual Response Monitoring data for weak vision users")
async def submit_visual_response_monitoring_weak_vision(response: VisualResponseData, db: Session = Depends(get_db)):
    """Submit Visual Response Monitoring data and get analysis"""
    try:
        user = db.query(User).filter(User.id == response.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        test_result = db.query(TestResult).filter(
            TestResult.session_id == response.session_id,
            TestResult.test_name == "Visual Response Time Monitoring"
        ).first()
        
        if not test_result:
            raise HTTPException(status_code=404, detail="Test result not found")
        
        # Create behavioral test result
        avg_response_time = sum(response.response_times) / len(response.response_times) if response.response_times else 0
        
        behavioral_result = BehavioralTestResult(
            id=str(uuid.uuid4()),
            test_result_id=test_result.id,
            test_name="Visual Response Time Monitoring",
            response_times=json.dumps(response.response_times),
            accuracy=response.accuracy_rate,
            efficiency=100.0 / avg_response_time if avg_response_time > 0 else 0,
            details={
                "target_types": response.target_types,
                "error_types": response.error_types,
                "average_response_time": avg_response_time,
                "visual_adaptations": ["large_buttons", "high_contrast"]
            }
        )
        db.add(behavioral_result)
        
        # Prepare analysis data
        behavioral_data = {
            "user_type": "weak_vision",
            "test_type": "visual_response_monitoring",
            "response_times": response.response_times,
            "accuracy_rates": [response.accuracy_rate],
            "response_variability": _calculate_variability(response.response_times),
            "error_patterns": {error_type: response.error_types.count(error_type) for error_type in set(response.error_types)},
            "fatigue_indicators": []
        }
        
        user_context = {
            "age": user.age,
            "education_level": user.education_level,
            "user_type": "weak_vision",
            "adaptations": ["large_buttons", "high_contrast", "clear_focus"]
        }
        
        # Analyze behavioral patterns
        analysis_result = await _analyze_behavioral_data(behavioral_data, user_context)
        
        # Update main test result
        test_result.score = response.accuracy_rate
        test_result.max_score = 100.0
        test_result.analysis_result = analysis_result
        test_result.risk_level = _determine_risk_level(response.accuracy_rate, avg_response_time)
        
        db.commit()
        
        return {
            "test_result_id": test_result.id,
            "average_response_time": avg_response_time,
            "accuracy_rate": response.accuracy_rate,
            "response_variability": _calculate_variability(response.response_times),
            "analysis": analysis_result,
            "status": "completed"
        }
    
    except Exception as e:
        logger.error(f"Visual Response Monitoring submit failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# NON-EDUCATED USER BEHAVIORAL TESTS
@router.post("/non-educated/game-engagement/start", summary="Start Game Engagement Tracking for non-educated users")
async def start_game_engagement_non_educated(request: BehavioralTestRequest, db: Session = Depends(get_db)):
    """Start Game Engagement Tracking for non-educated users"""
    try:
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        test_config = await behavioral_test_engine.run_game_engagement_tracking(request.user_id)
        
        test_result = TestResult(
            id=str(uuid.uuid4()),
            session_id=request.session_id,
            test_name="Game Engagement Tracking",
            test_type="behavioral",
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
        logger.error(f"Game Engagement Tracking start failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/non-educated/game-engagement/submit", summary="Submit Game Engagement data for non-educated users")
async def submit_game_engagement_non_educated(response: GameEngagementData, db: Session = Depends(get_db)):
    """Submit Game Engagement data and get analysis"""
    try:
        user = db.query(User).filter(User.id == response.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        test_result = db.query(TestResult).filter(
            TestResult.session_id == response.session_id,
            TestResult.test_name == "Game Engagement Tracking"
        ).first()
        
        if not test_result:
            raise HTTPException(status_code=404, detail="Test result not found")
        
        # Create behavioral test result
        behavioral_result = BehavioralTestResult(
            id=str(uuid.uuid4()),
            test_result_id=test_result.id,
            test_name="Game Engagement Tracking",
            response_times=[],  # Not applicable for engagement
            accuracy=response.completion_rate,
            efficiency=response.completion_rate / response.session_duration if response.session_duration > 0 else 0,
            details={
                "games_completed": response.games_completed,
                "session_duration": response.session_duration,
                "help_requests": response.help_requests,
                "retry_attempts": response.retry_attempts,
                "engagement_score": _calculate_engagement_score(response)
            }
        )
        db.add(behavioral_result)
        
        # Prepare analysis data
        behavioral_data = {
            "user_type": "non_educated",
            "test_type": "game_engagement",
            "completion_rates": [response.completion_rate],
            "session_duration": response.session_duration,
            "help_requests": response.help_requests,
            "retry_attempts": response.retry_attempts,
            "engagement_indicators": {
                "games_completed": len(response.games_completed),
                "average_game_time": response.session_duration / len(response.games_completed) if response.games_completed else 0
            }
        }
        
        user_context = {
            "age": user.age,
            "education_level": user.education_level,
            "user_type": "non_educated",
            "adaptations": ["large_icons", "simple_interface", "encouraging_feedback"]
        }
        
        # Analyze engagement patterns
        analysis_result = await _analyze_behavioral_data(behavioral_data, user_context)
        
        # Calculate engagement score
        engagement_score = _calculate_engagement_score(response)
        
        # Update main test result
        test_result.score = engagement_score
        test_result.max_score = 100.0
        test_result.analysis_result = analysis_result
        test_result.risk_level = "low" if engagement_score >= 80 else "medium" if engagement_score >= 60 else "high"
        
        db.commit()
        
        return {
            "test_result_id": test_result.id,
            "engagement_score": engagement_score,
            "completion_rate": response.completion_rate,
            "session_duration": response.session_duration,
            "games_completed": len(response.games_completed),
            "analysis": analysis_result,
            "status": "completed"
        }
    
    except Exception as e:
        logger.error(f"Game Engagement submit failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# EDUCATED USER BEHAVIORAL TESTS
@router.post("/educated/complex-interaction/start", summary="Start Complex Interaction Monitoring for educated users")
async def start_complex_interaction_educated(request: BehavioralTestRequest, db: Session = Depends(get_db)):
    """Start Complex Interaction Monitoring for educated users"""
    try:
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        test_config = await behavioral_test_engine.run_complex_interaction_monitoring(request.user_id)
        
        test_result = TestResult(
            id=str(uuid.uuid4()),
            session_id=request.session_id,
            test_name="Complex Interaction Monitoring",
            test_type="behavioral",
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
        logger.error(f"Complex Interaction Monitoring start failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/educated/complex-interaction/submit", summary="Submit Complex Interaction data for educated users")
async def submit_complex_interaction_educated(response: ComplexInteractionData, db: Session = Depends(get_db)):
    """Submit Complex Interaction data and get analysis"""
    try:
        user = db.query(User).filter(User.id == response.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        test_result = db.query(TestResult).filter(
            TestResult.session_id == response.session_id,
            TestResult.test_name == "Complex Interaction Monitoring"
        ).first()
        
        if not test_result:
            raise HTTPException(status_code=404, detail="Test result not found")
        
        # Create behavioral test result
        avg_completion_time = sum(response.completion_times) / len(response.completion_times) if response.completion_times else 0
        avg_accuracy = sum(response.accuracy_rates) / len(response.accuracy_rates) if response.accuracy_rates else 0
        
        behavioral_result = BehavioralTestResult(
            id=str(uuid.uuid4()),
            test_result_id=test_result.id,
            test_name="Complex Interaction Monitoring",
            response_times=json.dumps(response.completion_times),
            accuracy=avg_accuracy,
            efficiency=100.0 / avg_completion_time if avg_completion_time > 0 else 0,
            details={
                "tasks_completed": response.tasks_completed,
                "error_patterns": response.error_patterns,
                "cognitive_load_indicators": response.cognitive_load_indicators,
                "average_completion_time": avg_completion_time,
                "task_complexity_handling": _analyze_task_complexity(response.tasks_completed)
            }
        )
        db.add(behavioral_result)
        
        # Prepare analysis data
        behavioral_data = {
            "user_type": "educated",
            "test_type": "complex_interaction_monitoring",
            "completion_times": response.completion_times,
            "accuracy_rates": response.accuracy_rates,
            "error_patterns": response.error_patterns,
            "cognitive_load_indicators": response.cognitive_load_indicators,
            "task_complexity": "high"
        }
        
        user_context = {
            "age": user.age,
            "education_level": user.education_level,
            "user_type": "educated",
            "adaptations": ["standard_interface"]
        }
        
        # Analyze complex interaction patterns
        analysis_result = await _analyze_behavioral_data(behavioral_data, user_context)
        
        # Update main test result
        test_result.score = avg_accuracy
        test_result.max_score = 100.0
        test_result.analysis_result = analysis_result
        test_result.risk_level = _determine_risk_level(avg_accuracy, avg_completion_time)
        
        db.commit()
        
        return {
            "test_result_id": test_result.id,
            "average_completion_time": avg_completion_time,
            "average_accuracy": avg_accuracy,
            "tasks_completed": len(response.tasks_completed),
            "error_patterns": response.error_patterns,
            "analysis": analysis_result,
            "status": "completed"
        }
    
    except Exception as e:
        logger.error(f"Complex Interaction submit failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# HELPER METHODS
def _calculate_variability(response_times: List[float]) -> float:
    """Calculate coefficient of variation for response times"""
    if not response_times or len(response_times) < 2:
        return 0.0
    
    mean_rt = sum(response_times) / len(response_times)
    variance = sum((rt - mean_rt) ** 2 for rt in response_times) / (len(response_times) - 1)
    std_dev = variance ** 0.5
    
    return (std_dev / mean_rt) * 100 if mean_rt > 0 else 0.0

def _determine_risk_level(accuracy: float, response_time: float) -> str:
    """Determine risk level based on accuracy and response time"""
    if accuracy >= 85 and response_time <= 2000:  # 2 seconds
        return "low"
    elif accuracy >= 70 and response_time <= 4000:  # 4 seconds
        return "medium"
    else:
        return "high"

def _calculate_engagement_score(response: GameEngagementData) -> float:
    """Calculate engagement score for non-educated users"""
    base_score = response.completion_rate * 0.4  # 40% weight
    duration_score = min(response.session_duration / 10, 20) * 0.3  # 30% weight, cap at 10 minutes
    interaction_score = max(0, 30 - response.help_requests * 2 - response.retry_attempts) * 0.3  # 30% weight
    
    return max(0, min(100, base_score + duration_score + interaction_score))

def _analyze_task_complexity(tasks_completed: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze how user handled different task complexities"""
    complexity_analysis = {
        "simple_tasks": 0,
        "medium_tasks": 0,
        "complex_tasks": 0,
        "task_progression": []
    }
    
    for task in tasks_completed:
        complexity = task.get("complexity", "medium")
        complexity_analysis[f"{complexity}_tasks"] += 1
        complexity_analysis["task_progression"].append({
            "task_name": task.get("task_name", "unknown"),
            "complexity": complexity,
            "completion_time": task.get("completion_time", 0),
            "success": task.get("success", False)
        })
    
    return complexity_analysis

async def _analyze_behavioral_data(behavioral_data: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze behavioral data using LLM"""
    # This would use the LLM analysis engine for behavioral analysis
    # For now, returning a basic analysis structure
    return {
        "analysis_type": "behavioral",
        "user_type": user_context.get("user_type", "unknown"),
        "performance_summary": {
            "processing_speed": "normal",
            "attention": "normal",
            "executive_function": "normal",
            "adaptation": "good"
        },
        "risk_indicators": [],
        "recommendations": ["Continue regular monitoring"],
        "analysis_timestamp": datetime.utcnow().isoformat()
    }