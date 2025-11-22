# Adaptive Question Generation Tool for Teachers

An intelligent web application that analyzes student exit ticket responses and generates personalized, multi-level practice questions to help students build conceptual proficiency.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/Rashpinder1985/CodingTutor.git
cd CodingTutor

# Install dependencies
pip install -r requirements.txt

# Install and run Ollama (Mac/Linux)
ollama pull llama3.2

# Start the web server
python3 app.py
```

Open **http://localhost:5000** and start generating questions!

📖 **[Full Installation Guide](INSTALLATION.md)**

### Or Use One-Line Setup:

```bash
git clone https://github.com/Rashpinder1985/CodingTutor.git && cd CodingTutor && chmod +x setup.sh && ./setup.sh
```

## ✨ Features

- **🎉 NEW: Concept-by-Concept Generation**: Generate questions one concept at a time for better control
- **📊 Google Forms/Quiz Support**: Upload exit tickets directly from Google Forms, Microsoft Forms, or other quiz platforms
- **🤖 Adaptive Question Generation**: Generates questions at three difficulty levels (beginner, intermediate, advanced)
- **💻 Multi-Language Support**: Supports Python, Java, C++, and JavaScript for programming courses
- **🎯 Intelligent AI**: Uses local LLM (Ollama) or OpenAI for question generation
- **📚 Comprehensive Feedback**: Provides detailed explanations and feedback for each question
- **🔗 Learning Resources**: Suggests curated open-source learning materials
- **📂 Smart Grouping**: Organizes questions by concepts where students struggled
- **🔄 Auto-Format Detection**: Automatically detects and converts different exit ticket formats
- **🌐 Web Interface**: Beautiful, modern UI for easy interaction
- **🔒 Privacy-Focused**: Run completely offline with Ollama

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

### Web Interface (Recommended!)

1. Start the Flask server:
```bash
python3 app.py
```

2. Open your browser to: **http://localhost:5000**

3. Upload your exit ticket file:
   - Google Forms export (automatic conversion)
   - Excel file in normalized format
   - Sample file: `Exit_response.xlsx` or `sample_exit_ticket.xlsx`

4. Select concepts and generate questions one at a time

5. Download JSON files for each concept

For detailed usage, see [GOOGLE_FORMS_GUIDE.md](GOOGLE_FORMS_GUIDE.md) and [USAGE_GUIDE.md](USAGE_GUIDE.md).

## Usage

### Via Web Interface (Recommended)

```bash
python3 app.py
# Open http://localhost:5000
```

### Features

- ✅ Upload Google Forms exports directly
- ✅ Automatic format detection and conversion
- ✅ Select specific concepts to generate questions
- ✅ Download questions immediately after generation
- ✅ Real-time progress tracking
- ✅ Beautiful, modern UI

## Input Format

### Google Forms/Quiz Format (Recommended) 🎯

Export directly from Google Forms, Microsoft Forms, or similar platforms. The file should have:
- Student email/ID column
- Question columns with question text as headers
- "Points - [Question Text]" columns with 0 (incorrect) or 1 (correct)

**Example from Exit_response.xlsx:**
```
| Student_Email | What is a loop? | Points - What is a loop? | What is break? | Points - What is break? |
| student@x.com | Iteration       | 1                        | Stops loop     | 1                       |
| student2@x.com| Function        | 0                        | Continues      | 0                       |
```

See [GOOGLE_FORMS_GUIDE.md](GOOGLE_FORMS_GUIDE.md) for full details.

### Normalized Format (Alternative)

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

## Additional Tools

### Convert Format Tool

Convert Google Forms exports to normalized format:
```bash
python convert_format.py --input Exit_response.xlsx --output normalized.xlsx
```

## Documentation

- **[INSTALLATION.md](INSTALLATION.md)** - Complete setup guide
- **[GOOGLE_FORMS_GUIDE.md](GOOGLE_FORMS_GUIDE.md)** - 🆕 Using Google Forms/Quiz exports
- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Detailed usage instructions
- **[CONCEPT_BY_CONCEPT_CHANGES.md](CONCEPT_BY_CONCEPT_CHANGES.md)** - New features explained
- **[PLATFORM_UPLOAD_GUIDE.md](PLATFORM_UPLOAD_GUIDE.md)** - Export to learning platforms
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Codebase organization
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Technical details

## 📸 Screenshots

![Upload Interface](docs/screenshot-upload.png)
![Concept Selection](docs/screenshot-concepts.png)
![Question Generation](docs/screenshot-generate.png)

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- AI powered by [Ollama](https://ollama.ai/) or [OpenAI](https://openai.com/)
- UI components from [Bootstrap](https://getbootstrap.com/)

## 📧 Contact

For questions or support, please open an issue on GitHub.

## ⭐ Star History

If you find this project helpful, please consider giving it a star!

