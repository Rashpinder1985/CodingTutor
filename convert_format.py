#!/usr/bin/env python3
"""
Format Conversion Utility
Converts Google Forms/Quiz format to normalized format for the question generator.
"""

import argparse
import sys
import yaml
from pathlib import Path
from src.format_converter import FormatConverter

def load_question_mapping(mapping_path: str) -> dict:
    """Load question mapping from YAML file."""
    try:
        with open(mapping_path, 'r') as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        print(f"Warning: Question mapping file not found: {mapping_path}")
        print("Using auto-inference for concepts...")
        return {}
    except Exception as e:
        print(f"Error loading question mapping: {e}")
        return {}

def main():
    parser = argparse.ArgumentParser(
        description='Convert Google Forms/Quiz format to normalized format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input Exit_response.xlsx --output normalized_responses.xlsx
  %(prog)s --input quiz_results.xlsx --output normalized.xlsx --mapping questions.yaml
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Path to Excel file in Google Forms/Quiz format'
    )
    
    parser.add_argument(
        '--output', '-o',
        required=True,
        help='Path for output file in normalized format'
    )
    
    parser.add_argument(
        '--mapping', '-m',
        default='question_mapping_template.yaml',
        help='Path to question mapping YAML file (default: question_mapping_template.yaml)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("Format Converter - Google Forms to Normalized Format")
    print("=" * 70)
    print()
    
    try:
        # Load question mapping
        question_mapping = {}
        if Path(args.mapping).exists():
            print(f"Loading question mapping from: {args.mapping}")
            question_mapping = load_question_mapping(args.mapping)
            print(f"✓ Loaded {len(question_mapping)} question mappings")
        else:
            print(f"Note: No question mapping file found at {args.mapping}")
            print("Will use auto-inference for concepts and categories")
        print()
        
        # Create converter
        print(f"Reading file: {args.input}")
        converter = FormatConverter(args.input, question_mapping)
        
        # Detect format
        format_type = converter.detect_format()
        print(f"✓ Detected format: {format_type}")
        print()
        
        if format_type == 'normalized':
            print("File is already in normalized format. No conversion needed.")
            print("You can use this file directly with the question generator.")
            sys.exit(0)
        
        # Convert
        print("Converting to normalized format...")
        normalized_df = converter.convert()
        
        print(f"✓ Converted {len(normalized_df)} responses")
        print()
        
        # Show summary
        print("Conversion Summary:")
        print(f"  Students: {normalized_df['Student_ID'].nunique()}")
        print(f"  Questions: {normalized_df['Question_ID'].nunique()}")
        print(f"  Concepts: {normalized_df['Concept'].nunique()}")
        print(f"  Programming questions: {len(normalized_df[normalized_df['Course_Category'] == 'programming'])}")
        print(f"  Non-programming questions: {len(normalized_df[normalized_df['Course_Category'] == 'non-programming'])}")
        print()
        
        # Show concept breakdown
        print("Concepts found:")
        for concept in sorted(normalized_df['Concept'].unique()):
            count = len(normalized_df[normalized_df['Concept'] == concept])
            print(f"  - {concept}: {count} responses")
        print()
        
        # Save
        print(f"Saving normalized format to: {args.output}")
        converter.save_normalized(args.output)
        
        print()
        print("=" * 70)
        print("✓ SUCCESS! Conversion complete.")
        print("=" * 70)
        print()
        print("Next steps:")
        print(f"  1. Review the converted file: {args.output}")
        print(f"  2. Run question generator: python main.py --input {args.output}")
        print("     Or use the web interface: python web_app.py")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

