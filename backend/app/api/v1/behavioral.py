from fastapi import APIRouter, HTTPException
from app.models.schemas import BehavioralDataInput, BehavioralAnalysisResult
from app.services.groq_client import GroqClient, PromptTemplates
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent.parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

router = APIRouter()
groq_client = GroqClient()

@router.post("/behavioral", response_model=BehavioralAnalysisResult)
async def behavioral_analysis(data_input: BehavioralDataInput):
    """Analyze behavioral patterns from user interactions"""
    try:
        # Get user locale
        user = await db.users.find_one({"user_id": data_input.user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        locale = user.get("locale", "en")
        
        # Analyze with Groq
        prompt = PromptTemplates.behavioral_analysis(locale, data_input.interaction_summary)
        result = groq_client.call_llm(prompt)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Create result object
        behavioral_result = BehavioralAnalysisResult(
            user_id=data_input.user_id,
            response_time_trend=result.get("response_time_trend", "stable"),
            error_frequency=result.get("error_frequency", "low"),
            navigation_efficiency=result.get("navigation_efficiency", "good"),
            learning_adaptation=result.get("learning_adaptation", "good"),
            completion_consistency=result.get("completion_consistency", "high"),
            behavioral_indicators=result.get("behavioral_indicators", []),
            risk_level=result.get("risk_level", "low"),
            confidence=result.get("confidence", "medium"),
            clinical_notes=result.get("clinical_notes", "")
        )
        
        # Store in database
        await db.behavioral_analyses.insert_one(behavioral_result.dict())
        
        return behavioral_result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))