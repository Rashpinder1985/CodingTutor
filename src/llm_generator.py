"""
LLM Integration Module
Interfaces with Large Language Models to generate question variations and content.
"""

import os
import time
import logging
from typing import Dict, List, Optional
from openai import OpenAI
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMGenerator:
    """Generates question content using LLM APIs."""
    
    def __init__(self, config: Dict):
        """
        Initialize the LLM generator.
        
        Args:
            config: Configuration dictionary with LLM settings
        """
        self.config = config
        self.llm_config = config.get('llm', {})
        
        # Initialize OpenAI client
        api_key = os.getenv(self.llm_config.get('api_key_env', 'OPENAI_API_KEY'))
        if not api_key:
            raise ValueError(f"API key not found. Set {self.llm_config.get('api_key_env', 'OPENAI_API_KEY')} environment variable.")
        
        self.client = OpenAI(api_key=api_key)
        self.model = self.llm_config.get('model', 'gpt-4')
        self.temperature = self.llm_config.get('temperature', 0.7)
        self.max_tokens = self.llm_config.get('max_tokens', 2000)
        self.retry_attempts = self.llm_config.get('retry_attempts', 3)
        self.retry_delay = self.llm_config.get('retry_delay', 2)
        
        logger.info(f"Initialized LLM generator with model: {self.model}")
    
    def _make_api_call(self, messages: List[Dict], temperature: Optional[float] = None) -> str:
        """
        Make an API call to the LLM with retry logic.
        
        Args:
            messages: List of message dictionaries
            temperature: Override temperature setting
            
        Returns:
            Generated text response
        """
        temp = temperature if temperature is not None else self.temperature
        
        for attempt in range(self.retry_attempts):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temp,
                    max_tokens=self.max_tokens
                )
                return response.choices[0].message.content.strip()
                
            except Exception as e:
                logger.warning(f"API call attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise Exception(f"Failed to generate content after {self.retry_attempts} attempts: {str(e)}")
    
    def generate_mcq_question(self, template: Dict, concept: str, language: Optional[str] = None) -> Dict:
        """
        Generate a multiple choice question based on template.
        
        Args:
            template: Question template dictionary
            concept: Concept to test
            language: Programming language (if applicable)
            
        Returns:
            Complete question dictionary with options and answer
        """
        language_info = f" in {language}" if language else ""
        
        prompt = f"""Generate a {template['difficulty']} level multiple choice question about {concept}{language_info}.

Template type: {template.get('type', 'mcq')}
Base template: {template.get('template', '')}

Requirements:
1. Create a clear, focused question
2. Provide {template.get('options_count', 4)} answer options (label them A, B, C, D)
3. Ensure only one correct answer
4. Make distractors plausible but clearly incorrect
5. Keep language appropriate for {template['difficulty']} level
6. If code is needed, provide properly formatted code

Return ONLY a JSON object with this structure:
{{
    "question": "the question text",
    "options": {{"A": "option 1", "B": "option 2", "C": "option 3", "D": "option 4"}},
    "correct_answer": "A",
    "explanation": "why the correct answer is correct"
}}"""

        messages = [
            {"role": "system", "content": "You are an expert educator creating high-quality assessment questions."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_api_call(messages)
        
        # Parse JSON response
        try:
            # Extract JSON from response (sometimes LLM adds extra text)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                question_data = json.loads(json_str)
            else:
                question_data = json.loads(response)
            
            question_data['type'] = 'mcq'
            question_data['difficulty'] = template['difficulty']
            question_data['concept'] = concept
            if language:
                question_data['language'] = language
            
            return question_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response was: {response}")
            # Return a basic structure
            return {
                "question": response,
                "type": "mcq",
                "difficulty": template['difficulty'],
                "concept": concept,
                "note": "Failed to parse structured response"
            }
    
    def generate_code_snippet_question(self, template: Dict, concept: str, language: str) -> Dict:
        """
        Generate a code snippet question (debugging, completion, etc.).
        
        Args:
            template: Question template dictionary
            concept: Concept to test
            language: Programming language
            
        Returns:
            Complete question dictionary
        """
        prompt = f"""Generate an {template['difficulty']} level code snippet question about {concept} in {language}.

Template type: {template.get('type', 'code_snippet')}
Base template: {template.get('template', '')}

Requirements:
1. Provide a code snippet that tests understanding of {concept}
2. Make it appropriate for {template['difficulty']} level
3. If it's debugging, include a subtle but realistic bug
4. If it's fill-in-the-blank, mark blanks with ___BLANK___
5. If it's explanation, provide code that demonstrates the concept
6. Include the expected output or behavior

Return ONLY a JSON object with this structure:
{{
    "question": "the question prompt",
    "code": "the code snippet (properly formatted)",
    "task": "what the student needs to do",
    "solution": "the correct solution or answer",
    "explanation": "detailed explanation of the solution"
}}"""

        messages = [
            {"role": "system", "content": "You are an expert programming educator creating practical coding exercises."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_api_call(messages)
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                question_data = json.loads(json_str)
            else:
                question_data = json.loads(response)
            
            question_data['type'] = template.get('type', 'code_snippet')
            question_data['difficulty'] = template['difficulty']
            question_data['concept'] = concept
            question_data['language'] = language
            
            return question_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return {
                "question": response,
                "type": template.get('type', 'code_snippet'),
                "difficulty": template['difficulty'],
                "concept": concept,
                "language": language,
                "note": "Failed to parse structured response"
            }
    
    def generate_programming_problem(self, template: Dict, concept: str, language: str) -> Dict:
        """
        Generate a full programming problem with test cases.
        
        Args:
            template: Question template dictionary
            concept: Concept to test
            language: Programming language
            
        Returns:
            Complete problem dictionary with test cases
        """
        prompt = f"""Generate an {template['difficulty']} level programming problem about {concept} in {language}.

Template type: {template.get('type', 'implementation')}

Requirements:
1. Create a problem that tests deep understanding of {concept}
2. Make it challenging but solvable for {template['difficulty']} level
3. Provide clear problem description and constraints
4. Include function signature or expected format
5. Provide at least 3 test cases (input and expected output)
6. Include edge cases in test cases

Return ONLY a JSON object with this structure:
{{
    "title": "problem title",
    "description": "detailed problem description",
    "function_signature": "expected function signature",
    "constraints": ["constraint 1", "constraint 2"],
    "test_cases": [
        {{"input": "test input", "expected_output": "expected result", "explanation": "why"}},
        {{"input": "test input 2", "expected_output": "expected result 2", "explanation": "why"}}
    ],
    "hints": ["hint 1", "hint 2"],
    "solution_approach": "high-level approach to solve"
}}"""

        messages = [
            {"role": "system", "content": "You are an expert programming educator creating challenging but educational problems."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_api_call(messages, temperature=0.8)
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                question_data = json.loads(json_str)
            else:
                question_data = json.loads(response)
            
            question_data['type'] = template.get('type', 'implementation')
            question_data['difficulty'] = template['difficulty']
            question_data['concept'] = concept
            question_data['language'] = language
            
            return question_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return {
                "title": f"Problem on {concept}",
                "description": response,
                "type": template.get('type', 'implementation'),
                "difficulty": template['difficulty'],
                "concept": concept,
                "language": language,
                "note": "Failed to parse structured response"
            }
    
    def generate_scenario_question(self, template: Dict, concept: str) -> Dict:
        """
        Generate a scenario-based question for non-programming courses.
        
        Args:
            template: Question template dictionary
            concept: Concept to test
            
        Returns:
            Complete scenario question dictionary
        """
        prompt = f"""Generate an {template['difficulty']} level scenario-based question about {concept}.

Template type: {template.get('type', 'scenario_mcq')}

Requirements:
1. Create a realistic scenario that requires applying knowledge of {concept}
2. Make it appropriate for {template['difficulty']} level
3. Provide {template.get('options_count', 4)} answer options (label them A, B, C, D)
4. Ensure the scenario is relevant and engaging
5. Make students think critically about applying the concept

Return ONLY a JSON object with this structure:
{{
    "scenario": "the scenario description",
    "question": "the question based on the scenario",
    "options": {{"A": "option 1", "B": "option 2", "C": "option 3", "D": "option 4"}},
    "correct_answer": "A",
    "explanation": "why this is the best answer in this scenario"
}}"""

        messages = [
            {"role": "system", "content": "You are an expert educator creating engaging scenario-based questions."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_api_call(messages)
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                question_data = json.loads(json_str)
            else:
                question_data = json.loads(response)
            
            question_data['type'] = template.get('type', 'scenario_mcq')
            question_data['difficulty'] = template['difficulty']
            question_data['concept'] = concept
            
            return question_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return {
                "question": response,
                "type": template.get('type', 'scenario_mcq'),
                "difficulty": template['difficulty'],
                "concept": concept,
                "note": "Failed to parse structured response"
            }
    
    def generate_activity_question(self, template: Dict, concept: str) -> Dict:
        """
        Generate an activity-based question for non-programming courses.
        
        Args:
            template: Question template dictionary
            concept: Concept to test
            
        Returns:
            Complete activity question dictionary
        """
        prompt = f"""Generate an {template['difficulty']} level activity-based question about {concept}.

Template type: {template.get('type', 'activity')}

Requirements:
1. Create an engaging activity that requires deep understanding of {concept}
2. Make it appropriate for {template['difficulty']} level
3. Provide clear instructions and expectations
4. Include evaluation criteria
5. Make it practical and applicable to real-world situations

Return ONLY a JSON object with this structure:
{{
    "title": "activity title",
    "description": "what the student needs to do",
    "requirements": ["requirement 1", "requirement 2"],
    "deliverables": ["what to submit/create"],
    "evaluation_criteria": ["criterion 1", "criterion 2"],
    "guidance": "helpful guidance for completing the activity",
    "example_response": "brief example of what a good response might look like"
}}"""

        messages = [
            {"role": "system", "content": "You are an expert educator creating meaningful learning activities."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_api_call(messages, temperature=0.8)
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                question_data = json.loads(json_str)
            else:
                question_data = json.loads(response)
            
            question_data['type'] = template.get('type', 'activity')
            question_data['difficulty'] = template['difficulty']
            question_data['concept'] = concept
            
            return question_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return {
                "title": f"Activity on {concept}",
                "description": response,
                "type": template.get('type', 'activity'),
                "difficulty": template['difficulty'],
                "concept": concept,
                "note": "Failed to parse structured response"
            }
    
    def generate_feedback(self, question: Dict, concept: str) -> str:
        """
        Generate detailed feedback for a question.
        
        Args:
            question: Question dictionary
            concept: Concept being tested
            
        Returns:
            Feedback text
        """
        question_type = question.get('type', 'general')
        difficulty = question.get('difficulty', 'beginner')
        
        prompt = f"""Generate helpful feedback for students working on this {difficulty} level {question_type} question about {concept}.

The feedback should:
1. Explain common misconceptions about {concept}
2. Provide hints for understanding the concept better
3. Point out key things to remember
4. Be encouraging and educational
5. Be 2-3 sentences long

Keep it concise but informative."""

        messages = [
            {"role": "system", "content": "You are a supportive educator providing helpful feedback."},
            {"role": "user", "content": prompt}
        ]
        
        return self._make_api_call(messages, temperature=0.7)

