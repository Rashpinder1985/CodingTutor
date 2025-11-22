# Quick Reference Card

## Setup (One-time)

```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate it
source venv/bin/activate  # macOS/Linux
# or: venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up API key
echo "OPENAI_API_KEY=your_key_here" > .env
```

## Common Commands

### Generate Questions (Basic)
```bash
python3 main.py --input your_file.xlsx
```

### Test with Sample Data
```bash
# Create sample data
python3 create_sample_data.py

# Generate questions
python3 main.py --input sample_exit_ticket.xlsx
```

### Filter by Concept
```bash
python3 main.py --input data.xlsx --concept "loops"
```

### Filter by Language
```bash
python3 main.py --input data.xlsx --language python
```

### Custom Output File
```bash
python3 main.py --input data.xlsx --output my_questions.json
```

### With Summary Report
```bash
python3 main.py --input data.xlsx --summary
```

### Verbose Output
```bash
python3 main.py --input data.xlsx --verbose
```

### Complete Example
```bash
python3 main.py \
  --input student_data.xlsx \
  --output week5_questions.json \
  --concept "loops" \
  --language python \
  --summary \
  --verbose
```

## Excel File Format

Required columns:
- `Student_ID` - Unique student identifier
- `Question_ID` - Question identifier  
- `Student_Answer` - What student answered
- `Correct_Answer` - The correct answer
- `Concept` - Topic/concept being tested
- `Question_Type` - MCQ, Code, etc.
- `Course_Category` - "programming" or "non-programming"
- `Programming_Language` - (Optional) python, java, cpp, javascript

## Output Structure

```
generated_questions.json
├── generation_metadata
│   ├── timestamp
│   ├── source_file
│   └── statistics
└── concepts
    └── [concept_name]
        ├── concept_name
        ├── affected_students
        └── levels
            ├── beginner
            │   ├── questions
            │   ├── required_correct
            │   ├── progress_guidance
            │   └── learning_resources
            ├── intermediate
            └── advanced
```

## Configuration Quick Edits

Edit `config.yaml` to change:

### Number of Questions
```yaml
question_limits:
  beginner:
    default: 4  # Change this number
  intermediate:
    default: 3
  advanced:
    default: 2
```

### Progression Requirements
```yaml
progression:
  beginner_to_intermediate: 3  # Correct answers needed
  intermediate_to_advanced: 3
```

### LLM Model
```yaml
llm:
  model: "gpt-4"  # or "gpt-3.5-turbo"
  temperature: 0.7
```

## Troubleshooting

### API Key Error
```bash
# Check .env file exists and contains:
OPENAI_API_KEY=sk-...
```

### Module Not Found
```bash
# Activate virtual environment
source venv/bin/activate
# Install dependencies
pip install -r requirements.txt
```

### Excel Format Error
```bash
# Verify your Excel has all required columns
# Use create_sample_data.py to see expected format
python3 create_sample_data.py
```

### No Questions Generated
- Tool only generates for incorrect answers
- Check that Student_Answer ≠ Correct_Answer for some rows
- Use --verbose to see what's being processed

## Quick Workflow

1. **After Assessment**
   ```bash
   # Export student responses to Excel
   # Ensure correct format
   ```

2. **Generate Questions**
   ```bash
   python3 main.py --input responses.xlsx --summary
   ```

3. **Review Output**
   ```bash
   # Check generated_questions.json
   # Read generated_questions.summary.txt
   ```

4. **Share with Students**
   - Extract questions for each concept
   - Share appropriate level based on student needs
   - Include learning resources

5. **Track Progress**
   - Students complete questions
   - Record new responses
   - Re-run tool to generate new questions

## Help Commands

```bash
# Show all options
python3 main.py --help

# Check version
python3 main.py --version  # (if implemented)
```

## File Locations

- **Input**: Your Excel file
- **Output**: `generated_questions.json` (default)
- **Summary**: `generated_questions.summary.txt` (with --summary)
- **Config**: `config.yaml`
- **Logs**: Console output (redirect with `> log.txt`)

## Question Types by Level

### Programming
- **Beginner**: MCQs on syntax and concepts
- **Intermediate**: Code snippets, debugging
- **Advanced**: Full programs with test cases

### Non-Programming  
- **Beginner**: MCQs on definitions
- **Intermediate**: Scenario-based questions
- **Advanced**: Activity-based questions

## Supported Languages

- Python (`python`)
- Java (`java`)
- C++ (`cpp`)
- JavaScript (`javascript`)

## Tips

- Run after each assessment for best results
- Use concept filter for focused practice
- Review questions before sharing with students
- Regenerate questions for variety
- Share learning resources with struggling students

## Documentation Files

- `README.md` - Project overview
- `USAGE_GUIDE.md` - Detailed instructions
- `PROJECT_STRUCTURE.md` - Architecture details
- `IMPLEMENTATION_SUMMARY.md` - What was built
- `QUICK_REFERENCE.md` - This file

## Support

For issues:
1. Check error message (usually helpful)
2. Run with `--verbose` for details
3. Review USAGE_GUIDE.md
4. Check configuration in config.yaml
5. Verify Excel file format

---

**Remember**: Always activate your virtual environment before running!
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

