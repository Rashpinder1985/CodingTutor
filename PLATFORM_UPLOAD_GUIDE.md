# Platform Upload Guide for Teachers

## 📦 Exported JSON Files Overview

After generating questions, you can export them in **platform-ready formats** for easy upload to coding platforms and LMS systems.

## 🚀 Quick Start

### Step 1: Generate Questions
```bash
python3 main.py --input your_exit_ticket.xlsx
```

### Step 2: Export for Platforms
```bash
python3 export_for_platforms.py --all
```

This creates multiple JSON files in the `platform_exports/` directory.

---

## 📁 Available Export Formats

### 1. **By Difficulty Level** (Recommended for Most Platforms)

Three separate JSON files, one for each difficulty level:

- ✅ `beginner_questions.json` - Foundation-building MCQs
- ✅ `intermediate_questions.json` - Code snippets and scenarios  
- ✅ `advanced_questions.json` - Full programming problems

**Best for:** Gradual skill progression, adaptive learning platforms

**Use case:** Assign beginner questions first, then intermediate after students pass, then advanced.

#### Structure:
```json
{
  "level": "beginner",
  "total_questions": 4,
  "generated_at": "2025-11-22T15:02:18",
  "questions": [
    {
      "id": "beginner_python_1",
      "concept": "Python Loops",
      "category": "programming",
      "language": "python",
      "difficulty": "beginner",
      "question": "What type of loop is used...",
      "type": "mcq",
      "options": {
        "A": "For loop",
        "B": "While loop",
        "C": "Do-while loop",
        "D": "Foreach loop"
      },
      "correct_answer": "B",
      "explanation": "A while loop is used...",
      "feedback": {...},
      "learning_resources": [...]
    }
  ]
}
```

---

### 2. **By Concept** (Recommended for Targeted Practice)

Each concept gets its own JSON file in `by_concept/`:

- ✅ `python-loops.json` - All questions about Python Loops (all levels)
- ✅ `java-methods.json` - All questions about Java Methods
- ✅ `arrays.json` - All questions about Arrays
- etc.

**Best for:** Topic-specific practice, remedial work on specific concepts

**Use case:** Student struggled with "Python Loops"? Give them the `python-loops.json` file with all related questions.

#### Structure:
```json
{
  "concept": "Python Loops",
  "category": "programming",
  "language": "python",
  "affected_students": ["S001", "S003", "S006", "S009"],
  "total_questions": 9,
  "generated_at": "2025-11-22T15:02:18",
  "levels": {
    "beginner": {
      "total_questions": 4,
      "required_correct": 3,
      "questions": [...],
      "learning_resources": [...],
      "progress_guidance": {...}
    },
    "intermediate": {...},
    "advanced": {...}
  }
}
```

---

### 3. **LeetCode Format** (For Coding Platforms)

Compatible with LeetCode-style platforms in `leetcode_format/`:

- ✅ `problems.json` - All programming problems in LeetCode format

**Best for:** Competitive programming platforms, judge systems

**Use case:** Upload directly to platforms that accept LeetCode-style problem definitions.

#### Structure:
```json
{
  "generated_at": "2025-11-22T15:02:18",
  "total_problems": 2,
  "problems": [
    {
      "questionId": "python_loops_advanced_1",
      "title": "Python Loops - Advanced Problem 1",
      "difficulty": "Advanced",
      "content": "Write a Python function...",
      "hints": ["Consider using...", "Think about..."],
      "constraints": ["1 <= n <= 1000"],
      "codeSnippets": [
        {
          "lang": "Python",
          "code": "def solve(n):\n    # Write your solution here\n    pass"
        }
      ],
      "testCases": [
        {
          "input": "5",
          "output": "[0, 1, 2, 3, 4]",
          "explanation": "Loop should iterate 5 times"
        }
      ]
    }
  ]
}
```

---

## 🎯 How to Use Each Format

### For **Moodle / Canvas / Blackboard**

1. Export by level: `python3 export_for_platforms.py --format level`
2. Use the quiz import feature:
   - Import `beginner_questions.json` as "Week 1 - Beginner Quiz"
   - Import `intermediate_questions.json` as "Week 2 - Intermediate Quiz"
   - Import `advanced_questions.json` as "Week 3 - Advanced Quiz"
3. Configure passing criteria (suggested: 3/4 for beginner, 3/3 for intermediate)

### For **Coding Practice Platforms** (HackerRank, CodeChef, etc.)

1. Export LeetCode format: `python3 export_for_platforms.py --format leetcode`
2. Open `leetcode_format/problems.json`
3. Each problem includes:
   - Problem statement
   - Test cases
   - Hints
   - Function signature
4. Create problems in your platform using this data

### For **Google Classroom / Microsoft Teams**

1. Export by concept: `python3 export_for_platforms.py --format concept`
2. For each struggling student:
   - Find their weak concept (e.g., "Python Loops")
   - Attach `platform_exports/by_concept/python-loops.json`
   - Student works through beginner → intermediate → advanced
3. Share learning resources included in the JSON

### For **Custom LMS / Gradescope**

1. Export all formats: `python3 export_for_platforms.py --all`
2. Parse JSON programmatically:
   ```python
   import json
   
   with open('platform_exports/beginner_questions.json') as f:
       data = json.load(f)
       
   for question in data['questions']:
       # Upload to your platform
       upload_question(
           question_text=question['question'],
           options=question['options'],
           correct_answer=question['correct_answer']
       )
   ```

---

## 📊 JSON Field Reference

### Common Fields (All Question Types)

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique question identifier |
| `concept` | string | Concept being tested |
| `category` | string | "programming" or "non-programming" |
| `language` | string | Programming language (if applicable) |
| `difficulty` | string | "beginner", "intermediate", or "advanced" |
| `type` | string | Question type (see below) |
| `feedback` | object | Detailed feedback and hints |
| `learning_resources` | array | Curated learning links |

### Question Types

#### MCQ Questions (`type: "mcq"`)
```json
{
  "type": "mcq",
  "question": "What is...",
  "options": {"A": "...", "B": "...", "C": "...", "D": "..."},
  "correct_answer": "B",
  "explanation": "Because..."
}
```

#### Code Snippet Questions (`type: "code_snippet"`)
```json
{
  "type": "code_snippet",
  "question": "Fix the following code...",
  "code": "def func():\n    ...",
  "task": "Debug and fix the error",
  "solution": "Corrected code here",
  "explanation": "The bug was..."
}
```

#### Programming Problems (`type: "implementation"`)
```json
{
  "type": "implementation",
  "title": "Implement Sum Function",
  "description": "Write a function that...",
  "function_signature": "def sum(a, b):",
  "constraints": ["1 <= a, b <= 1000"],
  "test_cases": [
    {
      "input": "sum(2, 3)",
      "expected_output": "5",
      "explanation": "2 + 3 = 5"
    }
  ],
  "hints": ["Consider..."],
  "solution_approach": "Use..."
}
```

#### Activity Questions (`type: "activity"`)
```json
{
  "type": "activity",
  "title": "Design a Loop",
  "description": "Create a project that...",
  "requirements": ["Must include...", "Should demonstrate..."],
  "deliverables": ["Source code", "Documentation"],
  "evaluation_criteria": ["Correctness", "Efficiency"]
}
```

---

## 🔄 Typical Teacher Workflow

### Week 1: Assessment
```bash
# 1. Students take exit ticket (export to Excel)
# 2. Generate questions
python3 main.py --input week1_exit_ticket.xlsx

# 3. Export for platform
python3 export_for_platforms.py --all
```

### Week 2: Distribute Practice
```bash
# Upload beginner_questions.json to your LMS
# Assign to students who struggled
# Set passing threshold: 3/4 correct
```

### Week 3: Progress to Next Level
```bash
# Students who passed beginner get intermediate_questions.json
# Track progress in your LMS
```

### Week 4: Advanced Challenge
```bash
# Students who mastered intermediate get advanced_questions.json
# These include full programming problems with test cases
```

---

## 💡 Tips for Teachers

### 1. **Progressive Difficulty**
- Don't skip levels - students should master beginner before intermediate
- Use the `required_correct` field to set passing criteria
- Monitor student progress through each level

### 2. **Concept-Based Remediation**
- When a student fails a quiz, look at which concepts they missed
- Assign the concept-specific JSON file for targeted practice
- Include the learning resources provided in each file

### 3. **Test Case Validation**
- For programming problems, use the included test cases
- Test cases include input, expected output, and explanation
- Add more test cases if needed for your platform

### 4. **Adaptive Assignment**
- Start all students at beginner level
- Automatically assign next level when `required_correct` threshold is met
- Track individual student progress

### 5. **Learning Resources**
- Each question includes 5+ curated learning links
- Share these with struggling students
- Resources are specific to the programming language and concept

---

## 🛠️ Advanced Usage

### Custom Export for Specific Students

```bash
# Generate questions only for specific concepts
python3 main.py --input data.xlsx --concept "Python Loops"

# Export just that concept
python3 export_for_platforms.py --format concept
```

### Filter by Language

```bash
# Generate only Python questions
python3 main.py --input data.xlsx --language python

# Export for platform
python3 export_for_platforms.py --all
```

### Batch Processing

```bash
# Process multiple exit tickets
for file in exit_tickets/*.xlsx; do
    python3 main.py --input "$file"
    python3 export_for_platforms.py --all
    mv platform_exports "exports_$(basename $file .xlsx)"
done
```

---

## 📝 Example Integration Code

### Python (Generic Upload)
```python
import json
import requests

def upload_to_platform(json_file, platform_api_url):
    with open(json_file) as f:
        data = json.load(f)
    
    for question in data['questions']:
        response = requests.post(
            platform_api_url,
            json={
                'question': question['question'],
                'type': question['type'],
                'difficulty': question['difficulty'],
                'options': question.get('options', {}),
                'correct_answer': question.get('correct_answer', ''),
                'explanation': question.get('explanation', ''),
                'concept': question['concept']
            }
        )
        print(f"Uploaded: {question['id']} - Status: {response.status_code}")

# Usage
upload_to_platform('platform_exports/beginner_questions.json', 'https://your-lms.com/api/questions')
```

### JavaScript (Web Upload)
```javascript
async function uploadQuestions(jsonFile) {
    const response = await fetch(jsonFile);
    const data = await response.json();
    
    for (const question of data.questions) {
        await fetch('https://your-platform.com/api/upload', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                id: question.id,
                question: question.question,
                options: question.options,
                correctAnswer: question.correct_answer,
                difficulty: question.difficulty
            })
        });
    }
}
```

---

## ✅ Checklist for Upload

Before uploading to your platform:

- [ ] Generated questions successfully
- [ ] Exported in desired format(s)
- [ ] Reviewed question quality
- [ ] Verified test cases (for programming problems)
- [ ] Set appropriate difficulty levels
- [ ] Configured passing criteria
- [ ] Included learning resources
- [ ] Tested upload with one question first
- [ ] Ready for batch upload

---

## 🆘 Troubleshooting

### Questions Not Generating?
- Check Excel format (must have required columns)
- Ensure there are incorrect responses (tool only generates for mistakes)
- Verify Ollama is running: `ollama list`

### Export Command Not Working?
```bash
# Make sure you're in the right directory
cd /Users/rashpinderkaur/Agent_Compute

# Activate virtual environment
source venv/bin/activate

# Run export
python3 export_for_platforms.py --all
```

### Platform Won't Accept JSON?
- Check if platform needs specific format
- Consider converting to CSV:
  ```python
  import json, csv
  # Convert JSON to CSV for your platform
  ```

---

## 📧 Support

For questions or issues:
1. Check the main README.md
2. Review USAGE_GUIDE.md
3. See code examples above
4. Check platform-specific documentation

---

**Happy Teaching! 🎓**

Your students will benefit from personalized, adaptive practice questions tailored to their specific needs.

