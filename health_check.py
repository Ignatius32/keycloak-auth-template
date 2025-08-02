#!/usr/bin/env python3
"""
Health check script for the User Authentication API
Tests basic functionality to ensure everything is working correctly
"""
import asyncio
import httpx
import sys
import os
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = "http://localhost:8001"

async def test_health_endpoints():
    """Test basic health endpoints"""
    print("🏥 Testing health endpoints...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Test root endpoint
            response = await client.get(f"{API_BASE_URL}/")
            if response.status_code == 200:
                print("✅ Root endpoint: OK")
            else:
                print(f"❌ Root endpoint failed: {response.status_code}")
                return False
            
            # Test health endpoint
            response = await client.get(f"{API_BASE_URL}/health")
            if response.status_code == 200:
                print("✅ Health endpoint: OK")
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                return False
                
            return True
        except Exception as e:
            print(f"❌ Connection error: {e}")
            print("Make sure the API server is running: python main.py")
            return False

async def test_auth_endpoints():
    """Test authentication endpoints structure"""
    print("\n🔐 Testing authentication endpoints...")
    
    async with httpx.AsyncClient() as client:
        try:
            # Test login endpoint structure (should return 422 for missing data)
            response = await client.post(f"{API_BASE_URL}/auth/login", json={})
            if response.status_code == 422:
                print("✅ Login endpoint: Structure OK")
            else:
                print(f"⚠️ Login endpoint returned: {response.status_code}")
            
            # Test register endpoint structure
            response = await client.post(f"{API_BASE_URL}/auth/register", json={})
            if response.status_code == 422:
                print("✅ Register endpoint: Structure OK")
            else:
                print(f"⚠️ Register endpoint returned: {response.status_code}")
            
            # Test password reset endpoint structure
            response = await client.post(f"{API_BASE_URL}/auth/password-reset", json={})
            if response.status_code == 422:
                print("✅ Password reset endpoint: Structure OK")
            else:
                print(f"⚠️ Password reset endpoint returned: {response.status_code}")
                
            return True
        except Exception as e:
            print(f"❌ Auth endpoints error: {e}")
            return False

def check_configuration():
    """Check basic configuration"""
    print("⚙️ Checking configuration...")
    
    required_env_vars = [
        "KEYCLOAK_BASE_URL",
        "KEYCLOAK_REALM", 
        "KEYCLOAK_CLIENT_ID",
        "JWT_SECRET_KEY"
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file configuration")
        return False
    else:
        print("✅ Environment variables: OK")
        return True

async def main():
    """Main health check function"""
    print("🚀 User Authentication API Health Check")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Check configuration
    if not check_configuration():
        all_tests_passed = False
    
    # Test endpoints
    if not await test_health_endpoints():
        all_tests_passed = False
    
    if not await test_auth_endpoints():
        all_tests_passed = False
    
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("✅ All health checks passed!")
        print("\n📋 Available endpoints:")
        print("  • API Documentation: http://localhost:8001/docs")
        print("  • Health Check: http://localhost:8001/health")
        print("  • User Status: http://localhost:8001/auth/status")
    else:
        print("❌ Some health checks failed!")
        print("\n🔧 Troubleshooting:")
        print("  1. Make sure the API server is running: python main.py")
        print("  2. Check your .env file configuration")
        print("  3. Verify Keycloak is running and accessible")
        print("  4. Check database connection")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
