from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import random
from enum import Enum

class UserType(Enum):
    BLIND = "blind"
    WEAK_VISION = "weak_vision"
    NON_EDUCATED = "non_educated"
    EDUCATED = "educated"

class CognitiveTestEngine:
    """Comprehensive cognitive test engine for all user scenarios"""
    
    def __init__(self):
        self.test_data = self._initialize_test_data()
    
    def _initialize_test_data(self) -> Dict[str, Any]:
        """Initialize test data for different cognitive assessments"""
        return {
            "avlt_words": [
                "drum", "curtain", "bell", "coffee", "school", "parent", "moon", "garden",
                "hat", "farmer", "nose", "turkey", "color", "house", "river"
            ],
            "mmse_words": ["apple", "penny", "table"],
            "moca_words": ["face", "velvet", "church", "daisy", "red"],
            "simple_objects": [
                {"name": "apple", "category": "fruit"},
                {"name": "dog", "category": "animal"},
                {"name": "car", "category": "vehicle"},
                {"name": "house", "category": "building"},
                {"name": "book", "category": "object"}
            ],
            "patterns": {
                "colors": ["red", "blue", "green", "yellow"],
                "shapes": ["circle", "square", "triangle", "star"],
                "numbers": list(range(1, 26))
            }
        }
    
    # BLIND USER TESTS
    async def run_avlt_test(self, user_id: str, trial_number: int = 1) -> Dict[str, Any]:
        """Auditory Verbal Learning Test for blind users"""
        words = self.test_data["avlt_words"]
        
        test_result = {
            "test_name": "AVLT",
            "user_type": UserType.BLIND.value,
            "trial_number": trial_number,
            "words_presented": words,
            "presentation_time": datetime.utcnow().isoformat(),
            "max_score": len(words),
            "instructions": {
                "audio": "I will read you a list of 15 words. Listen carefully and try to remember them. After I finish, tell me as many words as you can remember in any order.",
                "voice_prompts": [
                    "Ready to begin? Here are the words:",
                    "Now please tell me all the words you can remember",
                    "Take your time, say any additional words you remember"
                ]
            }
        }
        
        return test_result
    
    async def run_digit_span_test(self, user_id: str, direction: str = "forward") -> Dict[str, Any]:
        """Digit Span Test for blind users"""
        # Generate digit sequences of increasing length
        sequences = []
        for length in range(3, 9):  # 3 to 8 digits
            sequence = [random.randint(0, 9) for _ in range(length)]
            sequences.append(sequence)
        
        test_result = {
            "test_name": "Digit Span",
            "user_type": UserType.BLIND.value,
            "direction": direction,
            "sequences": sequences,
            "max_score": len(sequences),
            "instructions": {
                "audio": f"I will say some numbers. Listen carefully and repeat them back to me in the {'same' if direction == 'forward' else 'reverse'} order.",
                "voice_prompts": [
                    "Listen to these numbers:",
                    "Now repeat them back to me",
                    "Let's try the next sequence"
                ]
            }
        }
        
        return test_result
    
    async def run_category_fluency_test(self, user_id: str, category: str = "animals") -> Dict[str, Any]:
        """Category Fluency Test for blind users"""
        test_result = {
            "test_name": "Category Fluency",
            "user_type": UserType.BLIND.value,
            "category": category,
            "time_limit": 60,  # seconds
            "instructions": {
                "audio": f"I want you to name as many {category} as you can think of. You have 60 seconds. Ready? Go!",
                "voice_prompts": [
                    f"Name as many {category} as possible",
                    "You have 30 seconds left",
                    "10 seconds remaining",
                    "Time's up!"
                ]
            }
        }
        
        return test_result
    
    # WEAK VISION USER TESTS
    async def run_mmse_test(self, user_id: str) -> Dict[str, Any]:
        """Mini-Mental State Examination for weak vision users"""
        test_result = {
            "test_name": "MMSE",
            "user_type": UserType.WEAK_VISION.value,
            "sections": {
                "orientation_time": {
                    "questions": [
                        "What year is it?",
                        "What season is it?",
                        "What month is it?",
                        "What date is it?",
                        "What day of the week is it?"
                    ],
                    "max_score": 5,
                    "display_format": "large_text"
                },
                "orientation_place": {
                    "questions": [
                        "What country are we in?",
                        "What state/province are we in?",
                        "What city are we in?",
                        "What building are we in?",
                        "What floor are we on?"
                    ],
                    "max_score": 5,
                    "display_format": "large_text"
                },
                "registration": {
                    "words": self.test_data["mmse_words"],
                    "max_score": 3,
                    "display_format": "large_text_with_audio"
                },
                "attention": {
                    "task": "serial_7s",
                    "instruction": "Count backwards from 100 by 7s",
                    "max_score": 5,
                    "display_format": "large_text"
                },
                "recall": {
                    "words": self.test_data["mmse_words"],
                    "max_score": 3,
                    "display_format": "large_text_with_audio"
                },
                "language": {
                    "tasks": [
                        {"type": "naming", "objects": ["watch", "pencil"]},
                        {"type": "repetition", "phrase": "No ifs, ands, or buts"},
                        {"type": "command", "instruction": "Take this paper, fold it in half, and put it on the floor"}
                    ],
                    "max_score": 8,
                    "display_format": "large_text_with_audio"
                }
            },
            "total_max_score": 30,
            "ui_adaptations": {
                "text_size": "48px",
                "contrast": "high",
                "voice_guidance": True
            }
        }
        
        return test_result
    
    async def run_moca_test(self, user_id: str) -> Dict[str, Any]:
        """Montreal Cognitive Assessment for weak vision users"""
        test_result = {
            "test_name": "MoCA",
            "user_type": UserType.WEAK_VISION.value,
            "sections": {
                "visuospatial": {
                    "tasks": [
                        {"type": "trail_making", "description": "Connect numbers and letters alternately"},
                        {"type": "cube_copy", "description": "Copy this cube"},
                        {"type": "clock_drawing", "time": "10 past 11"}
                    ],
                    "max_score": 5,
                    "display_format": "large_high_contrast"
                },
                "naming": {
                    "animals": ["lion", "rhinoceros", "camel"],
                    "max_score": 3,
                    "display_format": "large_images_with_audio"
                },
                "attention": {
                    "tasks": [
                        {"type": "digit_span", "direction": "forward"},
                        {"type": "digit_span", "direction": "backward"},
                        {"type": "vigilance", "target_letter": "A"}
                    ],
                    "max_score": 6,
                    "display_format": "large_text_with_audio"
                },
                "language": {
                    "tasks": [
                        {"type": "sentence_repetition", "sentences": ["I only know that John is the one to help today", "The cat always hid under the couch when dogs were in the room"]},
                        {"type": "verbal_fluency", "letter": "F", "time_limit": 60}
                    ],
                    "max_score": 3,
                    "display_format": "large_text_with_audio"
                },
                "abstraction": {
                    "pairs": [["train", "bicycle"], ["watch", "ruler"]],
                    "max_score": 2,
                    "display_format": "large_text"
                },
                "memory": {
                    "words": self.test_data["moca_words"],
                    "max_score": 5,
                    "display_format": "large_text_with_audio"
                },
                "orientation": {
                    "questions": [
                        "What is the date?", "What is the month?", "What is the year?",
                        "What is the day of the week?", "What is the place?", "What city are we in?"
                    ],
                    "max_score": 6,
                    "display_format": "large_text"
                }
            },
            "total_max_score": 30,
            "ui_adaptations": {
                "text_size": "48px",
                "contrast": "high",
                "voice_guidance": True,
                "large_buttons": True
            }
        }
        
        return test_result
    
    async def run_clock_drawing_test(self, user_id: str, time: str = "10 past 11") -> Dict[str, Any]:
        """Clock Drawing Test for weak vision users"""
        test_result = {
            "test_name": "Clock Drawing Test",
            "user_type": UserType.WEAK_VISION.value,
            "time_to_draw": time,
            "instructions": {
                "text": f"Please draw a clock face with the hands showing {time}",
                "display_format": "large_text",
                "voice_guidance": True
            },
            "scoring_criteria": {
                "contour": 2,
                "numbers": 4,
                "hands": 4
            },
            "max_score": 10,
            "ui_adaptations": {
                "canvas_size": "large",
                "high_contrast": True,
                "thick_pen": True
            }
        }
        
        return test_result
    
    # NON-EDUCATED USER TESTS
    async def run_simple_memory_test(self, user_id: str) -> Dict[str, Any]:
        """Simplified Memory Test for non-educated users"""
        simple_words = ["water", "food", "home", "family", "sun"]
        
        test_result = {
            "test_name": "Simple Memory Test",
            "user_type": UserType.NON_EDUCATED.value,
            "words": simple_words,
            "max_score": len(simple_words),
            "presentation": {
                "icons": True,
                "large_images": True,
                "voice_guidance": True,
                "simple_language": True
            },
            "instructions": {
                "audio": "I will show you some pictures. Try to remember them. Then I will ask you to tell me what you saw.",
                "visual_icons": [
                    {"word": "water", "icon": "💧"},
                    {"word": "food", "icon": "🍎"},
                    {"word": "home", "icon": "🏠"},
                    {"word": "family", "icon": "👨‍👩‍👧‍👦"},
                    {"word": "sun", "icon": "☀️"}
                ]
            }
        }
        
        return test_result
    
    async def run_pattern_recognition_game(self, user_id: str, level: int = 1) -> Dict[str, Any]:
        """Pattern Recognition Game for non-educated users"""
        patterns = {
            1: {"colors": ["red", "blue"], "sequence_length": 3},
            2: {"colors": ["red", "blue", "green"], "sequence_length": 4},
            3: {"colors": ["red", "blue", "green", "yellow"], "sequence_length": 5}
        }
        
        current_pattern = patterns[min(level, 3)]
        sequence = [random.choice(current_pattern["colors"]) for _ in range(current_pattern["sequence_length"])]
        
        test_result = {
            "test_name": "Pattern Recognition Game",
            "user_type": UserType.NON_EDUCATED.value,
            "level": level,
            "sequence": sequence,
            "colors_available": current_pattern["colors"],
            "max_score": current_pattern["sequence_length"],
            "presentation": {
                "large_colored_buttons": True,
                "simple_icons": True,
                "voice_guidance": True,
                "gamified": True
            },
            "instructions": {
                "audio": "Watch the colors light up. Then press the same colors in the same order.",
                "visual_cues": True,
                "demonstration": True
            }
        }
        
        return test_result
    
    async def run_object_recognition_test(self, user_id: str) -> Dict[str, Any]:
        """Object Recognition Test for non-educated users"""
        objects = self.test_data["simple_objects"]
        
        test_result = {
            "test_name": "Object Recognition Test",
            "user_type": UserType.NON_EDUCATED.value,
            "objects": objects,
            "max_score": len(objects),
            "presentation": {
                "large_clear_images": True,
                "simple_interface": True,
                "voice_guidance": True
            },
            "instructions": {
                "audio": "I will show you pictures of things. Tell me what each thing is.",
                "simple_language": True,
                "encouragement": True
            }
        }
        
        return test_result
    
    # EDUCATED USER TESTS
    async def run_full_mmse_test(self, user_id: str) -> Dict[str, Any]:
        """Full MMSE test for educated users"""
        # This is the complete, standard MMSE
        test_result = await self.run_mmse_test(user_id)
        test_result["user_type"] = UserType.EDUCATED.value
        test_result["test_name"] = "Full MMSE"
        
        # Add more complex sections for educated users
        test_result["sections"]["complex_attention"] = {
            "tasks": [
                {"type": "serial_7s", "instruction": "Count backwards from 100 by 7s"},
                {"type": "spell_world_backwards", "word": "WORLD"}
            ],
            "max_score": 5
        }
        
        test_result["sections"]["complex_language"] = {
            "tasks": [
                {"type": "reading", "sentence": "Close your eyes"},
                {"type": "writing", "instruction": "Write a complete sentence"},
                {"type": "copying", "shape": "intersecting pentagons"}
            ],
            "max_score": 3
        }
        
        return test_result
    
    async def run_full_moca_test(self, user_id: str) -> Dict[str, Any]:
        """Full MoCA test for educated users"""
        test_result = await self.run_moca_test(user_id)
        test_result["user_type"] = UserType.EDUCATED.value
        test_result["test_name"] = "Full MoCA"
        
        # Remove UI adaptations for educated users
        test_result["ui_adaptations"] = {
            "standard_interface": True,
            "detailed_instructions": True
        }
        
        return test_result
    
    async def run_trail_making_test(self, user_id: str, version: str = "A") -> Dict[str, Any]:
        """Trail Making Test for educated users"""
        if version == "A":
            sequence = list(range(1, 26))
            instruction = "Connect the numbers in order from 1 to 25"
        else:  # Version B
            sequence = [(i, chr(64 + i)) for i in range(1, 14)]  # 1-A, 2-B, etc.
            instruction = "Connect numbers and letters alternately: 1-A-2-B-3-C..."
        
        test_result = {
            "test_name": f"Trail Making Test {version}",
            "user_type": UserType.EDUCATED.value,
            "version": version,
            "sequence": sequence,
            "instruction": instruction,
            "scoring": {
                "time_limit": 300,  # 5 minutes
                "error_penalty": True
            }
        }
        
        return test_result
    
    async def run_stroop_test(self, user_id: str) -> Dict[str, Any]:
        """Stroop Test for educated users"""
        colors = ["red", "blue", "green", "yellow"]
        
        # Create congruent and incongruent trials
        congruent_trials = [{"word": color, "color": color} for color in colors] * 5
        incongruent_trials = [
            {"word": word, "color": color} 
            for word in colors for color in colors if word != color
        ][:20]
        
        test_result = {
            "test_name": "Stroop Test",
            "user_type": UserType.EDUCATED.value,
            "trials": {
                "congruent": congruent_trials,
                "incongruent": incongruent_trials
            },
            "instruction": "Name the color of the word, not what the word says",
            "scoring": {
                "measure_reaction_time": True,
                "calculate_interference": True
            }
        }
        
        return test_result

# Global instance
cognitive_test_engine = CognitiveTestEngine()