"""
Adaptive Prompt Engineering
Dynamically enhances prompts based on course characteristics and learned patterns.
"""

import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class AdaptivePromptEngine:
    """Enhances prompts with course-specific context and learned best practices."""
    
    def __init__(self, course_knowledge):
        """
        Initialize adaptive prompt engine.
        
        Args:
            course_knowledge: CourseKnowledge instance
        """
        self.knowledge = course_knowledge
        logger.info("AdaptivePromptEngine initialized")
    
    def enhance_question_prompt(self, base_prompt: str, concept: str, course_type: str,
                               course_category: Optional[str] = None, 
                               language: Optional[str] = None,
                               domain_hints: Optional[List[str]] = None) -> str:
        """
        Enhance question generation prompt with course context and learnings.
        
        Args:
            base_prompt: Original prompt
            concept: Concept being tested
            course_type: 'programming' or 'non-programming'
            course_category: Additional course category
            language: Programming language
            domain_hints: Domain keywords for context retrieval
            
        Returns:
            Enhanced prompt with adaptive guidance
        """
        try:
            # Get course context
            context = self.knowledge.get_course_context(course_type, domain_hints)
            strategy = self.knowledge.get_adaptive_strategy(course_type, concept, 
                                                           domain_hints[0] if domain_hints else None)
            
            # Build enhancement
            enhancements = []
            
            # Add best practices
            if strategy.get('best_practices'):
                enhancements.append("BEST PRACTICES (learned from similar courses):")
                for practice in strategy['best_practices'][:3]:
                    enhancements.append(f"- {practice}")
            
            # Add recommended question types
            if strategy.get('recommended_question_types'):
                enhancements.append(f"\nRECOMMENDED QUESTION TYPES for {course_type} courses:")
                for q_type in strategy['recommended_question_types']:
                    enhancements.append(f"- {q_type}")
            
            # Add difficulty approach
            if strategy.get('difficulty_approach'):
                enhancements.append(f"\nDIFFICULTY APPROACH: {strategy['difficulty_approach']}")
            
            # Add insights
            if strategy.get('insights'):
                enhancements.append(f"\nCOURSE-SPECIFIC INSIGHTS:")
                for insight in strategy['insights']:
                    enhancements.append(f"- {insight}")
            
            # Inject enhancements into prompt
            if enhancements:
                enhancement_text = "\n".join(enhancements)
                enhanced_prompt = f"""{base_prompt}

---
ADAPTIVE GUIDANCE (Based on learned patterns):
{enhancement_text}
---
"""
                logger.info(f"Enhanced prompt for {concept} with {len(enhancements)} adaptive elements")
                return enhanced_prompt
            
            return base_prompt
            
        except Exception as e:
            logger.error(f"Error enhancing question prompt: {e}")
            return base_prompt
    
    def enhance_analysis_prompt(self, base_prompt: str, activity_template: str,
                               course_type: str = 'non-programming',
                               domain_hints: Optional[List[str]] = None) -> str:
        """
        Enhance activity analysis prompt with course context.
        
        Args:
            base_prompt: Original prompt
            activity_template: Activity description
            course_type: Course type
            domain_hints: Domain keywords
            
        Returns:
            Enhanced prompt
        """
        try:
            # Get course context
            context = self.knowledge.get_course_context(course_type, domain_hints)
            strategy = self.knowledge.get_adaptive_strategy(course_type, None,
                                                           domain_hints[0] if domain_hints else None)
            
            enhancements = []
            
            # Add theme category guidance
            if strategy.get('theme_categories'):
                enhancements.append("EFFECTIVE THEME CATEGORIES (learned from similar courses):")
                for category in strategy['theme_categories']:
                    enhancements.append(f"- {category}")
            
            # Add analysis approach
            if strategy.get('analysis_approach'):
                enhancements.append(f"\nANALYSIS APPROACH: {strategy['analysis_approach']}")
            
            # Add best practices
            if strategy.get('best_practices'):
                enhancements.append("\nBEST PRACTICES:")
                for practice in strategy['best_practices'][:3]:
                    enhancements.append(f"- {practice}")
            
            # Inject enhancements
            if enhancements:
                enhancement_text = "\n".join(enhancements)
                enhanced_prompt = f"""{base_prompt}

---
ADAPTIVE GUIDANCE (Based on learned patterns):
{enhancement_text}
---
"""
                logger.info(f"Enhanced analysis prompt with {len(enhancements)} adaptive elements")
                return enhanced_prompt
            
            return base_prompt
            
        except Exception as e:
            logger.error(f"Error enhancing analysis prompt: {e}")
            return base_prompt
    
    def inject_best_practices(self, prompt: str, course_type: str) -> str:
        """
        Inject learned best practices into any prompt.
        
        Args:
            prompt: Original prompt
            course_type: Course type
            
        Returns:
            Prompt with best practices injected
        """
        try:
            context = self.knowledge.get_course_context(course_type)
            best_practices = context.get('best_practices', [])
            
            if best_practices:
                practices_text = "\n".join([f"- {p}" for p in best_practices[:5]])
                return f"""{prompt}

LEARNED BEST PRACTICES:
{practices_text}
"""
            
            return prompt
            
        except Exception as e:
            logger.error(f"Error injecting best practices: {e}")
            return prompt

