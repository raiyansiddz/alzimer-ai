from fastapi import APIRouter, HTTPException
from app.models.schemas import PatternTestInput, PatternTestResult
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

CORRECT_ANSWER = "Circle"  # Pattern: Circle, Square, Circle, Square, ___?

@router.post("/pattern", response_model=PatternTestResult)
async def pattern_test(test_input: PatternTestInput):
    """Process pattern recognition test"""
    try:
        # Get user locale
        user = await db.users.find_one({"user_id": test_input.user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        locale = user.get("locale", "en")
        
        # Analyze with Groq
        prompt = PromptTemplates.pattern_test(
            locale, 
            test_input.user_answer, 
            CORRECT_ANSWER,
            test_input.response_time_ms
        )
        result = groq_client.call_llm(prompt)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Create result object
        pattern_result = PatternTestResult(
            user_id=test_input.user_id,
            is_correct=result.get("is_correct", False),
            correct_answer=CORRECT_ANSWER,
            user_answer=test_input.user_answer,
            response_category=result.get("response_category", "medium"),
            cognitive_indicators=result.get("cognitive_indicators", []),
            risk_level=result.get("risk_level", "low"),
            confidence=result.get("confidence", "medium"),
            notes=result.get("notes", "")
        )
        
        # Store in database
        await db.pattern_tests.insert_one(pattern_result.dict())
        
        return pattern_result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))