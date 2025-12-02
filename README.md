# Adaptive Question Generation & Activity Analysis Tool for Teachers

An intelligent web application for educators with **two powerful modes**:
1. **Programming Courses**: Analyze exit tickets and generate adaptive practice questions
2. **Non-Programming Courses**: Analyze activity-based exit tickets with qualitative insights

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/Rashpinder1985/CodingTutor.git
cd CodingTutor

# Install dependencies
pip install -r requirements.txt

# Start the web server
python3 app.py
```

Open **http://localhost:5000** and select your analysis mode!

📖 **[Full Installation Guide](INSTALLATION.md)**

## ✨ Two Analysis Modes

### 🖥️ Mode 1: Generate Practice Questions (Programming Courses)

For courses with **correct/incorrect answers** (MCQs, coding questions):
- Upload exit ticket with student responses
- AI generates adaptive questions at 3 levels (beginner, intermediate, advanced)
- Download Word documents with practice questions
- Supports Python, Java, C++, JavaScript

### 📊 Mode 2: Activity Analysis (Non-Programming Courses) - NEW!

For courses with **open-ended reflections** (activity-based learning):
- Upload exit ticket + activity template
- AI analyzes ALL student responses using NLP
- **Cognitive Domain Analysis**: "Learned Well" vs "Needs Reinforcement"
- **Affective Domain Analysis**: "Wants to Explore" vs "General Interest"
- Download teacher-friendly Word report with top 10 responses

## 🎯 Features

### Programming Course Features
- **Concept-by-Concept Generation**: Generate questions one concept at a time
- **AI Fallback Support**: Ollama → Gemini → OpenAI for reliability
- **Google Forms Support**: Upload directly from Google Forms/Microsoft Forms
- **Multi-Level Questions**: Beginner, Intermediate, Advanced difficulty
- **Multi-Language**: Python, Java, C++, JavaScript
- **Word Document Output**: Professional formatted question papers

### Activity Analysis Features (NEW!)
- **Visual Analytics Dashboard**: Tables showing learning outcomes
- **Cognitive Domain**: Categorizes learning quality
- **Affective Domain**: Measures student engagement
- **Top 10 Best Responses**: Selected using keyword extraction + thematic clustering + LLM scoring
- **Teacher-Friendly Report**: Simple Student ID + Response format
- **Auto-Generated Recommendations**: Actionable insights for instructors

## 📋 Exit Ticket Formats

### For Programming Courses

**Google Forms Format:**
```
| Student_Email | What is a loop? | Points - What is a loop? |
| student@x.com | Iteration       | 1 (correct)              |
| student2@x.com| Function        | 0 (incorrect)            |
```

### For Activity Analysis (NEW!)

**Exit Ticket Columns:**
- `Student_ID`: Unique identifier
- `Q1_Response`: "Write three things you learned during this lesson"
- `Q2_Response`: "Write two questions you have about the material"
- `Q3_Response`: "Write one aspect you found most interesting to explore"

**Activity Template:** `.txt` or `.docx` file describing the activity

## 📊 Sample Output

### Activity Analysis Report Structure

**Page 1: Visual Analytics Dashboard**
| Category | Students | Percentage |
|----------|----------|------------|
| ✓ Learned Well | 12 | 80% |
| ⚠ Needs Reinforcement | 3 | 20% |

**Pages 3-5: Top 10 Responses (Simple Format)**
```
1. Student S001
   "I learned that Newton's First Law states that objects at rest 
   stay at rest unless acted upon by a force..."

2. Student S006
   "I learned that Newton's Second Law is F=ma..."
```

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/Rashpinder1985/CodingTutor.git
cd CodingTutor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Set up AI providers:
   - **Ollama (Free, Local)**: `ollama pull llama3.2`
   - **Gemini (Free, Cloud)**: Set `GEMINI_API_KEY`
   - **OpenAI (Paid)**: Set `OPENAI_API_KEY`

4. Start the server:
```bash
python3 app.py
```

## 📖 Usage

### Programming Course Mode

1. Open http://localhost:5000
2. Select **"Generate Practice Questions"** mode
3. Upload exit ticket Excel file
4. Select concepts and generate questions
5. Download Word documents

### Activity Analysis Mode

1. Open http://localhost:5000
2. Select **"Activity Analysis (Qualitative)"** mode
3. Upload:
   - Exit ticket Excel (Student_ID, Q1_Response, Q2_Response, Q3_Response)
   - Activity template (`.txt` or `.docx`)
4. Select AI provider
5. Click "Analyze Activity"
6. Download teacher-friendly Word report

## 📁 Project Structure

```
├── app.py                          # Main Flask application
├── config.yaml                     # Configuration settings
├── requirements.txt                # Python dependencies
├── templates/
│   └── index.html                  # Web UI
├── src/
│   ├── input_processor.py          # Programming exit ticket processor
│   ├── question_generator.py       # Question generation logic
│   ├── word_formatter.py           # Question Word formatter
│   ├── activity_input_processor.py # Activity exit ticket processor
│   ├── activity_analyzer.py        # Activity analysis with NLP
│   ├── activity_word_formatter.py  # Teacher-friendly report formatter
│   ├── keyword_extractor.py        # TF-IDF keyword extraction
│   ├── thematic_analyzer.py        # KMeans thematic clustering
│   └── llm_generator.py            # Multi-provider LLM interface
├── sample_exit_ticket.xlsx         # Sample for programming mode
├── sample_activity_exit_ticket.xlsx # Sample for activity mode
└── sample_activity_template.txt    # Sample activity description
```

## ⚙️ Configuration

Edit `config.yaml` to customize:

```yaml
# LLM Provider
llm:
  provider: "ollama"  # or "gemini", "openai"
  model: "llama3.2"
  fallback_enabled: true

# Activity Analysis Settings
activity_analysis:
  top_responses_per_question: 10
  scoring_weights:
    keyword_match: 0.4
    llm_quality: 0.4
    theme_diversity: 0.2
```

## 📚 Documentation

- **[INSTALLATION.md](INSTALLATION.md)** - Complete setup guide
- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Detailed usage instructions
- **[ACTIVITY_ANALYSIS_GUIDE.md](ACTIVITY_ANALYSIS_GUIDE.md)** - Activity analysis documentation

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- AI powered by [Ollama](https://ollama.ai/), [Google Gemini](https://ai.google.dev/), or [OpenAI](https://openai.com/)
- NLP with [scikit-learn](https://scikit-learn.org/) and [NLTK](https://www.nltk.org/)
- UI components from [Bootstrap](https://getbootstrap.com/)

## ⭐ Star History

If you find this project helpful, please consider giving it a star!
