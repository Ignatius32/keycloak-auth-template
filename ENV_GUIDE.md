# 🔧 Environment Configuration Guide

This project uses **two environment files** for clean separation between development and production:

## 📁 **Environment Files**

### **`.env` - Development Configuration**
- ✅ **Used for local development**
- ✅ **Safe to commit** (no real secrets)
- ✅ **Points to local services**
- ✅ **Debug logging enabled**

### **`.env.prod` - Production Configuration**  
- ⚠️ **Used for production deployment**
- ❌ **NEVER commit this file** (contains real secrets)
- ✅ **Secure passwords and keys**
- ✅ **Production logging levels**

## 🚀 **Usage**

### **Development**
```bash
# Uses .env automatically
python main.py

# Or with Docker
docker-compose up -d
```

### **Production**
```bash
# Manual deployment uses .env.prod
source venv/bin/activate
python main.py

# Docker deployment
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

### **Automated Deployment**
```bash
# The deploy.sh script will:
# 1. Generate secure passwords
# 2. Create/update .env.prod
# 3. Deploy with correct environment
./deploy.sh
```

## ⚙️ **Configuration Details**

### **Development (.env) Settings:**
- Database: `astrosim_db` (your existing dev database)
- Keycloak: Points to `localhost:8080` 
- Logging: `DEBUG` level
- API: `localhost:8001`

### **Production (.env.prod) Settings:**
- Database: `auth_prod` (clean production database)
- Keycloak: External production instance
- Logging: `INFO` level  
- Security: Production-ready secrets

## 🔐 **Security Notes**

### **What's Safe to Commit:**
- ✅ `.env` (development config)
- ✅ `docker-compose.yml` (uses .env)
- ✅ `docker-compose.prod.yml` (references .env.prod)

### **What to NEVER Commit:**
- ❌ `.env.prod` (production secrets)
- ❌ `.env.prod.backup.*` (backup files)

### **Git Configuration:**
```bash
# Add to .gitignore (already included)
echo ".env.prod" >> .gitignore
echo ".env.prod.backup.*" >> .gitignore
echo ".env.backup.*" >> .gitignore
```

## 🔄 **Quick Commands**

```bash
# Check which environment is loaded
grep -E "DATABASE_URL|LOG_LEVEL" .env

# Generate secure production secrets
openssl rand -base64 48  # For JWT_SECRET_KEY
openssl rand -base64 32  # For passwords

# Switch between environments (manual)
mv .env .env.dev
mv .env.prod .env  # Use prod config
# Remember to switch back!

# Test configuration
curl http://localhost:8001/health
```

## 📋 **Environment Variables Reference**

| Variable | Dev (.env) | Prod (.env.prod) |
|----------|------------|------------------|
| `DATABASE_URL` | astrosim_db | auth_prod |
| `KEYCLOAK_REALM` | ASTRO | production |
| `JWT_SECRET_KEY` | dev-key | secure-generated |
| `LOG_LEVEL` | DEBUG | INFO |
| `API_PORT` | 8001 | 8001 |

---

**🎯 This setup gives you clean separation between dev and prod environments while keeping configuration simple and secure!**
