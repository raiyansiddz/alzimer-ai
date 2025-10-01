# Cognitive Test Analysis Prompts

def get_avlt_prompt(test_data: dict, user_context: dict) -> str:
    return f"""
You are a neurologist specializing in cognitive assessment. Analyze this Auditory Verbal Learning Test (AVLT) results.

Test Data:
- Words presented: {test_data.get('words_presented', [])}
- Trial 1 recall: {test_data.get('trial_1', [])}
- Trial 2 recall: {test_data.get('trial_2', [])}
- Trial 3 recall: {test_data.get('trial_3', [])}
- Trial 4 recall: {test_data.get('trial_4', [])}
- Trial 5 recall: {test_data.get('trial_5', [])}
- Delayed recall: {test_data.get('delayed_recall', [])}
- Recognition: {test_data.get('recognition', [])}

User Context:
- Age: {user_context.get('age')}
- Education: {user_context.get('education_level')}
- Language: {user_context.get('language')}
- Vision: {user_context.get('vision_type')}

Provide comprehensive analysis in JSON format with:
- learning_curve_assessment
- memory_consolidation
- recognition_memory
- norm_comparison
- impairment_indicators (array)
- confidence_level
- recommendations (array)
- risk_level
- clinical_notes
"""

def get_mmse_prompt(test_data: dict, user_context: dict) -> str:
    return f"""
You are a neurologist specializing in cognitive assessment. Analyze this Mini-Mental State Examination (MMSE) results.

Test Data:
- Orientation score: {test_data.get('orientation_score')}/10
- Registration score: {test_data.get('registration_score')}/3
- Attention and calculation score: {test_data.get('attention_score')}/5
- Recall score: {test_data.get('recall_score')}/3
- Language score: {test_data.get('language_score')}/9
- Total MMSE score: {test_data.get('total_score')}/30

User Context:
- Age: {user_context.get('age')}
- Education: {user_context.get('education_level')}
- Language: {user_context.get('language')}
- Vision: {user_context.get('vision_type')}

Provide comprehensive analysis in JSON format with:
- overall_cognitive_status
- orientation
- memory
- attention
- language
- norm_comparison
- impairment_classification
- confidence_level
- recommendations (array)
- risk_level
- clinical_notes
"""

def get_moca_prompt(test_data: dict, user_context: dict) -> str:
    return f"""
You are a neurologist specializing in cognitive assessment. Analyze this Montreal Cognitive Assessment (MoCA) results.

Test Data:
- Visuospatial/executive score: {test_data.get('visuospatial_score')}/5
- Naming score: {test_data.get('naming_score')}/3
- Attention score: {test_data.get('attention_score')}/6
- Language score: {test_data.get('language_score')}/3
- Abstraction score: {test_data.get('abstraction_score')}/2
- Delayed recall score: {test_data.get('recall_score')}/5
- Orientation score: {test_data.get('orientation_score')}/6
- Total MoCA score: {test_data.get('total_score')}/30

User Context:
- Age: {user_context.get('age')}
- Education: {user_context.get('education_level')}
- Language: {user_context.get('language')}
- Vision: {user_context.get('vision_type')}

Provide comprehensive analysis in JSON format with:
- overall_cognitive_status
- visuospatial
- naming
- attention
- language
- abstraction
- memory
- norm_comparison
- impairment_classification
- confidence_level
- recommendations (array)
- risk_level
- clinical_notes
"""

def get_digit_span_prompt(test_data: dict, user_context: dict) -> str:
    return f"""
You are a neurologist specializing in cognitive assessment. Analyze this Digit Span Test results.

Test Data:
- Forward digit span: {test_data.get('forward_span')}
- Forward span sequence: {test_data.get('forward_sequence', [])}
- Backward digit span: {test_data.get('backward_span')}
- Backward span sequence: {test_data.get('backward_sequence', [])}
- Response time forward: {test_data.get('forward_time')} ms
- Response time backward: {test_data.get('backward_time')} ms

User Context:
- Age: {user_context.get('age')}
- Education: {user_context.get('education_level')}
- Language: {user_context.get('language')}
- Vision: {user_context.get('vision_type')}

Provide comprehensive analysis in JSON format with:
- working_memory_capacity
- attention_span
- executive_function
- norm_comparison
- impairment_indicators (array)
- confidence_level
- recommendations (array)
- risk_level
- clinical_notes
"""
