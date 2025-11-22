"""
Format Converter Module
Converts Google Forms/Quiz exit ticket format to normalized format for processing.
"""

import pandas as pd
import logging
from typing import Dict, List, Tuple, Optional
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FormatConverter:
    """Converts various exit ticket formats to the normalized format."""
    
    def __init__(self, file_path: str, question_mapping: Optional[Dict] = None):
        """
        Initialize the format converter.
        
        Args:
            file_path: Path to the Excel file
            question_mapping: Optional mapping of question text to concept/metadata
        """
        self.file_path = file_path
        self.question_mapping = question_mapping or {}
        self.df = None
        
    def detect_format(self) -> str:
        """
        Detect which format the Excel file is in.
        
        Returns:
            'google_forms' or 'normalized'
        """
        self.df = pd.read_excel(self.file_path)
        
        # Check if it has the normalized format columns
        normalized_cols = ['Student_ID', 'Question_ID', 'Student_Answer', 
                          'Correct_Answer', 'Concept', 'Question_Type', 'Course_Category']
        
        if all(col in self.df.columns for col in normalized_cols):
            logger.info("Detected normalized format")
            return 'normalized'
        
        # Check for Google Forms format (has "Points -" columns)
        points_cols = [col for col in self.df.columns if 'Points' in str(col)]
        if points_cols and ('Student_Email' in self.df.columns or 'S.No' in self.df.columns):
            logger.info("Detected Google Forms/Quiz format")
            return 'google_forms'
        
        raise ValueError("Unknown format. File must be either normalized or Google Forms format.")
    
    def extract_question_pairs(self) -> List[Tuple[str, str]]:
        """
        Extract question and points column pairs from Google Forms format.
        
        Returns:
            List of (question_col, points_col) tuples
        """
        question_pairs = []
        
        for col in self.df.columns:
            if 'Points -' in str(col):
                # Find the corresponding question column
                question_text = col.replace('Points - ', '').strip()
                
                # Find exact match in columns
                for potential_q_col in self.df.columns:
                    if potential_q_col.strip() == question_text:
                        question_pairs.append((potential_q_col, col))
                        break
        
        logger.info(f"Found {len(question_pairs)} question-points pairs")
        return question_pairs
    
    def map_question_to_metadata(self, question_text: str, question_num: int) -> Dict:
        """
        Map a question text to its metadata (concept, type, category, language).
        
        Args:
            question_text: The question text
            question_num: The question number
            
        Returns:
            Dictionary with concept, question_type, course_category, programming_language
        """
        # Check if we have a mapping for this question
        question_key = question_text.strip().lower()
        
        if question_key in self.question_mapping:
            return self.question_mapping[question_key]
        
        # Default: Try to infer from question text
        metadata = {
            'concept': 'Unknown Concept',
            'question_type': 'MCQ',
            'course_category': 'non-programming',
            'programming_language': None
        }
        
        # Infer programming language from keywords
        language_keywords = {
            'python': ['python', 'def ', 'print(', 'range(', 'for i in', 'import '],
            'java': ['java', 'public class', 'public static void', 'System.out'],
            'javascript': ['javascript', 'function ', 'const ', 'let ', 'var ', 'console.log'],
            'cpp': ['c++', 'cpp', 'cout', 'cin', '#include', 'std::']
        }
        
        question_lower = question_text.lower()
        
        for lang, keywords in language_keywords.items():
            if any(keyword in question_lower for keyword in keywords):
                metadata['programming_language'] = lang
                metadata['course_category'] = 'programming'
                break
        
        # Infer concept from question text
        concept_keywords = {
            'Loops': ['loop', 'for', 'while', 'iteration', 'break', 'continue'],
            'Functions': ['function', 'method', 'def ', 'return'],
            'Variables': ['variable', 'declaration', 'assignment'],
            'Arrays': ['array', 'list', 'index'],
            'Conditionals': ['if', 'else', 'condition', 'switch'],
            'Objects': ['object', 'class', 'instance']
        }
        
        for concept, keywords in concept_keywords.items():
            if any(keyword in question_lower for keyword in keywords):
                metadata['concept'] = concept
                break
        
        # If still unknown, use question number as concept
        if metadata['concept'] == 'Unknown Concept':
            metadata['concept'] = f"Concept Q{question_num}"
        
        # Determine question type
        if 'code' in question_lower or any(kw in question_lower for kw in ['print', 'output', 'result']):
            metadata['question_type'] = 'Code'
        
        return metadata
    
    def convert_google_forms_to_normalized(self) -> pd.DataFrame:
        """
        Convert Google Forms format to normalized format.
        
        Returns:
            DataFrame in normalized format
        """
        question_pairs = self.extract_question_pairs()
        
        if not question_pairs:
            raise ValueError("No question-points pairs found in the file")
        
        # First pass: collect correct answers for each question
        correct_answers_by_question = {}
        
        for idx, row in self.df.iterrows():
            for q_num, (question_col, points_col) in enumerate(question_pairs, start=1):
                student_answer = row[question_col]
                points = row[points_col]
                
                # If student got it right (points = 1), this is the correct answer
                if points == 1 and not pd.isna(student_answer) and str(student_answer).strip():
                    question_id = f"Q{q_num}"
                    if question_id not in correct_answers_by_question:
                        correct_answers_by_question[question_id] = str(student_answer).strip()
        
        normalized_rows = []
        
        # Second pass: create normalized rows
        for idx, row in self.df.iterrows():
            # Get student identifier
            if 'Student_Email' in self.df.columns:
                student_id = row['Student_Email']
            elif 'S.No' in self.df.columns:
                student_id = f"Student_{row['S.No']}"
            else:
                student_id = f"Student_{idx + 1}"
            
            # Process each question
            for q_num, (question_col, points_col) in enumerate(question_pairs, start=1):
                student_answer = row[question_col]
                points = row[points_col]
                
                # Skip if no answer provided
                if pd.isna(student_answer) or str(student_answer).strip() == '':
                    continue
                
                question_id = f"Q{q_num}"
                
                # Get question metadata
                metadata = self.map_question_to_metadata(question_col, q_num)
                
                # Determine correct answer
                if question_id in correct_answers_by_question:
                    correct_answer = correct_answers_by_question[question_id]
                else:
                    # No one got it right, or we couldn't find it
                    # Use the student's answer if points = 1, else mark as different
                    if points == 1:
                        correct_answer = str(student_answer).strip()
                    else:
                        # Mark as different from student answer
                        if str(student_answer).strip().upper() in ['A', 'B', 'C', 'D']:
                            options = ['A', 'B', 'C', 'D']
                            try:
                                options.remove(str(student_answer).strip().upper())
                                correct_answer = options[0]
                            except ValueError:
                                correct_answer = "CORRECT_ANSWER_UNKNOWN"
                        else:
                            correct_answer = "CORRECT_ANSWER_UNKNOWN"
                
                normalized_rows.append({
                    'Student_ID': student_id,
                    'Question_ID': question_id,
                    'Student_Answer': str(student_answer).strip(),
                    'Correct_Answer': correct_answer,
                    'Concept': metadata['concept'],
                    'Question_Type': metadata['question_type'],
                    'Course_Category': metadata['course_category'],
                    'Programming_Language': metadata['programming_language']
                })
        
        normalized_df = pd.DataFrame(normalized_rows)
        logger.info(f"Converted {len(normalized_df)} responses from Google Forms format")
        
        return normalized_df
    
    def convert(self) -> pd.DataFrame:
        """
        Auto-detect format and convert to normalized format.
        
        Returns:
            DataFrame in normalized format
        """
        format_type = self.detect_format()
        
        if format_type == 'normalized':
            logger.info("File is already in normalized format")
            return self.df
        elif format_type == 'google_forms':
            logger.info("Converting from Google Forms format to normalized format")
            return self.convert_google_forms_to_normalized()
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def save_normalized(self, output_path: str) -> None:
        """
        Convert and save to normalized format.
        
        Args:
            output_path: Path to save the normalized Excel file
        """
        normalized_df = self.convert()
        normalized_df.to_excel(output_path, index=False)
        logger.info(f"Saved normalized format to {output_path}")


def create_question_mapping_from_template(template_path: str) -> Dict:
    """
    Create a question mapping dictionary from a template file.
    
    Args:
        template_path: Path to a JSON or YAML file with question mappings
        
    Returns:
        Dictionary mapping question text to metadata
    """
    # This can be expanded to read from JSON/YAML files
    # For now, return an empty dict (use auto-inference)
    return {}

