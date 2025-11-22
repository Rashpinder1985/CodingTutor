"""
Programming Question Templates
Templates for generating programming-related questions at different difficulty levels.
"""

from typing import Dict, List


class ProgrammingTemplates:
    """Templates for programming questions across different languages and levels."""
    
    # Beginner Level: Multiple Choice Questions
    BEGINNER_MCQ_TEMPLATES = {
        'syntax': {
            'template': 'What is the correct syntax for {concept} in {language}?',
            'type': 'mcq',
            'options_count': 4
        },
        'output_prediction': {
            'template': 'What will be the output of the following {language} code?\n{code}',
            'type': 'mcq',
            'options_count': 4
        },
        'concept_identification': {
            'template': 'Which of the following best describes {concept} in {language}?',
            'type': 'mcq',
            'options_count': 4
        },
        'error_identification': {
            'template': 'Which line in the following {language} code contains an error?\n{code}',
            'type': 'mcq',
            'options_count': 4
        },
        'basic_usage': {
            'template': 'In {language}, which statement correctly uses {concept}?',
            'type': 'mcq',
            'options_count': 4
        }
    }
    
    # Intermediate Level: Code Snippets
    INTERMEDIATE_SNIPPET_TEMPLATES = {
        'fill_in_blank': {
            'template': 'Complete the following {language} code snippet to {task}:\n{code_with_blanks}',
            'type': 'code_completion',
            'blanks_count': '1-2'
        },
        'debug_code': {
            'template': 'The following {language} code has a bug. Identify and fix the error:\n{buggy_code}\nExpected output: {expected_output}',
            'type': 'debugging',
        },
        'explain_code': {
            'template': 'Explain what the following {language} code does:\n{code}\nProvide a step-by-step explanation.',
            'type': 'code_explanation',
        },
        'modify_code': {
            'template': 'Modify the following {language} code to {modification_task}:\n{original_code}',
            'type': 'code_modification',
        },
        'trace_execution': {
            'template': 'Trace the execution of this {language} code and show the value of variables at each step:\n{code}',
            'type': 'execution_trace',
        }
    }
    
    # Advanced Level: Full Programs with Test Cases
    ADVANCED_PROGRAM_TEMPLATES = {
        'implement_function': {
            'template': 'Write a {language} function that {task_description}.\n\nFunction signature:\n{function_signature}\n\nRequirements:\n{requirements}',
            'type': 'implementation',
            'include_test_cases': True
        },
        'solve_problem': {
            'template': 'Solve the following problem in {language}:\n\n{problem_description}\n\nConstraints:\n{constraints}\n\nInput format:\n{input_format}\n\nOutput format:\n{output_format}',
            'type': 'problem_solving',
            'include_test_cases': True
        },
        'optimize_code': {
            'template': 'The following {language} code works but is inefficient:\n{inefficient_code}\n\nOptimize this code to improve its time/space complexity. Explain your optimization.',
            'type': 'optimization',
            'include_test_cases': True
        },
        'implement_algorithm': {
            'template': 'Implement the {algorithm_name} algorithm in {language}.\n\nDescription:\n{algorithm_description}\n\nYour implementation should handle:\n{edge_cases}',
            'type': 'algorithm_implementation',
            'include_test_cases': True
        }
    }
    
    # Language-specific syntax patterns
    LANGUAGE_SYNTAX = {
        'python': {
            'function_def': 'def function_name(parameters):',
            'loop': 'for item in iterable:',
            'conditional': 'if condition:',
            'class_def': 'class ClassName:',
            'comment': '#',
            'print': 'print()',
            'indent': '    '  # 4 spaces
        },
        'java': {
            'function_def': 'public static returnType methodName(parameters) {',
            'loop': 'for (int i = 0; i < n; i++) {',
            'conditional': 'if (condition) {',
            'class_def': 'public class ClassName {',
            'comment': '//',
            'print': 'System.out.println()',
            'indent': '    '  # 4 spaces
        },
        'cpp': {
            'function_def': 'returnType functionName(parameters) {',
            'loop': 'for (int i = 0; i < n; i++) {',
            'conditional': 'if (condition) {',
            'class_def': 'class ClassName {',
            'comment': '//',
            'print': 'cout << ',
            'indent': '    '  # 4 spaces
        },
        'javascript': {
            'function_def': 'function functionName(parameters) {',
            'loop': 'for (let i = 0; i < n; i++) {',
            'conditional': 'if (condition) {',
            'class_def': 'class ClassName {',
            'comment': '//',
            'print': 'console.log()',
            'indent': '  '  # 2 spaces
        }
    }
    
    # Common programming concepts
    PROGRAMMING_CONCEPTS = {
        'loops': ['for loops', 'while loops', 'loop control', 'nested loops', 'iteration'],
        'conditionals': ['if statements', 'else clauses', 'elif/else if', 'switch/case', 'ternary operators'],
        'functions': ['function definition', 'parameters', 'return values', 'scope', 'recursion'],
        'arrays': ['array declaration', 'array indexing', 'array methods', 'multidimensional arrays'],
        'strings': ['string manipulation', 'string methods', 'string concatenation', 'string formatting'],
        'objects': ['object creation', 'properties', 'methods', 'this/self keyword'],
        'classes': ['class definition', 'constructors', 'inheritance', 'polymorphism'],
        'data_structures': ['lists', 'dictionaries', 'sets', 'tuples', 'stacks', 'queues'],
        'algorithms': ['sorting', 'searching', 'recursion', 'dynamic programming'],
        'error_handling': ['try-catch', 'exceptions', 'error types', 'debugging']
    }
    
    @staticmethod
    def get_beginner_template(concept: str, language: str) -> Dict:
        """
        Get a beginner-level MCQ template.
        
        Args:
            concept: Programming concept
            language: Programming language
            
        Returns:
            Template dictionary
        """
        # Cycle through different template types
        import random
        template_type = random.choice(list(ProgrammingTemplates.BEGINNER_MCQ_TEMPLATES.keys()))
        template = ProgrammingTemplates.BEGINNER_MCQ_TEMPLATES[template_type].copy()
        template['concept'] = concept
        template['language'] = language
        template['difficulty'] = 'beginner'
        return template
    
    @staticmethod
    def get_intermediate_template(concept: str, language: str) -> Dict:
        """
        Get an intermediate-level code snippet template.
        
        Args:
            concept: Programming concept
            language: Programming language
            
        Returns:
            Template dictionary
        """
        import random
        template_type = random.choice(list(ProgrammingTemplates.INTERMEDIATE_SNIPPET_TEMPLATES.keys()))
        template = ProgrammingTemplates.INTERMEDIATE_SNIPPET_TEMPLATES[template_type].copy()
        template['concept'] = concept
        template['language'] = language
        template['difficulty'] = 'intermediate'
        return template
    
    @staticmethod
    def get_advanced_template(concept: str, language: str) -> Dict:
        """
        Get an advanced-level programming problem template.
        
        Args:
            concept: Programming concept
            language: Programming language
            
        Returns:
            Template dictionary
        """
        import random
        template_type = random.choice(list(ProgrammingTemplates.ADVANCED_PROGRAM_TEMPLATES.keys()))
        template = ProgrammingTemplates.ADVANCED_PROGRAM_TEMPLATES[template_type].copy()
        template['concept'] = concept
        template['language'] = language
        template['difficulty'] = 'advanced'
        return template
    
    @staticmethod
    def get_language_syntax(language: str) -> Dict:
        """
        Get syntax patterns for a specific language.
        
        Args:
            language: Programming language
            
        Returns:
            Dictionary of syntax patterns
        """
        return ProgrammingTemplates.LANGUAGE_SYNTAX.get(language, {})
    
    @staticmethod
    def get_related_subconcepts(concept: str) -> List[str]:
        """
        Get related subconcepts for a main concept.
        
        Args:
            concept: Main programming concept
            
        Returns:
            List of related subconcepts
        """
        concept_lower = concept.lower()
        for key, subconcepts in ProgrammingTemplates.PROGRAMMING_CONCEPTS.items():
            if key in concept_lower or concept_lower in key:
                return subconcepts
        return [concept]

