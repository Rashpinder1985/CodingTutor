# Web UI Guide - Teacher Interface

## 🌐 Open Source Web Interface for Teachers

Your question generator now has a **beautiful web interface** where teachers can:
- Upload Excel files via drag-and-drop
- Generate questions with one click
- Download results instantly
- No command line needed!

---

## 🚀 Quick Start

### Start the Web Server

```bash
# 1. Navigate to project directory
cd /Users/rashpinderkaur/Agent_Compute

# 2. Activate virtual environment
source venv/bin/activate

# 3. Start the web server
python3 app.py
```

### Access the Web Interface

Open your web browser and go to:

```
http://localhost:5000
```

**That's it!** You'll see a beautiful interface.

---

## 📱 How to Use the Web Interface

### Step 1: Open the Web App
- Start the server (see above)
- Open browser to `http://localhost:5000`
- You'll see the upload interface

### Step 2: Upload Your Exit Ticket File
Two ways to upload:
1. **Drag & Drop**: Drag your Excel file onto the upload zone
2. **Click to Browse**: Click the upload zone to select a file

Supported format: `.xlsx` (Excel files)
Maximum size: 16MB

### Step 3: (Optional) Apply Filters
- **Filter by Concept**: Enter specific concept name (e.g., "Python Loops")
- **Filter by Language**: Select programming language from dropdown

### Step 4: Generate Questions
- Click the "Generate Questions" button
- Wait while AI generates questions (1-10 minutes)
- Progress indicator will show

### Step 5: Download Your Questions
After generation completes, you'll see:
- **Summary statistics** (concepts, students, counts)
- **Concept breakdown** with question counts
- **Two download options**:
  1. **Complete Output (JSON)** - Single file with all data
  2. **All Formats (ZIP)** - Complete package with beginner/intermediate/advanced separated

---

## 🎨 Features

### Beautiful Interface
- Modern, gradient design
- Responsive (works on mobile, tablet, desktop)
- Drag-and-drop file upload
- Real-time feedback
- Progress indicators

### Privacy-Focused
- ✅ Runs completely locally
- ✅ Uses Ollama (no cloud API)
- ✅ Your data never leaves your machine
- ✅ No internet connection needed (after setup)

### Teacher-Friendly
- No command line knowledge needed
- Visual feedback at every step
- Clear error messages
- One-click downloads
- Mobile-responsive

---

## 📊 What You Get

### JSON Output Includes:
- Complete question sets for all concepts
- Three difficulty levels per concept
- Detailed feedback for each question
- Learning resources (5+ links per concept)
- Student lists (who needs help with what)
- Progress guidance for students

### ZIP Package Includes:
- `complete_output.json` - Everything in one file
- `beginner_questions.json` - All beginner level questions
- `intermediate_questions.json` - All intermediate questions
- `advanced_questions.json` - All advanced questions
- `by_concept/concept-name.json` - Separate file per concept

---

## 🖥️ Server Commands

### Start Server
```bash
python3 app.py
```

### Stop Server
Press `CTRL+C` in the terminal

### Run in Background
```bash
python3 app.py &
```

### Check if Running
```bash
# Visit http://localhost:5000 in browser
# Or use curl
curl http://localhost:5000
```

---

## 🌍 Sharing with Other Teachers

### On Same Network
Other teachers on your network can access at:
```
http://YOUR_IP_ADDRESS:5000
```

To find your IP:
```bash
# macOS/Linux
ifconfig | grep "inet "

# Windows
ipconfig
```

### Example:
If your IP is `192.168.1.100`, share:
```
http://192.168.1.100:5000
```

**Note**: Make sure firewall allows port 5000.

---

## ⚙️ Configuration

### Change Port
Edit `app.py`, change last line:
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Change 5000 to 8080
```

### File Size Limit
Edit `app.py`:
```python
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB instead of 16MB
```

---

## 🎯 Use Cases

### Use Case 1: Weekly Exit Tickets
1. Friday: Students take exit ticket
2. Friday evening: Export to Excel, upload to web UI
3. Saturday: Download generated questions
4. Monday: Assign questions to struggling students

### Use Case 2: Department Collaboration
1. Start server on your machine
2. Share URL with department colleagues
3. Everyone can upload their exit tickets
4. Everyone downloads their personalized questions

### Use Case 3: Remote Teaching
1. Students submit responses via Google Forms
2. Export to Excel
3. Upload via web UI
4. Share generated questions via LMS/email

---

## 🔧 Troubleshooting

### Server Won't Start
**Problem**: Port 5000 already in use

**Solution**:
```bash
# Kill existing process on port 5000
lsof -ti:5000 | xargs kill -9

# Or use different port
# Edit app.py and change port number
```

### Can't Upload File
**Problem**: File too large or wrong format

**Solution**:
- Check file is `.xlsx` format
- Check file is under 16MB
- Try exporting Excel as new file

### No Questions Generated
**Problem**: All student answers correct

**Solution**:
- Verify some answers are incorrect
- Check `Student_Answer` ≠ `Correct_Answer` for some rows
- Review required Excel columns

### Generation Takes Too Long
**Problem**: Large number of concepts

**Solution**:
- Use concept filter to generate one at a time
- Start with one concept to test
- Consider running overnight for large datasets

---

## 📸 Screenshots

### Main Interface
- Clean upload zone with drag-and-drop
- Visual feedback when file selected
- Optional filters for concept/language

### Processing
- Animated loading spinner
- Status message
- Estimated time

### Results
- Summary statistics card
- Concept breakdown with badges
- Two clear download buttons
- Option to generate more

---

## 💡 Tips for Teachers

### Best Practices
1. **Test First**: Use sample data before real exit tickets
2. **One Concept**: Start by filtering to one concept
3. **Review Questions**: Always review before sharing with students
4. **Save Outputs**: Keep a library of generated questions
5. **Track Progress**: Name files with dates (auto-generated)

### Workflow Optimization
1. **Template Excel**: Create template with proper columns
2. **Quick Export**: Set up Google Forms → Excel export
3. **Batch Process**: Upload multiple exit tickets in one session
4. **Share Links**: Bookmark `http://localhost:5000` for quick access

---

## 🎓 For School IT Administrators

### Install on Server
```bash
# Clone repository
git clone https://github.com/Rashpinder1985/CodingTutor.git
cd CodingTutor

# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run as service (systemd example)
# Create /etc/systemd/system/question-gen.service
```

### Security Considerations
- Runs locally, no external API calls
- File uploads are temporary and deleted
- No user authentication (add if deploying publicly)
- Consider nginx reverse proxy for production

---

## 📞 Support

### Common Questions

**Q: Do I need internet?**  
A: No! Runs completely offline with Ollama.

**Q: Is my data safe?**  
A: Yes! Everything stays on your machine.

**Q: Can multiple teachers use it?**  
A: Yes! Share the URL on your local network.

**Q: Can I use it on Windows?**  
A: Yes! Just use `venv\Scripts\activate` instead of `source venv/bin/activate`

---

## 🔄 Updates

### Check for Updates
```bash
cd /Users/rashpinderkaur/Agent_Compute
git pull
pip install -r requirements.txt  # Update dependencies if needed
```

---

## ✨ What's Next?

Future enhancements (not yet implemented):
- User authentication
- Question history/library
- Student progress tracking
- Batch processing
- Email notifications
- Integration with Google Classroom
- Mobile app

---

## 📝 Quick Reference Card

```
┌─────────────────────────────────────────┐
│  ADAPTIVE QUESTION GENERATOR WEB UI     │
├─────────────────────────────────────────┤
│                                         │
│  🚀 Start:  python3 app.py              │
│  🌐 URL:    http://localhost:5000       │
│  🛑 Stop:   CTRL+C                      │
│                                         │
│  📤 Upload: Drag Excel file             │
│  ⚙️  Filter: Optional concept/language  │
│  🎯 Generate: Click button              │
│  📥 Download: JSON or ZIP               │
│                                         │
└─────────────────────────────────────────┘
```

---

**Made with ❤️ for Teachers**

Simple. Beautiful. Powerful.

