"""
Input Processing Module
Parses Excel files containing student exit ticket responses and identifies areas of struggle.
Supports both normalized format and Google Forms/Quiz format.
"""

import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging
from src.format_converter import FormatConverter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InputProcessor:
    """Processes student exit ticket responses from Excel files."""
    
    REQUIRED_COLUMNS = [
        'Student_ID',
        'Question_ID',
        'Student_Answer',
        'Correct_Answer',
        'Concept',
        'Question_Type',
        'Course_Category'
    ]
    
    def __init__(self, file_path: str, question_mapping: Optional[Dict] = None):
        """
        Initialize the input processor.
        
        Args:
            file_path: Path to the Excel file containing student responses
            question_mapping: Optional mapping for Google Forms question conversion
        """
        self.file_path = file_path
        self.question_mapping = question_mapping
        self.df = None
        self.incorrect_responses = None
        self.concepts_by_category = {}
        self.original_format = None
        
    def load_and_validate(self) -> bool:
        """
        Load the Excel file and validate its structure.
        Auto-detects format and converts if needed.
        
        Returns:
            True if valid, raises exception otherwise
        """
        try:
            # Try to auto-detect and convert format if needed
            converter = FormatConverter(self.file_path, self.question_mapping)
            
            try:
                self.original_format = converter.detect_format()
                logger.info(f"Detected format: {self.original_format}")
                
                # Convert to normalized format
                self.df = converter.convert()
                
                if self.original_format == 'google_forms':
                    logger.info(f"Converted from Google Forms format: {len(self.df)} records")
                else:
                    logger.info(f"Loaded {len(self.df)} records from {self.file_path}")
                    
            except ValueError as e:
                # If format detection fails, try loading as normalized format
                logger.warning(f"Format detection failed: {e}. Trying to load as normalized format...")
                self.df = pd.read_excel(self.file_path)
                self.original_format = 'normalized'
            
            # Validate required columns
            missing_cols = set(self.REQUIRED_COLUMNS) - set(self.df.columns)
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
            
            # Check for empty dataframe
            if self.df.empty:
                raise ValueError("Excel file is empty")
            
            # Convert columns to appropriate types
            self.df['Student_ID'] = self.df['Student_ID'].astype(str)
            self.df['Question_ID'] = self.df['Question_ID'].astype(str)
            self.df['Concept'] = self.df['Concept'].astype(str)
            self.df['Course_Category'] = self.df['Course_Category'].str.lower().str.strip()
            
            # Validate course categories
            valid_categories = {'programming', 'non-programming'}
            invalid_categories = set(self.df['Course_Category'].unique()) - valid_categories
            if invalid_categories:
                logger.warning(f"Found invalid course categories: {invalid_categories}. "
                             f"Valid categories are: {valid_categories}")
            
            logger.info("Excel file validation successful")
            return True
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Excel file not found: {self.file_path}")
        except Exception as e:
            raise Exception(f"Error loading Excel file: {str(e)}")
    
    def identify_incorrect_responses(self) -> pd.DataFrame:
        """
        Identify rows where student answers don't match correct answers.
        
        Returns:
            DataFrame containing only incorrect responses
        """
        # Handle different types of answers (convert to string for comparison)
        self.df['Student_Answer_str'] = self.df['Student_Answer'].astype(str).str.strip().str.lower()
        self.df['Correct_Answer_str'] = self.df['Correct_Answer'].astype(str).str.strip().str.lower()
        
        # Identify incorrect responses
        self.incorrect_responses = self.df[
            self.df['Student_Answer_str'] != self.df['Correct_Answer_str']
        ].copy()
        
        logger.info(f"Found {len(self.incorrect_responses)} incorrect responses "
                   f"out of {len(self.df)} total responses")
        
        return self.incorrect_responses
    
    def group_by_concept(self) -> Dict[str, Dict]:
        """
        Group incorrect responses by concept and course category.
        
        Returns:
            Dictionary with concept information including affected students
        """
        if self.incorrect_responses is None:
            self.identify_incorrect_responses()
        
        if self.incorrect_responses.empty:
            logger.warning("No incorrect responses found. Nothing to generate.")
            return {}
        
        grouped_data = {}
        
        # Group by concept
        for concept in self.incorrect_responses['Concept'].unique():
            concept_df = self.incorrect_responses[
                self.incorrect_responses['Concept'] == concept
            ]
            
            # Get course category (should be same for all rows of same concept)
            course_category = concept_df['Course_Category'].iloc[0]
            
            # Get affected students
            affected_students = sorted(concept_df['Student_ID'].unique().tolist())
            
            # Get programming language if applicable
            programming_language = None
            if course_category == 'programming' and 'Programming_Language' in concept_df.columns:
                # Get the most common language for this concept
                lang_series = concept_df['Programming_Language'].dropna()
                if not lang_series.empty:
                    programming_language = lang_series.mode().iloc[0] if len(lang_series.mode()) > 0 else None
                    if programming_language:
                        programming_language = str(programming_language).lower().strip()
            
            # Create concept key (URL-friendly)
            concept_key = concept.lower().replace(' ', '_').replace('-', '_')
            
            grouped_data[concept_key] = {
                'concept_name': concept,
                'course_category': course_category,
                'programming_language': programming_language,
                'affected_students': affected_students,
                'question_types': concept_df['Question_Type'].unique().tolist(),
                'total_incorrect': len(concept_df)
            }
        
        logger.info(f"Grouped data into {len(grouped_data)} concepts")
        for concept_key, data in grouped_data.items():
            logger.info(f"  - {data['concept_name']}: {len(data['affected_students'])} students, "
                       f"{data['total_incorrect']} incorrect responses")
        
        self.concepts_by_category = grouped_data
        return grouped_data
    
    def get_concept_details(self, concept_key: str) -> Dict:
        """
        Get detailed information about a specific concept.
        
        Args:
            concept_key: The key for the concept
            
        Returns:
            Dictionary with concept details
        """
        if not self.concepts_by_category:
            self.group_by_concept()
        
        return self.concepts_by_category.get(concept_key, {})
    
    def filter_by_concept(self, concept_filter: str) -> Dict[str, Dict]:
        """
        Filter concepts by a search term.
        
        Args:
            concept_filter: String to filter concepts by
            
        Returns:
            Filtered dictionary of concepts
        """
        if not self.concepts_by_category:
            self.group_by_concept()
        
        concept_filter_lower = concept_filter.lower()
        filtered = {
            key: value for key, value in self.concepts_by_category.items()
            if concept_filter_lower in key or concept_filter_lower in value['concept_name'].lower()
        }
        
        logger.info(f"Filtered to {len(filtered)} concepts matching '{concept_filter}'")
        return filtered
    
    def filter_by_language(self, language: str) -> Dict[str, Dict]:
        """
        Filter concepts by programming language.
        
        Args:
            language: Programming language to filter by
            
        Returns:
            Filtered dictionary of concepts
        """
        if not self.concepts_by_category:
            self.group_by_concept()
        
        language_lower = language.lower()
        filtered = {
            key: value for key, value in self.concepts_by_category.items()
            if value.get('programming_language') == language_lower
        }
        
        logger.info(f"Filtered to {len(filtered)} concepts for language '{language}'")
        return filtered
    
    def get_summary(self) -> Dict:
        """
        Get a summary of the processed data.
        
        Returns:
            Dictionary with summary statistics
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_and_validate() first.")
        
        if self.incorrect_responses is None:
            self.identify_incorrect_responses()
        
        if not self.concepts_by_category:
            self.group_by_concept()
        
        return {
            'total_responses': len(self.df),
            'total_incorrect': len(self.incorrect_responses),
            'total_students': len(self.df['Student_ID'].unique()),
            'affected_students': len(self.incorrect_responses['Student_ID'].unique()),
            'total_concepts': len(self.concepts_by_category),
            'programming_concepts': len([c for c in self.concepts_by_category.values() 
                                        if c['course_category'] == 'programming']),
            'non_programming_concepts': len([c for c in self.concepts_by_category.values() 
                                           if c['course_category'] == 'non-programming'])
        }

