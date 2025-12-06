# Railway Deployment Checklist

## Before Deploying

- [ ] Code committed and pushed to GitHub
- [ ] PostgreSQL database provisioned on Railway
- [ ] Environment variables set in Railway:
  - [ ] `SECRET_KEY` (generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
  - [ ] `API_KEY_ENCRYPTION_KEY` (optional, will auto-generate)
  - [ ] `DATABASE_URL` (auto-set by Railway when PostgreSQL is added)

## After Deploying

1. **Visit your Railway URL**
   - [ ] App loads without errors
   - [ ] Login/Register modal appears

2. **Test Registration**
   - [ ] Can register with email/password
   - [ ] Success message appears
   - [ ] Modal closes after registration

3. **Test API Key Management**
   - [ ] API Key Management section appears after login
   - [ ] Can save Gemini API key
   - [ ] Can save OpenAI API key
   - [ ] Status badges update correctly

4. **Test Features**
   - [ ] Can upload exit ticket (after setting API keys)
   - [ ] Can generate questions
   - [ ] Can analyze activity

5. **Test Database**
   - [ ] Go to Railway PostgreSQL → Data tab
   - [ ] Verify `users` table exists
   - [ ] Verify `user_api_keys` table exists
   - [ ] Check that API keys are encrypted (not plain text)

## Common Issues

**Issue:** "Database connection failed"
- Solution: Ensure PostgreSQL is provisioned and `DATABASE_URL` is set

**Issue:** "Encryption cipher not available"
- Solution: Set `API_KEY_ENCRYPTION_KEY` in Railway variables

**Issue:** Features don't work
- Solution: Check that user has set at least one API key
- Check Railway logs for errors

## Railway Logs

View logs in Railway dashboard:
1. Go to your service
2. Click "Deployments" tab
3. Click on latest deployment
4. View logs for errors

## Quick Commands

**Check Railway environment variables:**
- Go to Service → Variables tab

**View database:**
- Go to PostgreSQL service → Data tab

**View logs:**
- Go to Service → Deployments → Latest → Logs
