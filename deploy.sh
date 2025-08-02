#!/bin/bash
# 🚀 One-Click VM Deployment Script for Auth BFF Template
set -e

echo "🚀 Auth BFF Template - VM Deployment Script"
echo "============================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="auth-bff"
POSTGRES_DB="auth_prod"
POSTGRES_USER="auth_user"
API_PORT="8001"
KEYCLOAK_PORT="8080"

# Functions
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if script is run as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please do not run this script as root"
    exit 1
fi

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    OS_VERSION=$VERSION_ID
else
    print_error "Cannot detect OS. This script supports Ubuntu/Debian."
    exit 1
fi

print_status "Detected OS: $OS $OS_VERSION"

# Installation method selection
echo ""
echo "Choose deployment method:"
echo "1. 🐳 Docker Deployment (Recommended - Everything in containers)"
echo "2. 🔧 Manual Deployment (Direct system installation)"
echo ""
read -p "Enter your choice (1 or 2): " DEPLOYMENT_METHOD

case $DEPLOYMENT_METHOD in
    1)
        echo ""
        print_status "Starting Docker deployment..."
        
        # Install Docker
        print_status "Installing Docker..."
        if ! command -v docker &> /dev/null; then
            curl -fsSL https://get.docker.com -o get-docker.sh
            sudo sh get-docker.sh
            sudo usermod -aG docker $USER
            rm get-docker.sh
            print_success "Docker installed successfully"
        else
            print_success "Docker already installed"
        fi
        
        # Install Docker Compose
        if ! command -v docker-compose &> /dev/null; then
            sudo apt update
            sudo apt install -y docker-compose
            print_success "Docker Compose installed"
        else
            print_success "Docker Compose already installed"
        fi
        
        # Generate secure passwords
        POSTGRES_PASSWORD=$(openssl rand -base64 32)
        JWT_SECRET_KEY=$(openssl rand -base64 48)
        CLIENT_SECRET=$(openssl rand -base64 32)
        
        # Create environment file
        print_status "Creating production environment configuration..."
        
        # Backup existing .env.prod if it exists
        if [ -f .env.prod ]; then
            cp .env.prod .env.prod.backup.$(date +%Y%m%d_%H%M%S)
            print_warning "Existing .env.prod backed up"
        fi
        
        cat > .env.prod << EOF
# Generated automatically by deployment script
# Database Configuration
POSTGRES_DB=${POSTGRES_DB}
POSTGRES_USER=${POSTGRES_USER}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

# Keycloak Configuration (external - configure separately)
KEYCLOAK_BASE_URL=http://localhost:8080
KEYCLOAK_REALM=production
KEYCLOAK_CLIENT_ID=auth-client
KEYCLOAK_CLIENT_SECRET=${CLIENT_SECRET}
KEYCLOAK_ADMIN_USER=admin
KEYCLOAK_ADMIN_PASSWORD=change-this-password

# JWT Configuration
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
API_HOST=0.0.0.0
API_PORT=${API_PORT}
EOF
        
        # Deploy with Docker Compose
        print_status "Deploying services with Docker Compose..."
        docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
        
        # Wait for services to start
        print_status "Waiting for services to start..."
        sleep 30
        
        # Verify deployment
        print_status "Verifying deployment..."
        if curl -f http://localhost:${API_PORT}/health &> /dev/null; then
            print_success "API is running successfully!"
        else
            print_error "API health check failed"
            docker-compose -f docker-compose.prod.yml logs auth_api
            exit 1
        fi
        
        # Save credentials
        cat > deployment_info.txt << EOF
🎉 Auth BFF Template Deployment Complete!
========================================

📊 Service URLs:
- API: http://$(hostname -I | cut -d' ' -f1):${API_PORT}
- API Health: http://$(hostname -I | cut -d' ' -f1):${API_PORT}/health
- API Docs: http://$(hostname -I | cut -d' ' -f1):${API_PORT}/docs

🔐 Credentials (SAVE THESE SECURELY):
- Database User: ${POSTGRES_USER}
- Database Password: ${POSTGRES_PASSWORD}

⚠️  KEYCLOAK SETUP REQUIRED:
- Install Keycloak separately
- Configure realm: production
- Create client: auth-client
- Update KEYCLOAK_BASE_URL in .env.prod

🐳 Docker Management:
- View logs: docker-compose -f docker-compose.prod.yml logs -f
- Stop services: docker-compose -f docker-compose.prod.yml down
- Restart services: docker-compose -f docker-compose.prod.yml restart
- View status: docker-compose -f docker-compose.prod.yml ps

📁 Files Created:
- .env.prod (environment configuration)
- deployment_info.txt (this file)

⚠️  IMPORTANT: Keep your credentials safe and configure Keycloak separately!
EOF
        
        print_success "Docker deployment completed!"
        ;;
        
    2)
        echo ""
        print_status "Starting manual deployment..."
        
        # Update system
        print_status "Updating system packages..."
        sudo apt update
        
        # Install required packages
        print_status "Installing required packages..."
        sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib git curl nginx openssl
        
        # Setup PostgreSQL
        print_status "Setting up PostgreSQL..."
        POSTGRES_PASSWORD=$(openssl rand -base64 32)
        
        sudo -u postgres psql << EOF
CREATE DATABASE ${POSTGRES_DB};
CREATE USER ${POSTGRES_USER} WITH PASSWORD '${POSTGRES_PASSWORD}';
GRANT ALL PRIVILEGES ON DATABASE ${POSTGRES_DB} TO ${POSTGRES_USER};
\q
EOF
        
        # Setup Python environment
        print_status "Setting up Python environment..."
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        
        # Generate configuration
        JWT_SECRET_KEY=$(openssl rand -base64 48)
        
        # Backup existing .env if it exists
        if [ -f .env ]; then
            cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
            print_warning "Existing .env backed up"
        fi
        
        cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/${POSTGRES_DB}
DATABASE_ECHO=false

# Keycloak Configuration (requires separate setup)
KEYCLOAK_BASE_URL=http://localhost:8080
KEYCLOAK_REALM=production
KEYCLOAK_CLIENT_ID=auth-client
KEYCLOAK_CLIENT_SECRET=change-this-in-keycloak

# JWT Configuration
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
API_HOST=0.0.0.0
API_PORT=${API_PORT}
EOF
        
        # Initialize database
        print_status "Initializing database..."
        python setup_clean_database.py
        
        # Create systemd service
        print_status "Creating systemd service..."
        sudo tee /etc/systemd/system/auth-bff.service > /dev/null << EOF
[Unit]
Description=Auth BFF API
After=network.target postgresql.service

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
        
        # Enable and start service
        sudo systemctl daemon-reload
        sudo systemctl enable auth-bff
        sudo systemctl start auth-bff
        
        # Wait for service to start
        sleep 10
        
        # Verify deployment
        if curl -f http://localhost:${API_PORT}/health &> /dev/null; then
            print_success "API is running successfully!"
        else
            print_error "API health check failed"
            sudo journalctl -u auth-bff --no-pager -n 20
            exit 1
        fi
        
        # Save deployment info
        cat > deployment_info.txt << EOF
🎉 Auth BFF Template Manual Deployment Complete!
===============================================

📊 Service URLs:
- API: http://$(hostname -I | cut -d' ' -f1):${API_PORT}
- API Health: http://$(hostname -I | cut -d' ' -f1):${API_PORT}/health
- API Docs: http://$(hostname -I | cut -d' ' -f1):${API_PORT}/docs

🔐 Database Credentials (SAVE SECURELY):
- Database: ${POSTGRES_DB}
- User: ${POSTGRES_USER}
- Password: ${POSTGRES_PASSWORD}

⚠️  KEYCLOAK SETUP REQUIRED:
- Install Keycloak separately
- Configure realm and client settings
- Update .env with Keycloak details

⚙️  System Management:
- Start service: sudo systemctl start auth-bff
- Stop service: sudo systemctl stop auth-bff
- Restart service: sudo systemctl restart auth-bff
- View logs: sudo journalctl -u auth-bff -f
- Service status: sudo systemctl status auth-bff

📁 Files Created:
- .env (environment configuration)
- /etc/systemd/system/auth-bff.service (systemd service)
- deployment_info.txt (this file)

⚠️  TODO: Setup Keycloak separately
EOF
        
        print_success "Manual deployment completed!"
        ;;
        
    *)
        print_error "Invalid choice. Please run the script again."
        exit 1
        ;;
esac

# Final status
echo ""
echo "================================================================"
print_success "🎉 AUTH BFF TEMPLATE DEPLOYMENT COMPLETE!"
echo "================================================================"
echo ""
echo "📊 Your authentication API is now running at:"
echo "   http://$(hostname -I | cut -d' ' -f1):${API_PORT}"
echo ""
echo "📚 API Documentation available at:"
echo "   http://$(hostname -I | cut -d' ' -f1):${API_PORT}/docs"
echo ""
echo "🔍 Test the deployment:"
echo "   curl http://localhost:${API_PORT}/health"
echo ""
echo "📄 Deployment details saved to: deployment_info.txt"
echo ""
print_warning "IMPORTANT: Save your credentials securely!"
echo "================================================================"
