# Google Gemini Fallback Setup Guide

## 🚀 Quick Setup (5 minutes)

The system now has **automatic fallback** from Ollama to Gemini if Ollama fails!

---

## Why Gemini Fallback?

### Benefits:
- ✅ **Free Tier**: 60 requests/minute free
- ✅ **Fast**: Gemini-1.5-Flash is very quick
- ✅ **Reliable**: Cloud-based, always available
- ✅ **Automatic**: No manual intervention needed
- ✅ **Quality**: Similar quality to Ollama for question generation

### Fallback Order:
1. **Ollama** (local, free) - Primary
2. **Gemini** (cloud, free tier) - First fallback ⭐
3. **OpenAI** (cloud, paid) - Last fallback

---

## 📝 Step-by-Step Setup

### 1. Get Gemini API Key (Free)

Visit: https://makersuite.google.com/app/apikey

1. Sign in with your Google account
2. Click "Create API Key"
3. Copy the generated key

**Note:** Gemini is FREE with generous limits:
- 60 requests/minute
- 1,500 requests/day
- More than enough for question generation!

### 2. Set Environment Variable

#### macOS/Linux:
```bash
# Temporary (for current session)
export GEMINI_API_KEY="your-api-key-here"

# Permanent (add to ~/.zshrc or ~/.bashrc)
echo 'export GEMINI_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

#### Windows (PowerShell):
```powershell
# Temporary
$env:GEMINI_API_KEY="your-api-key-here"

# Permanent
[System.Environment]::SetEnvironmentVariable('GEMINI_API_KEY', 'your-api-key-here', 'User')
```

#### Using .env file (Alternative):
```bash
cd /Users/rashpinderkaur/Desktop/Agent_Compute
echo "GEMINI_API_KEY=your-api-key-here" >> .env
```

### 3. Install Gemini SDK

```bash
cd /Users/rashpinderkaur/Desktop/Agent_Compute
pip3 install google-generativeai --break-system-packages
```

Or if you already have requirements.txt:
```bash
pip3 install -r requirements.txt --break-system-packages
```

### 4. Verify Setup

```bash
python3 -c "import google.generativeai as genai; print('✓ Gemini SDK installed!')"
echo $GEMINI_API_KEY  # Should show your key
```

---

## ⚙️ Configuration

The fallback is already configured in `config.yaml`:

```yaml
llm:
  provider: "ollama"  # Primary provider
  model: "llama3.2"
  fallback_enabled: true  # ✓ Enabled by default
  
  fallback_providers:
    - provider: "gemini"
      model: "gemini-1.5-flash"
      api_key_env: "GEMINI_API_KEY"
    - provider: "openai"
      model: "gpt-3.5-turbo"
      api_key_env: "OPENAI_API_KEY"
```

### To Use Gemini as Primary:

If you want to use Gemini directly instead of Ollama:

```yaml
llm:
  provider: "gemini"
  model: "gemini-1.5-flash"
  api_key_env: "GEMINI_API_KEY"
```

---

## 🧪 Test the Fallback

### 1. Test with Ollama Working:
```bash
python3 app.py
# Upload file and generate questions
# Should use Ollama (check terminal)
```

### 2. Test Fallback (Stop Ollama):
```bash
# Stop Ollama
pkill ollama

# Start app
python3 app.py
# Upload file and generate questions
# Should automatically fallback to Gemini!
```

You'll see in the terminal:
```
WARNING: OLLAMA attempt 1 failed: Connection refused
WARNING: Primary provider ollama failed, trying fallbacks...
INFO: Attempting fallback to gemini (gemini-1.5-flash)...
INFO: ✓ Fallback to gemini succeeded!
```

---

## 📊 What Happens During Fallback

### Scenario 1: Ollama is Running ✅
```
Request → Ollama → Success → Return questions
```

### Scenario 2: Ollama Fails, Gemini Succeeds ✅
```
Request → Ollama (fails) → Gemini → Success → Return questions
```

### Scenario 3: Both Fail, OpenAI Succeeds ✅
```
Request → Ollama (fails) → Gemini (fails) → OpenAI → Success
```

### Scenario 4: All Fail ❌
```
Request → Ollama (fails) → Gemini (fails) → OpenAI (fails) → Error
```

---

## 💰 Cost Comparison

| Provider | Type | Cost | Speed | Setup |
|----------|------|------|-------|-------|
| **Ollama** | Local | Free | Medium | Easy |
| **Gemini** | Cloud | Free* | Fast | Very Easy |
| **OpenAI** | Cloud | $0.002-0.03/1K | Fast | Easy |

*Gemini Free Tier: 60 req/min, 1,500 req/day

---

## 🔍 Monitoring Fallback Usage

Check the terminal output:

### Normal Operation (Ollama):
```
INFO: Initialized LLM generator with Ollama model: llama3.2
INFO: Generated beginner programming question 1/4
```

### Fallback to Gemini:
```
WARNING: OLLAMA attempt 1 failed: ...
INFO: Attempting fallback to gemini (gemini-1.5-flash)...
INFO: Initialized LLM generator with Gemini model: gemini-1.5-flash
INFO: ✓ Fallback to gemini succeeded!
INFO: Generated beginner programming question 1/4
```

---

## ⚠️ Troubleshooting

### "Gemini API key not found"
```bash
# Check if set:
echo $GEMINI_API_KEY

# If empty, set it:
export GEMINI_API_KEY="your-key-here"
```

### "Module 'google.generativeai' not found"
```bash
pip3 install google-generativeai --break-system-packages
```

### "Fallback not working"
Check `config.yaml`:
```yaml
fallback_enabled: true  # Must be true
```

### "Rate limit exceeded"
Gemini free tier limits:
- 60 requests/minute
- 1,500 requests/day

If you hit limits, wait or upgrade to paid tier.

---

## 🎯 Best Practices

### For Development:
- Use Ollama (free, local, private)
- Set up Gemini as fallback for reliability

### For Production:
- Use Gemini as primary (reliable, fast)
- Set up OpenAI as fallback (most reliable)

### For Privacy:
- Use Ollama only (local, no data leaves your machine)
- Disable fallback: `fallback_enabled: false`

---

## 📚 Advanced Configuration

### Custom Fallback Chain:
```yaml
fallback_providers:
  - provider: "gemini"
    model: "gemini-1.5-pro"  # More capable model
    api_key_env: "GEMINI_API_KEY"
  - provider: "gemini"
    model: "gemini-1.5-flash"  # Faster model
    api_key_env: "GEMINI_API_KEY_BACKUP"
  - provider: "openai"
    model: "gpt-4"
    api_key_env: "OPENAI_API_KEY"
```

### Disable Fallback:
```yaml
fallback_enabled: false
```

### Change Retry Attempts:
```yaml
retry_attempts: 5  # Try more times before fallback
retry_delay: 3     # Wait longer between retries
```

---

## 🔗 Useful Links

- **Get Gemini API Key**: https://makersuite.google.com/app/apikey
- **Gemini Pricing**: https://ai.google.dev/pricing
- **Gemini Documentation**: https://ai.google.dev/docs
- **Rate Limits**: https://ai.google.dev/docs/rate_limits

---

## ✅ Summary

1. **Get Gemini API key** (free): https://makersuite.google.com/app/apikey
2. **Set environment variable**: `export GEMINI_API_KEY="your-key"`
3. **Install SDK**: `pip3 install google-generativeai`
4. **That's it!** Fallback is automatic

Your system now has:
- ✅ Primary: Ollama (local, free)
- ✅ Fallback: Gemini (cloud, free)
- ✅ Backup: OpenAI (cloud, paid)

**No manual intervention needed - it just works!** 🎉

---

**Questions?** Open an issue on GitHub or check the logs in the terminal.

