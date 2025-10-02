from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
from enum import Enum
import uuid
import random

class UserType(Enum):
    BLIND = "blind"
    WEAK_VISION = "weak_vision"
    NON_EDUCATED = "non_educated"
    EDUCATED = "educated"

class BehavioralTestEngine:
    """Comprehensive behavioral test engine for all user scenarios"""
    
    def __init__(self):
        self.test_data = self._initialize_test_data()
    
    def _initialize_test_data(self) -> Dict[str, Any]:
        """Initialize test data for different behavioral assessments"""
        return {
            "reaction_time_targets": {
                "audio_tones": ["high_beep", "low_beep", "double_beep"],
                "visual_targets": ["red_circle", "blue_square", "green_triangle"],
                "tactile_targets": ["short_vibration", "long_vibration", "double_vibration"]
            },
            "attention_tasks": {
                "vigilance_targets": ["A", "X", "7"],
                "go_no_go_stimuli": ["go", "no-go"]
            },
            "executive_function_tasks": {
                "card_sorting_rules": ["color", "shape", "number"],
                "task_switching_cues": ["letters", "numbers"]
            }
        }
    
    # BLIND USER TESTS
    async def run_voice_response_monitoring(self, user_id: str, duration_minutes: int = 10) -> Dict[str, Any]:
        """Voice response time monitoring for blind users"""
        commands = [
            "Say 'yes' when you hear the high tone",
            "Say 'no' when you hear the low tone",
            "Say 'stop' when you hear the double beep",
            "Repeat the word I just said",
            "Count from 1 to 5"
        ]
        
        test_result = {
            "test_name": "Voice Response Time Monitoring",
            "user_type": UserType.BLIND.value,
            "session_id": str(uuid.uuid4()),
            "duration_minutes": duration_minutes,
            "commands": commands,
            "audio_stimuli": self.test_data["reaction_time_targets"]["audio_tones"],
            "measurements": {
                "response_latency": "milliseconds",
                "voice_command_accuracy": "percentage",
                "response_consistency": "coefficient_of_variation",
                "attention_lapses": "count"
            },
            "instructions": {
                "audio": "You will hear different sounds and commands. Respond as quickly and accurately as possible.",
                "voice_prompts": [
                    "Listen for the sound",
                    "Respond now",
                    "Good, let's continue"
                ]
            },
            "adaptations": {
                "audio_only": True,
                "clear_audio_cues": True,
                "verbal_feedback": True
            }
        }
        
        return test_result
    
    async def run_audio_pattern_recognition(self, user_id: str) -> Dict[str, Any]:
        """Audio pattern recognition test for blind users"""
        tone_patterns = [
            ["high", "low", "high"],
            ["low", "low", "high", "low"],
            ["high", "low", "low", "high", "high"]
        ]
        
        rhythm_patterns = [
            ["short", "long", "short"],
            ["long", "short", "short", "long"],
            ["short", "short", "long", "short"]
        ]
        
        test_result = {
            "test_name": "Audio Pattern Recognition",
            "user_type": UserType.BLIND.value,
            "session_id": str(uuid.uuid4()),
            "tone_patterns": tone_patterns,
            "rhythm_patterns": rhythm_patterns,
            "max_score": len(tone_patterns) + len(rhythm_patterns),
            "instructions": {
                "audio": "You will hear patterns of sounds. Listen carefully and then repeat the pattern by saying 'high' or 'low' for tones, or 'short' or 'long' for rhythms.",
                "voice_prompts": [
                    "Listen to this pattern",
                    "Now repeat the pattern",
                    "Was that correct? Let's try another"
                ]
            },
            "measurements": {
                "pattern_accuracy": "percentage",
                "response_time": "seconds",
                "memory_span": "max_pattern_length"
            }
        }
        
        return test_result
    
    async def run_speech_pattern_monitoring(self, user_id: str) -> Dict[str, Any]:
        """Speech pattern changes monitoring for blind users"""
        test_result = {
            "test_name": "Speech Pattern Monitoring",
            "user_type": UserType.BLIND.value,
            "session_id": str(uuid.uuid4()),
            "monitoring_duration": "continuous",
            "speech_tasks": [
                "free_conversation",
                "structured_interview",
                "reading_aloud",
                "spontaneous_description"
            ],
            "analysis_parameters": {
                "acoustic_features": [
                    "fundamental_frequency",
                    "intensity_variation",
                    "voice_quality",
                    "speech_rate"
                ],
                "temporal_features": [
                    "pause_duration",
                    "pause_frequency",
                    "articulation_rate",
                    "response_latency"
                ],
                "linguistic_features": [
                    "word_finding_difficulty",
                    "semantic_fluency",
                    "syntactic_complexity"
                ]
            },
            "baseline_establishment": {
                "sessions_required": 3,
                "interval_days": 7
            }
        }
        
        return test_result
    
    # WEAK VISION USER TESTS
    async def run_visual_response_monitoring(self, user_id: str) -> Dict[str, Any]:
        """Visual response time monitoring for weak vision users"""
        test_result = {
            "test_name": "Visual Response Time Monitoring",
            "user_type": UserType.WEAK_VISION.value,
            "session_id": str(uuid.uuid4()),
            "visual_stimuli": {
                "large_buttons": {
                    "size": "100x100px",
                    "colors": ["high_contrast_red", "high_contrast_blue", "high_contrast_green"]
                },
                "text_targets": {
                    "font_size": "48px",
                    "contrast_ratio": "21:1",
                    "targets": ["YES", "NO", "STOP"]
                }
            },
            "measurements": {
                "simple_reaction_time": "milliseconds",
                "choice_reaction_time": "milliseconds",
                "accuracy": "percentage",
                "response_variability": "coefficient_of_variation"
            },
            "ui_adaptations": {
                "high_contrast_interface": True,
                "large_buttons": "100px",
                "clear_visual_feedback": True,
                "adjustable_brightness": True
            },
            "instructions": {
                "text": "Press the button as quickly as possible when you see the target.",
                "text_size": "24px",
                "voice_backup": True
            }
        }
        
        return test_result
    
    async def run_navigation_pattern_analysis(self, user_id: str) -> Dict[str, Any]:
        """Navigation pattern analysis for weak vision users"""
        test_result = {
            "test_name": "Navigation Pattern Analysis",
            "user_type": UserType.WEAK_VISION.value,
            "session_id": str(uuid.uuid4()),
            "navigation_tasks": [
                {
                    "task": "menu_navigation",
                    "description": "Navigate through large menu items",
                    "ui_features": "large_text_high_contrast"
                },
                {
                    "task": "form_completion",
                    "description": "Complete form with large input fields",
                    "ui_features": "large_fields_clear_labels"
                },
                {
                    "task": "content_browsing",
                    "description": "Browse through content with large text",
                    "ui_features": "large_text_good_spacing"
                }
            ],
            "measurements": {
                "task_completion_time": "seconds",
                "navigation_efficiency": "clicks_per_task",
                "error_rate": "percentage",
                "assistance_requests": "count"
            },
            "ui_adaptations": {
                "font_size": "32px",
                "button_size": "80px_height",
                "high_contrast": True,
                "clear_focus_indicators": True
            }
        }
        
        return test_result
    
    async def run_visual_attention_test(self, user_id: str) -> Dict[str, Any]:
        """Visual attention test for weak vision users"""
        test_result = {
            "test_name": "Visual Attention Test",
            "user_type": UserType.WEAK_VISION.value,
            "session_id": str(uuid.uuid4()),
            "attention_tasks": {
                "vigilance_task": {
                    "target_letter": "X",
                    "distractor_letters": ["O", "C", "Q"],
                    "presentation_rate": "1_per_second",
                    "duration_minutes": 5
                },
                "divided_attention": {
                    "primary_task": "track_moving_dot",
                    "secondary_task": "respond_to_color_changes",
                    "duration_minutes": 3
                }
            },
            "ui_adaptations": {
                "large_stimuli": "60px",
                "high_contrast": "black_on_white",
                "reduced_visual_clutter": True,
                "clear_target_highlighting": True
            },
            "measurements": {
                "hit_rate": "percentage",
                "false_alarm_rate": "percentage",
                "response_time": "milliseconds",
                "sustained_attention_decrement": "percentage"
            }
        }
        
        return test_result
    
    # NON-EDUCATED USER TESTS
    async def run_simple_interaction_monitoring(self, user_id: str) -> Dict[str, Any]:
        """Simple interaction monitoring for non-educated users"""
        test_result = {
            "test_name": "Simple Interaction Monitoring",
            "user_type": UserType.NON_EDUCATED.value,
            "session_id": str(uuid.uuid4()),
            "interaction_tasks": [
                {
                    "task": "icon_selection",
                    "description": "Touch the happy face when you see it",
                    "icon": "😊",
                    "distractors": ["😢", "😐", "😴"]
                },
                {
                    "task": "color_matching",
                    "description": "Touch the same color",
                    "target_color": "red",
                    "options": ["red", "blue", "green", "yellow"]
                },
                {
                    "task": "simple_counting",
                    "description": "Count the dots and touch the number",
                    "dots": 3,
                    "number_options": [1, 2, 3, 4, 5]
                }
            ],
            "measurements": {
                "selection_accuracy": "percentage",
                "response_time": "seconds",
                "task_engagement": "completion_rate",
                "learning_progress": "improvement_over_trials"
            },
            "ui_adaptations": {
                "very_large_icons": "120px",
                "bright_colors": True,
                "simple_layout": True,
                "encouraging_feedback": True,
                "game_like_interface": True
            }
        }
        
        return test_result
    
    async def run_game_engagement_tracking(self, user_id: str) -> Dict[str, Any]:
        """Game engagement tracking for non-educated users"""
        simple_games = [
            {
                "name": "memory_match",
                "description": "Match the same pictures",
                "difficulty": "easy",
                "cards": 4  # 2 pairs
            },
            {
                "name": "color_sort",
                "description": "Put same colors together",
                "difficulty": "easy",
                "colors": ["red", "blue"]
            },
            {
                "name": "simple_puzzle",
                "description": "Put pieces in right place",
                "difficulty": "easy",
                "pieces": 4
            }
        ]
        
        test_result = {
            "test_name": "Game Engagement Tracking",
            "user_type": UserType.NON_EDUCATED.value,
            "session_id": str(uuid.uuid4()),
            "games": simple_games,
            "engagement_metrics": {
                "session_duration": "minutes",
                "game_completion_rate": "percentage",
                "retry_attempts": "count",
                "help_requests": "count",
                "positive_interactions": "count"
            },
            "adaptive_features": {
                "difficulty_adjustment": True,
                "encouragement_frequency": "high",
                "celebration_animations": True,
                "progress_visualization": "simple_stars"
            },
            "ui_adaptations": {
                "colorful_design": True,
                "large_friendly_buttons": True,
                "clear_instructions": "audio_and_visual",
                "minimal_text": True
            }
        }
        
        return test_result
    
    async def run_learning_curve_analysis(self, user_id: str) -> Dict[str, Any]:
        """Learning curve analysis for non-educated users"""
        test_result = {
            "test_name": "Learning Curve Analysis",
            "user_type": UserType.NON_EDUCATED.value,
            "session_id": str(uuid.uuid4()),
            "learning_tasks": [
                {
                    "task": "icon_recognition",
                    "progression": "introduce_one_new_icon_per_session",
                    "icons": ["🏠", "🚗", "🍎", "📱", "👨‍👩‍👧‍👦"]
                },
                {
                    "task": "sequence_learning",
                    "progression": "increase_sequence_length",
                    "starting_length": 2,
                    "max_length": 5
                },
                {
                    "task": "category_sorting",
                    "progression": "add_new_categories",
                    "categories": ["food", "animals", "vehicles"]
                }
            ],
            "measurements": {
                "learning_rate": "trials_to_criterion",
                "retention": "performance_after_delay",
                "transfer": "performance_on_similar_tasks",
                "plateau_detection": "performance_stability"
            },
            "session_structure": {
                "sessions_per_week": 3,
                "session_duration": "15_minutes",
                "break_frequency": "every_5_minutes"
            }
        }
        
        return test_result
    
    # EDUCATED USER TESTS
    async def run_complex_interaction_monitoring(self, user_id: str) -> Dict[str, Any]:
        """Complex interaction monitoring for educated users"""
        test_result = {
            "test_name": "Complex Interaction Monitoring",
            "user_type": UserType.EDUCATED.value,
            "session_id": str(uuid.uuid4()),
            "interaction_tasks": [
                {
                    "task": "multi_step_form_completion",
                    "description": "Complete complex form with validation",
                    "steps": 8,
                    "validation_rules": True
                },
                {
                    "task": "hierarchical_navigation",
                    "description": "Navigate through multi-level menus",
                    "menu_depth": 4,
                    "items_per_level": 6
                },
                {
                    "task": "data_entry_accuracy",
                    "description": "Enter data with high accuracy requirements",
                    "fields": 12,
                    "data_types": ["text", "numbers", "dates", "selections"]
                }
            ],
            "measurements": {
                "task_completion_time": "seconds",
                "accuracy_rate": "percentage",
                "error_recovery_time": "seconds",
                "cognitive_load_indicators": ["pause_patterns", "backtracking", "help_usage"]
            },
            "interface_complexity": {
                "standard_web_interface": True,
                "multiple_simultaneous_tasks": True,
                "context_switching_required": True
            }
        }
        
        return test_result
    
    async def run_executive_function_monitoring(self, user_id: str) -> Dict[str, Any]:
        """Executive function monitoring for educated users"""
        test_result = {
            "test_name": "Executive Function Monitoring",
            "user_type": UserType.EDUCATED.value,
            "session_id": str(uuid.uuid4()),
            "executive_tasks": {
                "task_switching": {
                    "description": "Switch between classifying by color vs shape",
                    "switch_trials": 50,
                    "repeat_trials": 50,
                    "cue_target_interval": [100, 500, 1000]  # milliseconds
                },
                "working_memory_updating": {
                    "description": "Keep track of running count in multiple categories",
                    "categories": 3,
                    "items_per_category": 20,
                    "update_frequency": "random"
                },
                "inhibitory_control": {
                    "description": "Respond to target while ignoring distractors",
                    "target_frequency": 0.2,
                    "distractor_similarity": "high",
                    "response_deadline": 1500  # milliseconds
                }
            },
            "measurements": {
                "switch_cost": "rt_difference_switch_vs_repeat",
                "working_memory_capacity": "max_items_tracked_accurately",
                "inhibition_efficiency": "accuracy_under_interference",
                "cognitive_flexibility": "adaptation_to_rule_changes"
            },
            "session_parameters": {
                "total_duration": "45_minutes",
                "break_intervals": "every_15_minutes",
                "performance_feedback": "delayed_until_end"
            }
        }
        
        return test_result
    
    async def run_learning_adaptation_test(self, user_id: str) -> Dict[str, Any]:
        """Learning and adaptation test for educated users"""
        test_result = {
            "test_name": "Learning and Adaptation Test",
            "user_type": UserType.EDUCATED.value,
            "session_id": str(uuid.uuid4()),
            "learning_paradigms": {
                "probabilistic_classification": {
                    "description": "Learn to classify patterns based on feedback",
                    "categories": 2,
                    "feedback_probability": 0.8,
                    "trials": 200
                },
                "sequence_learning": {
                    "description": "Implicit learning of repeating sequences",
                    "sequence_length": 12,
                    "sequence_repetitions": 20,
                    "random_trials": 40
                },
                "reversal_learning": {
                    "description": "Adapt when reward contingencies reverse",
                    "initial_learning_trials": 50,
                    "reversal_points": 3,
                    "trials_per_phase": 30
                }
            },
            "measurements": {
                "learning_rate": "trials_to_criterion",
                "asymptotic_performance": "final_accuracy_level",
                "adaptation_speed": "trials_to_readjust_after_change",
                "strategy_flexibility": "response_to_changing_demands"
            },
            "cognitive_load_manipulation": {
                "dual_task_conditions": True,
                "time_pressure_conditions": True,
                "distraction_conditions": True
            }
        }
        
        return test_result
    
    # Longitudinal monitoring methods
    async def generate_behavioral_baseline(self, user_id: str, user_type: UserType) -> Dict[str, Any]:
        """Generate behavioral baseline for longitudinal comparison"""
        baseline_tests = {
            UserType.BLIND: [
                "voice_response_monitoring",
                "audio_pattern_recognition",
                "speech_pattern_monitoring"
            ],
            UserType.WEAK_VISION: [
                "visual_response_monitoring",
                "navigation_pattern_analysis",
                "visual_attention_test"
            ],
            UserType.NON_EDUCATED: [
                "simple_interaction_monitoring",
                "game_engagement_tracking",
                "learning_curve_analysis"
            ],
            UserType.EDUCATED: [
                "complex_interaction_monitoring",
                "executive_function_monitoring",
                "learning_adaptation_test"
            ]
        }
        
        baseline_result = {
            "user_id": user_id,
            "user_type": user_type.value,
            "baseline_tests": baseline_tests[user_type],
            "baseline_period": {
                "duration_weeks": 2,
                "sessions_per_week": 3,
                "session_duration_minutes": 30
            },
            "stability_criteria": {
                "coefficient_of_variation": "<0.15",
                "trend_significance": "p>0.05",
                "minimum_sessions": 5
            },
            "created_at": datetime.utcnow().isoformat()
        }
        
        return baseline_result
    
    async def calculate_behavioral_changes(self, user_id: str, baseline_data: Dict[str, Any], current_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate behavioral changes from baseline"""
        change_analysis = {
            "user_id": user_id,
            "comparison_date": datetime.utcnow().isoformat(),
            "baseline_period": baseline_data.get("baseline_period"),
            "current_period": {
                "start_date": (datetime.utcnow() - timedelta(weeks=1)).isoformat(),
                "end_date": datetime.utcnow().isoformat()
            },
            "behavioral_changes": {
                "response_time_change": "percentage_change_from_baseline",
                "accuracy_change": "percentage_change_from_baseline",
                "engagement_change": "percentage_change_from_baseline",
                "consistency_change": "coefficient_of_variation_change"
            },
            "statistical_significance": {
                "t_test_results": "p_values_for_each_measure",
                "effect_sizes": "cohens_d_for_each_measure",
                "confidence_intervals": "95_percent_ci"
            },
            "clinical_interpretation": {
                "meaningful_change_threshold": "1_standard_deviation",
                "change_direction": "improvement_decline_stable",
                "change_magnitude": "small_medium_large"
            }
        }
        
        return change_analysis

# Global instance
behavioral_test_engine = BehavioralTestEngine()