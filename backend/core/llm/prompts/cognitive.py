"""
Enhanced cognitive test prompts with multilingual support
"""

def get_avlt_prompt(test_data, user_context):
    """Auditory Verbal Learning Test prompt"""
    return f"""
Analyze this AVLT (Auditory Verbal Learning Test) result for comprehensive memory assessment.

Test Data: {test_data}
User Context: {user_context}

This test measures:
- Immediate memory span
- Learning curve across trials
- Retention after delay
- Recognition vs recall
- Intrusion errors and confabulations

Provide detailed analysis focusing on:
1. Learning pattern across trials 1-5
2. Immediate vs delayed recall performance
3. Recognition memory performance
4. Error analysis (intrusions, perseverations)
5. Comparison to age/education norms
6. Clinical significance of findings
"""

def get_mmse_prompt(test_data, user_context):
    """Mini-Mental State Examination prompt"""
    return f"""
Analyze this MMSE (Mini-Mental State Examination) result for global cognitive screening.

Test Data: {test_data}
User Context: {user_context}

MMSE domains to analyze:
- Orientation (time/place): /10 points
- Registration: /3 points
- Attention/Calculation: /5 points
- Recall: /3 points
- Language: /9 points

Consider:
- Total score interpretation (≥24 typically normal)
- Domain-specific patterns
- Education level adjustments
- Cultural/linguistic factors
- Specific error patterns indicating cognitive domains affected
"""

def get_moca_prompt(test_data, user_context):
    """Montreal Cognitive Assessment prompt"""
    return f"""
Analyze this MoCA (Montreal Cognitive Assessment) result for detailed cognitive screening.

Test Data: {test_data}
User Context: {user_context}

MoCA domains (30 points total):
- Visuospatial/Executive: /5 points
- Naming: /3 points
- Memory: /5 points
- Attention: /6 points
- Language: /3 points
- Abstraction: /2 points
- Delayed Recall: /5 points
- Orientation: /6 points

Education adjustment: +1 point if ≤12 years education

Provide analysis of:
- Overall cognitive status
- Domain-specific strengths/weaknesses
- Pattern consistent with specific conditions
- Recommendations for further assessment
"""

def get_digit_span_prompt(test_data, user_context):
    """Digit Span Test prompt"""
    return f"""
Analyze this Digit Span test result for working memory and attention assessment.

Test Data: {test_data}
User Context: {user_context}

Components to analyze:
- Forward span: measures attention and auditory processing
- Backward span: measures working memory and cognitive flexibility
- Sequencing span (if included): measures working memory manipulation

Consider:
- Normal ranges by age and education
- Forward vs backward span discrepancy
- Error patterns (omissions, substitutions, sequence errors)
- Clinical implications for daily functioning
"""

def get_clock_drawing_prompt(test_data, user_context):
    """Clock Drawing Test prompt"""
    return f"""
Analyze this Clock Drawing Test result for visuospatial and executive function assessment.

Test Data: {test_data}
User Context: {user_context}

Scoring elements to consider:
- Circle drawing (contour, closure)
- Number placement (position, sequence, orientation)
- Hand placement (correct time, appropriate length, center point)
- Overall organization and planning

Clinical significance:
- Executive function indicators
- Visuospatial processing abilities
- Constructional apraxia signs
- Hemispatial neglect indicators
"""

def get_verbal_fluency_prompt(test_data, user_context):
    """Verbal Fluency Test prompt"""
    return f"""
Analyze this Verbal Fluency test result for language and executive function assessment.

Test Data: {test_data}
User Context: {user_context}

Types to analyze:
- Phonemic fluency (F-A-S or similar): executive/phonemic access
- Semantic fluency (categories): semantic memory/language
- Action fluency: verb generation and executive function

Analysis points:
- Total word count per category
- Clustering and switching patterns
- Error types (repetitions, rule violations, non-words)
- Temporal distribution (words per 15-second interval)
- Qualitative patterns suggesting cognitive changes
"""

def get_trail_making_prompt(test_data, user_context):
    """Trail Making Test prompt"""  
    return f"""
Analyze this Trail Making Test result for processing speed and cognitive flexibility.

Test Data: {test_data}
User Context: {user_context}

Components:
- Trail A: Processing speed and visual scanning
- Trail B: Cognitive flexibility and divided attention
- B-A difference: Pure cognitive flexibility measure

Analysis focus:
- Completion times vs normative data
- Error types and correction patterns
- Qualitative observations (hesitations, sequence breaks)
- Clinical implications for executive dysfunction
- Relationship between processing speed and flexibility
"""