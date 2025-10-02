from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from enum import Enum
from core.llm.groq_service import groq_service
from core.tests.cognitive_test_engine import UserType
import logging

logger = logging.getLogger(__name__)

class LLMAnalysisEngine:
    """Comprehensive LLM analysis engine with detailed prompts for all test scenarios"""
    
    def __init__(self):
        self.groq_service = groq_service
        self.analysis_prompts = self._initialize_analysis_prompts()
    
    def _initialize_analysis_prompts(self) -> Dict[str, Dict[str, str]]:
        """Initialize comprehensive analysis prompts for all test scenarios"""
        return {
            "blind_user_tests": {
                "avlt_analysis": """
You are a neurologist specializing in cognitive assessment. Analyze this Auditory Verbal Learning Test (AVLT) results for a blind user.

Test Data:
- Words presented: {words_presented}
- Trial 1 recall: {trial_1_recall}
- Trial 2 recall: {trial_2_recall}
- Trial 3 recall: {trial_3_recall}
- Trial 4 recall: {trial_4_recall}
- Trial 5 recall: {trial_5_recall}
- Delayed recall: {delayed_recall}
- Recognition: {recognition_results}
- Response times: {response_times}

User Context:
- Age: {user_age}
- Education: {education_level}
- Language: {user_language}
- Vision: Blind
- Test Adaptations: Audio-only presentation, verbal responses

Provide comprehensive analysis including:
1. Learning curve assessment (normal/mildly_impaired/moderately_impaired/severely_impaired)
2. Memory consolidation evaluation
3. Recognition memory analysis
4. Comparison with age/education norms adjusted for blind population
5. Cognitive impairment indicators specific to auditory processing
6. Confidence level in assessment given audio-only format
7. Recommendations for follow-up testing

Respond in JSON format with detailed clinical interpretation.
""",
                "digit_span_analysis": """
You are a neurologist specializing in cognitive assessment. Analyze this Digit Span Test results for a blind user.

Test Data:
- Forward digit span: {forward_span}
- Forward span sequences: {forward_sequences}
- Backward digit span: {backward_span}
- Backward span sequences: {backward_sequences}
- Response times: {response_times}
- Accuracy patterns: {accuracy_patterns}

User Context:
- Age: {user_age}
- Education: {education_level}
- Language: {user_language}
- Vision: Blind
- Test Adaptations: Audio presentation, verbal responses

Analyze:
1. Working memory capacity assessment
2. Attention span evaluation considering auditory processing strengths
3. Executive function analysis (backward span performance)
4. Comparison with normative data for blind population
5. Auditory attention and processing efficiency
6. Impact of visual impairment on working memory performance

Respond in JSON format with clinical recommendations.
""",
                "category_fluency_analysis": """
You are a neurologist specializing in cognitive assessment. Analyze this Category Fluency Test for a blind user.

Test Data:
- Category: {category}
- Words generated: {words_generated}
- Total word count: {total_count}
- Clusters identified: {clusters}
- Switches between clusters: {switches}
- Perseverations: {perseverations}
- Response pattern: {response_pattern}
- Time distribution: {time_distribution}

User Context:
- Age: {user_age}
- Education: {education_level}
- Language: {user_language}
- Vision: Blind

Analyze considering blind users may have:
- Enhanced auditory and verbal processing
- Different semantic organization strategies
- Compensatory cognitive mechanisms

1. Semantic fluency assessment
2. Executive function evaluation (clustering and switching)
3. Lexical access efficiency
4. Strategic approach to category generation
5. Comparison with blind population norms

Respond in JSON format with detailed analysis.
"""
            },
            "weak_vision_tests": {
                "mmse_analysis": """
You are a neurologist specializing in cognitive assessment. Analyze this Mini-Mental State Examination (MMSE) results for a user with weak vision.

Test Data:
- Orientation to time: {orientation_time_score}/5
- Orientation to place: {orientation_place_score}/5
- Registration: {registration_score}/3
- Attention/Calculation: {attention_score}/5
- Recall: {recall_score}/3
- Language tasks: {language_score}/9
- Total MMSE score: {total_score}/30
- Completion time: {completion_time}
- Adaptations used: {adaptations_used}

User Context:
- Age: {user_age}
- Education: {education_level}
- Language: {user_language}
- Vision: Weak vision
- Test Adaptations: Large text (48px), high contrast, voice guidance available

Consider:
1. Impact of visual adaptations on performance
2. Potential underestimation due to visual processing demands
3. Domains most/least affected by vision impairment
4. Validity of visual-dependent items
5. Compensatory strategies observed

Provide analysis with adjusted interpretation for vision impairment.
Respond in JSON format.
""",
                "moca_analysis": """
You are a neurologist specializing in cognitive assessment. Analyze this Montreal Cognitive Assessment (MoCA) results for a user with weak vision.

Test Data:
- Visuospatial/Executive: {visuospatial_score}/5
- Naming: {naming_score}/3
- Attention: {attention_score}/6
- Language: {language_score}/3
- Abstraction: {abstraction_score}/2
- Delayed Recall: {memory_score}/5
- Orientation: {orientation_score}/6
- Total MoCA score: {total_score}/30
- Visual task modifications: {visual_modifications}
- Task completion times: {completion_times}

User Context:
- Age: {user_age}
- Education: {education_level}
- Language: {user_language}
- Vision: Weak vision
- UI Adaptations: Large text, high contrast, enlarged buttons

Special Considerations:
1. Visuospatial tasks may be compromised by vision impairment
2. Clock drawing and cube copy adapted for large format
3. Trail making adapted with high contrast
4. Naming tasks with enlarged, high-contrast images

Analyze with vision-adjusted norms and provide detailed domain analysis.
Respond in JSON format.
""",
                "clock_drawing_analysis": """
You are a neurologist specializing in cognitive assessment. Analyze this Clock Drawing Test for a user with weak vision.

Test Data:
- Clock contour: {contour_quality}
- Number placement: {number_placement}
- Number sequence: {number_sequence}
- Hand placement: {hand_placement}
- Time accuracy: {time_accuracy}
- Size and proportion: {size_proportion}
- Drawing time: {drawing_time}
- Adaptations used: {adaptations}

User Context:
- Age: {user_age}
- Education: {education_level}
- Vision: Weak vision
- Drawing Adaptations: Large canvas, high contrast, thick pen tool
- Time to draw: {target_time}

Consider:
1. Visual-motor coordination challenges
2. Spatial planning with limited vision
3. Executive function assessment validity
4. Compensatory strategies employed
5. Distinction between cognitive and visual impairments

Provide analysis accounting for visual limitations.
Respond in JSON format.
"""
            },
            "non_educated_tests": {
                "simple_memory_analysis": """
You are a neurologist specializing in cognitive assessment. Analyze this Simplified Memory Test for a non-educated user.

Test Data:
- Words/Images presented: {items_presented}
- Items recalled correctly: {items_recalled}
- Recall accuracy: {accuracy_percentage}
- Response time: {response_time}
- Cues needed: {cues_needed}
- Recognition vs recall performance: {recognition_performance}

User Context:
- Age: {user_age}
- Education: Non-educated/Limited formal education
- Language: {user_language}
- Cultural background: {cultural_background}
- Test Adaptations: Icon-based, simple language, encouraging feedback

Important Considerations:
1. Educational bias in traditional cognitive tests
2. Cultural relevance of test materials
3. Impact of test anxiety in non-educated populations
4. Distinction between cognitive ability and educational exposure
5. Use of visual/iconic cues vs verbal instructions

Provide culturally sensitive analysis with appropriate normative comparisons.
Respond in JSON format.
""",
                "pattern_recognition_analysis": """
You are a neurologist specializing in cognitive assessment. Analyze this Pattern Recognition Game for a non-educated user.

Test Data:
- Game level: {game_level}
- Patterns completed: {patterns_completed}
- Pattern accuracy: {pattern_accuracy}
- Response times: {response_times}
- Learning curve: {learning_progression}
- Error patterns: {error_analysis}
- Engagement metrics: {engagement_data}

User Context:
- Age: {user_age}
- Education: Non-educated
- Test Format: Gamified, colorful, encouraging
- Cultural Adaptations: {cultural_adaptations}

Assess:
1. Executive function through pattern recognition
2. Working memory capacity
3. Learning ability and adaptation
4. Processing speed appropriate for education level
5. Problem-solving strategies
6. Motivation and engagement factors

Consider educational fairness and cultural appropriateness.
Respond in JSON format.
""",
                "object_recognition_analysis": """
You are a neurologist specializing in cognitive assessment. Analyze this Object Recognition Test for a non-educated user.

Test Data:
- Objects presented: {objects_list}
- Objects correctly named: {correct_identifications}
- Naming accuracy: {accuracy_percentage}
- Response times: {response_times}
- Cultural relevance of items: {cultural_relevance}
- Alternative names provided: {alternative_names}

User Context:
- Age: {user_age}
- Education: Non-educated
- Cultural background: {cultural_background}
- Language: {user_language}
- Test Adaptations: Culturally relevant objects, simple language

Analyze:
1. Semantic memory assessment
2. Lexical access and retrieval
3. Cultural and educational bias factors
4. Language versus cognitive factors
5. Object familiarity effects
6. Visual processing and recognition

Provide culturally sensitive interpretation.
Respond in JSON format.
"""
            },
            "educated_tests": {
                "full_mmse_analysis": """
You are a neurologist specializing in cognitive assessment. Analyze this comprehensive MMSE for an educated user.

Test Data:
- Detailed section scores: {section_scores}
- Error analysis: {error_patterns}
- Response strategies: {response_strategies}
- Completion efficiency: {completion_times}
- Qualitative observations: {qualitative_notes}
- Total score: {total_score}/30

User Context:
- Age: {user_age}
- Education: {education_level} (Higher education)
- Occupation: {occupation}
- Language: {user_language}

For educated users, analyze:
1. Subtle cognitive changes that might be masked by high premorbid functioning
2. Domain-specific vulnerabilities
3. Comparison with education-adjusted norms
4. Executive function efficiency
5. Processing speed and accuracy trade-offs
6. Early indicators of cognitive decline

Provide detailed analysis with high sensitivity to subtle changes.
Respond in JSON format.
""",
                "full_moca_analysis": """
You are a neurologist specializing in cognitive assessment. Analyze this comprehensive MoCA for an educated user.

Test Data:
- Executive/Visuospatial: {executive_score}/5 (details: {executive_details})
- Naming: {naming_score}/3
- Attention: {attention_score}/6 (breakdown: {attention_breakdown})
- Language: {language_score}/3
- Abstraction: {abstraction_score}/2
- Memory: {memory_score}/5 (learning curve: {learning_curve})
- Orientation: {orientation_score}/6
- Total: {total_score}/30

User Context:
- Age: {user_age}
- Education: {education_level}
- Occupation: {occupation}
- Premorbid IQ estimate: {premorbid_iq}

For educated users, provide:
1. Sensitive detection of mild cognitive impairment
2. Domain-specific analysis with high precision
3. Comparison with superior normative data
4. Cognitive efficiency and strategy analysis
5. Subtle executive dysfunction detection
6. Memory system detailed analysis

Respond in JSON format with comprehensive clinical interpretation.
""",
                "stroop_analysis": """
You are a neurologist specializing in cognitive assessment. Analyze this Stroop Test for an educated user.

Test Data:
- Congruent trials: {congruent_performance}
- Incongruent trials: {incongruent_performance}
- Stroop interference effect: {interference_effect}
- Error rates: {error_rates}
- Response time variability: {rt_variability}
- Practice effects: {practice_effects}

User Context:
- Age: {user_age}
- Education: {education_level}
- Occupation: {occupation}

Analyze:
1. Executive attention and inhibitory control
2. Processing speed under interference
3. Cognitive flexibility and adaptation
4. Sustained attention performance
5. Strategic approaches to conflict resolution
6. Age and education effects on interference

Provide detailed executive function analysis.
Respond in JSON format.
"""
            },
            "speech_analysis_prompts": {
                "cookie_theft_analysis": """
You are a speech-language pathologist specializing in cognitive-linguistic assessment. Analyze this Cookie Theft picture description.

Speech Sample:
- Transcription: "{transcription}"
- Duration: {duration_seconds} seconds
- Word count: {word_count}
- Information units identified: {information_units}
- Essential elements mentioned: {essential_elements}

User Context:
- Age: {user_age}
- Education: {education_level}
- Vision type: {vision_type}
- User type: {user_type}

Linguistic Analysis Required:
1. Information content and efficiency
2. Syntactic complexity and grammatical accuracy
3. Lexical diversity and word-finding abilities
4. Discourse coherence and organization
5. Pragmatic appropriateness
6. Fluency and rate of speech
7. Evidence of word-finding difficulties
8. Semantic content accuracy

Provide comprehensive speech-language analysis.
Respond in JSON format.
""",
                "narrative_speech_analysis": """
You are a speech-language pathologist analyzing narrative speech samples for cognitive assessment.

Narrative Data:
- Topic: {narrative_topic}
- Transcription: "{transcription}"
- Duration: {duration_seconds} seconds
- Prompt type: {prompt_type}

User Context:
- Age: {user_age}
- Education: {education_level}
- User type: {user_type}

Analyze:
1. Narrative structure and organization
2. Coherence and cohesion
3. Lexical diversity and complexity
4. Syntactic complexity
5. Semantic content richness
6. Temporal organization
7. Causal relationships
8. Abstract thinking indicators
9. Memory and attention indicators
10. Language formulation efficiency

Respond in JSON format with clinical recommendations.
""",
                "verbal_fluency_analysis": """
You are a neurologist analyzing verbal fluency performance for cognitive assessment.

Fluency Data:
- Test type: {fluency_type} (phonemic/semantic)
- Category/Letter: {category_or_letter}
- Words generated: {words_list}
- Total count: {total_count}
- Clusters identified: {clusters}
- Switches between clusters: {switches}
- Perseverations: {perseverations}
- Rule violations: {rule_violations}

User Context:
- Age: {user_age}
- Education: {education_level}
- User type: {user_type}

Analyze:
1. Executive function (clustering and switching strategies)
2. Semantic memory organization
3. Lexical access speed and efficiency
4. Strategic approach to word generation
5. Sustained attention and mental flexibility
6. Language processing efficiency
7. Comparison with normative data

Respond in JSON format.
"""
            },
            "behavioral_analysis_prompts": {
                "response_time_analysis": """
You are a neuropsychologist analyzing behavioral response patterns for cognitive assessment.

Behavioral Data:
- User type: {user_type}
- Test type: {test_type}
- Response times: {response_times}
- Accuracy rates: {accuracy_rates}
- Response variability: {response_variability}
- Error patterns: {error_patterns}
- Fatigue indicators: {fatigue_indicators}

User Context:
- Age: {user_age}
- Education: {education_level}
- Adaptive technology used: {adaptations}

Analyze:
1. Processing speed assessment
2. Attention and vigilance patterns
3. Response consistency and reliability
4. Speed-accuracy trade-offs
5. Fatigue effects over time
6. Learning and adaptation patterns
7. Executive control of responses
8. Comparison with user-type specific norms

Respond in JSON format with behavioral interpretation.
""",
                "engagement_analysis": """
You are a neuropsychologist analyzing engagement and behavioral patterns.

Engagement Data:
- Session duration: {session_duration}
- Task completion rates: {completion_rates}
- Help-seeking behavior: {help_requests}
- Error recovery patterns: {error_recovery}
- Motivation indicators: {motivation_indicators}
- Attention lapses: {attention_lapses}

User Context:
- Age: {user_age}
- User type: {user_type}
- Session adaptations: {adaptations}

Analyze:
1. Sustained attention capacity
2. Motivation and engagement levels
3. Executive function in task management
4. Metacognitive awareness
5. Adaptation to interface challenges
6. Learning efficiency patterns
7. Behavioral indicators of cognitive fatigue

Respond in JSON format.
"""
            }
        }
    
    # BLIND USER ANALYSIS METHODS
    async def analyze_avlt_blind(self, test_data: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze AVLT results for blind users"""
        prompt = self.analysis_prompts["blind_user_tests"]["avlt_analysis"].format(
            words_presented=test_data.get("words_presented", []),
            trial_1_recall=test_data.get("trial_1_recall", []),
            trial_2_recall=test_data.get("trial_2_recall", []),
            trial_3_recall=test_data.get("trial_3_recall", []),
            trial_4_recall=test_data.get("trial_4_recall", []),
            trial_5_recall=test_data.get("trial_5_recall", []),
            delayed_recall=test_data.get("delayed_recall", []),
            recognition_results=test_data.get("recognition_results", {}),
            response_times=test_data.get("response_times", []),
            user_age=user_context.get("age", "Unknown"),
            education_level=user_context.get("education_level", "Unknown"),
            user_language=user_context.get("language", "en")
        )
        
        try:
            analysis_result = await self.groq_service.analyze_with_groq(prompt)
            return {
                "test_name": "AVLT",
                "user_type": "blind",
                "analysis_result": analysis_result,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "llm_provider": "groq",
                "confidence_score": analysis_result.get("confidence_level", "medium")
            }
        except Exception as e:
            logger.error(f"AVLT analysis failed: {e}")
            return {"error": str(e), "test_name": "AVLT", "user_type": "blind"}
    
    async def analyze_digit_span_blind(self, test_data: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Digit Span results for blind users"""
        prompt = self.analysis_prompts["blind_user_tests"]["digit_span_analysis"].format(
            forward_span=test_data.get("forward_span", 0),
            forward_sequences=test_data.get("forward_sequences", []),
            backward_span=test_data.get("backward_span", 0),
            backward_sequences=test_data.get("backward_sequences", []),
            response_times=test_data.get("response_times", []),
            accuracy_patterns=test_data.get("accuracy_patterns", {}),
            user_age=user_context.get("age", "Unknown"),
            education_level=user_context.get("education_level", "Unknown"),
            user_language=user_context.get("language", "en")
        )
        
        try:
            analysis_result = await self.groq_service.analyze_with_groq(prompt)
            return {
                "test_name": "Digit Span",
                "user_type": "blind",
                "analysis_result": analysis_result,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "llm_provider": "groq"
            }
        except Exception as e:
            logger.error(f"Digit Span analysis failed: {e}")
            return {"error": str(e), "test_name": "Digit Span", "user_type": "blind"}
    
    # WEAK VISION USER ANALYSIS METHODS
    async def analyze_mmse_weak_vision(self, test_data: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze MMSE results for weak vision users"""
        prompt = self.analysis_prompts["weak_vision_tests"]["mmse_analysis"].format(
            orientation_time_score=test_data.get("orientation_time_score", 0),
            orientation_place_score=test_data.get("orientation_place_score", 0),
            registration_score=test_data.get("registration_score", 0),
            attention_score=test_data.get("attention_score", 0),
            recall_score=test_data.get("recall_score", 0),
            language_score=test_data.get("language_score", 0),
            total_score=test_data.get("total_score", 0),
            completion_time=test_data.get("completion_time", 0),
            adaptations_used=test_data.get("adaptations_used", []),
            user_age=user_context.get("age", "Unknown"),
            education_level=user_context.get("education_level", "Unknown"),
            user_language=user_context.get("language", "en")
        )
        
        try:
            analysis_result = await self.groq_service.analyze_with_groq(prompt)
            return {
                "test_name": "MMSE",
                "user_type": "weak_vision",
                "analysis_result": analysis_result,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "llm_provider": "groq"
            }
        except Exception as e:
            logger.error(f"MMSE analysis failed: {e}")
            return {"error": str(e), "test_name": "MMSE", "user_type": "weak_vision"}
    
    # NON-EDUCATED USER ANALYSIS METHODS  
    async def analyze_simple_memory_non_educated(self, test_data: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Simple Memory Test for non-educated users"""
        prompt = self.analysis_prompts["non_educated_tests"]["simple_memory_analysis"].format(
            items_presented=test_data.get("items_presented", []),
            items_recalled=test_data.get("items_recalled", []),
            accuracy_percentage=test_data.get("accuracy_percentage", 0),
            response_time=test_data.get("response_time", 0),
            cues_needed=test_data.get("cues_needed", 0),
            recognition_performance=test_data.get("recognition_performance", {}),
            user_age=user_context.get("age", "Unknown"),
            user_language=user_context.get("language", "en"),
            cultural_background=user_context.get("cultural_background", "Unknown")
        )
        
        try:
            analysis_result = await self.groq_service.analyze_with_groq(prompt)
            return {
                "test_name": "Simple Memory Test",
                "user_type": "non_educated",
                "analysis_result": analysis_result,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "llm_provider": "groq"
            }
        except Exception as e:
            logger.error(f"Simple Memory analysis failed: {e}")
            return {"error": str(e), "test_name": "Simple Memory Test", "user_type": "non_educated"}
    
    # EDUCATED USER ANALYSIS METHODS
    async def analyze_full_moca_educated(self, test_data: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze comprehensive MoCA for educated users"""
        prompt = self.analysis_prompts["educated_tests"]["full_moca_analysis"].format(
            executive_score=test_data.get("executive_score", 0),
            executive_details=test_data.get("executive_details", {}),
            naming_score=test_data.get("naming_score", 0),
            attention_score=test_data.get("attention_score", 0),
            attention_breakdown=test_data.get("attention_breakdown", {}),
            language_score=test_data.get("language_score", 0),
            abstraction_score=test_data.get("abstraction_score", 0),
            memory_score=test_data.get("memory_score", 0),
            learning_curve=test_data.get("learning_curve", []),
            orientation_score=test_data.get("orientation_score", 0),
            total_score=test_data.get("total_score", 0),
            user_age=user_context.get("age", "Unknown"),
            education_level=user_context.get("education_level", "Unknown"),
            occupation=user_context.get("occupation", "Unknown"),
            premorbid_iq=user_context.get("premorbid_iq", "Unknown")
        )
        
        try:
            analysis_result = await self.groq_service.analyze_with_groq(prompt)
            return {
                "test_name": "Full MoCA",
                "user_type": "educated",
                "analysis_result": analysis_result,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "llm_provider": "groq"
            }
        except Exception as e:
            logger.error(f"Full MoCA analysis failed: {e}")
            return {"error": str(e), "test_name": "Full MoCA", "user_type": "educated"}
    
    # SPEECH ANALYSIS METHODS
    async def analyze_cookie_theft_speech(self, speech_data: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Cookie Theft description speech sample"""
        prompt = self.analysis_prompts["speech_analysis_prompts"]["cookie_theft_analysis"].format(
            transcription=speech_data.get("transcription", ""),
            duration_seconds=speech_data.get("duration_seconds", 0),
            word_count=speech_data.get("word_count", 0),
            information_units=speech_data.get("information_units", []),
            essential_elements=speech_data.get("essential_elements", []),
            user_age=user_context.get("age", "Unknown"),
            education_level=user_context.get("education_level", "Unknown"),
            vision_type=user_context.get("vision_type", "Unknown"),
            user_type=user_context.get("user_type", "Unknown")
        )
        
        try:
            analysis_result = await self.groq_service.analyze_with_groq(prompt)
            return {
                "test_name": "Cookie Theft Description",
                "analysis_type": "speech",
                "analysis_result": analysis_result,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "llm_provider": "groq"
            }
        except Exception as e:
            logger.error(f"Cookie Theft speech analysis failed: {e}")
            return {"error": str(e), "test_name": "Cookie Theft Description", "analysis_type": "speech"}
    
    # COMPREHENSIVE ANALYSIS METHODS
    async def generate_comprehensive_analysis(self, all_test_results: List[Dict[str, Any]], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive analysis across all test results"""
        
        comprehensive_prompt = f"""
You are a senior neurologist providing a comprehensive cognitive assessment based on multiple test results.

User Profile:
- Age: {user_context.get('age', 'Unknown')}
- Education: {user_context.get('education_level', 'Unknown')}
- Vision Type: {user_context.get('vision_type', 'Unknown')}
- User Type: {user_context.get('user_type', 'Unknown')}
- Language: {user_context.get('language', 'en')}

Test Results Summary:
{json.dumps(all_test_results, indent=2)}

Provide a comprehensive analysis including:
1. Overall cognitive status assessment
2. Domain-specific strengths and weaknesses
3. Pattern of performance across tests
4. Consistency of findings
5. Impact of user-specific adaptations on results
6. Risk stratification (low/medium/high)
7. Recommendations for follow-up
8. Confidence in assessment given test adaptations
9. Suggested monitoring schedule
10. Clinical interpretation and next steps

Consider the user's specific characteristics and test adaptations in your interpretation.
Respond in detailed JSON format with clinical recommendations.
"""
        
        try:
            comprehensive_result = await self.groq_service.analyze_with_groq(comprehensive_prompt)
            return {
                "analysis_type": "comprehensive",
                "user_type": user_context.get("user_type", "Unknown"),
                "tests_analyzed": len(all_test_results),
                "comprehensive_analysis": comprehensive_result,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "llm_provider": "groq"
            }
        except Exception as e:
            logger.error(f"Comprehensive analysis failed: {e}")
            return {"error": str(e), "analysis_type": "comprehensive"}
    
    # PROGRESS ANALYSIS METHODS
    async def analyze_progress_over_time(self, historical_results: List[Dict[str, Any]], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze progress and changes over time"""
        
        progress_prompt = f"""
You are a neurologist analyzing cognitive performance changes over time.

User Profile:
- Age: {user_context.get('age', 'Unknown')}
- User Type: {user_context.get('user_type', 'Unknown')}
- Baseline Date: {user_context.get('baseline_date', 'Unknown')}

Historical Test Results (chronological order):
{json.dumps(historical_results, indent=2)}

Analyze:
1. Trajectory of cognitive performance (improving/stable/declining)
2. Rate of change in each cognitive domain
3. Consistency of changes across different tests
4. Seasonal or temporal patterns
5. Statistical significance of changes
6. Clinical significance of observed changes
7. Comparison with expected age-related changes
8. Impact of test familiarity or practice effects
9. Recommendations for monitoring frequency
10. Early warning indicators present

Provide detailed longitudinal analysis with clinical interpretation.
Respond in JSON format.
"""
        
        try:
            progress_result = await self.groq_service.analyze_with_groq(progress_prompt)
            return {
                "analysis_type": "longitudinal_progress",
                "time_span": len(historical_results),
                "progress_analysis": progress_result,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "llm_provider": "groq"
            }
        except Exception as e:
            logger.error(f"Progress analysis failed: {e}")
            return {"error": str(e), "analysis_type": "longitudinal_progress"}

# Global instance
llm_analysis_engine = LLMAnalysisEngine()