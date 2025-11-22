# Project Structure

## Overview

This document describes the organization and architecture of the Adaptive Question Generation Tool.

## Directory Structure

```
Agent_Compute/
├── main.py                          # Main CLI entry point
├── config.yaml                      # Configuration file
├── requirements.txt                 # Python dependencies
├── README.md                        # Project overview
├── USAGE_GUIDE.md                   # Detailed usage instructions
├── PROJECT_STRUCTURE.md             # This file
├── create_sample_data.py            # Sample data generator
├── .gitignore                       # Git ignore rules
│
├── src/                             # Source code
│   ├── __init__.py
│   ├── input_processor.py           # Excel file processing
│   ├── question_generator.py        # Main question generation engine
│   ├── llm_generator.py             # LLM API integration
│   ├── feedback_generator.py        # Feedback and resource curation
│   ├── output_formatter.py          # JSON output formatting
│   │
│   └── templates/                   # Question templates
│       ├── __init__.py
│       ├── programming_templates.py # Programming question templates
│       └── non_programming_templates.py # Non-programming templates
│
└── (generated files)
    ├── sample_exit_ticket.xlsx      # Sample input data
    ├── generated_questions.json     # Output questions
    └── generated_questions.summary.txt # Human-readable summary
```

## Module Descriptions

### `main.py`
**Purpose**: Command-line interface and orchestration

**Key Functions**:
- Parse command-line arguments
- Load configuration
- Coordinate the entire question generation pipeline
- Handle errors and logging

**Usage**: 
```bash
python3 main.py --input data.xlsx [options]
```

### `src/input_processor.py`
**Purpose**: Process Excel files containing student exit ticket responses

**Key Class**: `InputProcessor`

**Responsibilities**:
- Load and validate Excel files
- Identify incorrect student responses
- Group responses by concept
- Filter by concept or programming language
- Generate summary statistics

**Key Methods**:
- `load_and_validate()`: Load and validate Excel structure
- `identify_incorrect_responses()`: Find wrong answers
- `group_by_concept()`: Organize by concept
- `filter_by_concept()`: Filter specific concepts
- `filter_by_language()`: Filter by programming language

### `src/question_generator.py`
**Purpose**: Main engine for generating questions

**Key Class**: `QuestionGenerator`

**Responsibilities**:
- Orchestrate question generation for all concepts
- Generate questions at three difficulty levels
- Coordinate template selection and LLM generation
- Apply filters and limits
- Integrate feedback and resources

**Key Methods**:
- `generate_questions_for_concept()`: Generate all levels for one concept
- `generate_all_concepts()`: Generate for all concepts
- `_generate_programming_questions()`: Generate programming questions
- `_generate_non_programming_questions()`: Generate non-programming questions

### `src/llm_generator.py`
**Purpose**: Interface with Large Language Models (OpenAI API)

**Key Class**: `LLMGenerator`

**Responsibilities**:
- Make API calls to OpenAI
- Generate question variations using templates
- Handle retries and errors
- Parse and structure LLM responses

**Key Methods**:
- `generate_mcq_question()`: Generate multiple choice questions
- `generate_code_snippet_question()`: Generate code-based questions
- `generate_programming_problem()`: Generate full problems with test cases
- `generate_scenario_question()`: Generate scenario-based questions
- `generate_activity_question()`: Generate activity-based questions
- `generate_feedback()`: Generate feedback for questions

### `src/feedback_generator.py`
**Purpose**: Generate feedback and curate learning resources

**Key Class**: `FeedbackResourceGenerator`

**Responsibilities**:
- Generate detailed feedback for each question type
- Provide hints and tips
- Identify common misconceptions
- Curate relevant learning resources
- Create progress guidance

**Key Methods**:
- `generate_mcq_feedback()`: Feedback for MCQs
- `generate_code_feedback()`: Feedback for code questions
- `generate_problem_feedback()`: Feedback for programming problems
- `generate_activity_feedback()`: Feedback for activities
- `get_learning_resources()`: Curate resources for concepts
- `create_progress_guidance()`: Guide for level progression

### `src/output_formatter.py`
**Purpose**: Format and write output to JSON files

**Key Class**: `OutputFormatter`

**Responsibilities**:
- Structure data into JSON format
- Add metadata
- Write to files
- Generate human-readable summaries
- Log statistics

**Key Methods**:
- `format_output()`: Create complete output structure
- `write_to_file()`: Write JSON to file
- `create_summary_report()`: Generate text summary
- `write_summary_report()`: Write summary to file

### `src/templates/programming_templates.py`
**Purpose**: Templates for programming questions

**Key Class**: `ProgrammingTemplates`

**Contains**:
- Beginner MCQ templates
- Intermediate code snippet templates
- Advanced programming problem templates
- Language-specific syntax patterns
- Common programming concepts

**Supports**: Python, Java, C++, JavaScript

### `src/templates/non_programming_templates.py`
**Purpose**: Templates for non-programming questions

**Key Class**: `NonProgrammingTemplates`

**Contains**:
- Beginner MCQ templates
- Intermediate scenario-based templates
- Advanced activity-based templates
- Common concept categories

**Categories**: Science, Mathematics, History, Literature, Social Studies, Business, Arts, Language

## Data Flow

```
1. Excel Input (student responses)
   ↓
2. InputProcessor (parse, validate, group by concept)
   ↓
3. QuestionGenerator (orchestrate question generation)
   ↓
4. Templates + LLMGenerator (generate question variations)
   ↓
5. FeedbackGenerator (add feedback and resources)
   ↓
6. OutputFormatter (structure and write JSON)
   ↓
7. JSON Output (questions organized by concept and level)
```

## Configuration System

### `config.yaml`
Contains all configurable parameters:

1. **LLM Configuration**
   - Provider and model settings
   - API key environment variable
   - Temperature and token limits
   - Retry settings

2. **Question Limits**
   - Min/max/default questions per level
   - Beginner, intermediate, advanced settings

3. **Progression Thresholds**
   - Required correct answers to advance
   - Max attempts per concept

4. **Learning Resources**
   - URLs for programming languages
   - General educational resources
   - Organized by category

5. **Output Configuration**
   - Default filename
   - JSON formatting options
   - Metadata inclusion

## Question Generation Strategy

### Hybrid Approach
The tool uses a **template + LLM variation** approach:

1. **Template Selection**: Choose appropriate template based on:
   - Difficulty level (beginner/intermediate/advanced)
   - Course category (programming/non-programming)
   - Question type (MCQ/code/activity)

2. **LLM Generation**: Use template as a prompt to LLM:
   - Provides structure and requirements
   - LLM generates specific content
   - Ensures variety and relevance

3. **Feedback Integration**: Add educational components:
   - Explanations and hints
   - Common misconceptions
   - Learning resources
   - Progress guidance

### Question Types by Level

#### Programming Courses
- **Beginner**: Multiple Choice Questions on syntax and concepts
- **Intermediate**: Code snippets (debugging, completion, explanation)
- **Advanced**: Full programs with test cases

#### Non-Programming Courses
- **Beginner**: Multiple Choice Questions on definitions and concepts
- **Intermediate**: Scenario-based MCQs
- **Advanced**: Activity-based questions requiring detailed work

## Output Format

### JSON Structure
```json
{
  "generation_metadata": {
    "timestamp": "...",
    "source_file": "...",
    "statistics": {...}
  },
  "concepts": {
    "concept_key": {
      "concept_name": "...",
      "course_category": "...",
      "programming_language": "...",
      "affected_students": [...],
      "levels": {
        "beginner": {
          "questions": [...],
          "required_correct": 3,
          "progress_guidance": {...},
          "learning_resources": [...]
        },
        "intermediate": {...},
        "advanced": {...}
      }
    }
  }
}
```

## Extension Points

### Adding New Question Types
1. Add template in appropriate `templates/*.py` file
2. Add generation method in `llm_generator.py`
3. Add feedback method in `feedback_generator.py`
4. Update `question_generator.py` to use new type

### Supporting New Programming Languages
1. Add to `config.yaml` under `programming_languages`
2. Add syntax patterns in `programming_templates.py`
3. Add learning resources in `config.yaml`

### Adding New LLM Providers
1. Update `llm_generator.py` with new provider logic
2. Add configuration options in `config.yaml`
3. Update environment variable handling

## Testing

### Manual Testing
1. Create sample data: `python3 create_sample_data.py`
2. Run tool: `python3 main.py --input sample_exit_ticket.xlsx`
3. Verify output JSON structure
4. Check question quality and variety

### Test Scenarios
- Different course categories (programming vs non-programming)
- Different programming languages
- Various concepts
- Different numbers of affected students
- Filtering by concept and language

## Error Handling

The system handles various error scenarios:
- Missing/invalid Excel files
- Missing required columns
- Invalid data formats
- API failures (with retries)
- JSON parsing errors
- File write errors

All errors are logged with descriptive messages to help users troubleshoot.

## Performance Considerations

- **API Calls**: Generation time depends on number of concepts and LLM response time
- **Retries**: Built-in retry logic for API failures
- **Logging**: Informative progress logs during generation
- **Batching**: Questions generated sequentially to ensure quality

## Security

- API keys stored in `.env` file (gitignored)
- No sensitive data in logs
- Input validation on Excel data
- Sandboxed execution in development

## Future Enhancements

Potential improvements not in current version:
- Multi-language support (non-English)
- Database integration for question storage
- Web interface for teachers
- Student progress tracking system
- Question difficulty calibration
- Custom template editor
- Batch processing of multiple files
- Export to PDF/Word formats
- Integration with LMS platforms

