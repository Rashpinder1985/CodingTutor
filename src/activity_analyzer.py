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
            use_bigrams=keyword_config.get('use_bigrams', True),
            llm_generator=self.llm
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
    
    def _batch_get_llm_quality_scores(self, responses: List[str], activity_template: str, question_type: str) -> List[float]:
        """
        Get LLM quality scores for multiple responses in a single batch call.
        Much faster than individual calls.
        
        Args:
            responses: List of student response texts
            activity_template: Activity description
            question_type: 'q1', 'q2', or 'q3'
            
        Returns:
            List of quality scores (0-100)
        """
        if not responses:
            return []
        
        try:
            # Batch process in groups of 10-15 for efficiency
            batch_size = 12
            all_scores = []
            
            for batch_start in range(0, len(responses), batch_size):
                batch_responses = responses[batch_start:batch_start + batch_size]
                
                prompt_key = f'{question_type}_quality'
                prompt_template = self.activity_config.get('quality_prompts', {}).get(prompt_key, '')
                
                if not prompt_template:
                    prompt_template = """Rate each response (0-100) for quality, depth, and relevance."""
                
                # Add Q2-specific instructions to filter invalid responses
                q2_specific = ""
                if question_type == 'q2':
                    q2_specific = "\nIMPORTANT: Give score of 0-10 for invalid responses like 'no questions', 'no question', 'n/a', 'none', etc. These are not actual questions and should be filtered out."
                
                # Create batch prompt
                batch_prompt = f"""{prompt_template}{q2_specific}

Activity Context:
{activity_template[:500]}

Student Responses:
{chr(10).join([f"{i+1}. {r[:200]}" for i, r in enumerate(batch_responses)])}

Rate each response and return JSON:
{{"scores": [{{"index": 0, "score": 85}}, {{"index": 1, "score": 70}}, ...]}}

Response indices start at {batch_start}."""

                system_message = "You are an expert at evaluating student responses for quality and depth."
                
                llm_response = self.llm.generate_content(batch_prompt, system_message)
                analysis = self._parse_llm_response(llm_response)
                
                # Extract scores
                scores_list = analysis.get('scores', [])
                batch_scores = {}
                
                for score_data in scores_list:
                    idx = score_data.get('index', -1)
                    score = score_data.get('score', 50)
                    if 0 <= idx < len(batch_responses):
                        batch_scores[idx] = float(min(100, max(0, score)))
                
                # Fill in any missing scores with defaults
                for i in range(len(batch_responses)):
                    if i not in batch_scores:
                        batch_scores[i] = 50.0
                
                # Add to all_scores in order
                for i in range(len(batch_responses)):
                    all_scores.append(batch_scores[i])
            
            return all_scores
            
        except Exception as e:
            logger.error(f"Error in batch quality scoring: {str(e)}, falling back to individual calls")
            # Fallback to individual calls if batch fails
            return [self._get_llm_quality_score(r, activity_template, question_type) for r in responses]
    
    def _categorize_cognitive_domain(self, all_scored_responses: List[Dict]) -> Dict:
        """
        Categorize Q1 responses by learning quality (Cognitive Domain).
        
        Categories:
        - Learned Well: Score >= 50 (demonstrates understanding of key concepts)
        - Needs Reinforcement: Score < 50 (partial understanding, needs support)
        
        Args:
            all_scored_responses: All scored responses (not just top 10)
            
        Returns:
            Dictionary with categorization counts and student lists
        """
        learned_well = [r for r in all_scored_responses if r['total_score'] >= 50]
        needs_reinforcement = [r for r in all_scored_responses if r['total_score'] < 50]
        
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
        - Wants to Explore Further: Quality score >= 50 (shows curiosity and interest)
        - General Interest: Quality score < 50 (expressed interest but less specific)
        
        Args:
            all_scored_responses: All scored responses (not just top 10)
            
        Returns:
            Dictionary with categorization counts and student lists
        """
        wants_to_explore = [r for r in all_scored_responses if r['quality_score'] >= 50]
        general_interest = [r for r in all_scored_responses if r['quality_score'] < 50]
        
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
        Select top 10 responses from ALL students based on concept keyword match, quality, and diversity.
        Uses LLM to extract concept-related keywords (not generic vocabulary) for cognitive domain measurement.
        
        Args:
            responses: Dictionary of {student_id: {'q1': response, ...}}
            activity_template: Activity description
            
        Returns:
            Analysis results with top 10 responses, themes, and concept keywords
        """
        logger.info("Analyzing Q1: Three things learned (ALL students)")
        
        # Extract concept keywords from activity template using LLM (filters out generic vocabulary)
        concept_keywords = self.keyword_extractor.extract_concept_keywords_llm(activity_template)
        logger.info(f"Extracted {len(concept_keywords)} concept keywords: {concept_keywords[:10]}")
        
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
                'concept_keywords': concept_keywords
            }
        
        # Score all responses using concept keywords (for cognitive domain measurement)
        # Batch quality scoring for performance (much faster than individual calls)
        logger.info(f"Batch scoring {len(all_responses_text)} Q1 responses...")
        quality_scores = self._batch_get_llm_quality_scores(all_responses_text, activity_template, 'q1')
        
        scored_responses = []
        
        for idx, response in enumerate(all_responses_text):
            student_id = student_ids[idx]
            
            # Concept keyword overlap score (0-100) - measures alignment with taught concepts
            concept_score = self.keyword_extractor.score_concept_keyword_overlap(
                response, concept_keywords
            )
            
            # LLM quality score (0-100) - from batch call
            quality_score = quality_scores[idx] if idx < len(quality_scores) else 50.0
            
            # Combined score (weighted average)
            base_score = (concept_score * self.weight_keyword) + (quality_score * self.weight_quality)
            
            scored_responses.append({
                'student_id': student_id,
                'response': response,
                'keyword_score': round(concept_score, 2),  # Now represents concept alignment
                'quality_score': round(quality_score, 2),
                'total_score': round(base_score, 2),
                'response_idx': idx
            })
            
            logger.info(f"Q1 Student {student_id}: Concept={concept_score:.1f}, Quality={quality_score:.1f}, Total={base_score:.1f}")
        
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
            'concept_keywords': concept_keywords  # For teacher report - shows concepts taught
        }
    
    def _is_valid_question(self, response: str) -> bool:
        """
        Check if a Q2 response is a valid question (not "no questions", etc.).
        
        Args:
            response: Student response text
            
        Returns:
            True if valid question, False otherwise
        """
        if not response:
            return False
        
        response_lower = response.lower().strip()
        
        # Invalid patterns
        invalid_patterns = [
            'no questions',
            'no question',
            'no questionsss',
            'no questionss',
            'no questionssss',
            'no questionsssss',
            'no questionssssss',
            'n/a',
            'na',
            'none',
            'nothing',
            'no',
            'nope',
            'nothing to ask',
            'no questions to ask',
            'i have no questions',
            'i don\'t have questions',
            'i dont have questions',
            'no questions at this time',
            'no questions right now'
        ]
        
        # Check if response matches any invalid pattern
        for pattern in invalid_patterns:
            if response_lower == pattern or response_lower.startswith(pattern + ' ') or response_lower.endswith(' ' + pattern):
                return False
        
        # Check if response is too short or just punctuation
        if len(response_lower.replace(' ', '').replace('.', '').replace('!', '').replace('?', '')) < 5:
            return False
        
        # Check if it contains question words or question marks (indicates it's a question)
        question_indicators = ['?', 'how', 'what', 'why', 'when', 'where', 'who', 'which', 'can', 'could', 'should', 'would', 'will', 'do', 'does', 'did', 'is', 'are', 'was', 'were']
        has_question_indicator = any(indicator in response_lower for indicator in question_indicators)
        
        return has_question_indicator or len(response) >= 20  # Allow longer responses even without question indicators
    
    def analyze_q2_questions(self, responses: Dict, activity_template: str) -> Dict:
        """
        Analyze Q2: Two questions about the material.
        Groups questions by concept-based themes from activity template, shows frequency per theme.
        
        Args:
            responses: Dictionary of student responses
            activity_template: Activity description
            
        Returns:
            Analysis results with themes, example questions, frequency, and top 10 questions
        """
        logger.info("Analyzing Q2: Student questions (ALL students)")
        
        # Extract concepts from activity template using LLM
        concept_keywords = self.keyword_extractor.extract_concept_keywords_llm(activity_template)
        logger.info(f"Extracted {len(concept_keywords)} concepts for Q2 grouping: {concept_keywords[:10]}")
        
        # Collect all valid responses (filter out "no questions" etc.)
        all_responses_text = []
        student_ids = []
        
        for student_id, student_data in responses.items():
            response = student_data.get('q2', '').strip()
            # Check both length and validity
            if len(response) >= 10 and self._is_valid_question(response):
                all_responses_text.append(response)
                student_ids.append(student_id)
            else:
                logger.debug(f"Filtered out invalid Q2 response from {student_id}: '{response[:50]}'")
        
        if not all_responses_text:
            logger.warning("No valid Q2 responses found")
            return {
                'top_10_questions': [],
                'total_analyzed': 0,
                'themes': {},
                'concept_keywords': concept_keywords
            }
        
        # Map each question to the closest matching concept using LLM
        question_to_concept = self._map_questions_to_concepts(all_responses_text, concept_keywords, activity_template)
        
        # Group questions by concept theme
        themes = {}
        for idx, (question, student_id) in enumerate(zip(all_responses_text, student_ids)):
            concept = question_to_concept.get(idx, 'Other')
            
            if concept not in themes:
                themes[concept] = {
                    'concept': concept,
                    'questions': [],
                    'frequency': 0
                }
            
            themes[concept]['questions'].append({
                'student_id': student_id,
                'question': question
            })
            themes[concept]['frequency'] += 1
        
        # Sort themes by frequency (descending)
        sorted_themes = dict(sorted(themes.items(), key=lambda x: x[1]['frequency'], reverse=True))
        
        # Score all questions for top 10 selection
        # Batch quality scoring for performance
        logger.info(f"Batch scoring {len(all_responses_text)} Q2 questions...")
        quality_scores = self._batch_get_llm_quality_scores(all_responses_text, activity_template, 'q2')
        
        scored_questions = []
        for idx, response in enumerate(all_responses_text):
            student_id = student_ids[idx]
            
            # Double-check validity (in case batch scoring included invalid ones)
            if not self._is_valid_question(response):
                logger.debug(f"Skipping invalid question in scoring: {response[:50]}")
                continue
            
            # Use concept alignment score
            concept = question_to_concept.get(idx, 'Other')
            concept_score = 80.0 if concept != 'Other' else 40.0  # Higher score for concept-aligned questions
            
            # LLM quality score - from batch call
            quality_score = quality_scores[idx] if idx < len(quality_scores) else 50.0
            
            # Penalize low-quality responses (likely invalid questions that passed initial filter)
            if quality_score < 30:
                quality_score = 0  # Set to 0 for clearly invalid responses
            
            # Combined score
            base_score = (concept_score * self.weight_keyword) + (quality_score * self.weight_quality)
            
            scored_questions.append({
                'student_id': student_id,
                'question': response,
                'keyword_score': round(concept_score, 2),
                'quality_score': round(quality_score, 2),
                'total_score': round(base_score, 2),
                'response_idx': idx,
                'concept': concept
            })
        
        # Filter out any remaining invalid questions and select top 10
        valid_scored = [q for q in scored_questions if self._is_valid_question(q['question'])]
        top_10 = sorted(valid_scored, key=lambda x: x['total_score'], reverse=True)[:self.top_n]
        
        logger.info(f"Q2 Analysis complete: {len(sorted_themes)} themes identified, {len(scored_questions)} questions analyzed")
        for theme_name, theme_data in list(sorted_themes.items())[:5]:
            logger.info(f"  Theme '{theme_name}': {theme_data['frequency']} questions")
        
        return {
            'top_10_questions': top_10,
            'total_analyzed': len(scored_questions),
            'themes': sorted_themes,  # Theme-based grouping with frequency
            'concept_keywords': concept_keywords
        }
    
    def _map_questions_to_concepts(self, questions: List[str], concepts: List[str], activity_template: str) -> Dict[int, str]:
        """
        Map each student question to the closest matching concept from activity template.
        
        Args:
            questions: List of student questions
            concepts: List of concepts from activity template
            activity_template: Activity description for context
            
        Returns:
            Dictionary mapping question index to concept name
        """
        if not concepts or not questions:
            return {i: 'Other' for i in range(len(questions))}
        
        try:
            # Batch process questions for efficiency
            batch_size = 10
            question_to_concept = {}
            
            for batch_start in range(0, len(questions), batch_size):
                batch_questions = questions[batch_start:batch_start + batch_size]
                batch_indices = list(range(batch_start, min(batch_start + batch_size, len(questions))))
                
                # Create concept groups for better matching (e.g., "Restriction Enzymes" group includes "enzyme", "cutting", "restriction")
                concept_groups = {}
                for concept in concepts[:25]:  # Use more concepts
                    concept_lower = concept.lower()
                    # Create variations
                    words = concept_lower.split()
                    for word in words:
                        if len(word) > 3:  # Skip short words
                            if word not in concept_groups:
                                concept_groups[word] = []
                            concept_groups[word].append(concept)
                
                prompt = f"""Map each student question to the closest matching CONCEPT from the activity.
Be generous - if a question relates to a concept even partially, map it to that concept.
Only use "Other" if the question is completely unrelated to any concept.

Activity Context:
{activity_template[:1000]}

Available Concepts (be flexible with matching):
{', '.join(concepts[:25])}

Student Questions:
{chr(10).join([f"{i+1}. {q}" for i, q in enumerate(batch_questions)])}

IMPORTANT: 
- Questions about "enzymes" → map to concepts containing "enzyme" (e.g., "Restriction Enzymes")
- Questions about "DNA" → map to DNA-related concepts
- Questions about "plasmids" → map to "Plasmid" or "Recombinant DNA"
- Be flexible with partial matches and synonyms

Return JSON format:
{{"mappings": [{{"question_index": 0, "concept": "PCR"}}, {{"question_index": 1, "concept": "Restriction Enzymes"}}, ...]}}

Question indices start at {batch_start}."""

                system_message = "You are an expert at categorizing student questions by educational concepts. Be generous with matching - prefer mapping to concepts over 'Other'."
                
                response = self.llm.generate_content(prompt, system_message)
                
                # Parse response
                try:
                    if '```json' in response:
                        start = response.find('```json') + 7
                        end = response.find('```', start)
                        response = response[start:end].strip()
                    
                    json_start = response.find('{')
                    json_end = response.rfind('}') + 1
                    if json_start != -1 and json_end > json_start:
                        response = response[json_start:json_end]
                    
                    result = json.loads(response)
                    mappings = result.get('mappings', [])
                    
                    for mapping in mappings:
                        q_idx = mapping.get('question_index', -1)
                        concept = mapping.get('concept', 'Other')
                        # Validate concept is in our list or is "Other"
                        if concept not in concepts and concept != 'Other':
                            # Find closest match
                            concept_lower = concept.lower()
                            matched = False
                            for c in concepts:
                                if c.lower() in concept_lower or concept_lower in c.lower():
                                    concept = c
                                    matched = True
                                    break
                            if not matched:
                                concept = 'Other'
                        
                        if 0 <= q_idx < len(questions):
                            question_to_concept[q_idx] = concept
                    
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse Q2 concept mapping response, using enhanced fallback")
                    # Enhanced fallback: use better keyword matching
                    for idx, question in enumerate(batch_questions):
                        question_lower = question.lower()
                        best_match = 'Other'
                        best_score = 0
                        
                        # Try exact matches first
                        for concept in concepts:
                            concept_lower = concept.lower()
                            if concept_lower in question_lower:
                                score = len(concept) * 2  # Boost exact matches
                                if score > best_score:
                                    best_score = score
                                    best_match = concept
                        
                        # Try partial word matches if no exact match
                        if best_match == 'Other':
                            question_words = set(question_lower.split())
                            for concept in concepts:
                                concept_words = set(concept.lower().split())
                                overlap = len(question_words & concept_words)
                                if overlap > 0:
                                    score = overlap * 10
                                    if score > best_score:
                                        best_score = score
                                        best_match = concept
                        
                        # Try keyword-based matching (e.g., "enzyme" → "Restriction Enzymes")
                        if best_match == 'Other':
                            for concept in concepts:
                                concept_words = concept.lower().split()
                                for cw in concept_words:
                                    if len(cw) > 4 and cw in question_lower:
                                        score = len(cw)
                                        if score > best_score:
                                            best_score = score
                                            best_match = concept
                                            break
                        
                        question_to_concept[batch_indices[idx]] = best_match
                        
        except Exception as e:
            logger.error(f"Error mapping questions to concepts: {str(e)}")
            # Fallback: assign all to "Other"
            for i in range(len(questions)):
                if i not in question_to_concept:
                    question_to_concept[i] = 'Other'
        
        # Ensure all questions are mapped
        for i in range(len(questions)):
            if i not in question_to_concept:
                question_to_concept[i] = 'Other'
        
        return question_to_concept
    
    def analyze_q3_fascination(self, responses: Dict, activity_template: str) -> Dict:
        """
        Analyze Q3: One aspect found most interesting or want to explore.
        Classifies responses as "Content-related" (concepts) vs "Pedagogy-related" (teaching methods).
        Groups responses by theme within each category.
        
        Args:
            responses: Dictionary of student responses
            activity_template: Activity description
            
        Returns:
            Analysis results with content/pedagogy classification and themed groups
        """
        logger.info("Analyzing Q3: Fascination & exploration (ALL students)")
        
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
                'content_themes': {},
                'pedagogy_themes': {},
                'affective_categorization': {}
            }
        
        # Classify each response as content-related or pedagogy-related using LLM
        classifications = self._classify_content_vs_pedagogy(all_responses_text, activity_template)
        
        # Separate responses by category
        content_responses = []
        pedagogy_responses = []
        
        for idx, (response, student_id) in enumerate(zip(all_responses_text, student_ids)):
            category = classifications.get(idx, 'content')
            
            response_data = {
                'student_id': student_id,
                'response': response,
                'response_idx': idx,
                'category': category
            }
            
            if category == 'content':
                content_responses.append(response_data)
            else:
                pedagogy_responses.append(response_data)
        
        # Extract themes for content-related responses
        content_themes = {}
        if content_responses:
            content_texts = [r['response'] for r in content_responses]
            content_clusters = self.thematic_analyzer.cluster_responses(content_texts)
            
            # Generate clean theme names using LLM
            theme_name_map = self._generate_clean_theme_names(content_clusters, content_texts, activity_template, 'content')
            
            # Group by theme
            for resp_data in content_responses:
                idx = resp_data['response_idx']
                cluster_id = content_clusters['response_to_cluster'].get(content_responses.index(resp_data), 0)
                theme_keywords = content_clusters['themes'].get(cluster_id, ['general'])
                # Use cleaned theme name from LLM, fallback to keywords
                theme_name = theme_name_map.get(cluster_id, ', '.join(theme_keywords[:2]))
                
                if theme_name not in content_themes:
                    content_themes[theme_name] = {
                        'theme': theme_name,
                        'responses': [],
                        'example_phrasing': resp_data['response'][:100] + '...' if len(resp_data['response']) > 100 else resp_data['response']
                    }
                
                content_themes[theme_name]['responses'].append({
                    'student_id': resp_data['student_id'],
                    'response': resp_data['response']
                })
        
        # Extract themes for pedagogy-related responses
        pedagogy_themes = {}
        if pedagogy_responses:
            pedagogy_texts = [r['response'] for r in pedagogy_responses]
            pedagogy_clusters = self.thematic_analyzer.cluster_responses(pedagogy_texts)
            
            # Generate clean theme names using LLM
            theme_name_map = self._generate_clean_theme_names(pedagogy_clusters, pedagogy_texts, activity_template, 'pedagogy')
            
            # Group by theme
            for resp_data in pedagogy_responses:
                idx = resp_data['response_idx']
                cluster_id = pedagogy_clusters['response_to_cluster'].get(pedagogy_responses.index(resp_data), 0)
                theme_keywords = pedagogy_clusters['themes'].get(cluster_id, ['general'])
                # Use cleaned theme name from LLM, fallback to keywords
                theme_name = theme_name_map.get(cluster_id, ', '.join(theme_keywords[:2]))
                
                if theme_name not in pedagogy_themes:
                    pedagogy_themes[theme_name] = {
                        'theme': theme_name,
                        'responses': [],
                        'example_phrasing': resp_data['response'][:100] + '...' if len(resp_data['response']) > 100 else resp_data['response']
                    }
                
                pedagogy_themes[theme_name]['responses'].append({
                    'student_id': resp_data['student_id'],
                    'response': resp_data['response']
                })
        
        # Score all responses for top 10 selection
        # Batch quality scoring for performance
        logger.info(f"Batch scoring {len(all_responses_text)} Q3 responses...")
        quality_scores = self._batch_get_llm_quality_scores(all_responses_text, activity_template, 'q3')
        
        scored_responses = []
        for idx, response in enumerate(all_responses_text):
            student_id = student_ids[idx]
            
            # LLM quality score (focus on enthusiasm and exploration) - from batch call
            quality_score = quality_scores[idx] if idx < len(quality_scores) else 50.0
            
            scored_responses.append({
                'student_id': student_id,
                'response': response,
                'quality_score': round(quality_score, 2),
                'total_score': round(quality_score, 2),  # Q3 primarily uses quality score
                'response_idx': idx,
                'category': classifications.get(idx, 'content')
            })
        
        # Select top 10
        top_10 = sorted(scored_responses, key=lambda x: x['total_score'], reverse=True)[:self.top_n]
        
        # Categorize by affective domain (exploration intent)
        affective_categorization = self._categorize_affective_domain(scored_responses)
        
        logger.info(f"Q3 Analysis complete: {len(content_responses)} content-related, {len(pedagogy_responses)} pedagogy-related")
        logger.info(f"  Content themes: {len(content_themes)}, Pedagogy themes: {len(pedagogy_themes)}")
        logger.info(f"Affective Domain: {affective_categorization['wants_to_explore']['count']} want to explore, {affective_categorization['general_interest']['count']} general interest")
        
        return {
            'top_10_responses': top_10,
            'total_analyzed': len(scored_responses),
            'content_themes': content_themes,  # Content-related themes with responses
            'pedagogy_themes': pedagogy_themes,  # Pedagogy-related themes with responses
            'affective_categorization': affective_categorization  # For teacher report
        }
    
    def _classify_content_vs_pedagogy(self, responses: List[str], activity_template: str) -> Dict[int, str]:
        """
        Classify each Q3 response as "content-related" or "pedagogy-related" using LLM.
        
        Content-related: Focuses on concepts, topics, subject matter (e.g., "Plasmid", "CRISPR", "Recombinant DNA")
        Pedagogy-related: Focuses on teaching methods, activities, learning approaches (e.g., "LEGO activity", "hands-on", "visual demonstration")
        
        Args:
            responses: List of student responses
            activity_template: Activity description for context
            
        Returns:
            Dictionary mapping response index to category ('content' or 'pedagogy')
        """
        if not responses:
            return {}
        
        try:
            # Batch process for efficiency
            batch_size = 10
            classifications = {}
            
            for batch_start in range(0, len(responses), batch_size):
                batch_responses = responses[batch_start:batch_start + batch_size]
                batch_indices = list(range(batch_start, min(batch_start + batch_size, len(responses))))
                
                prompt = f"""Classify each student response as either "content-related" or "pedagogy-related".

CONTENT-RELATED: Responses about concepts, topics, subject matter, scientific principles, or technical content.
Examples: "Plasmid structure", "CRISPR mechanism", "Recombinant DNA technology", "Restriction enzymes"

PEDAGOGY-RELATED: Responses about teaching methods, learning activities, instructional approaches, or how the lesson was delivered.
Examples: "LEGO activity", "hands-on demonstration", "visual examples", "interactive learning", "group work"

Activity Context:
{activity_template[:800]}

Student Responses:
{chr(10).join([f"{i+1}. {r}" for i, r in enumerate(batch_responses)])}

Return JSON format:
{{"classifications": [{{"response_index": 0, "category": "content"}}, {{"response_index": 1, "category": "pedagogy"}}, ...]}}

Response indices start at {batch_start}."""

                system_message = "You are an expert at categorizing educational responses by content vs pedagogy."
                
                response = self.llm.generate_content(prompt, system_message)
                
                # Parse response
                try:
                    if '```json' in response:
                        start = response.find('```json') + 7
                        end = response.find('```', start)
                        response = response[start:end].strip()
                    
                    json_start = response.find('{')
                    json_end = response.rfind('}') + 1
                    if json_start != -1 and json_end > json_start:
                        response = response[json_start:json_end]
                    
                    result = json.loads(response)
                    classifs = result.get('classifications', [])
                    
                    for classif in classifs:
                        r_idx = classif.get('response_index', -1)
                        category = classif.get('category', 'content').lower()
                        if category not in ['content', 'pedagogy']:
                            category = 'content'  # Default to content
                        
                        if 0 <= r_idx < len(responses):
                            classifications[r_idx] = category
                    
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse Q3 classification response, using keyword fallback")
                    # Fallback: use keyword matching
                    pedagogy_keywords = ['activity', 'demonstration', 'hands-on', 'interactive', 'visual', 'example', 'teaching', 'learning method', 'pedagogy', 'approach', 'way', 'how we learned']
                    for idx, resp in enumerate(batch_responses):
                        resp_lower = resp.lower()
                        is_pedagogy = any(kw in resp_lower for kw in pedagogy_keywords)
                        classifications[batch_indices[idx]] = 'pedagogy' if is_pedagogy else 'content'
                        
        except Exception as e:
            logger.error(f"Error classifying content vs pedagogy: {str(e)}")
            # Fallback: default all to content
            for i in range(len(responses)):
                if i not in classifications:
                    classifications[i] = 'content'
        
        # Ensure all responses are classified
        for i in range(len(responses)):
            if i not in classifications:
                classifications[i] = 'content'
        
        return classifications
    
    def _generate_clean_theme_names(self, clusters: Dict, responses: List[str], activity_template: str, category: str) -> Dict[int, str]:
        """
        Generate clean, meaningful theme names from cluster keywords using LLM.
        
        Args:
            clusters: Cluster results from thematic analyzer
            responses: List of responses in clusters
            activity_template: Activity description for context
            category: 'content' or 'pedagogy'
            
        Returns:
            Dictionary mapping cluster_id to clean theme name
        """
        theme_name_map = {}
        
        try:
            themes = clusters.get('themes', {})
            if not themes:
                return theme_name_map
            
            # Collect sample responses for each theme
            theme_samples = {}
            for cluster_id, theme_keywords in themes.items():
                # Get a few sample responses from this cluster
                cluster_responses = []
                for idx, cluster_label in enumerate(clusters.get('response_to_cluster', {}).values()):
                    if cluster_label == cluster_id and idx < len(responses):
                        cluster_responses.append(responses[idx])
                        if len(cluster_responses) >= 3:  # Get 3 samples
                            break
                
                theme_samples[cluster_id] = {
                    'keywords': theme_keywords,
                    'samples': cluster_responses[:3]
                }
            
            # Generate clean names for all themes at once
            prompt = f"""Generate clean, professional theme names for student interest categories.
These are {category}-related themes from student responses about what they found interesting.

Activity Context:
{activity_template[:500]}

Theme Clusters (with keywords and sample responses):
{chr(10).join([f"Cluster {cid}: Keywords={', '.join(data['keywords'][:3])}, Samples={data['samples'][:2]}" for cid, data in list(theme_samples.items())[:10]])}

For each cluster, generate a concise, professional theme name (2-4 words) that captures the main concept.
Examples:
- "like, explore" → "Exploration Interest"
- "recombinant dna, recombinant" → "Recombinant DNA Technology"
- "gene editing, used gene" → "Gene Editing Applications"
- "activity, lego" → "Hands-on Learning Activity"

Return JSON:
{{"themes": [{{"cluster_id": 0, "name": "Vaccine Applications"}}, {{"cluster_id": 1, "name": "Gene Editing"}}, ...]}}"""

            system_message = "You are an expert at creating clear, professional theme names for educational content analysis."
            
            response = self.llm.generate_content(prompt, system_message)
            
            # Parse response
            try:
                if '```json' in response:
                    start = response.find('```json') + 7
                    end = response.find('```', start)
                    response = response[start:end].strip()
                
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    response = response[json_start:json_end]
                
                result = json.loads(response)
                theme_list = result.get('themes', [])
                
                for theme_data in theme_list:
                    cid = theme_data.get('cluster_id')
                    name = theme_data.get('name', '').strip()
                    if cid is not None and name:
                        theme_name_map[int(cid)] = name
                
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse theme name response, using keyword fallback")
                # Fallback: use first keyword capitalized
                for cid, data in theme_samples.items():
                    keywords = data['keywords']
                    if keywords:
                        # Capitalize first keyword
                        theme_name_map[cid] = keywords[0].title()
                    else:
                        theme_name_map[cid] = f"Theme {cid + 1}"
                        
        except Exception as e:
            logger.error(f"Error generating clean theme names: {str(e)}")
            # Fallback: use keywords
            themes = clusters.get('themes', {})
            for cid, keywords in themes.items():
                if keywords:
                    theme_name_map[cid] = keywords[0].title()
                else:
                    theme_name_map[cid] = f"Theme {cid + 1}"
        
        # Ensure all clusters have names
        themes = clusters.get('themes', {})
        for cid in themes.keys():
            if cid not in theme_name_map:
                keywords = themes.get(cid, ['general'])
                theme_name_map[cid] = keywords[0].title() if keywords else f"Theme {cid + 1}"
        
        return theme_name_map
    
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
