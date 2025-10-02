from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from enum import Enum
import uuid

class UserType(Enum):
    BLIND = "blind"
    WEAK_VISION = "weak_vision"
    NON_EDUCATED = "non_educated"
    EDUCATED = "educated"

class SpeechTestEngine:
    """Comprehensive speech test engine for all user scenarios"""
    
    def __init__(self):
        self.test_data = self._initialize_test_data()
    
    def _initialize_test_data(self) -> Dict[str, Any]:
        """Initialize test data for different speech assessments"""
        return {
            "cookie_theft_description": {
                "image_url": "/static/images/cookie_theft.jpg",
                "description": "Picture showing a woman washing dishes while children take cookies from a jar",
                "key_elements": [
                    "woman", "dishes", "sink", "water overflowing", "boy", "girl", 
                    "cookies", "jar", "stool", "falling", "kitchen"
                ]
            },
            "boston_naming_objects": [
                "cactus", "harmonica", "rhinoceros", "acorn", "igloo",
                "stilts", "dominoes", "calipers", "escalator", "tongs"
            ],
            "simple_objects": [
                "apple", "car", "house", "dog", "book", "chair", "tree", "ball"
            ],
            "fas_words": {
                "F": ["cat", "dog", "fish", "fire", "food", "family"],
                "A": ["apple", "animal", "arm", "art", "air", "airplane"],
                "S": ["sun", "sea", "school", "sister", "song", "street"]
            },
            "sentence_repetition": [
                "The quick brown fox jumps over the lazy dog",
                "She sells seashells by the seashore",
                "Peter Piper picked a peck of pickled peppers"
            ]
        }
    
    # BLIND USER TESTS
    async def run_boston_naming_audio(self, user_id: str) -> Dict[str, Any]:
        """Boston Naming Test adapted for blind users (audio descriptions)"""
        test_result = {
            "test_name": "Boston Naming Test (Audio)",
            "user_type": UserType.BLIND.value,
            "session_id": str(uuid.uuid4()),
            "objects": [
                {
                    "name": obj,
                    "audio_description": f"This is a {obj}. What is it called?",
                    "alternative_descriptions": self._get_audio_descriptions(obj)
                }
                for obj in self.test_data["boston_naming_objects"]
            ],
            "max_score": len(self.test_data["boston_naming_objects"]),
            "instructions": {
                "audio": "I will describe objects to you. Please tell me what each object is called.",
                "voice_prompts": [
                    "Listen to this description",
                    "What is this object called?",
                    "Take your time to think about it"
                ]
            },
            "adaptations": {
                "audio_only": True,
                "detailed_descriptions": True,
                "no_visual_cues": True
            }
        }
        
        return test_result
    
    async def run_narrative_speech_sample(self, user_id: str) -> Dict[str, Any]:
        """Narrative speech sample for blind users"""
        prompts = [
            "Tell me about a typical day in your life",
            "Describe a memorable experience from your childhood",
            "Tell me about your family",
            "Describe your favorite place"
        ]
        
        test_result = {
            "test_name": "Narrative Speech Sample",
            "user_type": UserType.BLIND.value,
            "session_id": str(uuid.uuid4()),
            "prompts": prompts,
            "recording_duration": 300,  # 5 minutes
            "instructions": {
                "audio": "I will give you a topic. Please talk about it for as long as you like. There's no right or wrong answer.",
                "voice_prompts": [
                    "Here's your topic:",
                    "Take your time",
                    "You can continue if you have more to say"
                ]
            },
            "analysis_criteria": [
                "narrative_coherence",
                "lexical_diversity",
                "grammatical_complexity",
                "speech_rate",
                "pause_patterns",
                "semantic_content"
            ]
        }
        
        return test_result
    
    async def run_cookie_theft_audio(self, user_id: str) -> Dict[str, Any]:
        """Cookie Theft description adapted for blind users"""
        test_result = {
            "test_name": "Cookie Theft Description (Audio)",
            "user_type": UserType.BLIND.value,
            "session_id": str(uuid.uuid4()),
            "scenario_description": "Imagine a kitchen scene where a woman is at the sink doing dishes, and two children are trying to get cookies from a high shelf. Describe what you think is happening in this scene.",
            "key_elements": self.test_data["cookie_theft_description"]["key_elements"],
            "instructions": {
                "audio": "I will describe a scene to you. Please tell me what you think is happening and describe the scene in detail.",
                "voice_prompts": [
                    "Listen to this scenario",
                    "What do you think is happening?",
                    "Can you tell me more details?"
                ]
            },
            "scoring": {
                "information_units": True,
                "narrative_coherence": True,
                "linguistic_efficiency": True
            }
        }
        
        return test_result
    
    # WEAK VISION USER TESTS
    async def run_cookie_theft_large_image(self, user_id: str) -> Dict[str, Any]:
        """Cookie Theft description for weak vision users with large, high-contrast image"""
        test_result = {
            "test_name": "Cookie Theft Description (Large Image)",
            "user_type": UserType.WEAK_VISION.value,
            "session_id": str(uuid.uuid4()),
            "image_adaptations": {
                "high_contrast": True,
                "large_size": "800x600",
                "enhanced_edges": True,
                "adjustable_zoom": True
            },
            "image_url": self.test_data["cookie_theft_description"]["image_url"],
            "key_elements": self.test_data["cookie_theft_description"]["key_elements"],
            "instructions": {
                "text": "Look at this picture and describe what you see. Tell me what is happening in the scene.",
                "text_size": "24px",
                "high_contrast_text": True,
                "voice_backup": True
            },
            "ui_adaptations": {
                "large_record_button": True,
                "high_contrast_interface": True,
                "voice_instructions": True
            }
        }
        
        return test_result
    
    async def run_reading_comprehension_test(self, user_id: str) -> Dict[str, Any]:
        """Reading comprehension test for weak vision users"""
        passages = [
            {
                "title": "The Garden",
                "text": "Mary loved to work in her garden. Every morning, she would water the flowers and pull the weeds. The roses were her favorite because they smelled so sweet.",
                "questions": [
                    "What did Mary love to do?",
                    "What were her favorite flowers?",
                    "Why did she like them?"
                ]
            }
        ]
        
        test_result = {
            "test_name": "Reading Comprehension Test",
            "user_type": UserType.WEAK_VISION.value,
            "session_id": str(uuid.uuid4()),
            "passages": passages,
            "text_adaptations": {
                "font_size": "32px",
                "high_contrast": True,
                "line_spacing": "2.0",
                "serif_font": True
            },
            "instructions": {
                "text": "Read this passage aloud, then I will ask you some questions about it.",
                "text_size": "24px",
                "voice_backup": True
            }
        }
        
        return test_result
    
    async def run_cowat_test(self, user_id: str) -> Dict[str, Any]:
        """Controlled Oral Word Association Test for weak vision users"""
        test_result = {
            "test_name": "COWAT (F-A-S Test)",
            "user_type": UserType.WEAK_VISION.value,
            "session_id": str(uuid.uuid4()),
            "letters": ["F", "A", "S"],
            "time_per_letter": 60,  # seconds
            "instructions": {
                "text": "I will give you a letter. Say as many words as you can that start with that letter. Do not use proper names or the same word with different endings.",
                "text_size": "24px",
                "voice_backup": True
            },
            "ui_adaptations": {
                "large_letter_display": "72px",
                "high_contrast": True,
                "timer_display": "large",
                "voice_prompts": True
            },
            "scoring": {
                "total_words": True,
                "clusters": True,
                "switches": True,
                "perseverations": True
            }
        }
        
        return test_result
    
    # NON-EDUCATED USER TESTS
    async def run_simple_naming_test(self, user_id: str) -> Dict[str, Any]:
        """Simple naming test for non-educated users"""
        test_result = {
            "test_name": "Simple Naming Test",
            "user_type": UserType.NON_EDUCATED.value,
            "session_id": str(uuid.uuid4()),
            "objects": [
                {
                    "name": obj,
                    "icon": self._get_simple_icon(obj),
                    "large_image": True
                }
                for obj in self.test_data["simple_objects"]
            ],
            "max_score": len(self.test_data["simple_objects"]),
            "instructions": {
                "audio": "I will show you pictures. Tell me what each thing is called.",
                "simple_language": True,
                "encouragement": "Good job! Let's try the next one."
            },
            "ui_adaptations": {
                "very_large_images": True,
                "simple_interface": True,
                "colorful_design": True,
                "large_buttons": True
            }
        }
        
        return test_result
    
    async def run_picture_description_simple(self, user_id: str) -> Dict[str, Any]:
        """Simplified picture description for non-educated users"""
        simple_scenes = [
            {
                "name": "family_dinner",
                "description": "A family sitting around a table eating dinner",
                "prompts": ["Who do you see?", "What are they doing?", "Where are they?"]
            },
            {
                "name": "park_scene",
                "description": "Children playing in a park",
                "prompts": ["What do you see?", "What are the children doing?", "Is it fun?"]
            }
        ]
        
        test_result = {
            "test_name": "Simple Picture Description",
            "user_type": UserType.NON_EDUCATED.value,
            "session_id": str(uuid.uuid4()),
            "scenes": simple_scenes,
            "instructions": {
                "audio": "Look at this picture. Tell me what you see.",
                "simple_language": True,
                "patient_tone": True
            },
            "ui_adaptations": {
                "bright_colorful_images": True,
                "simple_scenes": True,
                "large_interface": True,
                "encouraging_feedback": True
            }
        }
        
        return test_result
    
    async def run_story_telling_simple(self, user_id: str) -> Dict[str, Any]:
        """Simple story telling test for non-educated users"""
        story_prompts = [
            {
                "image": "happy_memory",
                "prompt": "Tell me about a happy time",
                "icon": "😊"
            },
            {
                "image": "family",
                "prompt": "Tell me about your family",
                "icon": "👨‍👩‍👧‍👦"
            }
        ]
        
        test_result = {
            "test_name": "Simple Story Telling",
            "user_type": UserType.NON_EDUCATED.value,
            "session_id": str(uuid.uuid4()),
            "prompts": story_prompts,
            "instructions": {
                "audio": "I will show you a picture. Tell me a story about it.",
                "simple_language": True,
                "encouraging": True
            },
            "ui_adaptations": {
                "large_friendly_icons": True,
                "warm_colors": True,
                "simple_layout": True
            }
        }
        
        return test_result
    
    # EDUCATED USER TESTS
    async def run_full_boston_diagnostic(self, user_id: str) -> Dict[str, Any]:
        """Full Boston Diagnostic Aphasia Examination for educated users"""
        test_result = {
            "test_name": "Boston Diagnostic Aphasia Examination",
            "user_type": UserType.EDUCATED.value,
            "session_id": str(uuid.uuid4()),
            "subtests": {
                "spontaneous_speech": {
                    "tasks": ["conversational_speech", "picture_description"],
                    "scoring": ["articulation", "phrase_length", "grammatical_form", "paraphasia"]
                },
                "auditory_comprehension": {
                    "tasks": ["word_discrimination", "commands", "complex_material"],
                    "scoring": ["word_recognition", "sequential_commands", "paragraph_comprehension"]
                },
                "naming": {
                    "tasks": ["responsive_naming", "boston_naming_test", "category_naming"],
                    "objects": self.test_data["boston_naming_objects"]
                },
                "repetition": {
                    "tasks": ["word_repetition", "sentence_repetition"],
                    "sentences": self.test_data["sentence_repetition"]
                },
                "reading": {
                    "tasks": ["word_reading", "sentence_reading", "paragraph_comprehension"]
                },
                "writing": {
                    "tasks": ["writing_to_dictation", "written_confrontation_naming"]
                }
            },
            "administration_time": "45-60 minutes",
            "scoring": "standardized_percentiles"
        }
        
        return test_result
    
    async def run_full_cookie_theft(self, user_id: str) -> Dict[str, Any]:
        """Full Cookie Theft description analysis for educated users"""
        test_result = {
            "test_name": "Cookie Theft Picture Description",
            "user_type": UserType.EDUCATED.value,
            "session_id": str(uuid.uuid4()),
            "image_url": self.test_data["cookie_theft_description"]["image_url"],
            "key_elements": self.test_data["cookie_theft_description"]["key_elements"],
            "instructions": {
                "text": "Look at this picture and tell me everything you see happening."
            },
            "analysis_measures": {
                "information_units": {
                    "main_concepts": 13,
                    "subordinate_concepts": 50
                },
                "efficiency_measures": {
                    "content_units_per_minute": True,
                    "words_per_minute": True
                },
                "linguistic_measures": {
                    "syntactic_complexity": True,
                    "lexical_diversity": True,
                    "semantic_fluency": True
                }
            },
            "scoring": "comprehensive_linguistic_analysis"
        }
        
        return test_result
    
    async def run_complex_sentence_repetition(self, user_id: str) -> Dict[str, Any]:
        """Complex sentence repetition for educated users"""
        complex_sentences = [
            "The lawyer's closing argument convinced him that his client was innocent.",
            "Despite the rain, the outdoor concert proceeded as scheduled.",
            "The committee postponed the meeting until next Wednesday afternoon."
        ]
        
        test_result = {
            "test_name": "Complex Sentence Repetition",
            "user_type": UserType.EDUCATED.value,
            "session_id": str(uuid.uuid4()),
            "sentences": complex_sentences,
            "instructions": {
                "text": "I will say some sentences. Listen carefully and repeat each sentence exactly as you heard it."
            },
            "scoring": {
                "exact_repetition": True,
                "semantic_accuracy": True,
                "syntactic_accuracy": True,
                "phonological_accuracy": True
            }
        }
        
        return test_result
    
    async def run_verbal_fluency_comprehensive(self, user_id: str) -> Dict[str, Any]:
        """Comprehensive verbal fluency test for educated users"""
        test_result = {
            "test_name": "Comprehensive Verbal Fluency",
            "user_type": UserType.EDUCATED.value,
            "session_id": str(uuid.uuid4()),
            "subtests": {
                "phonemic_fluency": {
                    "letters": ["F", "A", "S"],
                    "time_per_letter": 60,
                    "exclusions": ["proper_names", "same_word_different_endings"]
                },
                "semantic_fluency": {
                    "categories": ["animals", "fruits", "occupations"],
                    "time_per_category": 60
                },
                "alternating_fluency": {
                    "task": "alternate_between_fruits_and_furniture",
                    "time_limit": 60
                }
            },
            "analysis": {
                "clustering": True,
                "switching": True,
                "perseverations": True,
                "intrusions": True
            }
        }
        
        return test_result
    
    # Helper methods
    def _get_audio_descriptions(self, object_name: str) -> List[str]:
        """Generate audio descriptions for objects"""
        descriptions = {
            "cactus": ["A spiky plant that grows in the desert", "A green plant with thorns"],
            "harmonica": ["A small musical instrument you blow into", "A mouth organ with metal reeds"],
            "rhinoceros": ["A large gray animal with a horn on its nose", "A heavy animal found in Africa"]
        }
        return descriptions.get(object_name, [f"This is used to describe a {object_name}"])
    
    def _get_simple_icon(self, object_name: str) -> str:
        """Get simple emoji icons for objects"""
        icons = {
            "apple": "🍎",
            "car": "🚗",
            "house": "🏠",
            "dog": "🐕",
            "book": "📖",
            "chair": "🪑",
            "tree": "🌳",
            "ball": "⚽"
        }
        return icons.get(object_name, "📷")

# Global instance
speech_test_engine = SpeechTestEngine()