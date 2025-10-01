from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os
import matplotlib.pyplot as plt
import numpy as np

def generate_patient_report(user, session, test_results):
    """
    Generate patient-friendly PDF report
    """
    # Create reports directory
    reports_dir = "/tmp/reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    filename = f"patient_report_{session.id}.pdf"
    filepath = os.path.join(reports_dir, filename)
    
    # Create PDF
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    elements.append(Paragraph("Cognitive Assessment Report", title_style))
    elements.append(Spacer(1, 0.3 * inch))
    
    # Patient Information
    patient_data = [
        ['Patient Name:', user.name],
        ['Assessment Date:', session.started_at.strftime('%B %d, %Y')],
        ['Test Type:', session.session_type.title()],
        ['Overall Score:', f"{session.overall_score:.1f}%" if session.overall_score else "N/A"],
        ['Risk Level:', (session.overall_risk_level or "N/A").upper()]
    ]
    
    patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
    patient_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
    ]))
    
    elements.append(patient_table)
    elements.append(Spacer(1, 0.5 * inch))
    
    # Executive Summary
    elements.append(Paragraph("Executive Summary", styles['Heading2']))
    elements.append(Spacer(1, 0.2 * inch))
    
    summary_text = """
    Your cognitive assessment has been completed. This report summarizes your performance 
    across various cognitive tests designed to evaluate memory, attention, language, and 
    executive function. The results will help guide your healthcare provider in creating 
    a personalized care plan.
    """
    
    elements.append(Paragraph(summary_text, styles['Normal']))
    elements.append(Spacer(1, 0.3 * inch))
    
    # Test Results
    elements.append(Paragraph("Test Results", styles['Heading2']))
    elements.append(Spacer(1, 0.2 * inch))
    
    results_data = [['Test Name', 'Score', 'Risk Level', 'Status']]
    
    for result in test_results:
        score_str = f"{result.score:.1f}/{result.max_score:.1f}" if result.score and result.max_score else "N/A"
        risk_color = {
            'low': 'Normal',
            'medium': 'Monitor',
            'high': 'Attention Needed'
        }.get(result.risk_level, 'N/A')
        
        results_data.append([
            result.test_name.upper(),
            score_str,
            risk_color,
            '✓ Complete'
        ])
    
    results_table = Table(results_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    results_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
    ]))
    
    elements.append(results_table)
    elements.append(Spacer(1, 0.5 * inch))
    
    # Recommendations
    elements.append(Paragraph("Recommendations", styles['Heading2']))
    elements.append(Spacer(1, 0.2 * inch))
    
    recommendations = [
        "Continue with regular cognitive assessments as scheduled",
        "Maintain a healthy lifestyle with regular exercise and balanced diet",
        "Engage in mentally stimulating activities daily",
        "Ensure adequate sleep (7-9 hours per night)",
        "Stay socially active and connected with friends and family"
    ]
    
    for rec in recommendations:
        elements.append(Paragraph(f"• {rec}", styles['Normal']))
        elements.append(Spacer(1, 0.1 * inch))
    
    # Next Steps
    if session.next_recommended_date:
        elements.append(Spacer(1, 0.3 * inch))
        elements.append(Paragraph("Next Assessment", styles['Heading2']))
        elements.append(Spacer(1, 0.2 * inch))
        next_text = f"Your next assessment is recommended for {session.next_recommended_date.strftime('%B %d, %Y')}"
        elements.append(Paragraph(next_text, styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    
    return filepath

def generate_clinical_report(user, session, test_results):
    """
    Generate clinical-grade PDF report with detailed analysis
    """
    # Create reports directory
    reports_dir = "/tmp/reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    filename = f"clinical_report_{session.id}.pdf"
    filepath = os.path.join(reports_dir, filename)
    
    # Create PDF
    doc = SimpleDocTemplate(filepath, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    elements.append(Paragraph("Clinical Cognitive Assessment Report", title_style))
    elements.append(Spacer(1, 0.3 * inch))
    
    # Patient Demographics
    elements.append(Paragraph("Patient Demographics", styles['Heading2']))
    demo_data = [
        ['Name:', user.name],
        ['Age:', str(user.age) if user.age else 'N/A'],
        ['Education:', user.education_level or 'N/A'],
        ['Vision Status:', user.vision_type or 'N/A'],
        ['Language:', user.language]
    ]
    
    demo_table = Table(demo_data, colWidths=[2*inch, 3*inch])
    demo_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    
    elements.append(demo_table)
    elements.append(Spacer(1, 0.3 * inch))
    
    # Detailed Test Results with Clinical Interpretation
    elements.append(Paragraph("Detailed Assessment Results", styles['Heading2']))
    elements.append(Spacer(1, 0.2 * inch))
    
    for result in test_results:
        # Test name
        elements.append(Paragraph(f"<b>{result.test_name.upper()}</b>", styles['Heading3']))
        
        # Scores
        score_text = f"Score: {result.score:.1f}/{result.max_score:.1f}" if result.score and result.max_score else "Score: N/A"
        elements.append(Paragraph(score_text, styles['Normal']))
        
        # Clinical notes from AI analysis
        if result.analysis_result and 'clinical_notes' in result.analysis_result:
            elements.append(Paragraph("<b>Clinical Interpretation:</b>", styles['Normal']))
            elements.append(Paragraph(result.analysis_result['clinical_notes'], styles['Normal']))
        
        elements.append(Spacer(1, 0.2 * inch))
    
    # Build PDF
    doc.build(elements)
    
    return filepath
