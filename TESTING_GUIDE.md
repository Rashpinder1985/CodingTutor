# Testing Guide: User Authentication & API Key Management

## 🧪 Testing Checklist

### Prerequisites

1. **Local Testing:**
   - Python 3.11+ installed
   - PostgreSQL installed (or SQLite will be used automatically)
   - All dependencies installed: `pip install -r requirements.txt`

2. **Railway Testing:**
   - Railway account with project deployed
   - PostgreSQL database provisioned on Railway
   - Environment variables set

---

## 📋 Local Testing Steps

### Step 1: Install Dependencies

```bash
cd /Users/rashpinderkaur/Desktop/Agent_Compute
pip install -r requirements.txt
```

### Step 2: Set Up Database (Optional - SQLite works automatically)

**Option A: Use SQLite (Default - No setup needed)**
- The app will automatically create `app.db` in the project directory
- No additional configuration required

**Option B: Use PostgreSQL (Recommended for production-like testing)**
1. Install PostgreSQL: `brew install postgresql` (macOS) or use your package manager
2. Create database: `createdb agent_compute`
3. Set environment variable:
   ```bash
   export DATABASE_URL="postgresql://localhost/agent_compute"
   ```

### Step 3: Set Environment Variables (Optional)

```bash
# For encryption key (optional - will auto-generate if not set)
export API_KEY_ENCRYPTION_KEY="your-32-byte-base64-key-here"

# For Flask secret key (optional - has default)
export SECRET_KEY="your-secret-key-here"
```

**Generate encryption key:**
```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

### Step 4: Start Local Server

```bash
python app.py
```

Or with Gunicorn:
```bash
gunicorn app:app --bind 0.0.0.0:5000 --timeout 300
```

### Step 5: Test Authentication Flow

1. **Open Browser:** `http://localhost:5000`

2. **Test Registration:**
   - Click "Login / Register" button
   - Switch to "Register" tab
   - Enter email: `test@example.com`
   - Enter password: `testpassword123` (min 8 chars)
   - Click "Register"
   - ✅ Should see success message and modal closes
   - ✅ Should see your email in header

3. **Test API Key Management:**
   - After login, you should see "API Key Management" section
   - Enter a Gemini API key (get from https://aistudio.google.com/app/apikey)
   - Click "Save API Keys"
   - ✅ Should see "✓ Gemini key set" badge
   - ✅ Upload form should become enabled

4. **Test Logout:**
   - Click "Logout" button
   - ✅ Should redirect to login modal
   - ✅ Session cleared

5. **Test Login:**
   - Enter same email and password
   - Click "Login"
   - ✅ Should login successfully
   - ✅ API keys should still be saved

6. **Test Feature Access:**
   - Upload an exit ticket file
   - ✅ Should work if API keys are set
   - ✅ Should show error if no API keys

### Step 6: Verify Database

**If using SQLite:**
```bash
sqlite3 app.db
.tables
SELECT * FROM users;
SELECT user_id, gemini_api_key_encrypted IS NOT NULL as has_gemini, openai_api_key_encrypted IS NOT NULL as has_openai FROM user_api_keys;
```

**If using PostgreSQL:**
```bash
psql agent_compute
\dt
SELECT * FROM users;
SELECT user_id, gemini_api_key_encrypted IS NOT NULL as has_gemini, openai_api_key_encrypted IS NOT NULL as has_openai FROM user_api_keys;
```

---

## 🚀 Railway Testing Steps

### Step 1: Add PostgreSQL Database

1. Go to Railway dashboard: https://railway.app/dashboard
2. Select your project
3. Click "New" → "Database" → "Add PostgreSQL"
4. Railway will automatically set `DATABASE_URL` environment variable

### Step 2: Set Environment Variables

Go to your service → Variables tab and add:

1. **SECRET_KEY** (Required)
   - Generate a secure random string:
     ```bash
     python -c "import secrets; print(secrets.token_urlsafe(32))"
     ```
   - Add to Railway: `SECRET_KEY=your-generated-key`

2. **API_KEY_ENCRYPTION_KEY** (Optional but recommended)
   - Generate Fernet key:
     ```python
     from cryptography.fernet import Fernet
     print(Fernet.generate_key().decode())
     ```
   - Add to Railway: `API_KEY_ENCRYPTION_KEY=your-generated-key`

### Step 3: Deploy Code

```bash
git add .
git commit -m "Add user authentication and API key management"
git push origin main
```

Railway will automatically deploy.

### Step 4: Test on Railway

1. **Visit your Railway URL:** `https://your-app.up.railway.app`

2. **Test Registration:**
   - Click "Login / Register"
   - Register with a test email
   - ✅ Should work

3. **Test API Key Management:**
   - Set your Gemini or OpenAI API key
   - ✅ Should save successfully

4. **Test Features:**
   - Upload exit ticket
   - Generate questions
   - ✅ Should use your API keys

### Step 5: Verify Database on Railway

1. Go to Railway dashboard
2. Click on PostgreSQL database
3. Go to "Data" tab
4. Run query:
   ```sql
   SELECT * FROM users;
   SELECT user_id, 
          gemini_api_key_encrypted IS NOT NULL as has_gemini,
          openai_api_key_encrypted IS NOT NULL as has_openai 
   FROM user_api_keys;
   ```

---

## ✅ Test Scenarios

### Scenario 1: New User Registration
- [ ] Can register with valid email
- [ ] Cannot register with duplicate email
- [ ] Password must be at least 8 characters
- [ ] Email format is validated

### Scenario 2: Login/Logout
- [ ] Can login with correct credentials
- [ ] Cannot login with wrong password
- [ ] Cannot login with non-existent email
- [ ] Logout clears session

### Scenario 3: API Key Management
- [ ] Can save Gemini API key
- [ ] Can save OpenAI API key
- [ ] Can save both keys
- [ ] At least one key is required
- [ ] Keys are encrypted in database
- [ ] Keys are not visible in UI after saving

### Scenario 4: Feature Access
- [ ] Cannot upload files without login
- [ ] Cannot generate questions without API keys
- [ ] Can use features after setting API keys
- [ ] Each user's API keys are isolated

### Scenario 5: Session Management
- [ ] Session persists after page refresh
- [ ] Session expires on logout
- [ ] Multiple users can use app simultaneously

---

## 🐛 Troubleshooting

### Issue: "Database connection failed"
**Solution:**
- Check `DATABASE_URL` is set correctly
- For Railway: Ensure PostgreSQL is provisioned
- For local: Check PostgreSQL is running

### Issue: "Encryption cipher not available"
**Solution:**
- Set `API_KEY_ENCRYPTION_KEY` environment variable
- Or let it auto-generate (will show warning)

### Issue: "Authentication required" error
**Solution:**
- Make sure you're logged in
- Check browser cookies are enabled
- Clear cookies and try again

### Issue: "At least one API key required"
**Solution:**
- Go to API Key Management section
- Set either Gemini or OpenAI key
- Click "Save API Keys"

### Issue: Features not working after setting keys
**Solution:**
- Check API keys are valid
- Check browser console for errors
- Verify keys are saved in database

---

## 📊 Expected Database Schema

After first run, you should have:

**users table:**
- id (integer, primary key)
- email (string, unique)
- password_hash (string)
- created_at (datetime)
- updated_at (datetime)

**user_api_keys table:**
- id (integer, primary key)
- user_id (integer, foreign key to users.id)
- gemini_api_key_encrypted (text, nullable)
- openai_api_key_encrypted (text, nullable)
- created_at (datetime)
- updated_at (datetime)

---

## 🎯 Quick Test Commands

**Check if tables exist:**
```python
python -c "from app import app, db; app.app_context().push(); print(db.engine.table_names())"
```

**Create test user (Python shell):**
```python
from app import app, db
from src.auth import register_user
from src.database import User

with app.app_context():
    success, msg, user = register_user('test@example.com', 'testpass123')
    print(f"Success: {success}, Message: {msg}")
    print(f"Users in DB: {User.query.count()}")
```

---

## 📝 Notes

- **Local Development:** SQLite is fine for testing
- **Production (Railway):** Use PostgreSQL
- **API Keys:** Never commit real API keys to git
- **Encryption Key:** Generate once and keep it secure
- **Secret Key:** Change from default in production

---

## ✅ Success Criteria

Your implementation is working if:

1. ✅ Users can register and login
2. ✅ API keys can be saved and retrieved
3. ✅ Features require authentication and API keys
4. ✅ Database stores encrypted API keys
5. ✅ Multiple users can use the app independently
6. ✅ Works both locally and on Railway

