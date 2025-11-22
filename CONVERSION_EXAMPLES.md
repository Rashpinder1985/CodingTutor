# Format Conversion Examples

This document provides practical examples of converting Google Forms/Quiz exit tickets to the normalized format.

## Example 1: Python Loops Quiz

### Input (Google Forms Export - Exit_response.xlsx)

```
| S.No | Student_Email           | What will be the output? | Points - What will be the output? | What is break? | Points - What is break? |
|------|-------------------------|--------------------------|-----------------------------------|----------------|------------------------|
| 1    | student1@mitvpu.ac.in   | 0 1 2                   | 1                                 | Exits loop     | 1                      |
| 2    | student2@mitvpu.ac.in   | 1 2 3                   | 0                                 | Exits loop     | 1                      |
| 3    | student3@mitvpu.ac.in   | 0 1 2                   | 1                                 | Continues      | 0                      |
```

### Conversion Command

```bash
python convert_format.py \
  --input Exit_response.xlsx \
  --output normalized_loops.xlsx \
  --mapping question_mapping_template.yaml
```

### Output (Normalized Format)

```
| Student_ID             | Question_ID | Student_Answer | Correct_Answer | Concept       | Question_Type | Course_Category | Programming_Language |
|------------------------|-------------|----------------|----------------|---------------|---------------|-----------------|---------------------|
| student1@mitvpu.ac.in  | Q1          | 0 1 2         | 0 1 2         | Python Loops  | Code          | programming     | python              |
| student1@mitvpu.ac.in  | Q2          | Exits loop    | Exits loop    | Loop Control  | MCQ           | programming     | python              |
| student2@mitvpu.ac.in  | Q1          | 1 2 3         | 0 1 2         | Python Loops  | Code          | programming     | python              |
| student2@mitvpu.ac.in  | Q2          | Exits loop    | Exits loop    | Loop Control  | MCQ           | programming     | python              |
| student3@mitvpu.ac.in  | Q1          | 0 1 2         | 0 1 2         | Python Loops  | Code          | programming     | python              |
| student3@mitvpu.ac.in  | Q2          | Continues     | Exits loop    | Loop Control  | MCQ           | programming     | python              |
```

### Analysis

**Incorrect Responses Identified:**
- Student 2: Question 1 (answered "1 2 3" instead of "0 1 2")
- Student 3: Question 2 (answered "Continues" instead of "Exits loop")

**Practice Questions Will Be Generated For:**
- Concept: "Python Loops" → Student 2
- Concept: "Loop Control" → Student 3

---

## Example 2: Mixed Subject Quiz

### Input (Google Forms Export)

```
| Student_Email    | In Python, what is a variable? | Points | Who discovered gravity? | Points |
|------------------|-------------------------------|--------|------------------------|--------|
| alice@school.com | Storage location              | 1      | Newton                 | 1      |
| bob@school.com   | A function                    | 0      | Einstein               | 0      |
| carol@school.com | Storage location              | 1      | Newton                 | 1      |
```

### Custom Mapping (custom_mapping.yaml)

```yaml
"in python, what is a variable?":
  concept: "Python Variables"
  question_type: "MCQ"
  course_category: "programming"
  programming_language: "python"

"who discovered gravity?":
  concept: "Physics - Gravity"
  question_type: "MCQ"
  course_category: "non-programming"
  programming_language: null
```

### Conversion Command

```bash
python convert_format.py \
  --input mixed_quiz.xlsx \
  --output normalized_mixed.xlsx \
  --mapping custom_mapping.yaml
```

### Output Statistics

```
Conversion Summary:
  Students: 3
  Questions: 2
  Concepts: 2
  Programming questions: 3
  Non-programming questions: 3

Concepts found:
  - Python Variables: 3 responses
  - Physics - Gravity: 3 responses

Students with incorrect responses:
  - bob@school.com: 2 incorrect (Python Variables, Physics - Gravity)
```

---

## Example 3: Large Class Assessment

### Scenario

- 37 students
- 18 questions on Python loops
- Mixed MCQ and code questions
- Results from actual Exit_response.xlsx file

### Command

```bash
python convert_format.py \
  --input Exit_response.xlsx \
  --output class_results_normalized.xlsx \
  --mapping question_mapping_template.yaml
```

### Results

```
✓ Converted 663 responses

Conversion Summary:
  Students: 37
  Questions: 18
  Concepts: 9
  Programming questions: 663
  Non-programming questions: 0

Concepts found:
  - Python Loops: 148 responses
  - Python Output: 258 responses
  - Loop Control - Break: 36 responses
  - Loop Control - Continue: 37 responses
  - Infinite Loops: 37 responses
  - Loop Iteration Count: 36 responses
  - Debugging - Syntax Errors: 37 responses
  - Loop Control: 37 responses
  - Python Pass Statement: 37 responses

Incorrect responses: 154 (23.2%)
Students needing practice: 33 out of 37
```

### Generated Practice Questions

```bash
python main.py --input class_results_normalized.xlsx --output practice_questions.json
```

**Output:**
- 9 concept groups
- 81 practice questions total (beginner, intermediate, advanced)
- Personalized for 33 students who had incorrect answers
- Learning resources included for each concept

---

## Example 4: Direct Usage (Skip Conversion)

If you don't need to review the conversion, use the Google Forms export directly:

```bash
# One-step process
python main.py --input Exit_response.xlsx --output questions.json

# Or with filters
python main.py --input Exit_response.xlsx --concept "loops" --output loop_questions.json
```

The system will:
1. ✅ Auto-detect Google Forms format
2. ✅ Convert to normalized format internally
3. ✅ Identify incorrect responses (Points = 0)
4. ✅ Generate practice questions

---

## Example 5: Web Interface Usage

### Step 1: Start Server

```bash
python web_app.py
```

### Step 2: Upload File

1. Open http://localhost:5000
2. Click "Upload Exit Ticket"
3. Select your Google Forms export (.xlsx file)
4. (Optional) Apply filters by concept or language

### Step 3: Download Results

- **JSON Format**: Complete question set with metadata
- **By Level**: Separate files for beginner/intermediate/advanced
- **By Concept**: Individual files per concept
- **All Formats (ZIP)**: Everything in one download

---

## Common Patterns

### Pattern 1: All Students Got Everything Right

```
Input: 50 students, 10 questions, all Points = 1

Result:
✗ No incorrect responses found. Students answered all questions correctly!

Action: No practice questions needed. Consider making the quiz more challenging.
```

### Pattern 2: One Difficult Question

```
Input: 30 students, 5 questions
Question 3: 25 students got Points = 0

Result:
✓ Identified Concept: "Nested Loops" as challenging
✓ Generated extra practice questions for this concept
✓ 25 students tagged for practice

Action: Review teaching materials for "Nested Loops" concept.
```

### Pattern 3: Mixed Performance

```
Input: 40 students, 8 questions
- Beginner questions (Q1-Q3): 90% correct
- Intermediate (Q4-Q6): 60% correct
- Advanced (Q7-Q8): 30% correct

Result:
✓ Generated questions matching performance levels
✓ More intermediate and advanced practice questions created
✓ Students grouped by concept mastery

Action: Assign level-appropriate practice questions to students.
```

---

## Troubleshooting Examples

### Issue: "No question-points pairs found"

**Cause:** Points columns not detected

**Example Bad Format:**
```
| Student | Q1 | Score_Q1 | Q2 | Score_Q2 |
```

**Example Good Format:**
```
| Student | Q1 | Points - Q1 | Q2 | Points - Q2 |
```

**Solution:** Ensure columns are named exactly "Points - [Question Text]"

---

### Issue: All concepts are "Unknown Concept"

**Cause:** Question text doesn't contain identifiable keywords

**Example:**
```
| Question | Detected Concept |
|----------|-----------------|
| Q1       | Unknown Concept  |
| Q2       | Unknown Concept  |
```

**Solution:** Create a custom mapping file:

```yaml
"q1":
  concept: "Python Syntax"
  question_type: "MCQ"
  course_category: "programming"
  programming_language: "python"

"q2":
  concept: "Loop Iteration"
  question_type: "Code"
  course_category: "programming"
  programming_language: "python"
```

---

## Best Practices

### 1. Use Descriptive Question Text

❌ Bad:
```
| Q1 | Points - Q1 |
```

✅ Good:
```
| What is the output of this loop? | Points - What is the output of this loop? |
```

### 2. Include Programming Language in Questions

❌ Bad:
```
What does break do?
```

✅ Good:
```
In Python, what does break do in a loop?
```

### 3. Create Reusable Mapping Files

For standardized assessments, create a mapping file once and reuse it:

```bash
# First time
python convert_format.py --input midterm_v1.xlsx --output norm_v1.xlsx --mapping midterm_map.yaml

# Next semester with same questions
python convert_format.py --input midterm_v2.xlsx --output norm_v2.xlsx --mapping midterm_map.yaml
```

### 4. Review Before Generating

For important assessments, review the conversion:

```bash
# Step 1: Convert and review
python convert_format.py --input exam.xlsx --output exam_normalized.xlsx

# Step 2: Check the normalized file in Excel/LibreOffice

# Step 3: Generate questions
python main.py --input exam_normalized.xlsx --output practice.json
```

---

## Quick Reference

| Task | Command |
|------|---------|
| **Convert with auto-detection** | `python convert_format.py -i input.xlsx -o output.xlsx` |
| **Convert with custom mapping** | `python convert_format.py -i input.xlsx -o output.xlsx -m mapping.yaml` |
| **Direct question generation** | `python main.py -i input.xlsx` |
| **Filter by concept** | `python main.py -i input.xlsx --concept "loops"` |
| **Filter by language** | `python main.py -i input.xlsx --language python` |
| **Web interface** | `python web_app.py` then open http://localhost:5000 |

---

## Next Steps

After conversion and review:

1. ✅ **Generate Practice Questions**: Run `main.py` with your normalized file
2. ✅ **Review Generated Questions**: Open the JSON output and verify quality
3. ✅ **Export for Platforms**: Use `export_for_platforms.py` for Moodle, Canvas, etc.
4. ✅ **Distribute to Students**: Share practice questions via your LMS or directly
5. ✅ **Track Progress**: Re-assess students after practice to measure improvement

