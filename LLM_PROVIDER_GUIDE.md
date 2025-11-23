# LLM Provider Selection Guide

## 🎯 Overview

You can now choose which AI provider to use for question generation directly from the web UI!

---

## 🚀 Quick Start

### Option 1: Use the Startup Script (Recommended)

```bash
cd /Users/rashpinderkaur/Desktop/Agent_Compute
./start_server.sh
```

This script:
- ✅ Sets GEMINI_API_KEY automatically
- ✅ Kills any existing server
- ✅ Starts Flask with correct config

### Option 2: Manual Start

```bash
cd /Users/rashpinderkaur/Desktop/Agent_Compute
export GEMINI_API_KEY="AIzaSyDsw7PUW8xj5Qgyv4CCnfMMrXowCtkMEpk"
python3 app.py
```

---

## 🤖 Available AI Providers

### 1. **Ollama** (Local, Free) 🏠

**Pros:**
- ✅ Completely private
- ✅ No cost
- ✅ No API key needed

**Cons:**
- ⚠️ Requires Ollama installed and running
- ⚠️ Can be slower
- ⚠️ Uses your computer resources

**Setup:**
```bash
# Check if Ollama is running
ollama list

# If not running, start it
ollama serve
```

**Select in UI:** Choose "Ollama (Local, Free) 🏠"

---

### 2. **Gemini** (Cloud, Free) ⚡

**Pros:**
- ✅ Fast generation
- ✅ Free tier (60 req/min, 1500/day)
- ✅ Reliable cloud service

**Cons:**
- ⚠️ Requires API key
- ⚠️ Data sent to Google

**Setup:**
1. Get API key: https://makersuite.google.com/app/apikey
2. Set environment variable:
   ```bash
   export GEMINI_API_KEY="your-key-here"
   ```
3. Or edit `start_server.sh` to include your key

**Select in UI:** Choose "Gemini (Cloud, Free) ⚡"

---

### 3. **OpenAI** (Cloud, Paid) 🚀

**Pros:**
- ✅ Highest quality
- ✅ Most reliable
- ✅ Well-tested

**Cons:**
- ⚠️ Costs money
- ⚠️ Requires API key
- ⚠️ Data sent to OpenAI

**Setup:**
1. Get API key: https://platform.openai.com/api-keys
2. Set environment variable:
   ```bash
   export OPENAI_API_KEY="your-key-here"
   ```

**Select in UI:** Choose "OpenAI (Cloud, Paid) 🚀"

---

### 4. **Auto (Fallback Chain)** 🔄 ⭐ **Recommended**

**How it works:**
```
Try Ollama → If fails → Try Gemini → If fails → Try OpenAI
```

**Pros:**
- ✅ Maximum reliability
- ✅ Automatic recovery
- ✅ No manual intervention

**Cons:**
- ⚠️ Still needs API keys for fallbacks

**Select in UI:** Choose "Auto (Fallback Chain) 🔄"

---

## 🎓 How to Use

### Step 1: Start Server
```bash
./start_server.sh
```

### Step 2: Open Browser
```
http://localhost:5000
```

### Step 3: Select AI Provider

In the upload form, you'll see a dropdown labeled **"AI Provider"**:

- **Ollama (Local, Free)** - Use if Ollama is running
- **Gemini (Cloud, Free)** - Use if you have Gemini API key
- **OpenAI (Cloud, Paid)** - Use if you have OpenAI API key
- **Auto (Fallback Chain)** - Recommended, tries all in order

### Step 4: Upload & Generate

1. Upload your exit ticket Excel file
2. Click "Analyze File"
3. Select a concept
4. Click "Generate Questions"
5. Watch the terminal to see which AI is being used!

---

## 📺 What You'll See

### When Using Ollama:
```bash
User selected LLM provider: ollama
INFO: Initialized LLM generator with Ollama model: llama3.2
```

### When Using Gemini:
```bash
User selected LLM provider: gemini
✓ Gemini API key found: AIzaSyDsw7...MEpk
INFO: Initialized LLM generator with Gemini model: gemini-1.5-flash
```

### When Using Auto (Fallback):
```bash
Using automatic fallback chain: Ollama → Gemini → OpenAI
INFO: Initialized LLM generator with Ollama model: llama3.2
(If Ollama fails)
WARNING: Primary provider ollama failed, trying fallbacks...
INFO: Attempting fallback to gemini (gemini-1.5-flash)...
INFO: ✓ Fallback to gemini succeeded!
```

---

## ⚠️ Troubleshooting

### Error: "No client initialized"

**Cause:** Selected provider couldn't initialize

**Solutions:**

**For Ollama:**
```bash
# Check if running
ollama list

# Start Ollama
ollama serve
```

**For Gemini:**
```bash
# Check if API key is set
echo $GEMINI_API_KEY

# Set it if not
export GEMINI_API_KEY="your-key-here"

# Or use start_server.sh which sets it automatically
./start_server.sh
```

**For OpenAI:**
```bash
# Check if API key is set
echo $OPENAI_API_KEY

# Set it if not
export OPENAI_API_KEY="your-key-here"
```

### Error: "Gemini API key not found"

**Solution:**
1. Make sure you start server with:
   ```bash
   ./start_server.sh
   ```

2. Or manually set before starting:
   ```bash
   export GEMINI_API_KEY="AIzaSyDsw7PUW8xj5Qgyv4CCnfMMrXowCtkMEpk"
   python3 app.py
   ```

### Error: "Port 5000 is in use"

**Solution:**
```bash
# Kill existing server
lsof -ti:5000 | xargs kill -9

# Restart
./start_server.sh
```

---

## 💡 Recommendations

### For Development / Testing:
- **Use:** Auto (Fallback Chain)
- **Why:** Most reliable, tries everything

### For Production (Privacy-Focused):
- **Use:** Ollama only
- **Why:** All data stays local

### For Production (Speed-Focused):
- **Use:** Gemini
- **Why:** Fast, free, reliable

### For Production (Quality-Focused):
- **Use:** OpenAI
- **Why:** Best quality, worth the cost

---

## 🔐 Security Notes

### API Keys:
- ✅ **DO** add your API key to `start_server.sh` for convenience
- ✅ **DO** use environment variables
- ❌ **DON'T** commit API keys to Git
- ❌ **DON'T** share your API keys

### Data Privacy:
- **Ollama:** ✅ Private (local processing)
- **Gemini:** ⚠️ Data sent to Google
- **OpenAI:** ⚠️ Data sent to OpenAI

---

## 📊 Cost Comparison

| Provider | Cost | Speed | Privacy | Setup |
|----------|------|-------|---------|-------|
| Ollama | Free | Medium | ✅ Full | Easy |
| Gemini | Free* | Fast | ⚠️ Cloud | Very Easy |
| OpenAI | Paid | Fast | ⚠️ Cloud | Easy |
| Auto | Mixed | Mixed | Mixed | Easy |

*Gemini free tier: 60 req/min, 1500 req/day

---

## 🎬 Quick Commands

### Check Status:
```bash
# Check if Ollama is running
ollama list

# Check if API keys are set
echo $GEMINI_API_KEY
echo $OPENAI_API_KEY

# Check if server is running
curl -s http://localhost:5000 > /dev/null && echo "✓ Running" || echo "✗ Not running"
```

### Start Server:
```bash
# Recommended way
./start_server.sh

# Manual way
export GEMINI_API_KEY="your-key"
python3 app.py
```

### Stop Server:
```bash
# Press Ctrl+C in terminal
# Or kill the process
lsof -ti:5000 | xargs kill -9
```

---

## ✅ Summary

1. **Start server:** `./start_server.sh`
2. **Open UI:** http://localhost:5000
3. **Select AI provider** from dropdown
4. **Upload & generate** questions
5. **Watch terminal** for status

**For most users:** Select **"Auto (Fallback Chain)"** and let the system handle everything!

---

## 🆘 Still Having Issues?

1. **Check terminal output** for error messages
2. **Verify API keys** are set: `echo $GEMINI_API_KEY`
3. **Check Ollama** is running: `ollama list`
4. **Restart server:** `./start_server.sh`
5. **Check GitHub** for updates

---

**Made with ❤️ for Teachers**

