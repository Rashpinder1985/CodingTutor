"""
Question Generator Engine
Main orchestrator for generating questions using templates and LLM.
"""

import logging
from typing import Dict, List, Optional
from src.templates.programming_templates import ProgrammingTemplates
from src.templates.non_programming_templates import NonProgrammingTemplates
from src.llm_generator import LLMGenerator
from src.feedback_generator import FeedbackResourceGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QuestionGenerator:
    """Main engine for generating adaptive questions."""
    
    def __init__(self, config: Dict):
        """
        Initialize the question generator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.question_limits = config.get('question_limits', {})
        self.llm_generator = LLMGenerator(config)
        self.feedback_generator = FeedbackResourceGenerator(config)
        
        logger.info("Question generator initialized")
    
    def generate_questions_for_concept(self, concept_data: Dict) -> Dict:
        """
        Generate all levels of questions for a concept.
        
        Args:
            concept_data: Dictionary with concept information
            
        Returns:
            Dictionary with questions organized by difficulty level
        """
        concept_name = concept_data['concept_name']
        course_category = concept_data['course_category']
        language = concept_data.get('programming_language')
        
        logger.info(f"Generating questions for concept: {concept_name} ({course_category})")
        
        result = {
            'beginner': self._generate_level_questions('beginner', concept_data),
            'intermediate': self._generate_level_questions('intermediate', concept_data),
            'advanced': self._generate_level_questions('advanced', concept_data)
        }
        
        logger.info(f"Generated {sum(len(result[level]['questions']) for level in result)} total questions")
        return result
    
    def _generate_level_questions(self, level: str, concept_data: Dict) -> Dict:
        """
        Generate questions for a specific difficulty level.
        
        Args:
            level: Difficulty level (beginner, intermediate, advanced)
            concept_data: Dictionary with concept information
            
        Returns:
            Dictionary with questions and metadata for the level
        """
        concept_name = concept_data['concept_name']
        course_category = concept_data['course_category']
        language = concept_data.get('programming_language')
        
        # Get question count for this level
        level_config = self.question_limits.get(level, {})
        num_questions = level_config.get('default', 3)
        
        questions = []
        
        try:
            if course_category == 'programming':
                questions = self._generate_programming_questions(
                    level, concept_name, language, num_questions
                )
            else:
                questions = self._generate_non_programming_questions(
                    level, concept_name, num_questions
                )
        except Exception as e:
            logger.error(f"Error generating {level} questions for {concept_name}: {str(e)}")
            questions = []
        
        # Get learning resources
        resources = self.feedback_generator.get_learning_resources(
            concept_name, course_category, language
        )
        
        # Get progress guidance
        progress_guidance = self.feedback_generator.create_progress_guidance(
            level, concept_name
        )
        
        # Determine required correct answers for progression
        progression_config = self.config.get('progression', {})
        if level == 'beginner':
            required_correct = progression_config.get('beginner_to_intermediate', 3)
        elif level == 'intermediate':
            required_correct = progression_config.get('intermediate_to_advanced', 3)
        else:
            required_correct = len(questions)  # Complete all advanced questions
        
        return {
            'questions': questions,
            'total_questions': len(questions),
            'required_correct': min(required_correct, len(questions)),
            'learning_resources': resources,
            'progress_guidance': progress_guidance
        }
    
    def _generate_programming_questions(self, level: str, concept: str, 
                                       language: str, count: int) -> List[Dict]:
        """
        Generate programming questions for a specific level.
        
        Args:
            level: Difficulty level
            concept: Programming concept
            language: Programming language
            count: Number of questions to generate
            
        Returns:
            List of question dictionaries
        """
        questions = []
        
        for i in range(count):
            try:
                if level == 'beginner':
                    # MCQ questions
                    template = ProgrammingTemplates.get_beginner_template(concept, language)
                    question = self.llm_generator.generate_mcq_question(
                        template, concept, language
                    )
                    feedback = self.feedback_generator.generate_mcq_feedback(
                        question, concept
                    )
                    
                elif level == 'intermediate':
                    # Code snippet questions
                    template = ProgrammingTemplates.get_intermediate_template(concept, language)
                    question = self.llm_generator.generate_code_snippet_question(
                        template, concept, language
                    )
                    feedback = self.feedback_generator.generate_code_feedback(
                        question, concept, language
                    )
                    
                else:  # advanced
                    # Full programming problems
                    template = ProgrammingTemplates.get_advanced_template(concept, language)
                    question = self.llm_generator.generate_programming_problem(
                        template, concept, language
                    )
                    feedback = self.feedback_generator.generate_problem_feedback(
                        question, concept, language
                    )
                
                # Validate question has proper content
                if not self._validate_question(question):
                    logger.warning(f"Skipping invalid {level} question {i+1} - incomplete or missing content")
                    continue
                
                # Add question ID and feedback
                question['question_id'] = f"{level}_{language}_{i+1}"
                question['feedback'] = feedback
                questions.append(question)
                
                logger.info(f"Generated {level} programming question {i+1}/{count}")
                
            except Exception as e:
                logger.error(f"Error generating question {i+1} for {level}: {str(e)}")
                continue
        
        return questions
    
    def _generate_non_programming_questions(self, level: str, concept: str, 
                                           count: int) -> List[Dict]:
        """
        Generate non-programming questions for a specific level.
        
        Args:
            level: Difficulty level
            concept: Subject concept
            count: Number of questions to generate
            
        Returns:
            List of question dictionaries
        """
        questions = []
        
        for i in range(count):
            try:
                if level == 'beginner':
                    # Basic MCQ questions
                    template = NonProgrammingTemplates.get_beginner_template(concept)
                    question = self.llm_generator.generate_mcq_question(
                        template, concept
                    )
                    feedback = self.feedback_generator.generate_mcq_feedback(
                        question, concept
                    )
                    
                elif level == 'intermediate':
                    # Scenario-based questions
                    template = NonProgrammingTemplates.get_intermediate_template(concept)
                    question = self.llm_generator.generate_scenario_question(
                        template, concept
                    )
                    feedback = self.feedback_generator.generate_mcq_feedback(
                        question, concept
                    )
                    
                else:  # advanced
                    # Activity-based questions
                    template = NonProgrammingTemplates.get_advanced_template(concept)
                    question = self.llm_generator.generate_activity_question(
                        template, concept
                    )
                    feedback = self.feedback_generator.generate_activity_feedback(
                        question, concept
                    )
                
                # Validate question has proper content
                if not self._validate_question(question):
                    logger.warning(f"Skipping invalid {level} non-programming question {i+1} - incomplete or missing content")
                    continue
                
                # Add question ID and feedback
                question['question_id'] = f"{level}_non_prog_{i+1}"
                question['feedback'] = feedback
                questions.append(question)
                
                logger.info(f"Generated {level} non-programming question {i+1}/{count}")
                
            except Exception as e:
                logger.error(f"Error generating question {i+1} for {level}: {str(e)}")
                continue
        
        return questions
    
    def generate_all_concepts(self, concepts_data: Dict) -> Dict:
        """
        Generate questions for all concepts.
        
        Args:
            concepts_data: Dictionary of all concept data
            
        Returns:
            Dictionary with all generated questions organized by concept
        """
        all_questions = {}
        
        for concept_key, concept_data in concepts_data.items():
            logger.info(f"Processing concept: {concept_data['concept_name']}")
            
            try:
                questions = self.generate_questions_for_concept(concept_data)
                
                all_questions[concept_key] = {
                    'concept_name': concept_data['concept_name'],
                    'course_category': concept_data['course_category'],
                    'programming_language': concept_data.get('programming_language'),
                    'affected_students': concept_data['affected_students'],
                    'total_incorrect': concept_data.get('total_incorrect', 0),
                    'levels': questions
                }
                
            except Exception as e:
                logger.error(f"Error processing concept {concept_key}: {str(e)}")
                continue
        
        return all_questions
    
    def generate_filtered_questions(self, concepts_data: Dict, 
                                   concept_filter: Optional[str] = None,
                                   language_filter: Optional[str] = None) -> Dict:
        """
        Generate questions with optional filters.
        
        Args:
            concepts_data: Dictionary of all concept data
            concept_filter: Optional filter for concept name
            language_filter: Optional filter for programming language
            
        Returns:
            Dictionary with filtered and generated questions
        """
        # Apply filters
        filtered_concepts = concepts_data.copy()
        
        if concept_filter:
            concept_filter_lower = concept_filter.lower()
            filtered_concepts = {
                key: value for key, value in filtered_concepts.items()
                if concept_filter_lower in key or 
                   concept_filter_lower in value['concept_name'].lower()
            }
            logger.info(f"Filtered to {len(filtered_concepts)} concepts matching '{concept_filter}'")
        
        if language_filter:
            language_filter_lower = language_filter.lower()
            filtered_concepts = {
                key: value for key, value in filtered_concepts.items()
                if value.get('programming_language') == language_filter_lower
            }
            logger.info(f"Filtered to {len(filtered_concepts)} concepts for language '{language_filter}'")
        
        if not filtered_concepts:
            logger.warning("No concepts match the filters")
            return {}
        
        # Generate questions for filtered concepts
        return self.generate_all_concepts(filtered_concepts)
    
    def _validate_question(self, question: Dict) -> bool:
        """
        Validate that a question has all required fields and proper content.
        
        Args:
            question: Question dictionary to validate
            
        Returns:
            True if question is valid, False otherwise
        """
        # Check required fields exist
        if not question or not isinstance(question, dict):
            return False
        
        # Check question text exists and is substantial
        question_text = question.get('question', '').strip()
        if not question_text or len(question_text) < 10:
            logger.warning(f"Question text too short or empty: '{question_text}'")
            return False
        
        # Check if question text contains placeholder text
        invalid_phrases = [
            'no question text',
            '[question]',
            'question text here',
            'insert question',
            'question placeholder'
        ]
        question_lower = question_text.lower()
        if any(phrase in question_lower for phrase in invalid_phrases):
            logger.warning(f"Question contains placeholder text: '{question_text}'")
            return False
        
        # Check options exist and are valid (for MCQ)
        if question.get('type') == 'mcq':
            options = question.get('options', {})
            if not options or len(options) < 2:
                logger.warning("MCQ question missing options")
                return False
            
            # Check each option has text
            for key, value in options.items():
                if not value or len(str(value).strip()) < 2:
                    logger.warning(f"Option {key} is empty or too short")
                    return False
        
        # Check correct answer exists
        if not question.get('correct_answer'):
            logger.warning("Question missing correct answer")
            return False
        
        # Check explanation exists and is substantial
        explanation = question.get('explanation', '').strip()
        if not explanation or len(explanation) < 10:
            logger.warning("Explanation too short or empty")
            return False
        
        return True

