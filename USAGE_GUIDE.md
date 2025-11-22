# Usage Guide - Adaptive Question Generation Tool

## Quick Start

### 1. Installation

First, set up a virtual environment and install dependencies:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

1. Set up your OpenAI API key:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

2. (Optional) Customize settings in `config.yaml`

### 3. Prepare Your Data

Create an Excel file with student exit ticket responses containing these columns:

| Column | Description | Example |
|--------|-------------|---------|
| Student_ID | Unique student identifier | S001 |
| Question_ID | Question identifier | Q1 |
| Student_Answer | Student's answer | A |
| Correct_Answer | The correct answer | B |
| Concept | Concept/topic being tested | Python Loops |
| Question_Type | Type of question | MCQ, Code |
| Course_Category | programming or non-programming | programming |
| Programming_Language | (Optional) For programming courses | python, java, cpp, javascript |

**Important**: The tool identifies incorrect responses by comparing `Student_Answer` with `Correct_Answer`. Questions will be generated only for concepts where students made mistakes.

### 4. Generate Sample Data (Optional)

To test the tool with sample data:

```bash
python3 create_sample_data.py
```

This creates `sample_exit_ticket.xlsx` with example student responses.

### 5. Generate Questions

Basic usage:
```bash
python3 main.py --input your_exit_ticket_data.xlsx
```

This will create `generated_questions.json` with personalized questions organized by concept and difficulty level.

## Advanced Usage

### Filter by Concept

Generate questions for a specific concept only:
```bash
python3 main.py --input data.xlsx --concept "loops"
```

### Filter by Programming Language

Generate questions for a specific language only:
```bash
python3 main.py --input data.xlsx --language python
```

### Custom Output Location

Specify where to save the generated questions:
```bash
python3 main.py --input data.xlsx --output my_questions.json
```

### Generate Summary Report

Create an additional human-readable summary:
```bash
python3 main.py --input data.xlsx --summary
```

This creates both `generated_questions.json` and `generated_questions.summary.txt`.

### Verbose Output

See detailed processing information:
```bash
python3 main.py --input data.xlsx --verbose
```

### Complete Example

```bash
python3 main.py \
  --input student_responses_2024.xlsx \
  --output questions_week5.json \
  --concept "loops" \
  --language python \
  --summary \
  --verbose
```

## Understanding the Output

The generated JSON file contains:

### 1. Metadata Section
```json
{
  "generation_metadata": {
    "timestamp": "2024-11-22T10:30:00",
    "source_file": "exit_ticket.xlsx",
    "total_students": 25,
    "affected_students": 12,
    "total_concepts": 5
  }
}
```

### 2. Concepts Section

For each concept where students struggled, you'll find:

```json
{
  "concepts": {
    "python_loops": {
      "concept_name": "Python Loops",
      "course_category": "programming",
      "programming_language": "python",
      "affected_students": ["S001", "S003", "S006"],
      "levels": {
        "beginner": { ... },
        "intermediate": { ... },
        "advanced": { ... }
      }
    }
  }
}
```

### 3. Questions by Difficulty Level

Each level contains:
- **Questions**: Array of generated questions
- **Required Correct**: Number of questions students should answer correctly to progress
- **Progress Guidance**: Tips for students at this level
- **Learning Resources**: Curated links for additional practice

#### Beginner Level (MCQs)
- Multiple choice questions testing basic concepts
- Focus on definitions, syntax, and fundamental understanding

#### Intermediate Level
- **Programming courses**: Code snippets, debugging, fill-in-the-blank
- **Non-programming courses**: Scenario-based MCQs

#### Advanced Level
- **Programming courses**: Full programming problems with test cases
- **Non-programming courses**: Activity-based questions requiring detailed responses

## How Teachers Can Use This

### 1. Initial Assessment
After an exit ticket or quiz:
1. Export student responses to Excel
2. Run the tool to generate questions
3. Review the output to see which concepts need reinforcement

### 2. Assign Personalized Practice

For each concept, you can assign questions based on student level:

- **Struggling students**: Start with beginner questions
- **Moderate understanding**: Assign intermediate questions
- **Advanced students**: Challenge with advanced problems

### 3. Track Progress

The output includes progression criteria:
- Students need to correctly answer a certain number at each level
- Use `required_correct` field to know when students can advance
- Re-run the tool after additional practice to generate new variations

### 4. Use Learning Resources

Share the curated learning resources with students who need additional help outside of class.

### 5. Provide Feedback

Each question includes:
- **Feedback**: Explanations and guidance
- **Hints**: Help for students who are stuck
- **Common Misconceptions**: Things to watch out for

## Configuration Options

Edit `config.yaml` to customize:

### Question Limits
```yaml
question_limits:
  beginner:
    default: 4  # Number of beginner questions per concept
  intermediate:
    default: 3
  advanced:
    default: 2
```

### Progression Thresholds
```yaml
progression:
  beginner_to_intermediate: 3  # Correct answers needed to advance
  intermediate_to_advanced: 3
```

### LLM Settings
```yaml
llm:
  model: "gpt-4"  # or "gpt-3.5-turbo" for faster/cheaper
  temperature: 0.7
  max_tokens: 2000
```

## Troubleshooting

### API Key Issues
```
Error: API key not found
```
**Solution**: Make sure you've created a `.env` file with `OPENAI_API_KEY=your_key_here`

### Excel Format Issues
```
Error: Missing required columns
```
**Solution**: Verify your Excel file has all required columns. Use `create_sample_data.py` to see the expected format.

### No Questions Generated
```
Warning: No incorrect responses found
```
**Solution**: The tool only generates questions for concepts where students made mistakes. If all answers are correct, no questions will be generated.

### Module Not Found
```
ModuleNotFoundError: No module named 'pandas'
```
**Solution**: Make sure you've activated your virtual environment and installed dependencies:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Tips for Best Results

1. **Clear Concept Names**: Use consistent, descriptive names for concepts in your Excel file
2. **Include Language Info**: For programming courses, always include the `Programming_Language` column
3. **Regular Updates**: Run the tool after each assessment to track student progress over time
4. **Combine with Teaching**: Use generated questions as supplementary practice, not replacement for instruction
5. **Review Questions**: Always review generated questions before sharing with students to ensure quality and relevance

## Getting Help

If you encounter issues:
1. Check this guide and the main README
2. Review the error messages - they often include helpful hints
3. Run with `--verbose` flag to see detailed processing information
4. Verify your input data format matches the requirements

## Example Workflow

Here's a complete workflow from assessment to question generation:

1. **Administer Exit Ticket**
   - Students complete a short quiz/exit ticket
   - Record responses in Excel with correct answers

2. **Generate Questions**
   ```bash
   python3 main.py --input exit_ticket_day1.xlsx --output questions_day1.json --summary
   ```

3. **Review Output**
   - Check the summary report
   - Identify which students need help with which concepts

4. **Share Questions**
   - Extract questions for each student/group
   - Share appropriate level questions
   - Include learning resources

5. **Track Progress**
   - Students complete practice questions
   - Record new responses
   - Run tool again to generate new questions or advance levels

6. **Iterate**
   - Continue cycle of assessment → practice → reassessment
   - Monitor student progression through difficulty levels

