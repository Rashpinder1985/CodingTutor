"""
Thematic Analyzer
Clusters student responses to discover themes and ensure diversity in selection.
"""

import logging
from typing import List, Dict, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np

logger = logging.getLogger(__name__)


class ThematicAnalyzer:
    """Clusters responses into themes and ensures diverse selection."""
    
    def __init__(self, n_themes=5):
        """
        Initialize the thematic analyzer.
        
        Args:
            n_themes: Target number of themes to discover
        """
        self.n_themes = n_themes
        self.vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1
        )
        
        logger.info(f"ThematicAnalyzer initialized (n_themes={n_themes})")
    
    def cluster_responses(self, responses: List[str]) -> Dict:
        """
        Cluster responses into themes using KMeans.
        
        Args:
            responses: List of response texts
            
        Returns:
            Dictionary with:
            - clusters: {cluster_id: [response_indices]}
            - themes: {cluster_id: [theme_keywords]}
            - response_to_cluster: {response_idx: cluster_id}
        """
        try:
            if not responses or len(responses) < 2:
                logger.warning("Too few responses for clustering")
                return {
                    'clusters': {0: list(range(len(responses)))},
                    'themes': {0: ['general']},
                    'response_to_cluster': {i: 0 for i in range(len(responses))}
                }
            
            # Vectorize responses
            try:
                X = self.vectorizer.fit_transform(responses)
            except Exception as e:
                logger.error(f"Vectorization failed: {str(e)}")
                # Return single cluster
                return {
                    'clusters': {0: list(range(len(responses)))},
                    'themes': {0: ['general']},
                    'response_to_cluster': {i: 0 for i in range(len(responses))}
                }
            
            # Determine optimal number of clusters
            n_clusters = min(self.n_themes, len(responses), X.shape[0])
            n_clusters = max(1, n_clusters)  # At least 1 cluster
            
            if n_clusters == 1:
                return {
                    'clusters': {0: list(range(len(responses)))},
                    'themes': {0: self._extract_theme_keywords(X, [0] * len(responses), 0)},
                    'response_to_cluster': {i: 0 for i in range(len(responses))}
                }
            
            # Perform clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(X)
            
            # Organize results
            clusters = {}
            response_to_cluster = {}
            
            for idx, label in enumerate(cluster_labels):
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(idx)
                response_to_cluster[idx] = int(label)
            
            # Extract theme keywords for each cluster
            themes = {}
            for cluster_id in clusters.keys():
                themes[cluster_id] = self._extract_theme_keywords(X, cluster_labels, cluster_id)
            
            logger.info(f"Clustered {len(responses)} responses into {len(clusters)} themes")
            
            return {
                'clusters': clusters,
                'themes': themes,
                'response_to_cluster': response_to_cluster
            }
            
        except Exception as e:
            logger.error(f"Error clustering responses: {str(e)}")
            # Return single cluster as fallback
            return {
                'clusters': {0: list(range(len(responses)))},
                'themes': {0: ['general']},
                'response_to_cluster': {i: 0 for i in range(len(responses))}
            }
    
    def _extract_theme_keywords(self, X, cluster_labels, cluster_id: int) -> List[str]:
        """
        Extract representative keywords for a cluster.
        
        Args:
            X: TF-IDF matrix
            cluster_labels: Array of cluster assignments
            cluster_id: Cluster to extract keywords for
            
        Returns:
            List of theme keywords
        """
        try:
            # Get indices of responses in this cluster
            cluster_indices = [i for i, label in enumerate(cluster_labels) if label == cluster_id]
            
            if not cluster_indices:
                return ['general']
            
            # Get feature names
            feature_names = self.vectorizer.get_feature_names_out()
            
            # Calculate mean TF-IDF for this cluster
            cluster_vectors = X[cluster_indices].toarray()
            mean_vector = np.mean(cluster_vectors, axis=0)
            
            # Get top keywords
            top_indices = np.argsort(mean_vector)[-5:][::-1]  # Top 5
            theme_keywords = [feature_names[idx] for idx in top_indices if mean_vector[idx] > 0]
            
            # Return at least one keyword
            return theme_keywords[:3] if theme_keywords else ['general']
            
        except Exception as e:
            logger.error(f"Error extracting theme keywords: {str(e)}")
            return ['general']
    
    def ensure_diversity(self, scored_responses: List[Dict], 
                        response_to_cluster: Dict, top_n=10) -> List[Dict]:
        """
        Select top N responses ensuring diversity across themes.
        
        Args:
            scored_responses: List of response dicts with 'total_score' key
            response_to_cluster: Mapping of response index to cluster ID
            top_n: Number of responses to select
            
        Returns:
            List of top N diverse responses
        """
        try:
            if not scored_responses:
                return []
            
            # Sort all responses by score (descending)
            sorted_responses = sorted(scored_responses, 
                                     key=lambda x: x.get('total_score', 0), 
                                     reverse=True)
            
            # If fewer responses than top_n, return all
            if len(sorted_responses) <= top_n:
                return sorted_responses
            
            # Group responses by cluster
            cluster_groups = {}
            for idx, resp in enumerate(sorted_responses):
                cluster_id = response_to_cluster.get(idx, 0)
                if cluster_id not in cluster_groups:
                    cluster_groups[cluster_id] = []
                cluster_groups[cluster_id].append((idx, resp))
            
            # Strategy: Ensure at least 1 response per cluster, then fill with highest scores
            selected = []
            selected_indices = set()
            
            # Phase 1: Select best from each cluster
            for cluster_id in sorted(cluster_groups.keys()):
                if len(selected) >= top_n:
                    break
                cluster_responses = cluster_groups[cluster_id]
                # Get best response from this cluster
                for idx, resp in cluster_responses:
                    if idx not in selected_indices:
                        selected.append(resp)
                        selected_indices.add(idx)
                        break
            
            # Phase 2: Fill remaining slots with highest scores
            for idx, resp in enumerate(sorted_responses):
                if len(selected) >= top_n:
                    break
                if idx not in selected_indices:
                    selected.append(resp)
                    selected_indices.add(idx)
            
            # Sort selected by score again
            selected = sorted(selected, key=lambda x: x.get('total_score', 0), reverse=True)
            
            logger.info(f"Selected {len(selected)} responses with diversity from {len(cluster_groups)} themes")
            return selected[:top_n]
            
        except Exception as e:
            logger.error(f"Error ensuring diversity: {str(e)}")
            # Fallback: just return top N by score
            sorted_responses = sorted(scored_responses, 
                                     key=lambda x: x.get('total_score', 0), 
                                     reverse=True)
            return sorted_responses[:top_n]
    
    def get_cluster_summary(self, clusters: Dict, themes: Dict) -> str:
        """
        Generate a human-readable summary of discovered themes.
        
        Args:
            clusters: Cluster assignments
            themes: Theme keywords per cluster
            
        Returns:
            Formatted string summary
        """
        summary_lines = []
        for cluster_id in sorted(clusters.keys()):
            count = len(clusters[cluster_id])
            keywords = ', '.join(themes[cluster_id])
            summary_lines.append(f"Theme {cluster_id + 1}: {keywords} ({count} responses)")
        
        return '\n'.join(summary_lines)

