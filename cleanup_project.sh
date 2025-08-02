#!/bin/bash
# 🧹 Project Structure Cleanup Script
# This script will clean up the project and keep only necessary files for a clean repository

set -e

echo "🧹 Cleaning up project structure for repository..."
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[REMOVE]${NC} $1"
}

print_keep() {
    echo -e "${GREEN}[KEEP]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Create backup directory
BACKUP_DIR="cleanup_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
print_status "Created backup directory: $BACKUP_DIR"

# Function to backup and remove file
backup_and_remove() {
    if [ -f "$1" ]; then
        cp "$1" "$BACKUP_DIR/"
        rm "$1"
        print_success "Removed $1 (backed up)"
    fi
}

# Function to just remove file
remove_file() {
    if [ -f "$1" ]; then
        rm "$1"
        print_success "Removed $1"
    fi
}

# Function to keep file
keep_file() {
    if [ -f "$1" ]; then
        print_keep "Keeping $1"
    fi
}

echo ""
print_status "Removing temporary and cleanup files..."

# Remove cleanup and temporary files
backup_and_remove "cleanup_database.py"
backup_and_remove "setup_clean_database.py"
backup_and_remove "setup_database.py"
backup_and_remove "fix_existing_user.py"
backup_and_remove "final_status.py"
backup_and_remove "demo_roles.py"
backup_and_remove "check_roles.py"
remove_file "setup.sh"  # We'll keep deploy.sh instead

# Remove excessive documentation files (keep only essential ones)
print_status "Removing redundant documentation..."
backup_and_remove "CLEANUP_SUMMARY.md"
backup_and_remove "DATABASE_CLEANUP_COMPLETE.md"
backup_and_remove "ENV_CLEANUP_SUMMARY.md"
backup_and_remove "DEPLOYMENT_GUIDE.md"  # Too detailed, we have VM_DEPLOYMENT_GUIDE
backup_and_remove "DOCKER_GUIDE.md"      # Redundant with other guides
backup_and_remove "ENV_GUIDE.md"         # Redundant, info is in other files
backup_and_remove "ROLE_BASED_ACCESS_GUIDE.md"  # Not essential for basic auth

# Remove redundant requirements file
backup_and_remove "requirements.docker.txt"

# Remove old schema file (we have cleaned database now)
backup_and_remove "schema.sql"

echo ""
print_status "Files to keep (essential for the repository):"

# Essential application files
keep_file "main.py"
keep_file "auth.py"
keep_file "database.py"
keep_file "db_models.py"
keep_file "models.py"
keep_file "user_service.py"
keep_file "role_management.py"
keep_file "health_check.py"

# Essential configuration files
keep_file ".env"
keep_file ".env.prod"
keep_file ".gitignore"
keep_file "requirements.txt"

# Docker files
keep_file "Dockerfile"
keep_file "Dockerfile.prod"
keep_file "docker-compose.yml"
keep_file "docker-compose.prod.yml"
keep_file "init.sql"

# Essential documentation
keep_file "README.md"
keep_file "DATABASE_SCHEMA.md"
keep_file "VM_DEPLOYMENT_GUIDE.md"
keep_file "KEYCLOAK_SETUP.md"
keep_file "QUICKSTART.md"

# Deployment script
keep_file "deploy.sh"

echo ""
print_status "Updating README.md to be the main documentation..."

# Create a comprehensive README that combines essential information
cat > README.md << 'EOF'
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
EOF

print_success "Updated README.md with comprehensive documentation"

echo ""
print_status "Creating .env.example template..."

# Create .env.example (safe template for repository)
cat > .env.example << 'EOF'
# ==============================================
# DEVELOPMENT ENVIRONMENT TEMPLATE
# Copy this to .env and update with your values
# ==============================================

# ==============================================
# DATABASE CONFIGURATION
# ==============================================
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
DATABASE_ECHO=false

# ==============================================
# KEYCLOAK CONFIGURATION (External)
# ==============================================
KEYCLOAK_BASE_URL=http://localhost:8080
KEYCLOAK_REALM=your-realm
KEYCLOAK_CLIENT_ID=your-client-id
KEYCLOAK_CLIENT_SECRET=your-client-secret
KEYCLOAK_ADMIN_USER=admin
KEYCLOAK_ADMIN_PASSWORD=admin

# ==============================================
# JWT CONFIGURATION
# ==============================================
JWT_SECRET_KEY=your-development-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# ==============================================
# API CONFIGURATION
# ==============================================
API_HOST=0.0.0.0
API_PORT=8001
LOG_LEVEL=DEBUG
EOF

print_success "Created .env.example template"

echo ""
print_status "Updating .gitignore..."

# Update .gitignore to include more patterns
cat >> .gitignore << 'EOF'

# Cleanup and backup files
cleanup_backup_*/
*.backup.*
deployment_info.txt
EOF

print_success "Updated .gitignore"

echo ""
print_status "Final project structure:"
echo "========================================"

# Show clean project structure
echo ""
echo "📁 Essential Application Files:"
echo "  ├── main.py              # Main FastAPI application"
echo "  ├── auth.py              # Authentication logic"
echo "  ├── models.py            # API models (Pydantic)"
echo "  ├── db_models.py         # Database models (SQLAlchemy)"
echo "  ├── database.py          # Database configuration"
echo "  ├── user_service.py      # User management service"
echo "  ├── role_management.py   # Role-based access control"
echo "  └── health_check.py      # Health monitoring"
echo ""
echo "🐳 Docker & Deployment:"
echo "  ├── Dockerfile           # Development container"
echo "  ├── Dockerfile.prod      # Production container"
echo "  ├── docker-compose.yml   # Development services"
echo "  ├── docker-compose.prod.yml # Production services"
echo "  ├── init.sql             # Database initialization"
echo "  └── deploy.sh            # Automated deployment script"
echo ""
echo "⚙️  Configuration:"
echo "  ├── .env                 # Development environment (your settings)"
echo "  ├── .env.example         # Environment template for repo"
echo "  ├── .env.prod            # Production environment (not committed)"
echo "  ├── .gitignore           # Git ignore rules"
echo "  └── requirements.txt     # Python dependencies"
echo ""
echo "📚 Documentation:"
echo "  ├── README.md            # Main project documentation"
echo "  ├── DATABASE_SCHEMA.md   # Database structure guide"
echo "  ├── VM_DEPLOYMENT_GUIDE.md # Complete deployment guide"
echo "  ├── KEYCLOAK_SETUP.md    # Keycloak configuration"
echo "  └── QUICKSTART.md        # Quick development setup"
echo ""

# Count files
TOTAL_FILES=$(find . -maxdepth 1 -type f | grep -v "^\./\." | wc -l)
echo "📊 Total files in project root: $TOTAL_FILES"

# Show backup info
echo ""
print_warning "Backup created in: $BACKUP_DIR"
echo "   This contains all removed files in case you need them later"

echo ""
echo "================================================================"
print_success "🎉 PROJECT CLEANUP COMPLETE!"
echo "================================================================"
echo ""
echo "✅ Your project is now clean and ready for repository!"
echo ""
echo "🚀 Next steps:"
echo "1. Review the cleaned project structure above"
echo "2. Test that everything still works: python main.py"
echo "3. Initialize git repository: git init"
echo "4. Add files: git add ."
echo "5. Commit: git commit -m 'Initial commit: Clean auth BFF template'"
echo "6. Push to your repository"
echo ""
echo "📁 Safe to commit: All development files and documentation"
echo "🔒 Protected: .env.prod and backup files are in .gitignore"
echo ""
