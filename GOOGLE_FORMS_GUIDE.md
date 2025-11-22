# Google Forms / Quiz Exit Ticket Guide

This guide explains how to use exit tickets from Google Forms, Microsoft Forms, or other quiz platforms that use a "Points" scoring system.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Format Requirements](#format-requirements)
3. [Conversion Process](#conversion-process)
4. [Customizing Question Mappings](#customizing-question-mappings)
5. [Examples](#examples)
6. [Troubleshooting](#troubleshooting)

---

## Overview

The system now supports **two formats** for exit tickets:

### Format 1: Google Forms/Quiz Format (NEW!)
- Exported directly from Google Forms, Microsoft Forms, or similar quiz platforms
- Contains question columns paired with "Points" columns
- Points = 0 indicates incorrect answers
- Points = 1 indicates correct answers
- Contains student emails or IDs

### Format 2: Normalized Format (Original)
- Clean, normalized structure with: `Student_ID`, `Question_ID`, `Student_Answer`, `Correct_Answer`, `Concept`, `Question_Type`, `Course_Category`, `Programming_Language`

---

## Format Requirements

### Google Forms Format Structure

Your Excel file should have:

1. **Student Identifier Column**: `Student_Email` or `S.No`
2. **Question Columns**: One column per question with the question text as header
3. **Points Columns**: One "Points - [Question Text]" column per question
   - Value = 0: Student got it wrong ❌
   - Value = 1: Student got it right ✅

**Example:**

| Student_Email | What is a loop? | Points - What is a loop? | What is break? | Points - What is break? |
|---------------|-----------------|-------------------------|----------------|------------------------|
| student1@example.com | Iteration | 1 | Stops loop | 1 |
| student2@example.com | Function | 0 | Continues loop | 0 |

---

## Conversion Process

### Option 1: Automatic Conversion (Recommended)

The system **automatically detects** and converts Google Forms format when you use it:

```bash
# CLI - Automatic conversion
python main.py --input Exit_response.xlsx --output questions.json

# Web Interface - Upload directly
python web_app.py
# Then upload your Google Forms export file
```

The system will:
1. ✅ Detect it's Google Forms format
2. ✅ Extract correct answers from students who scored points
3. ✅ Identify students with 0 points (incorrect answers)
4. ✅ Generate practice questions for those students

### Option 2: Manual Conversion (For Review)

If you want to review the conversion before generating questions:

```bash
# Convert and save as normalized format
python convert_format.py --input Exit_response.xlsx --output normalized.xlsx

# Review the normalized file, then generate questions
python main.py --input normalized.xlsx --output questions.json
```

---

## Customizing Question Mappings

To improve concept identification, create a custom question mapping file:

### 1. Create/Edit `question_mapping_template.yaml`

```yaml
"what is a loop?":
  concept: "Python Loops"
  question_type: "MCQ"
  course_category: "programming"
  programming_language: "python"

"what does break do?":
  concept: "Loop Control - Break"
  question_type: "MCQ"
  course_category: "programming"
  programming_language: "python"

"who discovered gravity?":
  concept: "Physics - Gravity"
  question_type: "MCQ"
  course_category: "non-programming"
  programming_language: null
```

### 2. Use the mapping file during conversion

```bash
python convert_format.py \
  --input Exit_response.xlsx \
  --output normalized.xlsx \
  --mapping my_questions.yaml
```

### Field Definitions:

- **`concept`**: The learning concept being tested (e.g., "Python Loops", "Variables", "Arrays")
- **`question_type`**: 
  - `MCQ` - Multiple Choice Question
  - `Code` - Code-based question
  - `Short Answer` - Written response
- **`course_category`**: 
  - `programming` - For programming courses
  - `non-programming` - For other subjects
- **`programming_language`**: 
  - `python`, `java`, `javascript`, `cpp` for programming
  - `null` for non-programming questions

---

## Examples

### Example 1: Basic Usage

```bash
# Step 1: Export from Google Forms as Excel (.xlsx)
# Step 2: Run the question generator
python main.py --input MyQuizResults.xlsx --output practice_questions.json
```

### Example 2: With Custom Mappings

```bash
# Step 1: Create custom mapping file
# Edit question_mapping_template.yaml with your questions

# Step 2: Convert with custom mappings
python convert_format.py \
  --input Exit_response.xlsx \
  --output normalized.xlsx \
  --mapping question_mapping_template.yaml

# Step 3: Generate questions
python main.py --input normalized.xlsx --output questions.json
```

### Example 3: Web Interface

```bash
# Start the web server
python web_app.py

# Open browser: http://localhost:5000
# Upload your Google Forms export file
# Download generated questions
```

---

## How It Works

### 1. Correct Answer Extraction

The system extracts correct answers by finding responses where **Points = 1**:

```
Question: "What is 2 + 2?"
- Student A: "4" (Points = 1) ← Correct answer identified!
- Student B: "5" (Points = 0) ← Needs practice
- Student C: "4" (Points = 1) ← Confirms correct answer
```

### 2. Incorrect Response Identification

Students with **Points = 0** are identified as needing help:

```
Students needing practice on "What is 2 + 2?":
- Student B (answered "5")
```

### 3. Practice Question Generation

The system generates **similar** practice questions for students who need help:

```
Generated Questions for "Basic Arithmetic":
- Beginner: "What is 3 + 3?"
- Beginner: "What is 5 + 2?"
- Intermediate: "What is 15 + 27?"
- Advanced: "What is (23 + 45) × 2?"
```

---

## Troubleshooting

### Issue: "No question-points pairs found"

**Problem**: The file doesn't have "Points - " columns.

**Solution**: 
- Make sure you exported the file with scores from Google Forms
- Check that columns are named "Points - [Question Text]"

### Issue: "Missing required columns"

**Problem**: Conversion failed.

**Solution**:
```bash
# Check what format was detected
python convert_format.py --input yourfile.xlsx --output test.xlsx --verbose

# If needed, create a normalized file manually
```

### Issue: Concepts are "Unknown Concept"

**Problem**: The system couldn't infer concepts from question text.

**Solution**: Create a custom `question_mapping_template.yaml` file (see [Customizing Question Mappings](#customizing-question-mappings))

### Issue: "All students got everything right"

**Problem**: No Points = 0 found (or no incorrect answers).

**Solution**: This is good! No practice questions needed. If you expected some incorrect answers, check:
- The Points columns have 0 and 1 values (not text like "Correct"/"Incorrect")
- The export includes the scoring data

---

## File Structure Comparison

### ❌ Before (Google Forms Export)

```
| Student_Email | Q1: What is a loop? | Points - Q1 | Q2: What is break? | Points - Q2 |
|---------------|---------------------|-------------|-------------------|-------------|
| student1@...  | Iteration           | 1           | Stops loop        | 1           |
| student2@...  | Function            | 0           | Continues         | 0           |
```

### ✅ After (Normalized Format)

```
| Student_ID   | Question_ID | Student_Answer | Correct_Answer | Concept       | ... |
|--------------|-------------|----------------|----------------|---------------|-----|
| student1@... | Q1          | Iteration      | Iteration      | Python Loops  | ... |
| student1@... | Q2          | Stops loop     | Stops loop     | Loop Control  | ... |
| student2@... | Q1          | Function       | Iteration      | Python Loops  | ... |
| student2@... | Q2          | Continues      | Stops loop     | Loop Control  | ... |
```

---

## Tips for Teachers

### 1. **Design Clear Questions**
- Use consistent phrasing
- Include the programming language in question text when applicable
- Example: "In Python, what does `break` do?"

### 2. **Use Descriptive Question Text**
- Include keywords that help concept identification
- Good: "What is the effect of break in a loop?"
- Better: "Python Loops - What is the effect of break?"

### 3. **Export with Scores**
- In Google Forms: Go to Responses → Click three dots → Download responses
- Make sure "Include point values" is checked

### 4. **Create Custom Mappings for Large Assessments**
- For 10+ questions, create a YAML mapping file
- This ensures accurate concept grouping
- You can reuse the same mapping file for future quizzes

### 5. **Review Converted Files**
- Use the manual conversion option first
- Review the `normalized.xlsx` file
- Verify concepts are correctly identified
- Then proceed with question generation

---

## Next Steps

After conversion and question generation:

1. **Review Generated Questions**: Check `generated_questions.json`
2. **Export for Learning Platforms**: Use `export_for_platforms.py` to export for Moodle, Canvas, etc.
3. **Share with Students**: Distribute practice questions to students who need them
4. **Track Progress**: Re-run exit tickets to measure improvement

---

## Support

For issues or questions:
- Check the main [README.md](README.md)
- Review [USAGE_GUIDE.md](USAGE_GUIDE.md)
- See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for technical details

