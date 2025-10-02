"""
Clinical accuracy enhancements for dementia detection system
Includes normative data, age/education adjustments, and error pattern analysis
"""

import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, date
import json

class ClinicalNorms:
    """
    Clinical normative data for cognitive tests with age and education adjustments
    Based on published research and clinical guidelines
    """
    
    def __init__(self):
        # MMSE Normative Data (Folstein et al., 1975; Crum et al., 1993)
        self.mmse_norms = {
            "by_age_education": {
                # Format: age_group: {education_level: {mean: X, std: Y, cutoff: Z}}
                "18-24": {
                    "grade_0-4": {"mean": 22.8, "std": 3.9, "cutoff": 17},
                    "grade_5-8": {"mean": 25.3, "std": 3.3, "cutoff": 20},
                    "grade_9-12": {"mean": 27.2, "std": 2.7, "cutoff": 23},
                    "college": {"mean": 28.5, "std": 1.8, "cutoff": 26}
                },
                "25-29": {
                    "grade_0-4": {"mean": 22.1, "std": 4.1, "cutoff": 16},
                    "grade_5-8": {"mean": 24.9, "std": 3.4, "cutoff": 19},
                    "grade_9-12": {"mean": 27.0, "std": 2.8, "cutoff": 22},
                    "college": {"mean": 28.3, "std": 1.9, "cutoff": 25}
                },
                "30-39": {
                    "grade_0-4": {"mean": 21.9, "std": 4.2, "cutoff": 15},
                    "grade_5-8": {"mean": 24.7, "std": 3.5, "cutoff": 19},
                    "grade_9-12": {"mean": 26.8, "std": 2.9, "cutoff": 22},
                    "college": {"mean": 28.1, "std": 2.0, "cutoff": 25}
                },
                "40-49": {
                    "grade_0-4": {"mean": 21.7, "std": 4.3, "cutoff": 15},
                    "grade_5-8": {"mean": 24.5, "std": 3.6, "cutoff": 18},
                    "grade_9-12": {"mean": 26.6, "std": 3.0, "cutoff": 21},
                    "college": {"mean": 27.9, "std": 2.1, "cutoff": 24}
                },
                "50-59": {
                    "grade_0-4": {"mean": 21.5, "std": 4.4, "cutoff": 14},
                    "grade_5-8": {"mean": 24.3, "std": 3.7, "cutoff": 18},
                    "grade_9-12": {"mean": 26.4, "std": 3.1, "cutoff": 21},
                    "college": {"mean": 27.7, "std": 2.2, "cutoff": 24}
                },
                "60-69": {
                    "grade_0-4": {"mean": 21.3, "std": 4.5, "cutoff": 14},
                    "grade_5-8": {"mean": 24.1, "std": 3.8, "cutoff": 17},
                    "grade_9-12": {"mean": 26.2, "std": 3.2, "cutoff": 20},
                    "college": {"mean": 27.5, "std": 2.3, "cutoff": 23}
                },
                "70-79": {
                    "grade_0-4": {"mean": 21.1, "std": 4.6, "cutoff": 13},
                    "grade_5-8": {"mean": 23.9, "std": 3.9, "cutoff": 17},
                    "grade_9-12": {"mean": 26.0, "std": 3.3, "cutoff": 20},
                    "college": {"mean": 27.3, "std": 2.4, "cutoff": 23}
                },
                "80+": {
                    "grade_0-4": {"mean": 20.9, "std": 4.7, "cutoff": 12},
                    "grade_5-8": {"mean": 23.7, "std": 4.0, "cutoff": 16},
                    "grade_9-12": {"mean": 25.8, "std": 3.4, "cutoff": 19},
                    "college": {"mean": 27.1, "std": 2.5, "cutoff": 22}
                }
            }
        }
        
        # MoCA Normative Data (Nasreddine et al., 2005)
        self.moca_norms = {
            "by_age_education": {
                "18-65": {
                    "grade_0-12": {"mean": 25.9, "std": 3.1, "cutoff": 22},
                    "college": {"mean": 27.4, "std": 2.1, "cutoff": 26}
                },
                "66-75": {
                    "grade_0-12": {"mean": 25.1, "std": 3.3, "cutoff": 21},
                    "college": {"mean": 26.8, "std": 2.3, "cutoff": 25}
                },
                "76+": {
                    "grade_0-12": {"mean": 24.3, "std": 3.5, "cutoff": 20},
                    "college": {"mean": 26.2, "std": 2.5, "cutoff": 24}
                }
            },
            "education_adjustment": 1  # Add 1 point if ≤12 years education
        }
        
        # Digit Span Normative Data (Wechsler, 1997)
        self.digit_span_norms = {
            "forward": {
                "16-17": {"mean": 6.0, "std": 1.2},
                "18-19": {"mean": 6.2, "std": 1.1}, 
                "20-24": {"mean": 6.4, "std": 1.0},
                "25-29": {"mean": 6.3, "std": 1.1},
                "30-34": {"mean": 6.2, "std": 1.1},
                "35-44": {"mean": 6.1, "std": 1.2},
                "45-54": {"mean": 6.0, "std": 1.2},
                "55-64": {"mean": 5.8, "std": 1.3},
                "65-69": {"mean": 5.7, "std": 1.3},
                "70-74": {"mean": 5.5, "std": 1.4},
                "75-79": {"mean": 5.3, "std": 1.4},
                "80-84": {"mean": 5.1, "std": 1.5},
                "85-89": {"mean": 4.9, "std": 1.5}
            },
            "backward": {
                "16-17": {"mean": 4.5, "std": 1.2},
                "18-19": {"mean": 4.7, "std": 1.1},
                "20-24": {"mean": 4.9, "std": 1.0},
                "25-29": {"mean": 4.8, "std": 1.1},
                "30-34": {"mean": 4.7, "std": 1.1},
                "35-44": {"mean": 4.6, "std": 1.2},
                "45-54": {"mean": 4.5, "std": 1.2},
                "55-64": {"mean": 4.3, "std": 1.3},
                "65-69": {"mean": 4.2, "std": 1.3},
                "70-74": {"mean": 4.0, "std": 1.4},
                "75-79": {"mean": 3.8, "std": 1.4},
                "80-84": {"mean": 3.6, "std": 1.5},
                "85-89": {"mean": 3.4, "std": 1.5}
            }
        }
        
        # Semantic Fluency Normative Data (Animals - Benton & Hamsher, 1989)
        self.semantic_fluency_norms = {
            "animals": {
                "20-39": {"mean": 22.0, "std": 6.0, "cutoff": 12},
                "40-49": {"mean": 20.0, "std": 6.0, "cutoff": 11},
                "50-59": {"mean": 19.0, "std": 5.5, "cutoff": 10},
                "60-69": {"mean": 17.0, "std": 5.0, "cutoff": 9},
                "70-79": {"mean": 15.0, "std": 4.5, "cutoff": 8},
                "80+": {"mean": 13.0, "std": 4.0, "cutoff": 7}
            }
        }

    def get_age_group(self, age: int) -> str:
        """Get appropriate age group for normative lookup"""
        if age < 25:
            return "18-24"
        elif age < 30:
            return "25-29"
        elif age < 40:
            return "30-39"
        elif age < 50:
            return "40-49"
        elif age < 60:
            return "50-59"
        elif age < 70:
            return "60-69"
        elif age < 80:
            return "70-79"
        else:
            return "80+"
    
    def get_education_group(self, education_level: str) -> str:
        """Map education level to normative group"""
        education_map = {
            'non_educated': 'grade_0-4',
            'primary': 'grade_5-8',
            'secondary': 'grade_9-12',
            'graduate': 'college',
            'postgraduate': 'college'
        }
        return education_map.get(education_level, 'grade_9-12')

class ClinicalScoring:
    """
    Enhanced clinical scoring with normative comparisons and accuracy improvements
    """
    
    def __init__(self):
        self.norms = ClinicalNorms()
    
    def score_mmse_with_norms(self, raw_score: float, age: int, education_level: str) -> Dict[str, Any]:
        """
        Score MMSE with normative data and clinical interpretation
        """
        age_group = self.norms.get_age_group(age)
        edu_group = self.norms.get_education_group(education_level)
        
        # Get normative data
        try:
            norm_data = self.norms.mmse_norms["by_age_education"][age_group][edu_group]
            expected_mean = norm_data["mean"]
            expected_std = norm_data["std"]
            clinical_cutoff = norm_data["cutoff"]
        except KeyError:
            # Default to most conservative norms if specific group not found
            expected_mean = 24.0
            expected_std = 3.0
            clinical_cutoff = 20
        
        # Calculate z-score and percentile
        z_score = (raw_score - expected_mean) / expected_std
        percentile = self.calculate_percentile(z_score)
        
        # Clinical interpretation
        if raw_score >= expected_mean - (0.5 * expected_std):
            interpretation = "normal"
            risk_level = "low"
        elif raw_score >= clinical_cutoff:
            interpretation = "borderline"
            risk_level = "mild"
        elif raw_score >= clinical_cutoff - 5:
            interpretation = "mild_impairment"
            risk_level = "moderate"
        else:
            interpretation = "significant_impairment"
            risk_level = "high"
        
        return {
            "raw_score": raw_score,
            "max_score": 30,
            "percentage": (raw_score / 30) * 100,
            "z_score": z_score,
            "percentile": percentile,
            "expected_mean": expected_mean,
            "clinical_cutoff": clinical_cutoff,
            "interpretation": interpretation,
            "risk_level": risk_level,
            "normative_comparison": f"Score is {abs(z_score):.1f} standard deviations {'above' if z_score > 0 else 'below'} age/education expected mean",
            "clinical_significance": self.get_mmse_clinical_significance(raw_score, risk_level)
        }
    
    def score_moca_with_norms(self, raw_score: float, age: int, education_level: str) -> Dict[str, Any]:
        """
        Score MoCA with normative data and education adjustment
        """
        # Apply education adjustment
        adjusted_score = raw_score
        if education_level in ['non_educated', 'primary']:
            adjusted_score += self.norms.moca_norms["education_adjustment"]
            adjusted_score = min(adjusted_score, 30)  # Cap at maximum
        
        # Determine age group for MoCA
        if age < 66:
            age_group = "18-65"
        elif age < 76:
            age_group = "66-75"
        else:
            age_group = "76+"
        
        # Determine education group for MoCA
        edu_group = "college" if education_level in ['graduate', 'postgraduate'] else "grade_0-12"
        
        # Get normative data
        norm_data = self.norms.moca_norms["by_age_education"][age_group][edu_group]
        expected_mean = norm_data["mean"]
        expected_std = norm_data["std"]
        clinical_cutoff = norm_data["cutoff"]
        
        # Calculate z-score
        z_score = (adjusted_score - expected_mean) / expected_std
        percentile = self.calculate_percentile(z_score)
        
        # Clinical interpretation (MoCA is more sensitive than MMSE)
        if adjusted_score >= 26:
            interpretation = "normal"
            risk_level = "low"
        elif adjusted_score >= 22:
            interpretation = "mild_cognitive_impairment"
            risk_level = "mild"
        elif adjusted_score >= 17:
            interpretation = "moderate_impairment"
            risk_level = "moderate"
        else:
            interpretation = "severe_impairment"
            risk_level = "high"
        
        return {
            "raw_score": raw_score,
            "adjusted_score": adjusted_score,
            "education_adjustment": adjusted_score - raw_score,
            "max_score": 30,
            "z_score": z_score,
            "percentile": percentile,
            "expected_mean": expected_mean,
            "clinical_cutoff": clinical_cutoff,
            "interpretation": interpretation,
            "risk_level": risk_level,
            "clinical_significance": self.get_moca_clinical_significance(adjusted_score, risk_level)
        }
    
    def analyze_error_patterns(self, test_responses: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze error patterns to identify specific cognitive deficits
        """
        error_patterns = {
            "memory_errors": [],
            "attention_errors": [],
            "language_errors": [],
            "visuospatial_errors": [],
            "executive_errors": [],
            "overall_pattern": ""
        }
        
        # Analyze MMSE error patterns
        if "mmse_sections" in test_responses:
            mmse_sections = test_responses["mmse_sections"]
            
            # Memory pattern analysis
            registration_score = mmse_sections.get("registration", {}).get("score", 3)
            recall_score = mmse_sections.get("delayed_recall", {}).get("score", 3)
            
            if registration_score < 3:
                error_patterns["memory_errors"].append("Immediate memory registration deficit")
            if recall_score < 2:
                error_patterns["memory_errors"].append("Delayed recall impairment")
            if recall_score < registration_score:
                error_patterns["memory_errors"].append("Memory consolidation deficit")
            
            # Attention pattern analysis
            attention_score = mmse_sections.get("attention_calculation", {}).get("score", 5)
            if attention_score < 3:
                error_patterns["attention_errors"].append("Sustained attention impairment")
            if attention_score < 2:
                error_patterns["attention_errors"].append("Working memory deficit")
            
            # Language pattern analysis
            naming_score = mmse_sections.get("language_naming", {}).get("score", 2)
            repetition_score = mmse_sections.get("language_repetition", {}).get("score", 1)
            
            if naming_score < 2:
                error_patterns["language_errors"].append("Object naming difficulty")
            if repetition_score < 1:
                error_patterns["language_errors"].append("Complex phrase repetition deficit")
            
            # Orientation pattern analysis
            time_orientation = mmse_sections.get("orientation_time", {}).get("score", 5)
            place_orientation = mmse_sections.get("orientation_place", {}).get("score", 5)
            
            if time_orientation < 4:
                error_patterns["attention_errors"].append("Temporal orientation impairment")
            if place_orientation < 4:
                error_patterns["attention_errors"].append("Spatial orientation impairment")
        
        # Determine overall cognitive pattern
        total_errors = sum(len(errors) for errors in error_patterns.values() if isinstance(errors, list))
        
        if total_errors == 0:
            error_patterns["overall_pattern"] = "No significant error patterns detected"
        elif len(error_patterns["memory_errors"]) >= 2:
            error_patterns["overall_pattern"] = "Memory-predominant pattern (suggestive of Alzheimer's type)"
        elif len(error_patterns["attention_errors"]) >= 2:
            error_patterns["overall_pattern"] = "Attention/Executive pattern (suggestive of vascular or mixed etiology)"
        elif len(error_patterns["language_errors"]) >= 1:
            error_patterns["overall_pattern"] = "Language-predominant pattern (requires aphasia evaluation)"
        else:
            error_patterns["overall_pattern"] = "Mixed cognitive pattern (requires comprehensive assessment)"
        
        return error_patterns
    
    def calculate_composite_score(self, test_scores: Dict[str, float], weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Calculate weighted composite cognitive score
        """
        if weights is None:
            # Default weights based on dementia diagnostic importance
            weights = {
                "mmse": 0.25,
                "moca": 0.25,
                "memory_tests": 0.30,  # AVLT, etc.
                "attention_tests": 0.10,  # Digit span, etc.
                "language_tests": 0.10   # Fluency, etc.
            }
        
        weighted_scores = []
        total_weight = 0
        
        for test_name, score in test_scores.items():
            if test_name in weights:
                weighted_scores.append(score * weights[test_name])
                total_weight += weights[test_name]
        
        if total_weight > 0:
            composite_score = sum(weighted_scores) / total_weight
        else:
            composite_score = np.mean(list(test_scores.values())) if test_scores else 0
        
        # Convert to risk categories
        if composite_score >= 85:
            risk_category = "low"
        elif composite_score >= 70:
            risk_category = "mild"
        elif composite_score >= 50:
            risk_category = "moderate"
        else:
            risk_category = "high"
        
        return {
            "composite_score": composite_score,
            "risk_category": risk_category,
            "individual_scores": test_scores,
            "weights_used": weights,
            "clinical_interpretation": self.get_composite_interpretation(composite_score, risk_category)
        }
    
    def calculate_percentile(self, z_score: float) -> float:
        """
        Convert z-score to percentile using normal distribution approximation
        """
        # Simple approximation of cumulative normal distribution
        if z_score < -3:
            return 0.1
        elif z_score > 3:
            return 99.9
        else:
            # Approximation formula
            percentile = 50 + 34.13 * z_score - 2.78 * (z_score ** 2) + 0.74 * (z_score ** 3)
            return max(0.1, min(99.9, percentile))
    
    def get_mmse_clinical_significance(self, score: float, risk_level: str) -> str:
        """
        Get clinical significance interpretation for MMSE scores
        """
        interpretations = {
            "low": "Score within normal limits for age and education. Continue routine monitoring.",
            "mild": "Borderline performance. Consider follow-up in 6-12 months or additional testing if clinical concerns.",
            "moderate": "Score suggests mild cognitive impairment. Recommend comprehensive neuropsychological evaluation.",
            "high": "Score indicates significant impairment. Urgent referral for medical evaluation recommended."
        }
        return interpretations.get(risk_level, "Score requires clinical interpretation.")
    
    def get_moca_clinical_significance(self, score: float, risk_level: str) -> str:
        """
        Get clinical significance interpretation for MoCA scores
        """
        interpretations = {
            "low": "Score within normal limits. MoCA shows good cognitive function across domains.",
            "mild": "Score suggests possible mild cognitive impairment. Consider detailed assessment of specific domains.",
            "moderate": "Score indicates moderate cognitive impairment. Comprehensive evaluation and medical consultation recommended.",
            "high": "Score suggests significant impairment across multiple domains. Immediate medical evaluation warranted."
        }
        return interpretations.get(risk_level, "Score requires clinical interpretation.")
    
    def get_composite_interpretation(self, score: float, risk_category: str) -> str:
        """
        Get clinical interpretation for composite cognitive scores
        """
        interpretations = {
            "low": f"Composite cognitive score ({score:.1f}) indicates preserved cognitive function across tested domains.",
            "mild": f"Composite cognitive score ({score:.1f}) suggests mild cognitive changes. Monitor closely and consider lifestyle interventions.",
            "moderate": f"Composite cognitive score ({score:.1f}) indicates moderate cognitive impairment. Medical evaluation recommended.",
            "high": f"Composite cognitive score ({score:.1f}) suggests significant cognitive decline. Immediate comprehensive assessment needed."
        }
        return interpretations.get(risk_category, f"Composite score of {score:.1f} requires professional interpretation.")