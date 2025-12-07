"""
Quality Evaluator
Evaluates output quality and tracks improvements over time.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class QualityEvaluator:
    """Evaluates and tracks quality of generated outputs."""
    
    def __init__(self, course_knowledge):
        """
        Initialize quality evaluator.
        
        Args:
            course_knowledge: CourseKnowledge instance for trend tracking
        """
        self.knowledge = course_knowledge
        logger.info("QualityEvaluator initialized")
    
    def evaluate_questions(self, questions: List[Dict], concept: str, course_type: str) -> Dict:
        """
        Evaluate question quality across multiple dimensions.
        
        Args:
            questions: List of generated questions
            concept: Concept being tested
            course_type: Course type
            
        Returns:
            Dictionary with quality scores and feedback
        """
        if not questions:
            return {
                'overall_score': 0.0,
                'dimensions': {},
                'feedback': 'No questions generated'
            }
        
        try:
            scores = {
                'relevance': self._score_relevance(questions, concept),
                'clarity': self._score_clarity(questions),
                'difficulty_alignment': self._score_difficulty_alignment(questions),
                'completeness': self._score_completeness(questions),
                'diversity': self._score_diversity(questions)
            }
            
            overall_score = sum(scores.values()) / len(scores)
            
            feedback = self._generate_feedback(scores, questions)
            
            return {
                'overall_score': round(overall_score, 2),
                'dimensions': scores,
                'feedback': feedback,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error evaluating questions: {e}")
            return {
                'overall_score': 50.0,
                'dimensions': {},
                'feedback': f'Evaluation error: {str(e)}'
            }
    
    def evaluate_analysis(self, analysis: Dict, activity_template: str) -> Dict:
        """
        Evaluate activity analysis quality.
        
        Args:
            analysis: Analysis results
            activity_template: Activity description
            
        Returns:
            Dictionary with quality scores
        """
        try:
            scores = {
                'depth': self._score_analysis_depth(analysis),
                'theme_quality': self._score_theme_quality(analysis),
                'concept_extraction': self._score_concept_extraction(analysis),
                'coverage': self._score_coverage(analysis),
                'actionability': self._score_actionability(analysis)
            }
            
            overall_score = sum(scores.values()) / len(scores)
            
            feedback = self._generate_analysis_feedback(scores, analysis)
            
            return {
                'overall_score': round(overall_score, 2),
                'dimensions': scores,
                'feedback': feedback,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error evaluating analysis: {e}")
            return {
                'overall_score': 50.0,
                'dimensions': {},
                'feedback': f'Evaluation error: {str(e)}'
            }
    
    def compare_with_past(self, quality_scores: Dict, course_type: str) -> Dict:
        """
        Compare current quality with past performance.
        
        Args:
            quality_scores: Current quality scores
            course_type: Course type
            
        Returns:
            Comparison dictionary
        """
        try:
            trends = self.knowledge.get_quality_trends(course_type)
            current_score = quality_scores.get('overall_score', 0)
            
            comparison = {
                'current_score': current_score,
                'average_score': trends.get('avg_score', 0),
                'recent_average': trends.get('recent_avg', 0),
                'trend': trends.get('trend', 'no_data'),
                'improvement': current_score - trends.get('recent_avg', current_score),
                'is_improving': current_score > trends.get('recent_avg', current_score)
            }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing with past: {e}")
            return {
                'current_score': quality_scores.get('overall_score', 0),
                'trend': 'unknown'
            }
    
    def _score_relevance(self, questions: List[Dict], concept: str) -> float:
        """Score how relevant questions are to the concept."""
        if not questions:
            return 0.0
        
        # Check if concept appears in questions
        concept_lower = concept.lower()
        relevant_count = sum(1 for q in questions 
                           if concept_lower in str(q.get('question', '')).lower() or
                              concept_lower in str(q.get('concept', '')).lower())
        
        return min(100, (relevant_count / len(questions)) * 100)
    
    def _score_clarity(self, questions: List[Dict]) -> float:
        """Score question clarity."""
        if not questions:
            return 0.0
        
        # Simple heuristic: longer questions (but not too long) are clearer
        avg_length = sum(len(str(q.get('question', ''))) for q in questions) / len(questions)
        
        # Optimal length: 50-200 characters
        if 50 <= avg_length <= 200:
            return 90.0
        elif 30 <= avg_length < 50 or 200 < avg_length <= 300:
            return 70.0
        else:
            return 50.0
    
    def _score_difficulty_alignment(self, questions: List[Dict]) -> float:
        """Score if difficulty levels are appropriate."""
        if not questions:
            return 0.0
        
        # Check if questions have difficulty specified
        has_difficulty = sum(1 for q in questions if q.get('difficulty'))
        return min(100, (has_difficulty / len(questions)) * 100)
    
    def _score_completeness(self, questions: List[Dict]) -> float:
        """Score if questions have all required fields."""
        if not questions:
            return 0.0
        
        required_fields = ['question', 'concept']
        complete_count = sum(1 for q in questions 
                           if all(field in q and q[field] for field in required_fields))
        
        return min(100, (complete_count / len(questions)) * 100)
    
    def _score_diversity(self, questions: List[Dict]) -> float:
        """Score question type diversity."""
        if not questions:
            return 0.0
        
        types = set(q.get('type', 'unknown') for q in questions)
        # More diverse types = better
        diversity_score = min(100, len(types) * 25)
        return diversity_score
    
    def _score_analysis_depth(self, analysis: Dict) -> float:
        """Score analysis depth."""
        q1_count = analysis.get('q1_analysis', {}).get('total_analyzed', 0)
        q2_count = analysis.get('q2_analysis', {}).get('total_analyzed', 0)
        q3_count = analysis.get('q3_analysis', {}).get('total_analyzed', 0)
        
        # Depth based on number of responses analyzed
        total = q1_count + q2_count + q3_count
        if total > 50:
            return 90.0
        elif total > 20:
            return 70.0
        elif total > 10:
            return 50.0
        else:
            return 30.0
    
    def _score_theme_quality(self, analysis: Dict) -> float:
        """Score theme quality."""
        q2_themes = len(analysis.get('q2_analysis', {}).get('themes', {}))
        q3_content = len(analysis.get('q3_analysis', {}).get('themes_discovered', {}).get('content', {}))
        q3_pedagogy = len(analysis.get('q3_analysis', {}).get('themes_discovered', {}).get('pedagogy', {}))
        
        total_themes = q2_themes + q3_content + q3_pedagogy
        # Good analysis has 3-10 themes
        if 3 <= total_themes <= 10:
            return 90.0
        elif total_themes > 10:
            return 70.0  # Too many themes
        else:
            return 50.0  # Too few themes
    
    def _score_concept_extraction(self, analysis: Dict) -> float:
        """Score concept keyword extraction quality."""
        concepts = analysis.get('q1_analysis', {}).get('concept_keywords', [])
        
        if len(concepts) >= 5:
            return 90.0
        elif len(concepts) >= 3:
            return 70.0
        else:
            return 50.0
    
    def _score_coverage(self, analysis: Dict) -> float:
        """Score how well analysis covers all students."""
        q1_count = analysis.get('q1_analysis', {}).get('total_analyzed', 0)
        q2_count = analysis.get('q2_analysis', {}).get('total_analyzed', 0)
        q3_count = analysis.get('q3_analysis', {}).get('total_analyzed', 0)
        
        # Coverage is good if all questions have responses
        coverage = sum(1 for count in [q1_count, q2_count, q3_count] if count > 0) / 3
        return coverage * 100
    
    def _score_actionability(self, analysis: Dict) -> float:
        """Score how actionable insights are for teachers."""
        # Check if analysis has actionable elements
        has_categorization = bool(analysis.get('q1_analysis', {}).get('cognitive_categorization'))
        has_themes = bool(analysis.get('q2_analysis', {}).get('themes'))
        has_affective = bool(analysis.get('q3_analysis', {}).get('affective_categorization'))
        
        actionable_count = sum([has_categorization, has_themes, has_affective])
        return (actionable_count / 3) * 100
    
    def _generate_feedback(self, scores: Dict, questions: List[Dict]) -> str:
        """Generate feedback based on scores."""
        feedback_parts = []
        
        if scores['relevance'] < 70:
            feedback_parts.append("Questions could be more relevant to the concept")
        if scores['clarity'] < 70:
            feedback_parts.append("Questions could be clearer")
        if scores['diversity'] < 50:
            feedback_parts.append("Add more question type diversity")
        
        if not feedback_parts:
            return "Questions meet quality standards"
        
        return "; ".join(feedback_parts)
    
    def _generate_analysis_feedback(self, scores: Dict, analysis: Dict) -> str:
        """Generate feedback for analysis."""
        feedback_parts = []
        
        if scores['depth'] < 70:
            feedback_parts.append("Analysis could be deeper")
        if scores['theme_quality'] < 70:
            feedback_parts.append("Themes could be more meaningful")
        if scores['actionability'] < 70:
            feedback_parts.append("Insights could be more actionable")
        
        if not feedback_parts:
            return "Analysis meets quality standards"
        
        return "; ".join(feedback_parts)

