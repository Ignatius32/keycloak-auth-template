# 🔑 # 🔐 Keycloak Setup Guide (External Installation)

Since Keycloak is now separate from your BFF deployment, you need to install and configure it separately. Here are your options:

## 🐳 **Option 1: Keycloak with Docker (Recommended)**

### **Simple Standalone Keycloak**
```bash
# Run Keycloak in a separate container
docker run -d \
  --name keycloak \
  -p 8080:8080 \
  -e KEYCLOAK_ADMIN=admin \
  -e KEYCLOAK_ADMIN_PASSWORD=admin \
  quay.io/keycloak/keycloak:latest start-dev

# Wait for Keycloak to start (about 30 seconds)
# Access admin console: http://localhost:8080
``` for User Authentication BFF

This guide explains how to configure Keycloak to work with the User Authentication BFF template.

## 🚀 Quick Setup

### 1. Start Keycloak

#### Option A: Docker (Recommended for Development)
```bash
# Start Keycloak with Docker
docker run -p 8080:8080 \
  -e KEYCLOAK_ADMIN=admin \
  -e KEYCLOAK_ADMIN_PASSWORD=admin \
  quay.io/keycloak/keycloak:latest \
  start-dev
```

#### Option B: Local Installation
1. Download Keycloak from https://www.keycloak.org/downloads
2. Extract and run: `bin/kc.sh start-dev`

### 2. Access Keycloak Admin Console
- URL: http://localhost:8080/admin
- Username: `admin` 
- Password: `admin`

## 🏗️ Configuration Steps

### Step 1: Create Realm

1. **Login** to Keycloak admin console
2. **Hover over** "master" realm in top-left
3. **Click** "Create Realm"
4. **Enter realm name**: `YOUR_REALM` (e.g., `astro-app`, `my-app`)
5. **Click** "Create"

### Step 2: Create Client

1. **Go to** "Clients" in left sidebar
2. **Click** "Create client"
3. **Configure**:
   - **Client type**: OpenID Connect
   - **Client ID**: `your-client-id` (e.g., `astro-client`)
   - **Name**: `Your App Client`
   - **Click** "Next"

4. **Capability config**:
   - **Client authentication**: ON ✅
   - **Authorization**: OFF
   - **Standard flow**: ON ✅
   - **Direct access grants**: ON ✅
   - **Click** "Next"

5. **Login settings**:
   - **Root URL**: `http://localhost:3000`
   - **Home URL**: `http://localhost:3000`
   - **Valid redirect URIs**: `http://localhost:3000/*`
   - **Valid post logout redirect URIs**: `http://localhost:3000/*`
   - **Web origins**: `http://localhost:3000`
   - **Click** "Save"

### Step 3: Get Client Secret

1. **Go to** your client → "Credentials" tab
2. **Copy** the "Client secret"
3. **Update** your `.env` file:
   ```env
   KEYCLOAK_CLIENT_SECRET=your-copied-secret-here
   ```

### Step 4: Create Roles

1. **Go to** "Realm roles" in left sidebar
2. **Click** "Create role"
3. **Create these roles**:
   - **Role name**: `user`
   - **Description**: `Standard user role`
   - **Click** "Save"
   
4. **Repeat** for additional roles like `admin`, `moderator`, etc.

### Step 5: Configure Email Settings (Optional but Recommended)

1. **Go to** "Realm settings" → "Email" tab
2. **Configure SMTP**:
   ```
   Host: smtp.gmail.com (or your provider)
   Port: 587
   From: noreply@yourapp.com
   Enable StartTLS: ON
   Username: your-email@gmail.com
   Password: your-app-password
   ```
3. **Test** email configuration

### Step 6: Test User Creation

1. **Go to** "Users" in left sidebar
2. **Click** "Add user"
3. **Configure**:
   - **Username**: `testuser`
   - **Email**: `test@example.com`
   - **First name**: `Test`
   - **Last name**: `User`
   - **Email verified**: ON ✅
   - **Click** "Create"

4. **Set password**:
   - **Go to** "Credentials" tab
   - **Click** "Set password"
   - **Password**: `test123`
   - **Temporary**: OFF
   - **Click** "Save"

5. **Assign role**:
   - **Go to** "Role mappings" tab
   - **Click** "Assign role"
   - **Select** `user` role
   - **Click** "Assign"

## 🔧 Environment Configuration

Update your `.env` file with the Keycloak settings:

```env
# Keycloak Configuration
KEYCLOAK_BASE_URL=http://localhost:8080
KEYCLOAK_REALM=YOUR_REALM
KEYCLOAK_CLIENT_ID=your-client-id  
KEYCLOAK_CLIENT_SECRET=your-copied-secret
KEYCLOAK_ADMIN_USER=admin
KEYCLOAK_ADMIN_PASSWORD=admin
```

## ✅ Test the Setup

### 1. Start Your API
```bash
python main.py
```

### 2. Test Registration
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

### 3. Test Login
```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "test123"
  }'
```

### 4. Run Health Check
```bash
python health_check.py
```

## 🛡️ Security Best Practices

### Development
- ✅ Use `start-dev` mode for development
- ✅ Keep default admin credentials for local development
- ✅ Use HTTP for local development

### Production
- 🔒 **Change admin password**
- 🔒 **Enable HTTPS**
- 🔒 **Use production database**
- 🔒 **Configure proper CORS origins**
- 🔒 **Enable SSL verification**
- 🔒 **Regular security updates**

### Client Security
```bash
# Update these for production:
Valid redirect URIs: https://yourapp.com/*
Web origins: https://yourapp.com
```

## 🔍 Troubleshooting

### "Connection refused" error
- ✅ Check Keycloak is running on port 8080
- ✅ Verify `KEYCLOAK_BASE_URL` in `.env`

### "Client not found" error  
- ✅ Verify `KEYCLOAK_CLIENT_ID` matches exactly
- ✅ Check you're using the correct realm

### "Invalid client credentials"
- ✅ Copy the correct client secret from Keycloak
- ✅ Ensure client authentication is enabled

### "User not found" error
- ✅ Check user exists in correct realm
- ✅ Verify username/email spelling
- ✅ Confirm user is enabled

### Email verification not working
- ✅ Configure SMTP settings in realm
- ✅ Test email configuration in Keycloak
- ✅ Check spam folder

## 📚 Advanced Configuration

### Custom User Attributes
1. **Go to** "User attributes" in realm settings
2. **Add** custom attributes for your app
3. **Update** your API to handle custom fields

### Social Login (Google, GitHub, etc.)
1. **Go to** "Identity providers"
2. **Add** provider (Google, GitHub, etc.)
3. **Configure** OAuth credentials
4. **Map** attributes and roles

### Multi-Factor Authentication
1. **Go to** "Authentication" → "Required actions"
2. **Enable** "Configure OTP"
3. **Configure** OTP policy in "Policies"

### Custom Themes
1. **Create** custom theme in `themes/` directory
2. **Configure** in "Realm settings" → "Themes"

## 🌐 Production Deployment

### Docker Compose Example
```yaml
version: '3.8'
services:
  keycloak:
    image: quay.io/keycloak/keycloak:latest
    environment:
      KEYCLOAK_ADMIN: admin
      KEYCLOAK_ADMIN_PASSWORD: your-secure-password
      KC_DB: postgres
      KC_DB_URL: jdbc:postgresql://db:5432/keycloak
      KC_DB_USERNAME: keycloak
      KC_DB_PASSWORD: password
    ports:
      - "8080:8080"
    command: start-dev
```

### Environment Variables for Production
```env
KEYCLOAK_BASE_URL=https://auth.yourapp.com
KEYCLOAK_REALM=production-realm
# ... other production settings
```

## 🆘 Support Resources

- **Keycloak Documentation**: https://www.keycloak.org/documentation
- **Server Administration Guide**: https://www.keycloak.org/docs/latest/server_admin/
- **REST API Documentation**: https://www.keycloak.org/docs-api/latest/rest-api/

---

✅ **Your Keycloak setup is now complete!** The BFF API should be able to authenticate users through Keycloak.
