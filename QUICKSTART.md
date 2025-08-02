# ⚡ Quick Start Guide

Get the User Authentication BFF template running in 5 minutes!

## 🚀 Prerequisites

- Python 3.11+
- PostgreSQL 12+
- Docker (for Keycloak)

## 🏃‍♂️ 5-Minute Setup

### 1. Clone and Install
```bash
# Clone the template
git clone <your-repo>
cd user-auth-bff

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep -E "(fastapi|sqlalchemy|uvicorn)"
```

### 2. Start Keycloak
```bash
# Start Keycloak with Docker (runs in background)
docker run -d -p 8080:8080 \
  -e KEYCLOAK_ADMIN=admin \
  -e KEYCLOAK_ADMIN_PASSWORD=admin \
  --name keycloak-dev \
  quay.io/keycloak/keycloak:latest start-dev

# Wait 30 seconds for Keycloak to start
sleep 30
```

### 3. Configure Environment
```bash
# Copy environment template
cp .env.template .env

# Edit .env file (use your preferred editor)
nano .env
```

**Minimal .env configuration:**
```env
# Database (update with your PostgreSQL credentials)
DATABASE_URL=postgresql://your_user:your_password@localhost:5432/your_db

# Keycloak (these work with the Docker setup above)
KEYCLOAK_BASE_URL=http://localhost:8080
KEYCLOAK_REALM=astro-app
KEYCLOAK_CLIENT_ID=astro-client
KEYCLOAK_CLIENT_SECRET=your-secret-will-be-generated
KEYCLOAK_ADMIN_USER=admin
KEYCLOAK_ADMIN_PASSWORD=admin

# JWT (change in production!)
JWT_SECRET_KEY=dev-secret-key-change-in-production
```

### 4. Setup Database
```bash
# Create database and tables
python setup_clean_database.py
```

### 5. Configure Keycloak

**Open Keycloak Admin Console:**
- URL: http://localhost:8080/admin
- Username: `admin`
- Password: `admin`

**Quick Configuration:**

1. **Create Realm:**
   - Click "Create Realm" → Name: `astro-app` → Create

2. **Create Client:**
   - Go to Clients → Create client
   - Client ID: `astro-client` → Next
   - Client authentication: ON → Next
   - Root URL: `http://localhost:3000` → Save

3. **Get Client Secret:**
   - Go to your client → Credentials tab
   - Copy the secret → Update `.env` file

4. **Create Role:**
   - Go to Realm roles → Create role
   - Role name: `user` → Save

5. **Create Test User:**
   - Go to Users → Add user
   - Username: `testuser`
   - Email: `test@example.com`
   - Email verified: ON → Create
   - Credentials tab → Set password: `test123` (Temporary: OFF)
   - Role mappings tab → Assign role → Select `user` → Assign

### 6. Start the API
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Start the development server
python main.py

# Alternative: using uvicorn directly
# uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# API will be running at http://localhost:8001
# Docs available at http://localhost:8001/docs
```

**Expected output:**
```
INFO:auth:Keycloak clients initialized for realm ASTRO
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started server process [12345]
INFO:     Application startup complete.
```

### 7. Test Everything
```bash
# Run the health check
python health_check.py

# Should see all green checkmarks ✅
```

## 🧪 Test the API

### Test Login
```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}'
```

**Expected response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Test Registration
```bash
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "password123",
    "email": "new@example.com",
    "first_name": "New",
    "last_name": "User",
    "role": "user"
  }'
```

### Test Protected Endpoint
```bash
# Use the token from login response
curl -X GET http://localhost:8001/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🎯 What You Get

After setup, you have:

- ✅ **Working Authentication API** at http://localhost:8001
- ✅ **Interactive API Docs** at http://localhost:8001/docs  
- ✅ **Keycloak Admin Console** at http://localhost:8080/admin
- ✅ **PostgreSQL Database** with user tables
- ✅ **JWT Token System** for session management
- ✅ **User Registration & Login** endpoints
- ✅ **Password Reset** functionality
- ✅ **User Profile** management
- ✅ **Role-Based Access** control

## 🔗 Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/auth/login` | POST | User login |
| `/auth/register` | POST | User registration |
| `/auth/me` | GET | Get current user |
| `/auth/status` | GET | User status for frontend |
| `/users/me` | GET/POST/PUT | User profile management |
| `/health` | GET | Health check |
| `/docs` | GET | API documentation |

## 🛠️ Next Steps

### For Development
1. **Install frontend** (React, Vue, etc.) 
2. **Configure CORS** in `main.py` for your frontend URL
3. **Add business logic** endpoints
4. **Customize user profile** fields

### For Production
1. **Change JWT secret** in `.env`
2. **Setup production database**
3. **Configure production Keycloak**
4. **Enable HTTPS**
5. **Setup monitoring**

## 🔍 Troubleshooting

### "Connection refused" → Keycloak not running
```bash
# Check if Keycloak container is running
docker ps | grep keycloak

# If not running, start it
docker start keycloak-dev
```

### "Database connection failed" → PostgreSQL issue
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Update DATABASE_URL in .env with correct credentials
```

### "Client not found" → Keycloak configuration
- Verify client ID matches exactly in Keycloak and `.env`
- Check you're in the correct realm
- Ensure client authentication is enabled

### "Invalid credentials" → User setup
- Check user exists in Keycloak
- Verify password is set (not temporary)
- Confirm user has the `user` role

## 📚 Learn More

- **Full Documentation**: See `README.md`
- **Keycloak Setup**: See `KEYCLOAK_SETUP.md`  
- **Database Schema**: See `DATABASE_SCHEMA.md`
- **API Docs**: http://localhost:8001/docs

---

**🎉 You're ready to build!** This template gives you a complete authentication foundation to build upon.
