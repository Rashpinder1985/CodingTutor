#!/usr/bin/env python3
"""
Export questions in platform-ready formats for coding platforms and LMS systems.
"""

import json
import argparse
from pathlib import Path
from datetime import datetime


def export_by_level(input_file: str, output_dir: str = "platform_exports"):
    """
    Export questions organized by difficulty level.
    Each level gets its own JSON file for easy upload.
    """
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Export summary
    all_questions = {
        'beginner': [],
        'intermediate': [],
        'advanced': []
    }
    
    for concept_key, concept_data in data['concepts'].items():
        concept_name = concept_data['concept_name']
        language = concept_data.get('programming_language', 'general')
        category = concept_data['course_category']
        
        for level in ['beginner', 'intermediate', 'advanced']:
            level_data = concept_data['levels'][level]
            
            for question in level_data['questions']:
                # Create platform-ready format
                platform_question = {
                    'id': question.get('question_id', f"{concept_key}_{level}"),
                    'concept': concept_name,
                    'category': category,
                    'language': language,
                    'difficulty': level,
                    'question': question.get('question', question.get('title', question.get('description', ''))),
                    'type': question.get('type', 'unknown'),
                }
                
                # Add type-specific fields
                if question.get('type') == 'mcq':
                    platform_question.update({
                        'options': question.get('options', {}),
                        'correct_answer': question.get('correct_answer', ''),
                        'explanation': question.get('explanation', '')
                    })
                elif question.get('type') in ['code_snippet', 'code_completion', 'debugging']:
                    platform_question.update({
                        'code': question.get('code', ''),
                        'task': question.get('task', ''),
                        'solution': question.get('solution', ''),
                        'explanation': question.get('explanation', '')
                    })
                elif question.get('type') in ['implementation', 'problem_solving']:
                    platform_question.update({
                        'title': question.get('title', ''),
                        'description': question.get('description', ''),
                        'function_signature': question.get('function_signature', ''),
                        'constraints': question.get('constraints', []),
                        'test_cases': question.get('test_cases', []),
                        'hints': question.get('hints', []),
                        'solution_approach': question.get('solution_approach', '')
                    })
                elif question.get('type') == 'activity':
                    platform_question.update({
                        'title': question.get('title', ''),
                        'description': question.get('description', ''),
                        'requirements': question.get('requirements', []),
                        'deliverables': question.get('deliverables', []),
                        'evaluation_criteria': question.get('evaluation_criteria', [])
                    })
                
                # Add feedback and resources
                platform_question['feedback'] = question.get('feedback', {})
                platform_question['learning_resources'] = level_data.get('learning_resources', [])
                
                all_questions[level].append(platform_question)
    
    # Export each level to separate file
    for level, questions in all_questions.items():
        if questions:
            level_file = output_path / f"{level}_questions.json"
            with open(level_file, 'w') as f:
                json.dump({
                    'level': level,
                    'total_questions': len(questions),
                    'generated_at': datetime.now().isoformat(),
                    'questions': questions
                }, f, indent=2)
            print(f"✓ Exported {len(questions)} {level} questions to: {level_file}")
    
    return output_path


def export_by_concept(input_file: str, output_dir: str = "platform_exports"):
    """
    Export questions organized by concept.
    Each concept gets its own JSON file.
    """
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    output_path = Path(output_dir) / "by_concept"
    output_path.mkdir(parents=True, exist_ok=True)
    
    for concept_key, concept_data in data['concepts'].items():
        concept_name = concept_data['concept_name']
        
        concept_export = {
            'concept': concept_name,
            'category': concept_data['course_category'],
            'language': concept_data.get('programming_language', 'general'),
            'affected_students': concept_data['affected_students'],
            'generated_at': datetime.now().isoformat(),
            'levels': {}
        }
        
        total_questions = 0
        for level in ['beginner', 'intermediate', 'advanced']:
            level_data = concept_data['levels'][level]
            concept_export['levels'][level] = {
                'total_questions': level_data['total_questions'],
                'required_correct': level_data['required_correct'],
                'questions': level_data['questions'],
                'learning_resources': level_data.get('learning_resources', []),
                'progress_guidance': level_data.get('progress_guidance', {})
            }
            total_questions += level_data['total_questions']
        
        concept_export['total_questions'] = total_questions
        
        # Save to file (use sanitized filename)
        filename = concept_key.replace('_', '-') + '.json'
        concept_file = output_path / filename
        with open(concept_file, 'w') as f:
            json.dump(concept_export, f, indent=2)
        print(f"✓ Exported {total_questions} questions for '{concept_name}' to: {concept_file}")
    
    return output_path


def export_leetcode_format(input_file: str, output_dir: str = "platform_exports"):
    """
    Export in LeetCode-compatible format for programming questions.
    """
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    output_path = Path(output_dir) / "leetcode_format"
    output_path.mkdir(parents=True, exist_ok=True)
    
    leetcode_problems = []
    
    for concept_key, concept_data in data['concepts'].items():
        if concept_data['course_category'] != 'programming':
            continue
        
        for level in ['beginner', 'intermediate', 'advanced']:
            level_data = concept_data['levels'][level]
            
            for idx, question in enumerate(level_data['questions'], 1):
                if question.get('type') in ['implementation', 'problem_solving']:
                    leetcode_problem = {
                        'questionId': f"{concept_key}_{level}_{idx}",
                        'title': question.get('title', f"{concept_data['concept_name']} - {level.title()} Problem {idx}"),
                        'difficulty': level.title(),
                        'content': question.get('description', question.get('question', '')),
                        'hints': question.get('hints', []),
                        'sampleTestCase': question.get('test_cases', [{}])[0].get('input', '') if question.get('test_cases') else '',
                        'constraints': question.get('constraints', []),
                        'topicTags': [concept_data['concept_name']],
                        'codeSnippets': [
                            {
                                'lang': concept_data.get('programming_language', 'python').title(),
                                'code': question.get('function_signature', '# Write your solution here')
                            }
                        ],
                        'testCases': [
                            {
                                'input': tc.get('input', ''),
                                'output': tc.get('expected_output', ''),
                                'explanation': tc.get('explanation', '')
                            }
                            for tc in question.get('test_cases', [])
                        ]
                    }
                    leetcode_problems.append(leetcode_problem)
    
    if leetcode_problems:
        leetcode_file = output_path / 'problems.json'
        with open(leetcode_file, 'w') as f:
            json.dump({
                'generated_at': datetime.now().isoformat(),
                'total_problems': len(leetcode_problems),
                'problems': leetcode_problems
            }, f, indent=2)
        print(f"✓ Exported {len(leetcode_problems)} LeetCode-format problems to: {leetcode_file}")
    else:
        print("⚠ No programming problems found for LeetCode export")
    
    return output_path


def export_all_formats(input_file: str):
    """Export in all available formats."""
    print("=" * 70)
    print("EXPORTING QUESTIONS IN MULTIPLE FORMATS")
    print("=" * 70)
    print()
    
    print("[1/3] Exporting by difficulty level...")
    export_by_level(input_file)
    print()
    
    print("[2/3] Exporting by concept...")
    export_by_concept(input_file)
    print()
    
    print("[3/3] Exporting in LeetCode format...")
    export_leetcode_format(input_file)
    print()
    
    print("=" * 70)
    print("✅ ALL EXPORTS COMPLETE!")
    print("=" * 70)
    print()
    print("📁 Files are in: platform_exports/")
    print()
    print("Available formats:")
    print("  • By Level: beginner_questions.json, intermediate_questions.json, advanced_questions.json")
    print("  • By Concept: by_concept/<concept-name>.json")
    print("  • LeetCode Format: leetcode_format/problems.json")
    print()


def main():
    parser = argparse.ArgumentParser(
        description='Export questions in platform-ready formats',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input generated_questions.json --all
  %(prog)s --input generated_questions.json --format level
  %(prog)s --input generated_questions.json --format concept
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        default='generated_questions.json',
        help='Input JSON file (default: generated_questions.json)'
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['level', 'concept', 'leetcode', 'all'],
        default='all',
        help='Export format (default: all)'
    )
    
    parser.add_argument(
        '--output', '-o',
        default='platform_exports',
        help='Output directory (default: platform_exports)'
    )
    
    parser.add_argument(
        '--all', '-a',
        action='store_true',
        help='Export in all formats (same as --format all)'
    )
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not Path(args.input).exists():
        print(f"❌ Error: Input file not found: {args.input}")
        print(f"   Please generate questions first using: python3 main.py --input <excel_file>")
        return
    
    # Export based on format
    if args.all or args.format == 'all':
        export_all_formats(args.input)
    elif args.format == 'level':
        export_by_level(args.input, args.output)
    elif args.format == 'concept':
        export_by_concept(args.input, args.output)
    elif args.format == 'leetcode':
        export_leetcode_format(args.input, args.output)


if __name__ == '__main__':
    main()

