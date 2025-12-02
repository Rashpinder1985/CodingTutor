"""
Activity Analyzer
Analyzes ALL student responses using keyword extraction, thematic clustering, and LLM quality scoring.
"""

import logging
import json
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class ActivityAnalyzer:
    """Analyzes student activity responses using combined NLP and LLM approaches."""
    
    def __init__(self, config: Dict, llm_generator):
        """
        Initialize the analyzer.
        
        Args:
            config: Configuration dictionary
            llm_generator: LLMGenerator instance
        """
        self.config = config
        self.llm = llm_generator
        self.activity_config = config.get('activity_analysis', {})
        
        # Initialize keyword extractor and thematic analyzer
        from src.keyword_extractor import KeywordExtractor
        from src.thematic_analyzer import ThematicAnalyzer
        
        keyword_config = self.activity_config.get('keyword_extraction', {})
        self.keyword_extractor = KeywordExtractor(
            max_keywords=keyword_config.get('max_keywords', 50),
            use_bigrams=keyword_config.get('use_bigrams', True)
        )
        
        theme_config = self.activity_config.get('thematic_clustering', {})
        self.thematic_analyzer = ThematicAnalyzer(
            n_themes=theme_config.get('n_themes', 5)
        )
        
        # Get scoring weights
        scoring_config = self.activity_config.get('scoring_weights', {})
        self.weight_keyword = scoring_config.get('keyword_match', 0.4)
        self.weight_quality = scoring_config.get('llm_quality', 0.4)
        self.weight_diversity = scoring_config.get('theme_diversity', 0.2)
        
        # Get top N responses to select
        self.top_n = self.activity_config.get('top_responses_per_question', 10)
        
        logger.info(f"ActivityAnalyzer initialized (top_n={self.top_n}, weights: K={self.weight_keyword}, Q={self.weight_quality}, D={self.weight_diversity})")
    
    def _parse_llm_response(self, response_text: str) -> Dict:
        """Parse LLM JSON response with error handling."""
        try:
            if '```json' in response_text:
                start = response_text.find('```json') + 7
                end = response_text.find('```', start)
                response_text = response_text[start:end].strip()
            elif '```' in response_text:
                start = response_text.find('```') + 3
                end = response_text.find('```', start)
                response_text = response_text[start:end].strip()
            
            return json.loads(response_text)
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse LLM response as JSON: {response_text[:100]}")
            return {}
    
    def _get_llm_quality_score(self, response: str, activity_template: str, question_type: str) -> float:
        """
        Get LLM quality assessment for a response.
        
        Args:
            response: Student response text
            activity_template: Activity description
            question_type: 'q1', 'q2', or 'q3'
            
        Returns:
            Quality score 0-100
        """
        try:
            prompt_key = f'{question_type}_quality'
            prompt_template = self.activity_config.get('quality_prompts', {}).get(prompt_key, '')
            
            if not prompt_template:
                # Default simple prompt
                prompt_template = """Rate this response (0-100) for quality, depth, and relevance.
Activity: {activity_description}
Response: {response}
Output JSON: {{"score": 85, "reasoning": "..."}}"""
            
            prompt = prompt_template.format(
                activity_description=activity_template[:500],
                response=response
            )
            
            llm_response = self.llm.generate_content(prompt)
            analysis = self._parse_llm_response(llm_response)
            
            score = analysis.get('score', 50)  # Default to middle score
            return float(min(100, max(0, score)))
            
        except Exception as e:
            logger.error(f"Error getting LLM quality score: {str(e)}")
            return 50.0  # Default to middle score on error
    
    def _categorize_cognitive_domain(self, all_scored_responses: List[Dict]) -> Dict:
        """
        Categorize Q1 responses by learning quality (Cognitive Domain).
        
        Categories:
        - Learned Well: Score >= 70 (strong understanding, clear learnings)
        - Needs Reinforcement: Score < 70 (partial understanding, needs support)
        
        Args:
            all_scored_responses: All scored responses (not just top 10)
            
        Returns:
            Dictionary with categorization counts and student lists
        """
        learned_well = [r for r in all_scored_responses if r['total_score'] >= 70]
        needs_reinforcement = [r for r in all_scored_responses if r['total_score'] < 70]
        
        total = len(all_scored_responses)
        
        return {
            'learned_well': {
                'count': len(learned_well),
                'percentage': round(len(learned_well) / total * 100, 1) if total > 0 else 0,
                'students': [r['student_id'] for r in learned_well],
                'description': 'Clear understanding, 3+ distinct learnings identified'
            },
            'needs_reinforcement': {
                'count': len(needs_reinforcement),
                'percentage': round(len(needs_reinforcement) / total * 100, 1) if total > 0 else 0,
                'students': [r['student_id'] for r in needs_reinforcement],
                'description': 'Partial understanding, may need additional support'
            }
        }
    
    def _categorize_affective_domain(self, all_scored_responses: List[Dict]) -> Dict:
        """
        Categorize Q3 responses by exploration intent (Affective Domain).
        
        Categories:
        - Wants to Explore Further: Quality score >= 70 (high curiosity, specific exploration intent)
        - General Interest: Quality score < 70 (expressed interest but no specific direction)
        
        Args:
            all_scored_responses: All scored responses (not just top 10)
            
        Returns:
            Dictionary with categorization counts and student lists
        """
        wants_to_explore = [r for r in all_scored_responses if r['quality_score'] >= 70]
        general_interest = [r for r in all_scored_responses if r['quality_score'] < 70]
        
        total = len(all_scored_responses)
        
        return {
            'wants_to_explore': {
                'count': len(wants_to_explore),
                'percentage': round(len(wants_to_explore) / total * 100, 1) if total > 0 else 0,
                'students': [r['student_id'] for r in wants_to_explore],
                'description': 'Shows curiosity and specific interest in further exploration'
            },
            'general_interest': {
                'count': len(general_interest),
                'percentage': round(len(general_interest) / total * 100, 1) if total > 0 else 0,
                'students': [r['student_id'] for r in general_interest],
                'description': 'Expressed interest but no specific exploration direction'
            }
        }
    
    def generate_instructor_recommendations(self, results: Dict) -> List[str]:
        """
        Generate actionable recommendations for instructor based on analysis.
        
        Args:
            results: Complete analysis results dictionary
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        total_students = results['metadata']['total_students']
        
        # Q1: Cognitive domain recommendations
        cognitive = results['q1_analysis'].get('cognitive_categorization', {})
        needs_reinforcement_count = cognitive.get('needs_reinforcement', {}).get('count', 0)
        needs_reinforcement_pct = needs_reinforcement_count / total_students * 100 if total_students > 0 else 0
        
        if needs_reinforcement_pct > 40:
            recommendations.append(
                f"Consider reviewing core concepts - {needs_reinforcement_pct:.0f}% of students "
                f"({needs_reinforcement_count} students) may need additional support."
            )
        elif needs_reinforcement_pct > 20:
            recommendations.append(
                f"Small group support recommended for {needs_reinforcement_count} students "
                f"who showed partial understanding."
            )
        else:
            recommendations.append(
                "Excellent learning outcomes - most students demonstrated strong understanding."
            )
        
        # Q2: Question-based recommendations
        q2_count = results['q2_analysis']['total_analyzed']
        if q2_count > 0:
            recommendations.append(
                f"Review the top {len(results['q2_analysis']['top_10_questions'])} student questions "
                f"to address common areas of curiosity in your next session."
            )
        
        # Q3: Affective domain recommendations
        affective = results['q3_analysis'].get('affective_categorization', {})
        wants_to_explore = affective.get('wants_to_explore', {}).get('count', 0)
        explore_pct = wants_to_explore / total_students * 100 if total_students > 0 else 0
        
        if explore_pct >= 50:
            recommendations.append(
                f"High engagement! {explore_pct:.0f}% of students want to explore further. "
                f"Consider providing extension resources or projects."
            )
        elif explore_pct >= 25:
            recommendations.append(
                f"{wants_to_explore} students showed specific exploration interests. "
                f"Consider offering optional enrichment activities."
            )
        
        return recommendations
    
    def analyze_q1_summaries(self, responses: Dict, activity_template: str) -> Dict:
        """
        Analyze Q1: Three things learned.
        Select top 10 responses from ALL students based on keyword match, quality, and diversity.
        
        Args:
            responses: Dictionary of {student_id: {'q1': response, ...}}
            activity_template: Activity description
            
        Returns:
            Analysis results with top 10 responses, themes, and keywords
        """
        logger.info("Analyzing Q1: Three things learned (ALL students)")
        
        # Extract activity keywords
        activity_keywords = self.keyword_extractor.extract_activity_keywords(activity_template)
        
        # Collect all valid responses
        all_responses_text = []
        student_ids = []
        
        for student_id, student_data in responses.items():
            response = student_data.get('q1', '').strip()
            if len(response) >= 20:  # Minimum length
                all_responses_text.append(response)
                student_ids.append(student_id)
        
        if not all_responses_text:
            logger.warning("No valid Q1 responses found")
            return {
                'top_10_responses': [],
                'total_analyzed': 0,
                'themes_discovered': {},
                'activity_keywords': [kw for kw, _ in activity_keywords[:10]]
            }
        
        # Extract emergent keywords from responses
        response_keywords = self.keyword_extractor.extract_response_keywords(all_responses_text)
        
        # Score all responses
        scored_responses = []
        
        for idx, response in enumerate(all_responses_text):
            student_id = student_ids[idx]
            
            # Keyword overlap score (0-100)
            keyword_score = self.keyword_extractor.score_keyword_overlap(
                response, activity_keywords, response_keywords
            )
            
            # LLM quality score (0-100)
            quality_score = self._get_llm_quality_score(response, activity_template, 'q1')
            
            # Combined score (weighted average)
            base_score = (keyword_score * self.weight_keyword) + (quality_score * self.weight_quality)
            
            scored_responses.append({
                'student_id': student_id,
                'response': response,
                'keyword_score': round(keyword_score, 2),
                'quality_score': round(quality_score, 2),
                'total_score': round(base_score, 2),
                'response_idx': idx
            })
            
            logger.info(f"Q1 Student {student_id}: K={keyword_score:.1f}, Q={quality_score:.1f}, Total={base_score:.1f}")
        
        # Cluster responses to find themes
        clusters = self.thematic_analyzer.cluster_responses(all_responses_text)
        
        # Add theme information to scored responses
        for resp in scored_responses:
            idx = resp['response_idx']
            cluster_id = clusters['response_to_cluster'].get(idx, 0)
            resp['cluster_id'] = cluster_id
            theme_keywords = clusters['themes'].get(cluster_id, ['general'])
            resp['theme'] = ', '.join(theme_keywords)
        
        # Select top 10 with diversity
        top_10 = self.thematic_analyzer.ensure_diversity(
            scored_responses, 
            clusters['response_to_cluster'], 
            top_n=self.top_n
        )
        
        # Categorize by cognitive domain (learned well vs needs reinforcement)
        cognitive_categorization = self._categorize_cognitive_domain(scored_responses)
        
        logger.info(f"Q1 Analysis complete: Selected {len(top_10)} from {len(scored_responses)} responses")
        logger.info(f"Cognitive Domain: {cognitive_categorization['learned_well']['count']} learned well, {cognitive_categorization['needs_reinforcement']['count']} need reinforcement")
        
        return {
            'top_10_responses': top_10,
            'total_analyzed': len(scored_responses),
            'cognitive_categorization': cognitive_categorization,  # For teacher report
            'themes_discovered': clusters['themes'],  # Backend use only
            'activity_keywords': [kw for kw, _ in activity_keywords[:10]]  # Backend use only
        }
    
    def analyze_q2_questions(self, responses: Dict, activity_template: str) -> Dict:
        """
        Analyze Q2: Two questions about the material.
        Select top 10 questions from ALL students.
        
        Args:
            responses: Dictionary of student responses
            activity_template: Activity description
            
        Returns:
            Analysis results with top 10 questions
        """
        logger.info("Analyzing Q2: Student questions (ALL students)")
        
        # Extract activity keywords
        activity_keywords = self.keyword_extractor.extract_activity_keywords(activity_template)
        
        # Collect all valid responses
        all_responses_text = []
        student_ids = []
        
        for student_id, student_data in responses.items():
            response = student_data.get('q2', '').strip()
            if len(response) >= 10:  # Minimum length for questions
                all_responses_text.append(response)
                student_ids.append(student_id)
        
        if not all_responses_text:
            logger.warning("No valid Q2 responses found")
            return {
                'top_10_questions': [],
                'total_analyzed': 0,
                'themes_discovered': {},
                'activity_keywords': [kw for kw, _ in activity_keywords[:10]]
            }
        
        # Extract emergent keywords
        response_keywords = self.keyword_extractor.extract_response_keywords(all_responses_text)
        
        # Score all questions
        scored_questions = []
        
        for idx, response in enumerate(all_responses_text):
            student_id = student_ids[idx]
            
            # Keyword overlap score
            keyword_score = self.keyword_extractor.score_keyword_overlap(
                response, activity_keywords, response_keywords
            )
            
            # LLM quality score
            quality_score = self._get_llm_quality_score(response, activity_template, 'q2')
            
            # Combined score
            base_score = (keyword_score * self.weight_keyword) + (quality_score * self.weight_quality)
            
            scored_questions.append({
                'student_id': student_id,
                'question': response,
                'keyword_score': round(keyword_score, 2),
                'quality_score': round(quality_score, 2),
                'total_score': round(base_score, 2),
                'response_idx': idx
            })
            
            logger.info(f"Q2 Student {student_id}: K={keyword_score:.1f}, Q={quality_score:.1f}, Total={base_score:.1f}")
        
        # Cluster questions
        clusters = self.thematic_analyzer.cluster_responses(all_responses_text)
        
        # Add theme information
        for quest in scored_questions:
            idx = quest['response_idx']
            cluster_id = clusters['response_to_cluster'].get(idx, 0)
            quest['cluster_id'] = cluster_id
            theme_keywords = clusters['themes'].get(cluster_id, ['general'])
            quest['theme'] = ', '.join(theme_keywords)
        
        # Select top 10 with diversity
        top_10 = self.thematic_analyzer.ensure_diversity(
            scored_questions,
            clusters['response_to_cluster'],
            top_n=self.top_n
        )
        
        logger.info(f"Q2 Analysis complete: Selected {len(top_10)} from {len(scored_questions)} questions")
        
        return {
            'top_10_questions': top_10,
            'total_analyzed': len(scored_questions),
            'themes_discovered': clusters['themes'],
            'activity_keywords': [kw for kw, _ in activity_keywords[:10]]
        }
    
    def analyze_q3_fascination(self, responses: Dict, activity_template: str) -> Dict:
        """
        Analyze Q3: One aspect found most interesting or want to explore.
        Select top 10 responses from ALL students.
        
        Args:
            responses: Dictionary of student responses
            activity_template: Activity description
            
        Returns:
            Analysis results with top 10 fascination responses
        """
        logger.info("Analyzing Q3: Fascination & exploration (ALL students)")
        
        # Extract activity keywords
        activity_keywords = self.keyword_extractor.extract_activity_keywords(activity_template)
        
        # Collect all valid responses
        all_responses_text = []
        student_ids = []
        
        for student_id, student_data in responses.items():
            response = student_data.get('q3', '').strip()
            if len(response) >= 15:  # Minimum length
                all_responses_text.append(response)
                student_ids.append(student_id)
        
        if not all_responses_text:
            logger.warning("No valid Q3 responses found")
            return {
                'top_10_responses': [],
                'total_analyzed': 0,
                'themes_discovered': {},
                'activity_keywords': [kw for kw, _ in activity_keywords[:10]]
            }
        
        # Extract emergent keywords
        response_keywords = self.keyword_extractor.extract_response_keywords(all_responses_text)
        
        # Score all responses
        scored_responses = []
        
        for idx, response in enumerate(all_responses_text):
            student_id = student_ids[idx]
            
            # Keyword overlap score
            keyword_score = self.keyword_extractor.score_keyword_overlap(
                response, activity_keywords, response_keywords
            )
            
            # LLM quality score (focus on enthusiasm and exploration)
            quality_score = self._get_llm_quality_score(response, activity_template, 'q3')
            
            # Combined score
            base_score = (keyword_score * self.weight_keyword) + (quality_score * self.weight_quality)
            
            scored_responses.append({
                'student_id': student_id,
                'response': response,
                'keyword_score': round(keyword_score, 2),
                'quality_score': round(quality_score, 2),
                'total_score': round(base_score, 2),
                'response_idx': idx
            })
            
            logger.info(f"Q3 Student {student_id}: K={keyword_score:.1f}, Q={quality_score:.1f}, Total={base_score:.1f}")
        
        # Cluster responses
        clusters = self.thematic_analyzer.cluster_responses(all_responses_text)
        
        # Add theme information
        for resp in scored_responses:
            idx = resp['response_idx']
            cluster_id = clusters['response_to_cluster'].get(idx, 0)
            resp['cluster_id'] = cluster_id
            theme_keywords = clusters['themes'].get(cluster_id, ['general'])
            resp['theme'] = ', '.join(theme_keywords)
        
        # Select top 10 with diversity
        top_10 = self.thematic_analyzer.ensure_diversity(
            scored_responses,
            clusters['response_to_cluster'],
            top_n=self.top_n
        )
        
        # Categorize by affective domain (exploration intent)
        affective_categorization = self._categorize_affective_domain(scored_responses)
        
        logger.info(f"Q3 Analysis complete: Selected {len(top_10)} from {len(scored_responses)} responses")
        logger.info(f"Affective Domain: {affective_categorization['wants_to_explore']['count']} want to explore, {affective_categorization['general_interest']['count']} general interest")
        
        return {
            'top_10_responses': top_10,
            'total_analyzed': len(scored_responses),
            'affective_categorization': affective_categorization,  # For teacher report
            'themes_discovered': clusters['themes'],  # Backend use only
            'activity_keywords': [kw for kw, _ in activity_keywords[:10]]  # Backend use only
        }
    
    def generate_analysis_report(self, students_data: Dict, activity_template: str) -> Dict:
        """
        Generate complete analysis report for all questions.
        
        Args:
            students_data: Dictionary of student responses
            activity_template: Activity description
            
        Returns:
            Complete analysis results dictionary
        """
        logger.info("Starting complete activity analysis (ALL students)")
        
        class_size = len(students_data)
        logger.info(f"Class size: {class_size}, Analyzing ALL students, Selecting top {self.top_n} per question")
        
        # Analyze each question
        q1_results = self.analyze_q1_summaries(students_data, activity_template)
        q2_results = self.analyze_q2_questions(students_data, activity_template)
        q3_results = self.analyze_q3_fascination(students_data, activity_template)
        
        # Compile results
        results = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_students': class_size,
                'top_responses_per_question': self.top_n,
                'activity_description': activity_template[:200] + '...' if len(activity_template) > 200 else activity_template,
                'scoring_method': f'Keyword Match ({self.weight_keyword*100:.0f}%) + LLM Quality ({self.weight_quality*100:.0f}%) + Diversity ({self.weight_diversity*100:.0f}%)'
            },
            'q1_analysis': q1_results,
            'q2_analysis': q2_results,
            'q3_analysis': q3_results,
            'summary': {
                'q1_responses_analyzed': q1_results['total_analyzed'],
                'q1_top_selected': len(q1_results['top_10_responses']),
                'q2_responses_analyzed': q2_results['total_analyzed'],
                'q2_top_selected': len(q2_results['top_10_questions']),
                'q3_responses_analyzed': q3_results['total_analyzed'],
                'q3_top_selected': len(q3_results['top_10_responses'])
            }
        }
        
        # Generate instructor recommendations
        results['recommendations'] = self.generate_instructor_recommendations(results)
        
        logger.info("Activity analysis complete")
        return results
