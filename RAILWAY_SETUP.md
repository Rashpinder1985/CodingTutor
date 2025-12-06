# Railway Deployment - Fix API Key Issue

## 🔴 Current Issue

Your app is deployed but **GEMINI_API_KEY is not set** in Railway environment variables.

## ✅ Quick Fix (2 minutes)

### Step 1: Get Your Gemini API Key
1. Go to https://aistudio.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key (starts with `AIza...`)

### Step 2: Add to Railway
1. Go to your Railway dashboard: https://railway.app/dashboard
2. Click on your project: **coding-tutor-production**
3. Click on the **service** (web service)
4. Go to **Variables** tab
5. Click **+ New Variable**
6. Add:
   - **Key:** `GEMINI_API_KEY`
   - **Value:** `your_api_key_here` (paste the key from Step 1)
7. Click **Add**
8. Railway will **automatically redeploy** your app

### Step 3: Verify
1. Wait 1-2 minutes for redeploy
2. Visit: https://coding-tutor-production.up.railway.app/
3. Try uploading files - should work now!

## 🔧 Additional Fixes Applied

I've also updated the code to:
- ✅ Skip Ollama in cloud environments (it's local-only)
- ✅ Better error handling for missing API keys
- ✅ Improved fallback chain for cloud deployments

## 📝 Environment Variables Needed

**Required:**
- `GEMINI_API_KEY` - Your Gemini API key (get from https://aistudio.google.com/app/apikey)

**Optional (for fallback):**
- `OPENAI_API_KEY` - If you want OpenAI as fallback

## 🚀 After Setting API Key

Your app will:
- ✅ Use Gemini for all LLM operations
- ✅ Work properly for activity analysis
- ✅ Generate questions correctly
- ✅ No more "API key not found" errors

## 💡 Pro Tip

Railway automatically redeploys when you add environment variables, so you don't need to manually redeploy!

