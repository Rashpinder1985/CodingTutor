"""
Feedback and Resources Module
Generates feedback for questions and curates learning resources.
"""

import logging
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeedbackResourceGenerator:
    """Generates feedback and curates learning resources for concepts."""
    
    def __init__(self, config: Dict):
        """
        Initialize the feedback and resource generator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.learning_resources = config.get('learning_resources', {})
        
    def generate_mcq_feedback(self, question: Dict, concept: str) -> Dict:
        """
        Generate feedback for a multiple choice question.
        
        Args:
            question: Question dictionary with options and correct answer
            concept: Concept being tested
            
        Returns:
            Feedback dictionary with explanations for each option
        """
        feedback = {
            'correct_answer': question.get('correct_answer', ''),
            'general_explanation': question.get('explanation', ''),
            'option_feedback': {}
        }
        
        # If detailed option feedback is provided, use it
        if 'option_feedback' in question:
            feedback['option_feedback'] = question['option_feedback']
        else:
            # Generate generic feedback for options
            correct = question.get('correct_answer', '')
            for option_key in question.get('options', {}).keys():
                if option_key == correct:
                    feedback['option_feedback'][option_key] = f"Correct! This is the right answer."
                else:
                    feedback['option_feedback'][option_key] = f"Incorrect. Review the concept of {concept}."
        
        # Add hints for wrong answers
        feedback['hints'] = [
            f"Review the key concepts related to {concept}",
            "Try to understand why each incorrect option doesn't work",
            "Look for patterns in similar questions"
        ]
        
        # Add common misconceptions if available
        if 'common_misconceptions' in question:
            feedback['common_misconceptions'] = question['common_misconceptions']
        else:
            feedback['common_misconceptions'] = [
                f"Common mistakes when learning {concept} include misunderstanding the basic principles",
                "Make sure you understand the context in which this concept is used"
            ]
        
        return feedback
    
    def generate_code_feedback(self, question: Dict, concept: str, language: str) -> Dict:
        """
        Generate feedback for code-based questions.
        
        Args:
            question: Question dictionary
            concept: Concept being tested
            language: Programming language
            
        Returns:
            Feedback dictionary
        """
        feedback = {
            'solution_explanation': question.get('explanation', ''),
            'key_points': [],
            'debugging_tips': [],
            'best_practices': []
        }
        
        # Add key points based on question type
        question_type = question.get('type', '')
        if question_type == 'debugging':
            feedback['debugging_tips'] = [
                f"Carefully trace through the code line by line",
                f"Pay attention to {language} syntax rules",
                f"Look for common errors related to {concept}",
                "Use print statements or a debugger to track variable values"
            ]
        elif question_type == 'code_completion':
            feedback['key_points'] = [
                f"Remember the syntax for {concept} in {language}",
                "Think about what the code is trying to accomplish",
                "Consider edge cases and error handling"
            ]
        elif question_type == 'code_explanation':
            feedback['key_points'] = [
                "Break down the code into smaller steps",
                f"Identify how {concept} is being used",
                "Think about the input and output",
                "Consider the time and space complexity"
            ]
        
        # Add language-specific best practices
        feedback['best_practices'] = self._get_language_best_practices(language, concept)
        
        # Add hints if available
        if 'hints' in question:
            feedback['hints'] = question['hints']
        
        return feedback
    
    def generate_problem_feedback(self, problem: Dict, concept: str, language: str) -> Dict:
        """
        Generate feedback for programming problems.
        
        Args:
            problem: Problem dictionary
            concept: Concept being tested
            language: Programming language
            
        Returns:
            Feedback dictionary
        """
        feedback = {
            'approach': problem.get('solution_approach', ''),
            'hints': problem.get('hints', []),
            'test_case_tips': [],
            'optimization_tips': [],
            'common_pitfalls': []
        }
        
        # Add test case tips
        feedback['test_case_tips'] = [
            "Always test with the provided test cases first",
            "Think about edge cases (empty input, single element, maximum values)",
            "Verify your solution handles all constraints",
            "Test with both typical and unusual inputs"
        ]
        
        # Add optimization tips based on difficulty
        difficulty = problem.get('difficulty', 'beginner')
        if difficulty == 'advanced':
            feedback['optimization_tips'] = [
                "Consider the time and space complexity of your solution",
                "Look for opportunities to use data structures efficiently",
                f"Think about how {concept} can be applied optimally",
                "Can you reduce redundant computations?"
            ]
        
        # Add common pitfalls
        feedback['common_pitfalls'] = [
            f"Not fully understanding how {concept} works in {language}",
            "Forgetting to handle edge cases",
            "Off-by-one errors in loops or array indexing",
            "Not considering the constraints properly"
        ]
        
        return feedback
    
    def generate_activity_feedback(self, activity: Dict, concept: str) -> Dict:
        """
        Generate feedback for activity-based questions.
        
        Args:
            activity: Activity dictionary
            concept: Concept being tested
            
        Returns:
            Feedback dictionary
        """
        feedback = {
            'evaluation_criteria': activity.get('evaluation_criteria', []),
            'guidance': activity.get('guidance', ''),
            'example_response': activity.get('example_response', ''),
            'tips_for_success': []
        }
        
        # Add tips based on activity type
        feedback['tips_for_success'] = [
            f"Ensure you thoroughly understand {concept} before starting",
            "Take time to plan your approach before diving in",
            "Use the evaluation criteria as a checklist",
            "Provide specific examples to support your work",
            "Review your work against the requirements before submitting"
        ]
        
        # Add reflection prompts
        feedback['reflection_prompts'] = [
            f"How does this activity demonstrate your understanding of {concept}?",
            "What was the most challenging part and how did you overcome it?",
            "What real-world applications can you identify for this concept?",
            "What would you do differently if you could start over?"
        ]
        
        return feedback
    
    def _get_language_best_practices(self, language: str, concept: str) -> List[str]:
        """
        Get language-specific best practices.
        
        Args:
            language: Programming language
            concept: Concept being tested
            
        Returns:
            List of best practice tips
        """
        practices = {
            'python': [
                "Follow PEP 8 style guidelines",
                "Use descriptive variable names",
                "Add docstrings to functions",
                "Use list comprehensions where appropriate"
            ],
            'java': [
                "Follow Java naming conventions",
                "Use meaningful variable and method names",
                "Add JavaDoc comments",
                "Handle exceptions appropriately"
            ],
            'cpp': [
                "Use const correctness",
                "Manage memory properly",
                "Follow RAII principles",
                "Use standard library containers"
            ],
            'javascript': [
                "Use const and let instead of var",
                "Follow ES6+ best practices",
                "Use meaningful variable names",
                "Handle async operations properly"
            ]
        }
        return practices.get(language, ["Follow language best practices", "Write clean, readable code"])
    
    def get_learning_resources(self, concept: str, course_category: str, 
                               language: Optional[str] = None) -> List[Dict]:
        """
        Get curated learning resources for a concept.
        
        Args:
            concept: Concept to find resources for
            course_category: 'programming' or 'non-programming'
            language: Programming language (if applicable)
            
        Returns:
            List of resource dictionaries with name and URL
        """
        resources = []
        
        if course_category == 'programming' and language:
            # Get language-specific resources
            lang_resources = self.learning_resources.get('programming', {}).get(language, [])
            resources.extend(lang_resources)
            
            # Add concept-specific resources
            concept_lower = concept.lower()
            additional_resources = self._get_concept_specific_resources(concept_lower, language)
            resources.extend(additional_resources)
            
        elif course_category == 'non-programming':
            # Get general non-programming resources
            general_resources = self.learning_resources.get('non-programming', {}).get('general', [])
            resources.extend(general_resources)
            
            # Add concept-specific resources
            concept_lower = concept.lower()
            additional_resources = self._get_concept_specific_resources(concept_lower, None)
            resources.extend(additional_resources)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_resources = []
        for resource in resources:
            if resource['url'] not in seen:
                seen.add(resource['url'])
                unique_resources.append(resource)
        
        logger.info(f"Found {len(unique_resources)} learning resources for {concept}")
        return unique_resources
    
    def _get_concept_specific_resources(self, concept: str, language: Optional[str]) -> List[Dict]:
        """
        Get concept-specific learning resources.
        
        Args:
            concept: Concept name (lowercase)
            language: Programming language (if applicable)
            
        Returns:
            List of resource dictionaries
        """
        resources = []
        
        # Common programming concepts
        if language:
            if 'loop' in concept or 'iteration' in concept:
                resources.append({
                    'name': f'Understanding Loops in {language.title()}',
                    'url': f'https://www.google.com/search?q={language}+loops+tutorial'
                })
            if 'function' in concept or 'method' in concept:
                resources.append({
                    'name': f'Functions in {language.title()}',
                    'url': f'https://www.google.com/search?q={language}+functions+tutorial'
                })
            if 'array' in concept or 'list' in concept:
                resources.append({
                    'name': f'Arrays and Lists in {language.title()}',
                    'url': f'https://www.google.com/search?q={language}+arrays+tutorial'
                })
            if 'class' in concept or 'object' in concept:
                resources.append({
                    'name': f'Object-Oriented Programming in {language.title()}',
                    'url': f'https://www.google.com/search?q={language}+oop+tutorial'
                })
        
        # Add general search resource as fallback
        if not resources:
            search_term = concept.replace(' ', '+')
            if language:
                search_term = f'{language}+{search_term}'
            resources.append({
                'name': f'Learn more about {concept}',
                'url': f'https://www.google.com/search?q={search_term}+tutorial'
            })
        
        return resources
    
    def create_progress_guidance(self, level: str, concept: str) -> Dict:
        """
        Create guidance for progressing through difficulty levels.
        
        Args:
            level: Current difficulty level
            concept: Concept being studied
            
        Returns:
            Progress guidance dictionary
        """
        guidance = {
            'current_level': level,
            'goal': '',
            'tips': [],
            'next_steps': []
        }
        
        if level == 'beginner':
            guidance['goal'] = f"Build foundational understanding of {concept}"
            guidance['tips'] = [
                "Focus on understanding the basic definitions and syntax",
                "Work through each question carefully",
                "Don't rush - mastery takes practice",
                "Use the learning resources if you're stuck"
            ]
            guidance['next_steps'] = [
                "Complete the beginner questions",
                "Review any mistakes and understand why",
                "Move to intermediate level when confident"
            ]
        elif level == 'intermediate':
            guidance['goal'] = f"Apply {concept} in practical scenarios"
            guidance['tips'] = [
                "Think about how concepts work in real code",
                "Practice debugging and problem-solving",
                "Try to solve before looking at hints",
                "Understand not just 'what' but 'why'"
            ]
            guidance['next_steps'] = [
                "Complete the intermediate exercises",
                "Try variations of the problems",
                "Move to advanced level when ready"
            ]
        elif level == 'advanced':
            guidance['goal'] = f"Master {concept} through complex challenges"
            guidance['tips'] = [
                "Focus on efficiency and best practices",
                "Consider edge cases and optimization",
                "Test your solutions thoroughly",
                "Understand the underlying principles deeply"
            ]
            guidance['next_steps'] = [
                "Complete the advanced problems",
                "Optimize your solutions",
                "Explore related advanced topics",
                "Help others learn this concept"
            ]
        
        return guidance

