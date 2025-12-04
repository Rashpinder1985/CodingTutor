"""
Keyword Extractor
Extracts key concepts and themes from activity templates and student responses.
"""

import logging
import json
from typing import List, Dict, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

logger = logging.getLogger(__name__)


class KeywordExtractor:
    """Extracts and scores keywords from text using TF-IDF and LLM."""
    
    def __init__(self, max_keywords=50, use_bigrams=True, llm_generator=None):
        """
        Initialize the keyword extractor.
        
        Args:
            max_keywords: Maximum number of keywords to extract
            use_bigrams: Whether to include 2-word phrases
            llm_generator: Optional LLMGenerator instance for concept extraction
        """
        self.max_keywords = max_keywords
        self.llm_generator = llm_generator
        ngram_range = (1, 2) if use_bigrams else (1, 1)
        
        self.vectorizer = TfidfVectorizer(
            max_features=max_keywords,
            stop_words='english',
            ngram_range=ngram_range,
            min_df=1,
            lowercase=True
        )
        
        logger.info(f"KeywordExtractor initialized (max_keywords={max_keywords}, bigrams={use_bigrams}, llm_enabled={llm_generator is not None})")
    
    def extract_activity_keywords(self, activity_text: str) -> List[Tuple[str, float]]:
        """
        Extract key concepts from activity template.
        
        Args:
            activity_text: Activity description text
            
        Returns:
            List of (keyword, score) tuples sorted by importance
        """
        try:
            # Clean text
            activity_text = self._clean_text(activity_text)
            
            if not activity_text or len(activity_text) < 50:
                logger.warning("Activity text too short for keyword extraction")
                return []
            
            # Fit vectorizer on activity text (treat as single document)
            tfidf_matrix = self.vectorizer.fit_transform([activity_text])
            
            # Get feature names and scores
            feature_names = self.vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]
            
            # Create keyword-score pairs
            keywords = [(feature_names[i], scores[i]) for i in range(len(feature_names))]
            
            # Sort by score descending
            keywords = sorted(keywords, key=lambda x: x[1], reverse=True)
            
            # Filter out low scores
            keywords = [(k, s) for k, s in keywords if s > 0.01]
            
            logger.info(f"Extracted {len(keywords)} keywords from activity template")
            return keywords
            
        except Exception as e:
            logger.error(f"Error extracting activity keywords: {str(e)}")
            return []
    
    def extract_response_keywords(self, responses: List[str]) -> Dict[str, float]:
        """
        Extract emergent keywords from all student responses.
        
        Args:
            responses: List of student response texts
            
        Returns:
            Dictionary of {keyword: importance_score}
        """
        try:
            # Clean responses
            cleaned_responses = [self._clean_text(r) for r in responses if r and len(r) > 10]
            
            if not cleaned_responses:
                logger.warning("No valid responses for keyword extraction")
                return {}
            
            # Fit vectorizer on all responses
            tfidf_matrix = self.vectorizer.fit_transform(cleaned_responses)
            
            # Get feature names
            feature_names = self.vectorizer.get_feature_names_out()
            
            # Calculate mean TF-IDF score across all documents
            mean_scores = np.mean(tfidf_matrix.toarray(), axis=0)
            
            # Create keyword dictionary
            keywords = {feature_names[i]: mean_scores[i] for i in range(len(feature_names))}
            
            # Filter low scores
            keywords = {k: v for k, v in keywords.items() if v > 0.01}
            
            logger.info(f"Extracted {len(keywords)} emergent keywords from {len(cleaned_responses)} responses")
            return keywords
            
        except Exception as e:
            logger.error(f"Error extracting response keywords: {str(e)}")
            return {}
    
    def score_keyword_overlap(self, response: str, activity_keywords: List[Tuple[str, float]], 
                             response_keywords: Dict[str, float] = None) -> float:
        """
        Score how well a response matches activity keywords.
        
        Args:
            response: Student response text
            activity_keywords: List of (keyword, score) from activity
            response_keywords: Dictionary of emergent keywords (optional, for bonus)
            
        Returns:
            Score from 0-100
        """
        try:
            response = self._clean_text(response)
            
            if not response or not activity_keywords:
                return 0.0
            
            # Extract activity keyword strings
            activity_kw_list = [kw for kw, _ in activity_keywords]
            activity_kw_weights = {kw: score for kw, score in activity_keywords}
            
            # Count keyword matches with weights
            total_weight = 0.0
            matched_weight = 0.0
            
            for keyword, weight in activity_keywords:
                total_weight += weight
                # Check if keyword appears in response (case-insensitive, word boundary)
                if self._keyword_in_text(keyword, response):
                    matched_weight += weight
            
            # Calculate base score (0-100)
            if total_weight > 0:
                base_score = (matched_weight / total_weight) * 100
            else:
                base_score = 0.0
            
            # Bonus for emergent keywords (up to 20 points)
            bonus = 0.0
            if response_keywords:
                emergent_matches = sum(1 for kw in response_keywords.keys() 
                                      if self._keyword_in_text(kw, response))
                bonus = min(20, emergent_matches * 2)
            
            final_score = min(100, base_score + bonus)
            
            return round(final_score, 2)
            
        except Exception as e:
            logger.error(f"Error scoring keyword overlap: {str(e)}")
            return 0.0
    
    def score_concept_keyword_overlap(self, response: str, concept_keywords: List[str]) -> float:
        """
        Score how well a response matches concept keywords (for Q1 cognitive domain measurement).
        
        Args:
            response: Student response text
            concept_keywords: List of concept keywords from activity template
            
        Returns:
            Score from 0-100 based on concept keyword matches
        """
        try:
            response = self._clean_text(response)
            
            if not response or not concept_keywords:
                return 0.0
            
            # Count concept keyword matches (each concept match is worth equal weight)
            matches = 0
            for concept in concept_keywords:
                if self._keyword_in_text(concept, response):
                    matches += 1
            
            # Score: percentage of concepts mentioned (capped at 100)
            # More lenient scoring - reward partial matches
            if len(concept_keywords) > 0:
                # Base score: percentage of concepts mentioned
                base_score = (matches / len(concept_keywords)) * 100
                
                # More generous scoring:
                # - If at least 1 concept mentioned, give minimum 30 points
                # - Boost for multiple concepts
                if matches >= 1:
                    score = max(30, base_score)  # Minimum 30 for any concept match
                else:
                    score = base_score
                
                # Boost score if multiple concepts mentioned (shows better understanding)
                if matches >= 2:
                    score = min(100, score * 1.3)  # 30% boost for 2+ concepts
                elif matches >= 1:
                    score = min(100, score * 1.1)  # 10% boost for 1+ concept
                
                return round(min(100, score), 2)
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Error scoring concept keyword overlap: {str(e)}")
            return 0.0
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        
        return text.strip()
    
    def _keyword_in_text(self, keyword: str, text: str) -> bool:
        """
        Check if keyword appears in text (word boundary aware).
        
        Args:
            keyword: Keyword to search for
            text: Text to search in
            
        Returns:
            True if keyword found
        """
        # For multi-word keywords, check for exact phrase
        if ' ' in keyword:
            return keyword.lower() in text.lower()
        
        # For single words, use word boundaries
        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
        return bool(re.search(pattern, text.lower()))
    
    def extract_concept_keywords_llm(self, activity_text: str) -> List[str]:
        """
        Extract concept-related keywords from activity template using LLM.
        Filters out generic English vocabulary and focuses on domain-specific concepts.
        
        Args:
            activity_text: Activity description text
            
        Returns:
            List of concept keywords (e.g., ["PCR", "Plasmid", "Recombinant DNA"])
        """
        if not self.llm_generator:
            logger.warning("LLM generator not available, falling back to TF-IDF extraction")
            # Fallback to regular extraction
            keywords = self.extract_activity_keywords(activity_text)
            return [kw for kw, _ in keywords[:20]]  # Return top 20 as concepts
        
        try:
            prompt = f"""Extract the key CONCEPT-RELATED keywords from this activity description.
Focus ONLY on domain-specific concepts, technical terms, and subject matter topics.
EXCLUDE generic English vocabulary, common words, and non-technical terms.

Activity Description:
{activity_text[:2000]}

Return a JSON array of concept keywords (e.g., ["PCR", "Plasmid", "Recombinant DNA", "Restriction Enzymes"]).
Each keyword should be a specific concept, technique, or topic discussed in the activity.
Do NOT include generic words like "learn", "understand", "activity", "lesson", etc.

Output format:
{{"concepts": ["concept1", "concept2", "concept3", ...]}}"""

            system_message = "You are an expert at identifying domain-specific concepts and technical terms in educational content."
            
            response = self.llm_generator.generate_content(prompt, system_message)
            
            # Parse JSON response
            try:
                if '```json' in response:
                    start = response.find('```json') + 7
                    end = response.find('```', start)
                    response = response[start:end].strip()
                elif '```' in response:
                    start = response.find('```') + 3
                    end = response.find('```', start)
                    response = response[start:end].strip()
                
                # Try to find JSON object
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    response = response[json_start:json_end]
                
                result = json.loads(response)
                concepts = result.get('concepts', [])
                
                # Filter and clean concepts
                concepts = [c.strip() for c in concepts if c and len(c.strip()) > 1]
                concepts = [c for c in concepts if not c.lower() in ['the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must']]
                
                logger.info(f"Extracted {len(concepts)} concept keywords using LLM")
                return concepts[:30]  # Limit to top 30 concepts
                
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse LLM response as JSON, attempting text extraction")
                # Fallback: try to extract concepts from text response
                lines = response.split('\n')
                concepts = []
                for line in lines:
                    line = line.strip()
                    if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                        concept = line.lstrip('-•*').strip()
                        if concept and len(concept) > 1:
                            concepts.append(concept)
                    elif ':' in line or ',' in line:
                        # Try to extract from structured text
                        parts = re.split(r'[:,]', line)
                        for part in parts:
                            part = part.strip()
                            if part and len(part) > 1 and not part.lower() in ['concepts', 'keywords', 'terms']:
                                concepts.append(part)
                
                if concepts:
                    logger.info(f"Extracted {len(concepts)} concept keywords from text fallback")
                    return concepts[:30]
                else:
                    # Final fallback to TF-IDF
                    keywords = self.extract_activity_keywords(activity_text)
                    return [kw for kw, _ in keywords[:20]]
                    
        except Exception as e:
            logger.error(f"Error extracting concept keywords with LLM: {str(e)}")
            # Fallback to TF-IDF extraction
            keywords = self.extract_activity_keywords(activity_text)
            return [kw for kw, _ in keywords[:20]]


