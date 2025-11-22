#!/usr/bin/env python3
"""
Adaptive Question Generation Tool - Main CLI Script
Generates personalized practice questions based on student exit ticket responses.
"""

import argparse
import sys
import yaml
import logging
from pathlib import Path
from dotenv import load_dotenv

from src.input_processor import InputProcessor
from src.question_generator import QuestionGenerator
from src.output_formatter import OutputFormatter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: str) -> dict:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config file
        
    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f"Loaded configuration from {config_path}")
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        logger.error(f"Error parsing configuration file: {e}")
        sys.exit(1)


def parse_arguments():
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Generate adaptive practice questions from student exit ticket data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input responses.xlsx
  %(prog)s --input responses.xlsx --output questions.json
  %(prog)s --input responses.xlsx --concept "loops"
  %(prog)s --input responses.xlsx --language python
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Path to Excel file with student responses'
    )
    
    parser.add_argument(
        '--output', '-o',
        default='generated_questions.json',
        help='Path for output JSON file (default: generated_questions.json)'
    )
    
    parser.add_argument(
        '--config', '-c',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    
    parser.add_argument(
        '--concept',
        help='Filter by specific concept (optional)'
    )
    
    parser.add_argument(
        '--language',
        choices=['python', 'java', 'cpp', 'javascript'],
        help='Filter by programming language (optional)'
    )
    
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Generate summary report in addition to JSON'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    return parser.parse_args()


def main():
    """Main execution function."""
    
    # Load environment variables
    load_dotenv()
    
    # Parse arguments
    args = parse_arguments()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("=" * 60)
    logger.info("Adaptive Question Generation Tool")
    logger.info("=" * 60)
    
    # Load configuration
    config = load_config(args.config)
    
    try:
        # Step 1: Process input Excel file
        logger.info("\n[Step 1/4] Processing input file...")
        processor = InputProcessor(args.input)
        processor.load_and_validate()
        processor.identify_incorrect_responses()
        concepts_data = processor.group_by_concept()
        
        if not concepts_data:
            logger.warning("No incorrect responses found. Nothing to generate.")
            sys.exit(0)
        
        # Apply filters if specified
        if args.concept:
            concepts_data = processor.filter_by_concept(args.concept)
        
        if args.language:
            concepts_data = processor.filter_by_language(args.language)
        
        if not concepts_data:
            logger.warning("No concepts match the specified filters.")
            sys.exit(0)
        
        # Get summary
        summary = processor.get_summary()
        logger.info(f"Found {summary['total_concepts']} concepts affecting "
                   f"{summary['affected_students']} students")
        
        # Step 2: Generate questions
        logger.info("\n[Step 2/4] Generating questions...")
        logger.info("This may take a few minutes depending on the number of concepts...")
        
        generator = QuestionGenerator(config)
        questions_data = generator.generate_all_concepts(concepts_data)
        
        if not questions_data:
            logger.error("Failed to generate questions")
            sys.exit(1)
        
        # Step 3: Format output
        logger.info("\n[Step 3/4] Formatting output...")
        formatter = OutputFormatter(config)
        output_data = formatter.format_output(questions_data, args.input, summary)
        
        # Step 4: Write to file
        logger.info("\n[Step 4/4] Writing output...")
        success = formatter.write_to_file(output_data, args.output)
        
        if not success:
            logger.error("Failed to write output file")
            sys.exit(1)
        
        # Write summary report if requested
        if args.summary:
            formatter.write_summary_report(output_data, args.output)
        
        # Print summary to console
        logger.info("\n" + formatter.create_summary_report(output_data))
        
        logger.info("\n" + "=" * 60)
        logger.info(f"SUCCESS! Questions written to: {args.output}")
        logger.info("=" * 60)
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()

