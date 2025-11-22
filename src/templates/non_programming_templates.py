"""
Non-Programming Question Templates
Templates for generating non-programming questions at different difficulty levels.
"""

from typing import Dict, List


class NonProgrammingTemplates:
    """Templates for non-programming questions across different subjects."""
    
    # Beginner Level: Basic MCQs
    BEGINNER_MCQ_TEMPLATES = {
        'definition': {
            'template': 'What is the definition of {concept}?',
            'type': 'mcq',
            'options_count': 4
        },
        'identification': {
            'template': 'Which of the following best describes {concept}?',
            'type': 'mcq',
            'options_count': 4
        },
        'true_false': {
            'template': 'True or False: {statement_about_concept}',
            'type': 'mcq',
            'options_count': 2
        },
        'characteristic': {
            'template': 'Which of the following is a characteristic of {concept}?',
            'type': 'mcq',
            'options_count': 4
        },
        'example': {
            'template': 'Which of the following is an example of {concept}?',
            'type': 'mcq',
            'options_count': 4
        },
        'comparison': {
            'template': 'What is the main difference between {concept} and {related_concept}?',
            'type': 'mcq',
            'options_count': 4
        }
    }
    
    # Intermediate Level: Scenario-Based MCQs
    INTERMEDIATE_SCENARIO_TEMPLATES = {
        'application': {
            'template': 'Consider the following scenario:\n{scenario}\n\nHow would you apply {concept} in this situation?',
            'type': 'scenario_mcq',
            'options_count': 4
        },
        'analysis': {
            'template': 'Read the following case:\n{case_study}\n\nWhich aspect of {concept} is most relevant here?',
            'type': 'scenario_mcq',
            'options_count': 4
        },
        'problem_solving': {
            'template': 'Given the following problem:\n{problem_description}\n\nWhich approach using {concept} would be most effective?',
            'type': 'scenario_mcq',
            'options_count': 4
        },
        'evaluation': {
            'template': 'Evaluate the following situation:\n{situation}\n\nWhat is the best course of action regarding {concept}?',
            'type': 'scenario_mcq',
            'options_count': 4
        },
        'inference': {
            'template': 'Based on the following information:\n{information}\n\nWhat can you infer about {concept}?',
            'type': 'scenario_mcq',
            'options_count': 4
        }
    }
    
    # Advanced Level: Activity-Based Questions
    ADVANCED_ACTIVITY_TEMPLATES = {
        'project_based': {
            'template': 'Design a project that demonstrates your understanding of {concept}.\n\nYour project should:\n{requirements}\n\nProvide:\n1. Project overview\n2. Implementation steps\n3. Expected outcomes\n4. How it relates to {concept}',
            'type': 'activity',
            'requires_detailed_response': True
        },
        'case_analysis': {
            'template': 'Analyze the following case study in detail:\n{detailed_case}\n\nIn your analysis:\n1. Identify how {concept} applies\n2. Evaluate the outcomes\n3. Suggest improvements\n4. Explain your reasoning',
            'type': 'activity',
            'requires_detailed_response': True
        },
        'presentation': {
            'template': 'Prepare a presentation outline on {concept} that includes:\n\n1. Introduction and importance\n2. Key components\n3. Real-world applications\n4. Common misconceptions\n5. Resources for further learning\n\nProvide your outline with brief explanations for each section.',
            'type': 'activity',
            'requires_detailed_response': True
        },
        'research': {
            'template': 'Conduct research on {concept} and answer the following:\n\n1. What are the historical origins of {concept}?\n2. How has it evolved over time?\n3. What are current trends or developments?\n4. What are practical applications?\n5. What are potential future directions?\n\nProvide sources for your research.',
            'type': 'activity',
            'requires_detailed_response': True
        },
        'comparative_analysis': {
            'template': 'Compare and contrast {concept} with {related_concept}:\n\nCreate a comprehensive analysis including:\n1. Similarities\n2. Differences\n3. Strengths and weaknesses of each\n4. When to use one over the other\n5. Examples illustrating your points',
            'type': 'activity',
            'requires_detailed_response': True
        },
        'problem_solution': {
            'template': 'Address the following complex problem:\n{complex_problem}\n\nDevelop a solution that:\n1. Applies principles of {concept}\n2. Considers multiple perspectives\n3. Addresses potential challenges\n4. Provides step-by-step implementation\n5. Includes evaluation criteria',
            'type': 'activity',
            'requires_detailed_response': True
        }
    }
    
    # Common non-programming concept categories
    CONCEPT_CATEGORIES = {
        'science': [
            'scientific method', 'hypothesis testing', 'data analysis',
            'experimental design', 'observations', 'conclusions'
        ],
        'mathematics': [
            'problem solving', 'equations', 'geometry', 'statistics',
            'probability', 'algebraic thinking', 'mathematical reasoning'
        ],
        'history': [
            'historical events', 'cause and effect', 'chronology',
            'primary sources', 'historical context', 'interpretation'
        ],
        'literature': [
            'literary devices', 'theme', 'characterization', 'plot',
            'symbolism', 'point of view', 'literary analysis'
        ],
        'social_studies': [
            'culture', 'geography', 'economics', 'government',
            'citizenship', 'social structures', 'global awareness'
        ],
        'business': [
            'marketing', 'management', 'finance', 'entrepreneurship',
            'strategy', 'operations', 'human resources'
        ],
        'arts': [
            'artistic techniques', 'composition', 'color theory',
            'art history', 'criticism', 'creative process'
        ],
        'language': [
            'grammar', 'vocabulary', 'writing skills', 'reading comprehension',
            'communication', 'rhetoric', 'linguistics'
        ]
    }
    
    @staticmethod
    def get_beginner_template(concept: str) -> Dict:
        """
        Get a beginner-level MCQ template.
        
        Args:
            concept: Subject concept
            
        Returns:
            Template dictionary
        """
        import random
        template_type = random.choice(list(NonProgrammingTemplates.BEGINNER_MCQ_TEMPLATES.keys()))
        template = NonProgrammingTemplates.BEGINNER_MCQ_TEMPLATES[template_type].copy()
        template['concept'] = concept
        template['difficulty'] = 'beginner'
        return template
    
    @staticmethod
    def get_intermediate_template(concept: str) -> Dict:
        """
        Get an intermediate-level scenario-based template.
        
        Args:
            concept: Subject concept
            
        Returns:
            Template dictionary
        """
        import random
        template_type = random.choice(list(NonProgrammingTemplates.INTERMEDIATE_SCENARIO_TEMPLATES.keys()))
        template = NonProgrammingTemplates.INTERMEDIATE_SCENARIO_TEMPLATES[template_type].copy()
        template['concept'] = concept
        template['difficulty'] = 'intermediate'
        return template
    
    @staticmethod
    def get_advanced_template(concept: str) -> Dict:
        """
        Get an advanced-level activity-based template.
        
        Args:
            concept: Subject concept
            
        Returns:
            Template dictionary
        """
        import random
        template_type = random.choice(list(NonProgrammingTemplates.ADVANCED_ACTIVITY_TEMPLATES.keys()))
        template = NonProgrammingTemplates.ADVANCED_ACTIVITY_TEMPLATES[template_type].copy()
        template['concept'] = concept
        template['difficulty'] = 'advanced'
        return template
    
    @staticmethod
    def identify_category(concept: str) -> str:
        """
        Identify the category of a concept.
        
        Args:
            concept: Subject concept
            
        Returns:
            Category name or 'general'
        """
        concept_lower = concept.lower()
        for category, keywords in NonProgrammingTemplates.CONCEPT_CATEGORIES.items():
            for keyword in keywords:
                if keyword in concept_lower or concept_lower in keyword:
                    return category
        return 'general'
    
    @staticmethod
    def get_related_concepts(concept: str) -> List[str]:
        """
        Get related concepts for a main concept.
        
        Args:
            concept: Main concept
            
        Returns:
            List of related concepts
        """
        category = NonProgrammingTemplates.identify_category(concept)
        if category != 'general':
            return NonProgrammingTemplates.CONCEPT_CATEGORIES[category]
        return [concept]

