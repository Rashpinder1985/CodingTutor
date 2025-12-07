"""
Course Knowledge Base
Stores and retrieves patterns learned from different courses to improve future analyses.
"""

import logging
import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class CourseKnowledge:
    """Manages knowledge base of learned patterns from different courses."""
    
    def __init__(self, storage_path: str = "course_knowledge.json"):
        """
        Initialize the course knowledge base.
        
        Args:
            storage_path: Path to JSON file for storage (or database in future)
        """
        self.storage_path = storage_path
        self.knowledge = self._load_knowledge()
        logger.info(f"CourseKnowledge initialized with {len(self.knowledge)} course patterns")
    
    def _load_knowledge(self) -> Dict:
        """Load knowledge from storage."""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading knowledge: {e}")
            return {}
    
    def _save_knowledge(self):
        """Save knowledge to storage."""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.knowledge, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving knowledge: {e}")
    
    def get_course_context(self, course_category: str, domain_hints: Optional[List[str]] = None) -> Dict:
        """
        Retrieve relevant patterns for a course type.
        
        Args:
            course_category: 'programming' or 'non-programming'
            domain_hints: Optional list of domain keywords (e.g., ['biology', 'PCR', 'DNA'])
            
        Returns:
            Dictionary with relevant patterns and best practices
        """
        context = {
            'course_type': course_category,
            'patterns': {},
            'best_practices': [],
            'learned_insights': []
        }
        
        # Find matching knowledge entries
        for key, knowledge_entry in self.knowledge.items():
            if knowledge_entry.get('course_type') == course_category:
                # Check domain match if hints provided
                if domain_hints:
                    domain = knowledge_entry.get('domain', '').lower()
                    if any(hint.lower() in domain for hint in domain_hints):
                        context['patterns'].update(knowledge_entry.get('patterns', {}))
                        context['best_practices'].extend(knowledge_entry.get('best_practices', []))
                        context['learned_insights'].extend(knowledge_entry.get('learned_insights', []))
                else:
                    # Use general patterns for this course type
                    context['patterns'].update(knowledge_entry.get('patterns', {}))
                    context['best_practices'].extend(knowledge_entry.get('best_practices', []))
                    context['learned_insights'].extend(knowledge_entry.get('learned_insights', []))
        
        # Deduplicate
        context['best_practices'] = list(set(context['best_practices']))
        context['learned_insights'] = list(set(context['learned_insights']))
        
        return context
    
    def update_knowledge(self, course_type: str, reflection: Dict, domain: Optional[str] = None):
        """
        Update knowledge base with learnings from reflection.
        
        Args:
            course_type: 'programming' or 'non-programming'
            reflection: Reflection dictionary from reasoning agent
            domain: Optional domain identifier (e.g., 'biology', 'computer_science')
        """
        try:
            learnings = reflection.get('learnings', {})
            if not learnings:
                return
            
            # Create or update knowledge entry
            key = f"{course_type}_{domain or 'general'}"
            
            if key not in self.knowledge:
                self.knowledge[key] = {
                    'course_type': course_type,
                    'domain': domain or 'general',
                    'patterns': {},
                    'best_practices': [],
                    'learned_insights': [],
                    'quality_scores': [],
                    'usage_count': 0,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
            
            entry = self.knowledge[key]
            
            # Update patterns
            if 'effective_question_types' in learnings:
                entry['patterns']['effective_question_types'] = learnings['effective_question_types']
            if 'optimal_difficulty_approach' in learnings:
                entry['patterns']['optimal_difficulty_approach'] = learnings['optimal_difficulty_approach']
            if 'effective_theme_categories' in learnings:
                entry['patterns']['effective_theme_categories'] = learnings['effective_theme_categories']
            if 'optimal_analysis_approach' in learnings:
                entry['patterns']['optimal_analysis_approach'] = learnings['optimal_analysis_approach']
            
            # Update best practices from improvements
            improvements = reflection.get('improvements', [])
            entry['best_practices'].extend(improvements[:3])  # Top 3
            entry['best_practices'] = list(set(entry['best_practices']))[-10:]  # Keep last 10 unique
            
            # Store insights
            if 'course_specific_insights' in learnings:
                entry['learned_insights'].append(learnings['course_specific_insights'])
            if 'course_specific_patterns' in learnings:
                entry['learned_insights'].append(learnings['course_specific_patterns'])
            entry['learned_insights'] = entry['learned_insights'][-5:]  # Keep last 5
            
            # Track quality scores
            quality_score = reflection.get('quality_score', 0)
            entry['quality_scores'].append(quality_score)
            entry['quality_scores'] = entry['quality_scores'][-20:]  # Keep last 20
            
            # Update metadata
            entry['usage_count'] += 1
            entry['updated_at'] = datetime.now().isoformat()
            
            # Save
            self._save_knowledge()
            logger.info(f"Updated knowledge for {key}: {len(entry['patterns'])} patterns, quality={quality_score:.1f}")
            
        except Exception as e:
            logger.error(f"Error updating knowledge: {e}")
    
    def get_adaptive_strategy(self, course_type: str, concept: Optional[str] = None, 
                            domain: Optional[str] = None) -> Dict:
        """
        Get best practices and adaptive strategy for a course type.
        
        Args:
            course_type: 'programming' or 'non-programming'
            concept: Optional concept name
            domain: Optional domain identifier
            
        Returns:
            Dictionary with adaptive strategy recommendations
        """
        context = self.get_course_context(course_type, [domain] if domain else None)
        
        strategy = {
            'recommended_question_types': context['patterns'].get('effective_question_types', []),
            'difficulty_approach': context['patterns'].get('optimal_difficulty_approach', 'balanced'),
            'theme_categories': context['patterns'].get('effective_theme_categories', []),
            'analysis_approach': context['patterns'].get('optimal_analysis_approach', 'standard'),
            'best_practices': context['best_practices'][:5],  # Top 5
            'insights': context['learned_insights'][:3]  # Top 3
        }
        
        return strategy
    
    def get_quality_trends(self, course_type: str) -> Dict:
        """
        Get quality trends over time for a course type.
        
        Args:
            course_type: Course type to analyze
            
        Returns:
            Dictionary with quality metrics
        """
        all_scores = []
        for key, entry in self.knowledge.items():
            if entry.get('course_type') == course_type:
                all_scores.extend(entry.get('quality_scores', []))
        
        if not all_scores:
            return {'avg_score': 0, 'trend': 'no_data', 'count': 0}
        
        avg_score = sum(all_scores) / len(all_scores)
        
        # Simple trend: compare recent vs older scores
        if len(all_scores) >= 10:
            recent = all_scores[-5:]
            older = all_scores[-10:-5]
            recent_avg = sum(recent) / len(recent)
            older_avg = sum(older) / len(older)
            trend = 'improving' if recent_avg > older_avg else 'declining' if recent_avg < older_avg else 'stable'
        else:
            trend = 'insufficient_data'
        
        return {
            'avg_score': round(avg_score, 2),
            'trend': trend,
            'count': len(all_scores),
            'recent_avg': round(sum(all_scores[-5:]) / len(all_scores[-5:]), 2) if len(all_scores) >= 5 else avg_score
        }

