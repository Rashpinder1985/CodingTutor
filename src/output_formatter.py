"""
Output Formatter Module
Formats generated questions into structured JSON output.
"""

import json
import logging
from datetime import datetime
from typing import Dict
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OutputFormatter:
    """Formats and writes question output to JSON files."""
    
    def __init__(self, config: Dict):
        """
        Initialize the output formatter.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.output_config = config.get('output', {})
        self.indent = self.output_config.get('indent', 2)
        self.include_metadata = self.output_config.get('include_metadata', True)
        
    def format_output(self, questions_data: Dict, source_file: str, 
                     summary: Dict) -> Dict:
        """
        Format questions into structured output.
        
        Args:
            questions_data: Dictionary of generated questions
            source_file: Path to source Excel file
            summary: Summary statistics from input processor
            
        Returns:
            Formatted output dictionary
        """
        output = {}
        
        # Add metadata if enabled
        if self.include_metadata:
            output['generation_metadata'] = self._create_metadata(
                source_file, summary
            )
        
        # Add concepts and questions
        output['concepts'] = self._format_concepts(questions_data)
        
        return output
    
    def _create_metadata(self, source_file: str, summary: Dict) -> Dict:
        """
        Create metadata section.
        
        Args:
            source_file: Path to source Excel file
            summary: Summary statistics
            
        Returns:
            Metadata dictionary
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'source_file': str(Path(source_file).name),
            'total_students': summary.get('total_students', 0),
            'affected_students': summary.get('affected_students', 0),
            'total_concepts': summary.get('total_concepts', 0),
            'total_responses': summary.get('total_responses', 0),
            'incorrect_responses': summary.get('total_incorrect', 0),
            'programming_concepts': summary.get('programming_concepts', 0),
            'non_programming_concepts': summary.get('non_programming_concepts', 0)
        }
    
    def _format_concepts(self, questions_data: Dict) -> Dict:
        """
        Format concepts section.
        
        Args:
            questions_data: Dictionary of generated questions by concept
            
        Returns:
            Formatted concepts dictionary
        """
        formatted_concepts = {}
        
        for concept_key, concept_info in questions_data.items():
            formatted_concepts[concept_key] = {
                'concept_name': concept_info['concept_name'],
                'course_category': concept_info['course_category'],
                'programming_language': concept_info.get('programming_language'),
                'affected_students': concept_info['affected_students'],
                'total_incorrect_responses': concept_info.get('total_incorrect', 0),
                'levels': self._format_levels(concept_info['levels'])
            }
        
        return formatted_concepts
    
    def _format_levels(self, levels_data: Dict) -> Dict:
        """
        Format difficulty levels section.
        
        Args:
            levels_data: Dictionary of questions by difficulty level
            
        Returns:
            Formatted levels dictionary
        """
        formatted_levels = {}
        
        for level_name, level_info in levels_data.items():
            formatted_levels[level_name] = {
                'total_questions': level_info['total_questions'],
                'required_correct': level_info['required_correct'],
                'progress_guidance': level_info.get('progress_guidance', {}),
                'questions': level_info['questions'],
                'learning_resources': level_info.get('learning_resources', [])
            }
        
        return formatted_levels
    
    def write_to_file(self, output_data: Dict, output_path: str) -> bool:
        """
        Write formatted output to JSON file.
        
        Args:
            output_data: Formatted output dictionary
            output_path: Path to output file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure parent directory exists
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write JSON file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=self.indent, ensure_ascii=False)
            
            logger.info(f"Successfully wrote output to {output_path}")
            
            # Log statistics
            self._log_statistics(output_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Error writing output file: {str(e)}")
            return False
    
    def _log_statistics(self, output_data: Dict):
        """
        Log statistics about generated questions.
        
        Args:
            output_data: Output dictionary
        """
        concepts = output_data.get('concepts', {})
        total_questions = 0
        total_concepts = len(concepts)
        
        for concept_info in concepts.values():
            levels = concept_info.get('levels', {})
            for level_info in levels.values():
                total_questions += level_info.get('total_questions', 0)
        
        logger.info(f"=== Generation Summary ===")
        logger.info(f"Total concepts: {total_concepts}")
        logger.info(f"Total questions generated: {total_questions}")
        
        if 'generation_metadata' in output_data:
            metadata = output_data['generation_metadata']
            logger.info(f"Affected students: {metadata.get('affected_students', 0)}")
            logger.info(f"Programming concepts: {metadata.get('programming_concepts', 0)}")
            logger.info(f"Non-programming concepts: {metadata.get('non_programming_concepts', 0)}")
    
    def create_summary_report(self, output_data: Dict) -> str:
        """
        Create a human-readable summary report.
        
        Args:
            output_data: Output dictionary
            
        Returns:
            Summary report as string
        """
        lines = []
        lines.append("=" * 60)
        lines.append("QUESTION GENERATION SUMMARY")
        lines.append("=" * 60)
        
        # Metadata
        if 'generation_metadata' in output_data:
            metadata = output_data['generation_metadata']
            lines.append(f"\nGeneration Time: {metadata.get('timestamp', 'N/A')}")
            lines.append(f"Source File: {metadata.get('source_file', 'N/A')}")
            lines.append(f"Total Students: {metadata.get('total_students', 0)}")
            lines.append(f"Affected Students: {metadata.get('affected_students', 0)}")
            lines.append(f"Total Concepts: {metadata.get('total_concepts', 0)}")
        
        # Concepts breakdown
        lines.append("\n" + "=" * 60)
        lines.append("CONCEPTS BREAKDOWN")
        lines.append("=" * 60)
        
        concepts = output_data.get('concepts', {})
        for concept_key, concept_info in concepts.items():
            lines.append(f"\n{concept_info['concept_name']}")
            lines.append(f"  Category: {concept_info['course_category']}")
            if concept_info.get('programming_language'):
                lines.append(f"  Language: {concept_info['programming_language']}")
            lines.append(f"  Affected Students: {len(concept_info['affected_students'])}")
            
            # Level statistics
            levels = concept_info.get('levels', {})
            for level_name, level_info in levels.items():
                lines.append(f"    {level_name.capitalize()}: "
                           f"{level_info.get('total_questions', 0)} questions "
                           f"(need {level_info.get('required_correct', 0)} correct)")
        
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)
    
    def write_summary_report(self, output_data: Dict, output_path: str) -> bool:
        """
        Write a summary report to a text file.
        
        Args:
            output_data: Output dictionary
            output_path: Path to output file (will add .summary.txt)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            summary_path = Path(output_path).with_suffix('.summary.txt')
            summary_text = self.create_summary_report(output_data)
            
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(summary_text)
            
            logger.info(f"Summary report written to {summary_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error writing summary report: {str(e)}")
            return False

