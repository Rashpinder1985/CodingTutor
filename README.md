# Exit Ticket Analysis Agent

An AI-powered reasoning agent for educators to analyze student exit tickets and generate insights. Features user authentication, per-user API key management, self-learning capabilities, and two powerful analysis modes for both programming and non-programming courses.

## 🤖 Reasoning Agent Capabilities

The agent **learns and improves** with each analysis:

- **Self-Reflection**: Evaluates its own question generation and analysis quality
- **Pattern Learning**: Stores and retrieves effective patterns from different courses
- **Adaptive Prompts**: Dynamically adjusts prompts based on learned best practices
- **Quality Tracking**: Monitors quality scores and trends over time
- **Visual Insights**: Web UI panel shows reasoning agent's work in real-time

## 🚀 Quick Start

### Local Development

```bash
# Clone the repository
git clone https://github.com/Rashpinder1985/CodingTutor.git
cd CodingTutor

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python app.py
```

Open **http://localhost:5000** and register/login to get started!

### Cloud Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for Railway.app deployment instructions.

---

## ✨ Features

### 🔐 User Authentication & API Key Management

- **Email/Password Registration & Login**: Secure user accounts
- **Per-User API Keys**: Each user provides their own Gemini or OpenAI API keys
- **Encrypted Storage**: API keys are encrypted in the database
- **Session Management**: Secure Flask sessions

### 🖥️ Mode 1: Generate Practice Questions (Programming Courses)

For courses with **correct/incorrect answers** (MCQs, coding questions):
- Upload exit ticket with student responses
- AI generates adaptive questions at 3 levels (beginner, intermediate, advanced)
- **Learning Resources**: Automatically included in generated reports
- Download Word documents with practice questions
- Supports Python, Java, C++, JavaScript
- Concept-by-concept generation

### 📊 Mode 2: Activity Analysis (Non-Programming Courses)

For courses with **open-ended reflections** (activity-based learning):
- Upload exit ticket + activity template
- AI analyzes ALL student responses using NLP
- **Cognitive Domain Analysis**: "Learned Well" vs "Needs Reinforcement"
- **Affective Domain Analysis**: "Wants to Explore" vs "General Interest"
- **Concept-Based Theming**: Groups responses by activity concepts
- **Content vs Pedagogy Classification**: Responses classified by theme category
- Download teacher-friendly Word report with top 10 responses

---

## 🎯 Key Capabilities

### Programming Course Features
- **Multi-LLM Support**: Ollama (local) → Gemini → OpenAI with automatic fallback
- **Adaptive Learning**: Agent learns from past question generation to improve quality
- **Learning Resources**: Curated resources included in question reports
- **Multi-Level Questions**: Beginner, Intermediate, Advanced difficulty
- **Multi-Language**: Python, Java, C++, JavaScript
- **Word Document Output**: Professional formatted question papers

### Activity Analysis Features
- **Visual Analytics Dashboard**: Tables showing learning outcomes
- **Cognitive Domain**: Categorizes learning quality (concept alignment)
- **Affective Domain**: Measures student engagement and exploration
- **Top 10 Best Responses**: Selected using keyword extraction + thematic clustering + LLM scoring
- **Concept-Based Grouping**: Students' questions grouped by activity concepts with frequency
- **Content vs Pedagogy**: Q3 responses classified and displayed separately
- **Teacher-Friendly Report**: Comprehensive Word document with all insights

### Reasoning Agent Features
- **Quality Scores**: Real-time quality metrics (0-100) for questions and analysis
- **Reflection Insights**: Shows strengths, improvements, and learned patterns
- **Quality Trends**: Tracks improvement over time (↑ improving, ↓ declining, → stable)
- **Adaptive Strategies**: Applies learned best practices automatically
- **Web UI Panel**: Collapsible panel showing reasoning agent's work

---

## 📋 Exit Ticket Formats

### For Programming Courses

**Required Columns:**
- `Student_ID`: Unique identifier
- `Question_ID`: Question identifier
- `Student_Answer`: Student's response
- `Correct_Answer`: Correct answer
- `Concept`: Programming concept (e.g., "For Loop", "Functions")
- `Question_Type`: Type of question (MCQ, Coding, etc.)
- `Course_Category`: "programming"
- `Programming_Language` (optional): Python, Java, C++, JavaScript

**Google Forms Format:**
```
| Student_Email | What is a loop? | Points - What is a loop? |
| student@x.com | Iteration       | 1 (correct)              |
| student2@x.com| Function        | 0 (incorrect)            |
```

### For Activity Analysis

**Exit Ticket Columns:**
- `Student_ID`: Unique identifier
- `Q1_Response`: "Write three things you learned during this lesson"
- `Q2_Response`: "Write two questions you have about the material"
- `Q3_Response`: "Write one aspect you found most interesting to explore"

**Activity Template:** `.txt` or `.docx` file describing the activity

---

## 🛠️ Installation

### Prerequisites

- Python 3.11+
- PostgreSQL (for production) or SQLite (for local development)

### Step-by-Step

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Rashpinder1985/CodingTutor.git
   cd CodingTutor
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up database:**
   - **Local (SQLite)**: Database will be created automatically as `instance/app.db`
   - **Production (PostgreSQL)**: Set `DATABASE_URL` environment variable

5. **Set environment variables (optional):**
   ```bash
   export SECRET_KEY="your-secret-key-here"
   export API_KEY_ENCRYPTION_KEY="your-encryption-key-here"
   ```

6. **Start the server:**
   ```bash
   python app.py
   # Or with Gunicorn:
   gunicorn app:app --bind 0.0.0.0:5000
   ```

7. **Access the app:**
   - Open http://localhost:5000
   - Register a new account
   - Set your API keys (Gemini or OpenAI)
   - Start using the features!

---

## 📖 Usage

### First Time Setup

1. **Register Account:**
   - Click "Login / Register"
   - Switch to "Register" tab
   - Enter email and password (min 8 characters)
   - Click "Register"

2. **Set API Keys:**
   - After login, you'll see "API Key Management" section
   - Enter at least one API key:
     - **Gemini**: Get from https://aistudio.google.com/app/apikey
     - **OpenAI**: Get from https://platform.openai.com/api-keys
   - Click "Save API Keys"
   - Features will be enabled once keys are set

### Programming Course Mode

1. Select **"Generate Practice Questions"** mode
2. Upload exit ticket Excel file
3. Select concepts to generate questions for
4. Click "Generate" for each concept
5. **View Reasoning Insights**: Panel shows quality scores and learned patterns
6. Download Word documents with practice questions and learning resources

### Activity Analysis Mode

1. Select **"Activity Analysis (Qualitative)"** mode
2. Upload:
   - Exit ticket Excel (Student_ID, Q1_Response, Q2_Response, Q3_Response)
   - Activity template (`.txt` or `.docx`)
3. Select AI provider (Gemini recommended)
4. Click "Analyze Activity"
5. **View Reasoning Insights**: Panel shows analysis quality and improvements
6. Download teacher-friendly Word report with:
   - Visual analytics dashboard
   - Top 10 responses per question
   - Concept-based themes
   - Content vs Pedagogy classification
   - Cognitive and affective domain analysis

---

## 📁 Project Structure

```
├── app.py                          # Main Flask application
├── config.yaml                     # Configuration settings
├── requirements.txt                # Python dependencies
├── nixpacks.toml                   # Railway deployment config
├── Procfile                        # Process configuration
├── runtime.txt                     # Python version
├── templates/
│   └── index.html                  # Web UI with authentication & reasoning panel
├── src/
│   ├── database.py                 # Database models (User, UserAPIKey)
│   ├── auth.py                     # Authentication system
│   ├── api_key_manager.py          # API key management
│   ├── reasoning_agent.py          # Self-reflection and learning module
│   ├── course_knowledge.py         # Knowledge base for learned patterns
│   ├── adaptive_prompts.py         # Adaptive prompt engineering
│   ├── quality_evaluator.py        # Quality scoring and tracking
│   ├── input_processor.py          # Programming exit ticket processor
│   ├── question_generator.py       # Question generation with reasoning
│   ├── word_formatter.py           # Question Word formatter
│   ├── activity_input_processor.py # Activity exit ticket processor
│   ├── activity_analyzer.py        # Activity analysis with NLP & reasoning
│   ├── activity_word_formatter.py  # Teacher-friendly report formatter
│   ├── keyword_extractor.py        # TF-IDF keyword extraction
│   ├── thematic_analyzer.py         # KMeans thematic clustering
│   ├── llm_generator.py            # Multi-provider LLM interface
│   ├── feedback_generator.py       # Learning resources generator
│   ├── format_converter.py         # Format conversion utilities
│   ├── output_formatter.py         # Output formatting utilities
│   └── templates/
│       ├── programming_templates.py    # Programming question templates
│       └── non_programming_templates.py # Non-programming templates
├── sample_exit_ticket.xlsx         # Sample for programming mode
├── sample_activity_exit_ticket.xlsx # Sample for activity mode
└── sample_activity_template.txt    # Sample activity description
```

---

## ⚙️ Configuration

Edit `config.yaml` to customize:

```yaml
# LLM Provider (users can override with their own API keys)
llm:
  provider: "gemini"  # or "ollama", "openai"
  model: "gemini-2.0-flash"
  fallback_enabled: true

# Activity Analysis Settings
activity_analysis:
  top_responses_per_question: 10
  scoring_weights:
    keyword_match: 0.3  # Concept alignment
    llm_quality: 0.5    # LLM-assessed quality
    theme_diversity: 0.2 # Theme diversity bonus
```

---

## 🔒 Security Features

- **Password Hashing**: Uses Werkzeug's secure password hashing
- **API Key Encryption**: Fernet symmetric encryption for stored API keys
- **Session Security**: Secure, httponly cookies
- **Input Validation**: Email format, password strength validation
- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries

---

## 🧪 Testing

See [TESTING_GUIDE.md](TESTING_GUIDE.md) for comprehensive testing instructions.

**Quick Test:**
```bash
./test_local.sh
```

---

## 📚 Documentation

- [DEPLOYMENT.md](DEPLOYMENT.md) - Cloud deployment guide (Railway.app)
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Testing instructions
- [INSTALLATION.md](INSTALLATION.md) - Detailed installation guide
- [USAGE_GUIDE.md](USAGE_GUIDE.md) - Usage instructions
- [ACTIVITY_ANALYSIS_GUIDE.md](ACTIVITY_ANALYSIS_GUIDE.md) - Activity analysis details

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 🙏 Acknowledgments

- Built with Flask, SQLAlchemy, and multiple LLM providers
- Uses NLTK and scikit-learn for NLP analysis
- Reasoning agent powered by self-reflection and adaptive learning
- Deployed on Railway.app

---

## ⭐ Star History

If you find this project helpful, please consider giving it a star!
