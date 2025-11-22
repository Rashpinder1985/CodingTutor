# Adaptive Question Generation Tool for Teachers

An intelligent CLI tool that analyzes student exit ticket responses and generates personalized, multi-level practice questions to help students build conceptual proficiency.

## Features

- **Adaptive Question Generation**: Generates questions at three difficulty levels (beginner, intermediate, advanced)
- **Multi-Language Support**: Supports Python, Java, C++, and JavaScript for programming courses
- **Hybrid Approach**: Combines question templates with LLM-powered variations for diverse questions
- **Comprehensive Feedback**: Provides detailed explanations and feedback for each question
- **Learning Resources**: Suggests curated open-source learning materials
- **Concept-Based Grouping**: Organizes questions by concepts where students struggled

## Installation

1. Clone the repository or download the source code

2. Create and activate a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your API key:
   - Create a `.env` file in the project root
   - Add your OpenAI API key: `OPENAI_API_KEY=your_key_here`

5. (Optional) Customize configuration in `config.yaml`

## Quick Start

Generate sample data to test the tool:
```bash
python3 create_sample_data.py
```

Then generate questions:
```bash
python3 main.py --input sample_exit_ticket.xlsx
```

For detailed usage instructions, see `USAGE_GUIDE.md`.

## Usage

Basic usage:
```bash
python main.py --input exit_ticket_responses.xlsx
```

With custom output file:
```bash
python main.py --input exit_ticket_responses.xlsx --output my_questions.json
```

Filter by specific concept:
```bash
python main.py --input exit_ticket_responses.xlsx --concept "loops"
```

Filter by programming language:
```bash
python main.py --input exit_ticket_responses.xlsx --language python
```

## Input Format

The input Excel file should have the following columns:
- `Student_ID`: Unique identifier for the student
- `Question_ID`: Identifier for the exit ticket question
- `Student_Answer`: The answer provided by the student
- `Correct_Answer`: The correct answer
- `Concept`: The concept/topic being tested
- `Question_Type`: Type of question (e.g., "MCQ", "Code")
- `Course_Category`: Either "programming" or "non-programming"

For programming courses, optionally include:
- `Programming_Language`: The programming language (python, java, cpp, javascript)

## Output Format

The tool generates a JSON file with the following structure:
```json
{
  "generation_metadata": {
    "timestamp": "2025-11-22T10:30:00Z",
    "source_file": "exit_ticket_responses.xlsx",
    "total_students": 25,
    "total_concepts": 5
  },
  "concepts": {
    "concept_key": {
      "concept_name": "Concept Name",
      "course_category": "programming",
      "programming_language": "python",
      "affected_students": ["S001", "S003"],
      "levels": {
        "beginner": {
          "questions": [...],
          "required_correct": 3,
          "learning_resources": [...]
        },
        "intermediate": {...},
        "advanced": {...}
      }
    }
  }
}
```

## Question Types

### Programming Courses
- **Beginner**: Multiple Choice Questions (MCQs) on syntax and basic concepts
- **Intermediate**: Code snippets (fill-in-the-blank, debugging, code explanation)
- **Advanced**: Full programming problems with test cases

### Non-Programming Courses
- **Beginner**: Multiple Choice Questions (MCQs) on definitions and concepts
- **Intermediate**: Scenario-based MCQs
- **Advanced**: Activity-based questions

## Configuration

Edit `config.yaml` to customize:
- Question generation limits per level
- Progression thresholds
- LLM parameters (temperature, max tokens)
- Learning resource links
- Retry logic for API calls

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

