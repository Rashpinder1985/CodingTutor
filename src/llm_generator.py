"""
LLM Integration Module
Interfaces with Large Language Models to generate question variations and content.
"""

import os
import time
import logging
import re
from typing import Dict, List, Optional
from openai import OpenAI
import json

# Try to import Gemini, but don't fail if not installed
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fix_json_string(json_str: str) -> str:
    """
    Attempt to fix common JSON formatting issues from LLM responses.
    
    Args:
        json_str: Potentially malformed JSON string
        
    Returns:
        Fixed JSON string
    """
    # Remove markdown code blocks if present
    json_str = re.sub(r'```json\s*', '', json_str)
    json_str = re.sub(r'```\s*$', '', json_str)
    
    # Fix trailing commas before closing braces/brackets
    json_str = re.sub(r',\s*}', '}', json_str)
    json_str = re.sub(r',\s*]', ']', json_str)
    
    # Fix missing commas between properties (common LLM error)
    json_str = re.sub(r'"\s*\n\s*"', '",\n"', json_str)
    
    # Fix single quotes to double quotes
    json_str = re.sub(r"'([^']*)':", r'"\1":', json_str)
    
    return json_str.strip()


def parse_json_response(response: str, logger_instance=None) -> Optional[Dict]:
    """
    Robustly parse JSON from LLM response with multiple fallback strategies.
    
    Args:
        response: Raw response from LLM
        logger_instance: Logger instance for logging
        
    Returns:
        Parsed JSON dict or None if all attempts fail
    """
    # Strategy 1: Try direct parsing
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass
    
    # Strategy 2: Extract JSON block and try again
    try:
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        if json_start != -1 and json_end > json_start:
            json_str = response[json_start:json_end]
            return json.loads(json_str)
    except json.JSONDecodeError:
        pass
    
    # Strategy 3: Try fixing common issues and parse again
    try:
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        if json_start != -1 and json_end > json_start:
            json_str = response[json_start:json_end]
            fixed_json = fix_json_string(json_str)
            return json.loads(fixed_json)
    except json.JSONDecodeError as e:
        if logger_instance:
            # Only log as warning, not error, since we have fallback handling
            logger_instance.debug(f"JSON parse failed after fixes: {e}")
    
    # Strategy 4: Try to extract key-value pairs manually (last resort)
    try:
        result = {}
        # Look for common patterns like "key": "value" or "key": {...}
        for match in re.finditer(r'"(\w+)":\s*"([^"]*)"', response):
            result[match.group(1)] = match.group(2)
        if result:
            return result
    except Exception:
        pass
    
    return None


class LLMGenerator:
    """Generates question content using LLM APIs."""
    
    def __init__(self, config: Dict):
        """
        Initialize the LLM generator with fallback support.
        
        Args:
            config: Configuration dictionary with LLM settings
        """
        self.config = config
        self.llm_config = config.get('llm', {})
        
        # Primary provider settings
        self.provider = self.llm_config.get('provider', 'ollama').lower()
        self.model = self.llm_config.get('model', 'llama3.2')
        self.temperature = self.llm_config.get('temperature', 0.7)
        self.max_tokens = self.llm_config.get('max_tokens', 2000)
        self.retry_attempts = self.llm_config.get('retry_attempts', 3)
        self.retry_delay = self.llm_config.get('retry_delay', 2)
        
        # Fallback configuration
        self.fallback_enabled = self.llm_config.get('fallback_enabled', True)
        self.fallback_providers = self.llm_config.get('fallback_providers', [])
        
        # Initialize primary provider
        self.client = None
        self.gemini_model = None
        self._init_provider(self.provider, self.model)
        
    def _init_provider(self, provider: str, model: str, api_key_env: str = None):
        """Initialize a specific provider."""
        try:
            if provider == 'ollama':
                # Initialize Ollama client (uses OpenAI-compatible API)
                self.client = OpenAI(
                    base_url='http://localhost:11434/v1',
                    api_key='ollama'  # Ollama doesn't need a real API key
                )
                logger.info(f"Initialized LLM generator with Ollama model: {model}")
                return True
                
            elif provider == 'gemini':
                if not GEMINI_AVAILABLE:
                    logger.warning("Google Gemini SDK not installed. Install with: pip install google-generativeai")
                    return False
                
                # Get API key
                key_env = api_key_env or self.llm_config.get('api_key_env', 'GEMINI_API_KEY')
                api_key = os.getenv(key_env)
                if not api_key:
                    logger.warning(f"Gemini API key not found. Set {key_env} environment variable.")
                    return False
                
                # Initialize Gemini
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel(model)
                logger.info(f"Initialized LLM generator with Gemini model: {model}")
                return True
                
            elif provider == 'openai':
                # Initialize OpenAI client
                key_env = api_key_env or self.llm_config.get('api_key_env', 'OPENAI_API_KEY')
                api_key = os.getenv(key_env)
                if not api_key:
                    logger.warning(f"OpenAI API key not found. Set {key_env} environment variable.")
                    return False
                
                self.client = OpenAI(api_key=api_key)
                logger.info(f"Initialized LLM generator with OpenAI model: {model}")
                return True
                
            else:
                logger.error(f"Unknown provider: {provider}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize {provider}: {e}")
            return False
    
    def _make_gemini_call(self, messages: List[Dict], temperature: float) -> str:
        """Make an API call to Gemini."""
        # Convert OpenAI format to Gemini format
        prompt = "\n\n".join([f"{m['role']}: {m['content']}" for m in messages])
        
        generation_config = genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=self.max_tokens,
        )
        
        response = self.gemini_model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        return response.text.strip()
    
    def _make_api_call(self, messages: List[Dict], temperature: Optional[float] = None) -> str:
        """
        Make an API call to the LLM with retry logic and fallback support.
        
        Args:
            messages: List of message dictionaries
            temperature: Override temperature setting
            
        Returns:
            Generated text response
        """
        temp = temperature if temperature is not None else self.temperature
        
        # Try primary provider first
        for attempt in range(self.retry_attempts):
            try:
                if self.provider == 'gemini' and self.gemini_model:
                    return self._make_gemini_call(messages, temp)
                elif self.client:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=temp,
                        max_tokens=self.max_tokens
                    )
                    return response.choices[0].message.content.strip()
                else:
                    raise Exception("No client initialized")
                    
            except Exception as e:
                logger.warning(f"{self.provider.upper()} attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay)
        
        # Primary provider failed, try fallbacks
        if self.fallback_enabled and self.fallback_providers:
            logger.warning(f"Primary provider {self.provider} failed, trying fallbacks...")
            
            for fallback in self.fallback_providers:
                try:
                    fb_provider = fallback.get('provider')
                    fb_model = fallback.get('model')
                    fb_api_key_env = fallback.get('api_key_env')
                    
                    logger.info(f"Attempting fallback to {fb_provider} ({fb_model})...")
                    
                    # Initialize fallback provider
                    old_provider = self.provider
                    old_model = self.model
                    old_client = self.client
                    old_gemini = self.gemini_model
                    
                    self.provider = fb_provider
                    self.model = fb_model
                    
                    if self._init_provider(fb_provider, fb_model, fb_api_key_env):
                        # Try the fallback
                        try:
                            if fb_provider == 'gemini' and self.gemini_model:
                                result = self._make_gemini_call(messages, temp)
                            elif self.client:
                                response = self.client.chat.completions.create(
                                    model=fb_model,
                                    messages=messages,
                                    temperature=temp,
                                    max_tokens=self.max_tokens
                                )
                                result = response.choices[0].message.content.strip()
                            else:
                                continue
                            
                            logger.info(f"✓ Fallback to {fb_provider} succeeded!")
                            return result
                            
                        except Exception as fb_error:
                            logger.warning(f"Fallback to {fb_provider} failed: {fb_error}")
                            # Restore original settings
                            self.provider = old_provider
                            self.model = old_model
                            self.client = old_client
                            self.gemini_model = old_gemini
                            continue
                    
                except Exception as e:
                    logger.warning(f"Error trying fallback {fallback.get('provider')}: {e}")
                    continue
        
        # All attempts failed
        raise Exception(f"Failed to generate content after all retry attempts and fallbacks")
    
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
        
        # Parse JSON response with robust error handling
        question_data = parse_json_response(response, logger)
        
        if question_data:
            # Successfully parsed
            question_data['type'] = 'mcq'
            question_data['difficulty'] = template['difficulty']
            question_data['concept'] = concept
            if language:
                question_data['language'] = language
            return question_data
        else:
            # Stop immediately if we can't parse the response
            error_msg = f"Failed to parse LLM response for {concept}. Response: {response[:200]}..."
            logger.error(error_msg)
            raise ValueError(error_msg)
    
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
        
        question_data = parse_json_response(response, logger)
        
        if question_data:
            question_data['type'] = template.get('type', 'code_snippet')
            question_data['difficulty'] = template['difficulty']
            question_data['concept'] = concept
            question_data['language'] = language
            return question_data
        else:
            error_msg = f"Failed to parse LLM response for {concept}. Response: {response[:200]}..."
            logger.error(error_msg)
            raise ValueError(error_msg)
    
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
        
        question_data = parse_json_response(response, logger)
        
        if question_data:
            question_data['type'] = template.get('type', 'implementation')
            question_data['difficulty'] = template['difficulty']
            question_data['concept'] = concept
            question_data['language'] = language
            return question_data
        else:
            error_msg = f"Failed to parse LLM response for {concept}. Response: {response[:200]}..."
            logger.error(error_msg)
            raise ValueError(error_msg)
    
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
        
        question_data = parse_json_response(response, logger)
        
        if question_data:
            question_data['type'] = template.get('type', 'scenario_mcq')
            question_data['difficulty'] = template['difficulty']
            question_data['concept'] = concept
            return question_data
        else:
            error_msg = f"Failed to parse LLM response for {concept}. Response: {response[:200]}..."
            logger.error(error_msg)
            raise ValueError(error_msg)
    
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
        
        question_data = parse_json_response(response, logger)
        
        if question_data:
            question_data['type'] = template.get('type', 'activity')
            question_data['difficulty'] = template['difficulty']
            question_data['concept'] = concept
            return question_data
        else:
            error_msg = f"Failed to parse LLM response for {concept}. Response: {response[:200]}..."
            logger.error(error_msg)
            raise ValueError(error_msg)
    
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

