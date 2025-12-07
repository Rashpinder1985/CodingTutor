"""
Reasoning Agent Module
Self-reflection and adaptive learning capabilities for improving question generation and analysis.
"""

import logging
from typing import Dict, List, Optional, Tuple
import json
from src.llm_generator import parse_json_response

logger = logging.getLogger(__name__)


class ReasoningAgent:
    """Agent that reflects on its outputs and learns to improve."""
    
    def __init__(self, llm_generator):
        """
        Initialize the reasoning agent.
        
        Args:
            llm_generator: LLMGenerator instance for reflection calls
        """
        self.llm = llm_generator
        logger.info("ReasoningAgent initialized")
    
    def reflect_on_questions(self, questions: List[Dict], concept: str, course_type: str, 
                           course_category: str = None, language: str = None) -> Dict:
        """
        Reflect on generated questions and evaluate their quality.
        
        Args:
            questions: List of generated questions
            concept: Concept being tested
            course_type: 'programming' or 'non-programming'
            course_category: Additional course category info
            language: Programming language (if applicable)
            
        Returns:
            Dictionary with reflection insights and improvement suggestions
        """
        if not questions:
            return {
                'quality_score': 0.0,
                'strengths': [],
                'weaknesses': [],
                'improvements': [],
                'learnings': {}
            }
        
        try:
            # Prepare questions summary for reflection
            questions_summary = []
            for i, q in enumerate(questions[:5], 1):  # Analyze first 5 questions
                q_type = q.get('type', 'unknown')
                difficulty = q.get('difficulty', 'unknown')
                question_text = q.get('question', '')[:200]  # Truncate for prompt
                questions_summary.append(f"{i}. Type: {q_type}, Difficulty: {difficulty}, Question: {question_text}")
            
            prompt = f"""You are an expert educational evaluator. Analyze the quality of these generated questions.

Context:
- Concept: {concept}
- Course Type: {course_type}
- Course Category: {course_category or 'general'}
- Language: {language or 'N/A'}

Generated Questions:
{chr(10).join(questions_summary)}

Evaluate these questions on:
1. **Relevance**: Do they test the concept effectively?
2. **Clarity**: Are they clear and unambiguous?
3. **Difficulty Alignment**: Do they match their stated difficulty level?
4. **Educational Value**: Will they help students learn?
5. **Course Appropriateness**: Are they suitable for this course type?

Return JSON format:
{{
    "quality_score": 0.0-100.0,
    "strengths": ["strength1", "strength2"],
    "weaknesses": ["weakness1", "weakness2"],
    "improvements": ["specific improvement suggestion 1", "suggestion 2"],
    "learnings": {{
        "effective_question_types": ["type1", "type2"],
        "optimal_difficulty_approach": "description",
        "course_specific_insights": "insights for this course type"
    }}
}}"""

            system_message = "You are an expert at evaluating educational content quality and providing actionable improvement suggestions."
            
            response = self.llm.generate_content(prompt, system_message, temperature=0.3)
            
            # Parse reflection
            reflection = parse_json_response(response, logger)
            
            if reflection:
                logger.info(f"Reflection on {concept}: Quality score = {reflection.get('quality_score', 0)}")
                return reflection
            else:
                # Fallback: basic evaluation
                return self._basic_question_evaluation(questions, concept, course_type)
                
        except Exception as e:
            logger.error(f"Error in question reflection: {e}")
            return self._basic_question_evaluation(questions, concept, course_type)
    
    def reflect_on_analysis(self, analysis_results: Dict, activity_template: str, 
                          course_type: str = 'non-programming') -> Dict:
        """
        Reflect on activity analysis quality and depth.
        
        Args:
            analysis_results: Results from activity analysis
            activity_template: Activity description
            course_type: Course type
            
        Returns:
            Dictionary with reflection insights
        """
        try:
            # Extract key metrics from analysis
            q1_count = analysis_results.get('q1_analysis', {}).get('total_analyzed', 0)
            q2_count = analysis_results.get('q2_analysis', {}).get('total_analyzed', 0)
            q3_count = analysis_results.get('q3_analysis', {}).get('total_analyzed', 0)
            
            q1_themes = len(analysis_results.get('q1_analysis', {}).get('concept_keywords', []))
            q2_themes = len(analysis_results.get('q2_analysis', {}).get('themes', {}))
            q3_content_themes = len(analysis_results.get('q3_analysis', {}).get('themes_discovered', {}).get('content', {}))
            q3_pedagogy_themes = len(analysis_results.get('q3_analysis', {}).get('themes_discovered', {}).get('pedagogy', {}))
            
            prompt = f"""You are an expert educational researcher. Evaluate the quality and depth of this activity analysis.

Context:
- Course Type: {course_type}
- Activity: {activity_template[:500]}...

Analysis Metrics:
- Q1 (Learning): {q1_count} responses analyzed, {q1_themes} concept keywords identified
- Q2 (Questions): {q2_count} questions analyzed, {q2_themes} concept-based themes
- Q3 (Interest): {q3_count} responses analyzed, {q3_content_themes} content themes, {q3_pedagogy_themes} pedagogy themes

Evaluate:
1. **Analysis Depth**: Are themes meaningful and well-categorized?
2. **Concept Extraction**: Are concept keywords domain-specific and relevant?
3. **Theme Quality**: Are themes clear and actionable for teachers?
4. **Coverage**: Does analysis capture student diversity?
5. **Insights Value**: Will this help teachers improve instruction?

Return JSON format:
{{
    "quality_score": 0.0-100.0,
    "strengths": ["strength1", "strength2"],
    "weaknesses": ["weakness1", "weakness2"],
    "improvements": ["improvement1", "improvement2"],
    "learnings": {{
        "effective_theme_categories": ["category1", "category2"],
        "optimal_analysis_approach": "description",
        "course_specific_patterns": "patterns for this course type"
    }}
}}"""

            system_message = "You are an expert at evaluating qualitative educational research and analysis quality."
            
            response = self.llm.generate_content(prompt, system_message, temperature=0.3)
            
            reflection = parse_json_response(response, logger)
            
            if reflection:
                logger.info(f"Analysis reflection: Quality score = {reflection.get('quality_score', 0)}")
                return reflection
            else:
                return self._basic_analysis_evaluation(analysis_results)
                
        except Exception as e:
            logger.error(f"Error in analysis reflection: {e}")
            return self._basic_analysis_evaluation(analysis_results)
    
    def identify_improvements(self, reflection: Dict) -> List[str]:
        """
        Extract actionable improvement suggestions from reflection.
        
        Args:
            reflection: Reflection dictionary
            
        Returns:
            List of improvement suggestions
        """
        improvements = reflection.get('improvements', [])
        weaknesses = reflection.get('weaknesses', [])
        
        # Combine and prioritize
        all_suggestions = improvements + [f"Address: {w}" for w in weaknesses]
        return all_suggestions[:5]  # Top 5 improvements
    
    def _basic_question_evaluation(self, questions: List[Dict], concept: str, course_type: str) -> Dict:
        """Basic fallback evaluation when LLM reflection fails."""
        return {
            'quality_score': 70.0,  # Default moderate score
            'strengths': ['Questions generated successfully'],
            'weaknesses': ['Unable to perform detailed reflection'],
            'improvements': ['Enable detailed reflection for better quality assessment'],
            'learnings': {}
        }
    
    def _basic_analysis_evaluation(self, analysis_results: Dict) -> Dict:
        """Basic fallback evaluation when LLM reflection fails."""
        return {
            'quality_score': 70.0,
            'strengths': ['Analysis completed successfully'],
            'weaknesses': ['Unable to perform detailed reflection'],
            'improvements': ['Enable detailed reflection for better quality assessment'],
            'learnings': {}
        }

