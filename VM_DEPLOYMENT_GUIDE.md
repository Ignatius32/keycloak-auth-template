# 🚀 VM Deployment Guide for Auth BFF Template

This guide shows you exactly how to deploy your cleaned authentication template on a fresh VM.

## 📋 **Deployment Options**

### **Option 1: Docker Deployment (Recommended)**
- ✅ **Easiest setup** - Everything in containers
- ✅ **Automatic PostgreSQL** - Database created automatically  
- ✅ **No manual configuration** - Just run and go
- ✅ **Production ready** - Includes monitoring and backups

### **Option 2: Manual Deployment**
- ✅ **More control** - Direct system installation
- ✅ **Better performance** - No container overhead
- ✅ **Custom configuration** - Full system customization

---

## 🐳 **Option 1: Docker Deployment (Recommended)**

### **Prerequisites**
```bash
# On your VM (Ubuntu/Debian)
sudo apt update
sudo apt install -y docker.io docker-compose git curl

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group (logout/login required)
sudo usermod -aG docker $USER
```

### **1. Clone and Setup**
```bash
# Clone your project
git clone https://github.com/yourusername/auth-bff.git
cd auth-bff

# Create production environment file
cp .env.template .env.prod
```

### **2. Configure Environment**
```bash
# Edit production settings
nano .env.prod
```

**Example `.env.prod`:**
```env
# Database Configuration (Docker will create this automatically)
POSTGRES_DB=auth_prod
POSTGRES_USER=auth_user
POSTGRES_PASSWORD=your_secure_production_password

# Keycloak Configuration
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=your_secure_admin_password
KEYCLOAK_REALM=production
KEYCLOAK_CLIENT_ID=auth-client
KEYCLOAK_CLIENT_SECRET=your-secure-client-secret
KEYCLOAK_HOSTNAME=your-domain.com  # Your VM's domain/IP

# JWT Configuration  
JWT_SECRET_KEY=your-super-secure-jwt-key-at-least-32-characters
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Optional: Keycloak Database (separate from main app)
KEYCLOAK_DB=keycloak
```

### **3. Deploy Everything**
```bash
# Deploy full stack (PostgreSQL + Keycloak + API)
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# Check status
docker-compose -f docker-compose.prod.yml ps
```

### **4. Verify Deployment**
```bash
# Check health
curl http://your-vm-ip:8001/health

# Check logs
docker-compose -f docker-compose.prod.yml logs -f auth_api

# Check database
docker exec -it auth_postgres_prod psql -U auth_user -d auth_prod -c "\dt"
```

### **🎉 That's it! Your deployment includes:**
- ✅ **PostgreSQL database** - Automatically created and configured
- ✅ **All requirements** - Installed in Docker containers
- ✅ **Keycloak** - Running and configured  
- ✅ **Your API** - Running on port 8001
- ✅ **Database tables** - Created automatically on first run

---

## 🔧 **Option 2: Manual Deployment**

### **Prerequisites**
```bash
# On your VM (Ubuntu/Debian)
sudo apt update
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx git curl
```

### **1. Setup PostgreSQL**
```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE auth_prod;
CREATE USER auth_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE auth_prod TO auth_user;
\q

# Configure PostgreSQL for remote connections (if needed)
sudo nano /etc/postgresql/15/main/postgresql.conf
# Uncomment: listen_addresses = '*'

sudo nano /etc/postgresql/15/main/pg_hba.conf  
# Add: host all all 0.0.0.0/0 md5

sudo systemctl restart postgresql
```

### **2. Setup Application**
```bash
# Clone and setup
git clone https://github.com/yourusername/auth-bff.git
cd auth-bff

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Configure environment
cp .env.template .env
nano .env
```

**Example `.env`:**
```env
# Database Configuration
DATABASE_URL=postgresql://auth_user:your_secure_password@localhost:5432/auth_prod

# Keycloak Configuration (install separately or use Docker)
KEYCLOAK_BASE_URL=http://localhost:8080
KEYCLOAK_REALM=production
KEYCLOAK_CLIENT_ID=auth-client
KEYCLOAK_CLIENT_SECRET=your-client-secret

# JWT Configuration
JWT_SECRET_KEY=your-super-secure-jwt-key-at-least-32-characters
```

### **3. Initialize Database**
```bash
# Run database setup
source venv/bin/activate
python setup_clean_database.py
```

### **4. Setup Systemd Service**
```bash
# Create service file
sudo nano /etc/systemd/system/auth-bff.service
```

**`auth-bff.service`:**
```ini
[Unit]
Description=Auth BFF API
After=network.target postgresql.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/auth-bff
Environment=PATH=/home/ubuntu/auth-bff/venv/bin
ExecStart=/home/ubuntu/auth-bff/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable auth-bff
sudo systemctl start auth-bff
sudo systemctl status auth-bff
```

### **5. Setup Nginx (Optional)**
```bash
# Create Nginx config
sudo nano /etc/nginx/sites-available/auth-bff
```

**Nginx config:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/auth-bff /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🚀 **Quick Deployment Scripts**

### **Docker One-Line Deployment**
```bash
# Copy this entire block and run on your VM
curl -fsSL https://get.docker.com -o get-docker.sh && \
sudo sh get-docker.sh && \
sudo usermod -aG docker $USER && \
git clone https://github.com/yourusername/auth-bff.git && \
cd auth-bff && \
cp .env.template .env.prod && \
echo "⚠️  Edit .env.prod with your settings, then run:" && \
echo "docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d"
```

### **Manual Deployment Script**
Create `deploy.sh`:
```bash
#!/bin/bash
set -e

echo "🚀 Deploying Auth BFF to VM..."

# Install dependencies
sudo apt update
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib git curl

# Setup PostgreSQL
sudo -u postgres createdb auth_prod
sudo -u postgres createuser auth_user
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE auth_prod TO auth_user;"

# Setup application
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
if [ ! -f .env ]; then
    cp .env.template .env
    echo "⚠️  Please edit .env with your settings"
    exit 1
fi

# Initialize database
python setup_clean_database.py

# Setup systemd service
sudo cp deploy/auth-bff.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable auth-bff
sudo systemctl start auth-bff

echo "✅ Deployment complete!"
echo "API running on http://$(hostname -I | cut -d' ' -f1):8001"
```

---

## ✅ **What Gets Installed Automatically**

### **Docker Deployment:**
1. **PostgreSQL 15** - Database server in container
2. **Python 3.12** - Inside the application container
3. **All Python packages** - From requirements.txt
4. **Database tables** - Created automatically on startup
5. **Keycloak** - Authentication server
6. **Nginx** - Optional load balancer

### **Manual Deployment:**
1. **PostgreSQL** - Installed on system
2. **Python environment** - Virtual environment created
3. **All dependencies** - Installed via pip
4. **Database schema** - Created via setup script
5. **Systemd service** - For auto-start and management

---

## 🔍 **Verification Steps**

### **Check Everything is Working:**
```bash
# 1. Check services are running
docker-compose -f docker-compose.prod.yml ps
# or for manual: sudo systemctl status auth-bff

# 2. Test database connection
curl http://your-vm-ip:8001/health

# 3. Check database tables exist
docker exec -it auth_postgres_prod psql -U auth_user -d auth_prod -c "\dt"

# 4. Test authentication endpoint
curl -X POST http://your-vm-ip:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass","email":"test@example.com"}'

# 5. Check logs
docker-compose -f docker-compose.prod.yml logs auth_api
# or: sudo journalctl -u auth-bff -f
```

---

## 🎯 **Summary**

**For Docker Deployment (Recommended):**
1. Install Docker on VM
2. Clone your project  
3. Configure `.env.prod`
4. Run `docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d`
5. Everything is automatically created and configured!

**For Manual Deployment:**
1. Install PostgreSQL and Python
2. Clone project and setup venv
3. Run database setup script
4. Configure systemd service
5. Start and monitor

Both methods will give you:
- ✅ **PostgreSQL database** - Created and configured
- ✅ **All Python dependencies** - Installed automatically
- ✅ **Database tables** - Created automatically
- ✅ **Running API** - Available on port 8001
- ✅ **Production ready** - With proper monitoring and restart policies

The Docker approach is recommended because it's more reliable and easier to manage!
