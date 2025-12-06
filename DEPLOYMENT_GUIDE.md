# Deployment Guide - Render.com

## Quick Deploy Steps

### Option 1: Deploy via Render Dashboard (Recommended)

1. **Go to Render Dashboard**
   - Visit https://render.com
   - Sign up/Login with your GitHub account

2. **Create New Web Service**
   - Click "New" → "Web Service"
   - Connect your GitHub repository: `Rashpinder1985/CodingTutor`
   - Select the `main` branch

3. **Configure Service**
   - **Name:** `coding-tutor` (or your preferred name)
   - **Environment:** Python 3
   - **Build Command:** (Auto-detected from render.yaml)
   - **Start Command:** (Auto-detected from render.yaml)
   - **Plan:** Starter (Free tier available, but spins down after 15 min inactivity)

4. **Add Environment Variables**
   - Click "Environment" tab
   - Add: `GEMINI_API_KEY` = `your_gemini_api_key_here`
   - (Get your key from: https://aistudio.google.com/app/apikey)

5. **Deploy**
   - Click "Create Web Service"
   - Wait 5-10 minutes for first deployment
   - Your app will be live at: `https://coding-tutor.onrender.com`

### Option 2: Auto-Deploy via render.yaml (If supported)

If Render supports Blueprint auto-deployment:
- Push to GitHub (already done)
- Render will auto-detect `render.yaml` and deploy automatically

## Post-Deployment

### Get Your Public URL
After deployment, you'll get a URL like:
```
https://coding-tutor.onrender.com
```

### Share with Users
Users can now:
- Upload exit tickets (Excel format)
- Upload activity templates (Text/Word)
- Generate questions (programming mode)
- Get analysis reports (activity mode)
- Download Word documents

**No installation required!** Everything runs in the browser.

## Important Notes

### Free Tier Limitations
- **Spins down** after 15 minutes of inactivity
- **First request** after sleep takes ~30 seconds (cold start)
- **750 hours/month** free (enough for most use cases)

### API Key Security
- ✅ Set `GEMINI_API_KEY` in Render dashboard (Environment tab)
- ❌ Never commit API keys to GitHub
- ✅ Keys are encrypted in Render

### File Storage
- Uploaded files are **temporary** (stored in temp directory)
- Reports must be **downloaded immediately**
- Files are cleared on service restart

## Troubleshooting

### Build Fails
- Check build logs in Render dashboard
- Ensure all dependencies in `requirements.txt` are correct
- Verify Python version (3.11)

### App Crashes
- Check logs in Render dashboard
- Verify `GEMINI_API_KEY` is set correctly
- Check timeout settings (currently 300 seconds)

### Slow Performance
- Free tier has limited resources
- Consider upgrading to paid plan for better performance
- Batch processing is already optimized (5-10x faster)

## Next Steps

1. Deploy to Render using steps above
2. Test the public URL
3. Share the link with users
4. Monitor usage in Render dashboard

Your app is ready for deployment! 🚀

