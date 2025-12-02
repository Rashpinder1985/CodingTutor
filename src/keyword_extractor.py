"""
Keyword Extractor
Extracts key concepts and themes from activity templates and student responses.
"""

import logging
from typing import List, Dict, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

logger = logging.getLogger(__name__)


class KeywordExtractor:
    """Extracts and scores keywords from text using TF-IDF."""
    
    def __init__(self, max_keywords=50, use_bigrams=True):
        """
        Initialize the keyword extractor.
        
        Args:
            max_keywords: Maximum number of keywords to extract
            use_bigrams: Whether to include 2-word phrases
        """
        self.max_keywords = max_keywords
        ngram_range = (1, 2) if use_bigrams else (1, 1)
        
        self.vectorizer = TfidfVectorizer(
            max_features=max_keywords,
            stop_words='english',
            ngram_range=ngram_range,
            min_df=1,
            lowercase=True
        )
        
        logger.info(f"KeywordExtractor initialized (max_keywords={max_keywords}, bigrams={use_bigrams})")
    
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
                             response_keywords: Dict[str, float]) -> float:
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

