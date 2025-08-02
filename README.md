# 🔐 User Authentication BFF Template

A clean, production-ready Backend for Frontend (BFF) authentication service with Keycloak integration and PostgreSQL storage.

## 🚀 **Quick Start**

### **Development**
```bash
# Clone and setup
git clone <your-repo-url>
cd auth-bff

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment (edit with your settings)
cp .env.example .env

# Run the API
python main.py
```

### **Production Deployment**
```bash
# One-command deployment
./deploy.sh

# Or manual Docker deployment
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

## 📋 **Features**

- ✅ **User Authentication** - Login, registration, password reset
- ✅ **Keycloak Integration** - External authentication server
- ✅ **User Profiles** - Store additional user information
- ✅ **JWT Tokens** - Secure API access
- ✅ **Role-based Access** - User roles and permissions
- ✅ **PostgreSQL** - Reliable data storage
- ✅ **Docker Ready** - Container deployment
- ✅ **Production Ready** - Security best practices

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │───▶│   Auth BFF      │───▶│   PostgreSQL    │
│   Application   │    │   (This API)    │    │   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │    Keycloak     │
                       │ (External Auth) │
                       └─────────────────┘
```

## 🔧 **Configuration**

### **Environment Files**
- **`.env`** - Development configuration
- **`.env.prod`** - Production configuration (not committed)

### **Key Environment Variables**
```env
# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Keycloak (external)
KEYCLOAK_BASE_URL=http://localhost:8080
KEYCLOAK_REALM=your-realm
KEYCLOAK_CLIENT_ID=your-client
KEYCLOAK_CLIENT_SECRET=your-secret

# JWT
JWT_SECRET_KEY=your-secure-secret-key
```

## 📊 **API Endpoints**

### **Authentication**
```
POST /auth/login           - User login
POST /auth/register        - User registration
POST /auth/password-reset  - Request password reset
POST /auth/change-password - Change password
GET  /auth/me             - Get current user info
GET  /auth/status         - User status for frontend routing
```

### **User Profiles**
```
GET  /users/me - Get user profile
POST /users/me - Create user profile
PUT  /users/me - Update user profile
```

### **System**
```
GET /health - Health check
GET /docs   - API documentation (Swagger)
```

## 🐳 **Docker Deployment**

### **Development**
```bash
docker-compose up -d
```

### **Production**
```bash
# Configure environment
cp .env.prod.example .env.prod
# Edit .env.prod with your settings

# Deploy
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

## 🔐 **Keycloak Setup**

Keycloak must be installed separately. See [KEYCLOAK_SETUP.md](KEYCLOAK_SETUP.md) for detailed instructions.

**Quick Keycloak with Docker:**
```bash
docker run -d --name keycloak -p 8080:8080 \
  -e KEYCLOAK_ADMIN=admin \
  -e KEYCLOAK_ADMIN_PASSWORD=admin \
  quay.io/keycloak/keycloak:latest start-dev
```

## 📖 **Documentation**

- **[VM_DEPLOYMENT_GUIDE.md](VM_DEPLOYMENT_GUIDE.md)** - Complete VM deployment guide
- **[KEYCLOAK_SETUP.md](KEYCLOAK_SETUP.md)** - Keycloak configuration
- **[DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)** - Database structure
- **[QUICKSTART.md](QUICKSTART.md)** - Quick development setup

## 🛠️ **Development**

### **Project Structure**
```
├── main.py              # FastAPI application
├── auth.py              # Authentication logic
├── models.py            # Pydantic models
├── db_models.py         # SQLAlchemy models
├── database.py          # Database configuration
├── user_service.py      # User management
├── role_management.py   # Role-based access
├── health_check.py      # Health monitoring
├── deploy.sh            # Deployment script
├── docker-compose.yml   # Development containers
├── docker-compose.prod.yml # Production containers
└── requirements.txt     # Python dependencies
```

### **Adding New Features**
1. **Add API endpoints** in `main.py`
2. **Add data models** in `models.py` (Pydantic) and `db_models.py` (SQLAlchemy)
3. **Add business logic** in appropriate service files
4. **Update database** if needed (migrations via Alembic)

## 🔒 **Security**

- ✅ **External Authentication** - Keycloak handles passwords
- ✅ **JWT Tokens** - Secure API access
- ✅ **Environment Variables** - No secrets in code
- ✅ **CORS Configuration** - Frontend integration
- ✅ **Input Validation** - Pydantic models
- ✅ **Database Security** - Prepared statements

## 📈 **Monitoring**

```bash
# Health check
curl http://localhost:8001/health

# View logs
docker-compose logs -f auth_api

# Database status
docker exec -it postgres_container psql -U user -d dbname -c "\dt"
```

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 **License**

[Your License Here]

---

**🎯 Ready-to-use authentication service for any application!**
