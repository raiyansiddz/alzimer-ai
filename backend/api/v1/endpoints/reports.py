from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime

from core.database.connection import get_db
from core.database.models import Report, TestSession, TestResult, User
from core.reporting.pdf_generator import generate_patient_report, generate_clinical_report

router = APIRouter()

class ReportResponse(BaseModel):
    id: str
    user_id: str
    session_id: str
    report_type: str
    file_url: str
    summary: Optional[str]
    recommendations: Optional[List[str]]
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.post("/generate/{session_id}")
async def generate_report(session_id: str, report_type: str, db: Session = Depends(get_db)):
    """
    Generate PDF report for a test session
    """
    # Verify session exists and is completed
    session = db.query(TestSession).filter(TestSession.id == str(session_id)).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.status != "completed":
        raise HTTPException(status_code=400, detail="Session not completed yet")
    
    # Get user
    user = db.query(User).filter(User.id == session.user_id).first()
    
    # Get all test results for this session
    test_results = db.query(TestResult).filter(TestResult.session_id == session.id).all()
    
    # Generate report based on type
    try:
        if report_type == "patient":
            file_path = generate_patient_report(user, session, test_results)
        elif report_type == "clinical":
            file_path = generate_clinical_report(user, session, test_results)
        else:
            raise HTTPException(status_code=400, detail="Invalid report type")
        
        # Create report record
        report = Report(
            id=str(uuid.uuid4()),
            user_id=session.user_id,
            session_id=session.id,
            report_type=report_type,
            file_url=file_path,
            summary=f"Report generated for {session.session_type} session",
            recommendations=["Follow recommended test schedule", "Maintain healthy lifestyle"],
            created_at=datetime.utcnow()
        )
        
        db.add(report)
        db.commit()
        db.refresh(report)
        
        return report
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@router.get("/download/{report_id}")
async def download_report(report_id: str, db: Session = Depends(get_db)):
    """
    Download generated report
    """
    report = db.query(Report).filter(Report.id == str(report_id)).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return FileResponse(
        path=report.file_url,
        filename=f"report_{report_id}.pdf",
        media_type="application/pdf"
    )

@router.get("/user/{user_id}", response_model=List[ReportResponse])
async def get_user_reports(user_id: str, db: Session = Depends(get_db)):
    """
    Get all reports for a user
    """
    reports = db.query(Report).filter(Report.user_id == str(user_id)).order_by(Report.created_at.desc()).all()
    return reports
