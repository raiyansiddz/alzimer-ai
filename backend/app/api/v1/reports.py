from fastapi import APIRouter, HTTPException
from app.models.schemas import ReportRequest, ComprehensiveReport, ClinicalReport, PatientFriendlyReport
from app.services.groq_client import GroqClient, PromptTemplates
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path
from typing import List

ROOT_DIR = Path(__file__).parent.parent.parent.parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

router = APIRouter()
groq_client = GroqClient()

@router.post("/report", response_model=ComprehensiveReport)
async def generate_report(report_request: ReportRequest):
    """Generate comprehensive clinical and patient-friendly report"""
    try:
        # Get user
        user = await db.users.find_one({"user_id": report_request.user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        locale = report_request.locale or user.get("locale", "en")
        
        # Gather all test results
        memory_tests = await db.memory_tests.find({"user_id": report_request.user_id}).to_list(100)
        pattern_tests = await db.pattern_tests.find({"user_id": report_request.user_id}).to_list(100)
        clock_tests = await db.clock_tests.find({"user_id": report_request.user_id}).to_list(100)
        speech_tests = await db.speech_tests.find({"user_id": report_request.user_id}).to_list(100)
        behavioral_analyses = await db.behavioral_analyses.find({"user_id": report_request.user_id}).to_list(100)
        
        # Prepare all results
        all_results = {
            "user_info": {
                "name": user.get("name"),
                "age": user.get("age"),
                "locale": locale
            },
            "memory_tests": [
                {
                    "score": t.get("score"),
                    "risk_level": t.get("risk_level"),
                    "cognitive_indicators": t.get("cognitive_indicators", [])
                } for t in memory_tests
            ],
            "pattern_tests": [
                {
                    "is_correct": t.get("is_correct"),
                    "risk_level": t.get("risk_level"),
                    "cognitive_indicators": t.get("cognitive_indicators", [])
                } for t in pattern_tests
            ],
            "clock_tests": [
                {
                    "overall_accuracy": t.get("overall_accuracy"),
                    "risk_level": t.get("risk_level"),
                    "dementia_indicators": t.get("dementia_indicators", [])
                } for t in clock_tests
            ],
            "speech_tests": [
                {
                    "task_type": t.get("task_type"),
                    "fluency_score": t.get("fluency_score"),
                    "risk_level": t.get("risk_level"),
                    "dementia_indicators": t.get("dementia_indicators", [])
                } for t in speech_tests
            ],
            "behavioral_analyses": [
                {
                    "response_time_trend": t.get("response_time_trend"),
                    "error_frequency": t.get("error_frequency"),
                    "risk_level": t.get("risk_level")
                } for t in behavioral_analyses
            ]
        }
        
        # Generate report with Groq
        prompt = PromptTemplates.comprehensive_report(locale, all_results, report_request.baseline)
        result = groq_client.call_llm(prompt, max_tokens=3000)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Parse clinical report
        clinical_data = result.get("clinical_report", {})
        clinical_report = ClinicalReport(
            overall_risk_score=clinical_data.get("overall_risk_score", 0.0),
            risk_level=clinical_data.get("risk_level", "low"),
            confidence=clinical_data.get("confidence", "medium"),
            key_findings=clinical_data.get("key_findings", []),
            significant_indicators=clinical_data.get("significant_indicators", []),
            baseline_comparison=clinical_data.get("baseline_comparison", ""),
            clinical_interpretation=clinical_data.get("clinical_interpretation", ""),
            recommendations=clinical_data.get("recommendations", []),
            follow_up=clinical_data.get("follow_up", ""),
            red_flags=clinical_data.get("red_flags", [])
        )
        
        # Parse patient-friendly report
        patient_data = result.get("patient_friendly", {})
        patient_report = PatientFriendlyReport(
            summary=patient_data.get("summary", ""),
            what_this_means=patient_data.get("what_this_means", ""),
            key_findings=patient_data.get("key_findings", []),
            next_steps=patient_data.get("next_steps", []),
            reassurance=patient_data.get("reassurance", "")
        )
        
        # Create comprehensive report
        comprehensive_report = ComprehensiveReport(
            user_id=report_request.user_id,
            clinical_report=clinical_report,
            patient_friendly=patient_report
        )
        
        # Store in database
        await db.reports.insert_one(comprehensive_report.dict())
        
        return comprehensive_report
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/report/{user_id}", response_model=List[ComprehensiveReport])
async def get_reports(user_id: str):
    """Get all reports for a user"""
    try:
        reports = await db.reports.find({"user_id": user_id}).to_list(100)
        return [ComprehensiveReport(**report) for report in reports]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
