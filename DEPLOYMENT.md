# Deployment Guide

This guide covers deploying the Exit Ticket Analysis Agent to cloud platforms.

## 🚀 Railway.app (Recommended)

**Free Tier:** $5/month credit (usually enough for small apps)

### Setup Steps

1. **Go to Railway**: https://railway.app
2. **Sign up** with GitHub
3. **New Project** → "Deploy from GitHub repo"
4. **Select repository**: `Rashpinder1985/CodingTutor`
5. **Add PostgreSQL Database**:
   - Click "New" → "Database" → "Add PostgreSQL"
   - Railway automatically sets `DATABASE_URL`
6. **Set Environment Variables** (Service → Variables):
   - `SECRET_KEY`: Generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`
   - `API_KEY_ENCRYPTION_KEY` (optional): Generate with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
7. **Deploy**: Railway auto-deploys on git push

### Configuration Files

- `nixpacks.toml` - Railway build configuration
- `Procfile` - Process configuration
- `runtime.txt` - Python version

### After Deployment

1. Visit your Railway URL
2. Register a new account
3. Set your API keys (Gemini or OpenAI)
4. Start using the app!

---

## 🌐 Alternative Platforms

See `DEPLOYMENT_ALTERNATIVES.md` for other options:
- Fly.io
- Render
- PythonAnywhere
- Heroku

---

## 📝 Environment Variables

**Required:**
- `SECRET_KEY` - Flask session secret key
- `DATABASE_URL` - PostgreSQL connection (auto-set by Railway)

**Optional:**
- `API_KEY_ENCRYPTION_KEY` - For encrypting user API keys (auto-generates if not set)
- `GEMINI_API_KEY` - Default Gemini key (users can override with their own)
- `OPENAI_API_KEY` - Default OpenAI key (users can override with their own)

---

## 🔧 Troubleshooting

**Database connection failed:**
- Ensure PostgreSQL is provisioned
- Check `DATABASE_URL` is set

**Encryption errors:**
- Set `API_KEY_ENCRYPTION_KEY` in environment variables

**App won't start:**
- Check Railway logs for errors
- Verify all dependencies are in `requirements.txt`
- Ensure Python version matches `runtime.txt`

---

## 📚 Additional Resources

- [Testing Guide](TESTING_GUIDE.md) - Local and Railway testing
- [Railway Checklist](railway_test_checklist.md) - Deployment checklist

