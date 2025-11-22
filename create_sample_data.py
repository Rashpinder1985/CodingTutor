#!/usr/bin/env python3
"""
Script to create sample exit ticket data for testing.
Run this script to generate a sample Excel file.
"""

import pandas as pd


def create_sample_data():
    """Create sample exit ticket data."""
    
    data = {
        'Student_ID': [
            'S001', 'S001', 'S002', 'S003', 'S003', 
            'S004', 'S005', 'S005', 'S006', 'S007', 
            'S008', 'S009', 'S010', 'S011', 'S012'
        ],
        'Question_ID': [
            'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 
            'Q6', 'Q7', 'Q8', 'Q9', 'Q10', 
            'Q11', 'Q12', 'Q13', 'Q14', 'Q15'
        ],
        'Student_Answer': [
            'A', 'for i in range(10)', 'B', 'A', 'public void method()', 
            'C', 'Newton', 'B', 'A', 'function test()', 
            'A', 'B', 'hypothesis', 'D', 'C'
        ],
        'Correct_Answer': [
            'B', 'for i in range(5)', 'B', 'C', 'public static void main()', 
            'A', 'Einstein', 'B', 'B', 'function test() {}', 
            'A', 'A', 'theory', 'B', 'A'
        ],
        'Concept': [
            'Python Loops', 'Python Loops', 'Variables', 'Python Loops', 'Java Methods', 
            'Arrays', 'Scientific Method', 'Variables', 'Python Loops', 'JavaScript Functions', 
            'Variables', 'Python Loops', 'Scientific Method', 'Data Structures', 'Arrays'
        ],
        'Question_Type': [
            'MCQ', 'Code', 'MCQ', 'MCQ', 'Code', 
            'MCQ', 'MCQ', 'MCQ', 'MCQ', 'Code', 
            'MCQ', 'MCQ', 'MCQ', 'MCQ', 'MCQ'
        ],
        'Course_Category': [
            'programming', 'programming', 'programming', 'programming', 'programming', 
            'programming', 'non-programming', 'programming', 'programming', 'programming', 
            'programming', 'programming', 'non-programming', 'programming', 'programming'
        ],
        'Programming_Language': [
            'python', 'python', 'python', 'python', 'java', 
            'python', None, 'python', 'python', 'javascript', 
            'python', 'python', None, 'python', 'python'
        ]
    }
    
    df = pd.DataFrame(data)
    output_file = 'sample_exit_ticket.xlsx'
    df.to_excel(output_file, index=False)
    
    print(f'✓ Created sample file: {output_file}')
    print(f'  Total records: {len(df)}')
    print(f'  Incorrect responses: {len(df[df["Student_Answer"] != df["Correct_Answer"]])}')
    print()
    print('Sample concepts included:')
    incorrect = df[df["Student_Answer"] != df["Correct_Answer"]]
    for concept in incorrect['Concept'].unique():
        count = len(incorrect[incorrect['Concept'] == concept])
        print(f'  - {concept}: {count} incorrect response(s)')
    print()
    print('You can now run:')
    print(f'  python3 main.py --input {output_file}')


if __name__ == '__main__':
    try:
        create_sample_data()
    except ImportError:
        print('Error: pandas or openpyxl not installed.')
        print('Please install dependencies first:')
        print('  pip install pandas openpyxl')
    except Exception as e:
        print(f'Error creating sample data: {e}')

