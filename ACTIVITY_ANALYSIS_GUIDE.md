# Activity Analysis Guide

## Overview

The **Activity Analysis Mode** is designed for qualitative analysis of open-ended student responses from activity-based learning. Unlike the question generation mode which creates practice questions, this mode analyzes student reflections, questions, and engagement levels using AI-powered natural language processing.

## When to Use This Mode

Use Activity Analysis when you have:
- Exit tickets with open-ended questions about student learning
- Activity-based reflections (not right/wrong answers)
- Student questions and doubts that need categorization
- Responses showing student engagement and curiosity

## Required Files

### 1. Exit Ticket (Excel File)

**Required Columns:**
- `Student_ID`: Unique student identifier
- `Q1_Response`: Learning summary responses
- `Q2_Response`: Student questions or doubts
- `Q3_Response`: Fascination or exploration interests

**Example:** `sample_activity_exit_ticket.xlsx`

### 2. Activity Template (Text or Word File)

A document describing the activity that students participated in. Include:
- Activity title and objectives
- What students did during the activity
- Key concepts covered
- Expected learning outcomes

**Formats:** `.txt` or `.docx`

**Example:** `sample_activity_template.txt`

## What Gets Analyzed

### Q1: Learning Summaries
- ✅ Identifies students who properly summarized their learning
- ⚠️ Detects off-topic or unclear responses
- 📊 Provides percentage of on-topic vs off-topic

### Q2: Student Questions & Doubts
- 🎯 Extracts relevant, high-quality questions
- 🗑️ Filters irrelevant or low-quality questions
- 🏷️ Groups questions by themes
- ⭐ Ranks questions by relevance score (1-10)

### Q3: Fascination & Exploration
- 😃 Identifies responses showing genuine excitement
- 🔍 Detects exploration intent and curiosity
- 📈 Scores excitement levels (1-10)
- 💡 Surfaces best responses for instructor review

## Sample Sizes (Cohen's Guidelines)

The tool automatically selects appropriate sample sizes based on class size:

| Class Size | Category | Responses Selected |
|-----------|----------|-------------------|
| < 20 students | Small | 5-8 responses |
| 20-50 students | Medium | 10-15 responses |
| > 50 students | Large | 15-20 responses |

## How to Use

1. **Open the web interface:** `http://localhost:5000`

2. **Select "Activity Analysis" mode**

3. **Upload both files:**
   - Exit ticket Excel file
   - Activity template (text or Word)

4. **Choose AI Provider:**
   - **Ollama** (Local, Free) - Best for privacy
   - **Gemini** (Cloud, Free) - Fast and accurate
   - **OpenAI** (Cloud, Paid) - Premium quality
   - **Auto** - Tries all providers in order

5. **Click "Analyze Activity"**

6. **Download the Word report** when analysis is complete

## Output Report

The generated Word document includes:

### Executive Summary
- Total students analyzed
- Sample size used
- Key statistics for all three questions

### Q1 Analysis
- List of students with on-topic summaries
- Detailed breakdown of off-topic responses with reasons

### Q2 Analysis
- Top student questions ranked by relevance
- Question themes and categories
- Filtered question count

### Q3 Analysis
- Top fascination responses with excitement scores
- Exploration intent responses with topics
- High engagement indicators

### Methodology Appendix
- Sample size rationale
- Scoring criteria
- AI analysis notes

## Tips for Best Results

### Prepare Your Exit Ticket
- ✅ Use clear, specific questions
- ✅ Ensure students write at least 2-3 sentences per response
- ✅ Review for any missing or very short responses

### Write a Good Activity Template
- ✅ Be specific about what students did
- ✅ List clear learning objectives
- ✅ Include key concepts covered
- ✅ Keep it focused (200-500 words is ideal)

### Interpreting Results
- 📊 Review the off-topic responses to identify confused students
- ❓ Use the filtered questions to address common doubts
- ⭐ Celebrate and share high engagement responses
- 🎯 Use themes to plan follow-up activities

## Troubleshooting

### "No valid student responses found"
- Check that your Excel has all required columns
- Ensure responses are not empty
- Verify column names match exactly

### "Failed to load activity template"
- Confirm file is .txt or .docx format
- Check that file is not empty
- Try saving as plain text if using Word

### Analysis takes too long
- Normal for 30+ students (up to 5-10 minutes)
- Try using Gemini or OpenAI for faster processing
- Ensure stable internet connection for cloud providers

## Example Use Case

**Scenario:** Physics teacher wants to understand student engagement after a Newton's Laws activity

**Exit Ticket Questions:**
1. Summarize what you learned from today's activity
2. What questions or doubts do you still have?
3. What fascinated you most? What would you like to explore further?

**Analysis Results:**
- 12/15 students (80%) properly summarized learning
- 3 students had off-topic responses → Follow up individually
- 10 relevant questions identified → Address in next class
- 5 students showed high exploration intent → Provide extension resources

## Technical Details

### AI Analysis Process
1. **Q1:** Uses semantic similarity to match responses against activity objectives
2. **Q2:** Scores questions using relevance, clarity, and critical thinking indicators
3. **Q3:** Performs sentiment analysis and detects curiosity markers

### Privacy
- When using Ollama, all processing happens locally
- Cloud providers (Gemini, OpenAI) process data remotely
- No student data is permanently stored by the application

### Accuracy
- Analysis should be reviewed by instructor
- Use results as insights, not absolute truth
- Better results with detailed activity templates
- Longer student responses provide more accurate analysis

## Support

For issues or questions:
- Check `INSTALLATION.md` for setup help
- Review `README.md` for general information
- Open an issue on GitHub

---

**Made with ❤️ for educators using AI-powered qualitative analysis**


