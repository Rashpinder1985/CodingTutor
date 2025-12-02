"""
Activity Input Processor
Parses exit ticket Excel files and activity templates for qualitative analysis.
"""

import pandas as pd
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from docx import Document

logger = logging.getLogger(__name__)


class ActivityInputProcessor:
    """Processes activity-based exit tickets and templates."""
    
    def __init__(self):
        """Initialize the processor."""
        self.required_columns = ['Student_ID', 'Q1_Response', 'Q2_Response', 'Q3_Response']
    
    def load_exit_ticket_excel(self, filepath: str) -> Dict:
        """
        Load and validate exit ticket Excel file.
        
        Expected columns:
        - Student_ID: Unique student identifier
        - Q1_Response: Learning summary response
        - Q2_Response: Student questions/doubts
        - Q3_Response: Fascination/exploration responses
        
        Args:
            filepath: Path to Excel file
            
        Returns:
            Dictionary with student responses
            
        Raises:
            ValueError: If required columns are missing or data is invalid
        """
        try:
            logger.info(f"Loading exit ticket from: {filepath}")
            df = pd.read_excel(filepath)
            
            # Check for required columns
            missing_cols = [col for col in self.required_columns if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
            
            # Remove rows with all empty responses
            df = df.dropna(subset=['Q1_Response', 'Q2_Response', 'Q3_Response'], how='all')
            
            if len(df) == 0:
                raise ValueError("No valid student responses found in the file")
            
            # Convert to dictionary format
            students_data = {}
            for _, row in df.iterrows():
                student_id = str(row['Student_ID']).strip()
                if not student_id or student_id.lower() == 'nan':
                    continue
                
                students_data[student_id] = {
                    'q1': str(row['Q1_Response']) if pd.notna(row['Q1_Response']) else "",
                    'q2': str(row['Q2_Response']) if pd.notna(row['Q2_Response']) else "",
                    'q3': str(row['Q3_Response']) if pd.notna(row['Q3_Response']) else ""
                }
            
            logger.info(f"Loaded responses from {len(students_data)} students")
            return students_data
            
        except Exception as e:
            logger.error(f"Error loading exit ticket: {str(e)}")
            raise ValueError(f"Failed to load exit ticket: {str(e)}")
    
    def load_activity_template(self, filepath: str) -> str:
        """
        Load activity template from text or Word file.
        
        Args:
            filepath: Path to activity template (.txt or .docx)
            
        Returns:
            Activity description as string
            
        Raises:
            ValueError: If file format is unsupported or file cannot be read
        """
        try:
            logger.info(f"Loading activity template from: {filepath}")
            path = Path(filepath)
            
            if path.suffix.lower() == '.txt':
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
            
            elif path.suffix.lower() == '.docx':
                doc = Document(filepath)
                content = '\n'.join([para.text for para in doc.paragraphs if para.text.strip()])
            
            else:
                raise ValueError(f"Unsupported file format: {path.suffix}. Use .txt or .docx")
            
            if not content:
                raise ValueError("Activity template is empty")
            
            logger.info(f"Loaded activity template ({len(content)} characters)")
            return content
            
        except Exception as e:
            logger.error(f"Error loading activity template: {str(e)}")
            raise ValueError(f"Failed to load activity template: {str(e)}")
    
    def validate_responses(self, students_data: Dict) -> Tuple[Dict, List[str]]:
        """
        Validate and clean student responses.
        
        Args:
            students_data: Dictionary of student responses
            
        Returns:
            Tuple of (cleaned_data, warnings)
        """
        warnings = []
        cleaned_data = {}
        
        for student_id, responses in students_data.items():
            # Check for empty responses
            empty_responses = []
            if not responses['q1'] or len(responses['q1'].strip()) < 10:
                empty_responses.append('Q1')
            if not responses['q2'] or len(responses['q2'].strip()) < 10:
                empty_responses.append('Q2')
            if not responses['q3'] or len(responses['q3'].strip()) < 10:
                empty_responses.append('Q3')
            
            if empty_responses:
                warnings.append(f"Student {student_id} has short/empty responses in: {', '.join(empty_responses)}")
            
            # Keep all students, even with some empty responses
            cleaned_data[student_id] = responses
        
        logger.info(f"Validation complete: {len(cleaned_data)} students, {len(warnings)} warnings")
        return cleaned_data, warnings
    
    def get_class_size_category(self, num_students: int) -> str:
        """
        Categorize class size for sample size determination.
        
        Args:
            num_students: Number of students
            
        Returns:
            'small', 'medium', or 'large'
        """
        if num_students < 20:
            return 'small'
        elif num_students <= 50:
            return 'medium'
        else:
            return 'large'

