# Installation Guide

This guide will help you set up the Adaptive Question Generator on your local machine.

## Prerequisites

- Python 3.8 or higher
- Ollama (for local AI) OR OpenAI API key (for cloud AI)
- Git

## Quick Start (5 minutes)

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/Agent_Compute.git
cd Agent_Compute
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up AI Model

**Option A: Use Ollama (Free, Local)**

Install Ollama from https://ollama.ai/download

Then pull a model:
```bash
ollama pull llama3.2
```

**Option B: Use OpenAI (Paid, Cloud)**

Edit `config.yaml`:
```yaml
llm:
  provider: "openai"
  model: "gpt-4"
```

Create `.env` file:
```
OPENAI_API_KEY=your-api-key-here
```

### 4. Start the Server

```bash
python3 app.py
```

Open http://localhost:5000 in your browser!

## Detailed Installation

### For Windows

1. Install Python from https://python.org/downloads
2. Install Git from https://git-scm.com/download/win
3. Open Command Prompt and follow Quick Start steps above

### For macOS

1. Install Homebrew (if not installed):
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. Install Python:
```bash
brew install python
```

3. Follow Quick Start steps above

### For Linux (Ubuntu/Debian)

```bash
# Install Python and pip
sudo apt update
sudo apt install python3 python3-pip git

# Clone and install
git clone https://github.com/YOUR_USERNAME/Agent_Compute.git
cd Agent_Compute
pip3 install -r requirements.txt

# Install Ollama
curl https://ollama.ai/install.sh | sh
ollama pull llama3.2

# Run
python3 app.py
```

## Configuration

### Customize Question Generation

Edit `config.yaml` to change:
- Number of questions per difficulty level
- LLM model and parameters
- Learning resources links

### Use Different LLM Models

Available Ollama models:
- `llama3.2` (2GB) - Recommended
- `gemma3:1b` (815MB) - Faster, less accurate
- `mistral` (4GB) - More accurate

Change in `config.yaml`:
```yaml
llm:
  model: "mistral"
```

Then pull the model:
```bash
ollama pull mistral
```

## Troubleshooting

### "ModuleNotFoundError"

```bash
pip install -r requirements.txt
```

### "Port 5000 already in use"

Kill the process:
```bash
lsof -ti:5000 | xargs kill -9
```

Or use a different port:
```bash
# Edit app.py, line 239, change port=5000 to port=5001
```

### "Ollama not found"

Make sure Ollama is running:
```bash
ollama serve
```

### "No module named 'src'"

Make sure you're in the project directory:
```bash
cd Agent_Compute
python3 app.py
```

## Usage

1. **Upload Exit Ticket**: Excel file with student responses
2. **Select Concepts**: Choose which concepts to generate questions for
3. **Generate**: Click "Generate" on each concept (takes 1-2 minutes)
4. **Download**: Get JSON file with practice questions

### Supported Formats

- **Google Forms export** (automatic conversion)
- **Normalized format** (see `sample_exit_ticket.xlsx`)

See [GOOGLE_FORMS_GUIDE.md](GOOGLE_FORMS_GUIDE.md) for details.

## Next Steps

- Check [USAGE_GUIDE.md](USAGE_GUIDE.md) for detailed usage
- See [GOOGLE_FORMS_GUIDE.md](GOOGLE_FORMS_GUIDE.md) for Google Forms integration
- Read [CONCEPT_BY_CONCEPT_CHANGES.md](CONCEPT_BY_CONCEPT_CHANGES.md) for new features

## Support

For issues or questions, please open an issue on GitHub.

