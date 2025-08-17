#!/usr/bin/env python3
"""
Quick Setup Verification Script
Tests your Appwrite connection and GitHub setup
"""

import os
import sys
import requests
from datetime import datetime

def check_github_setup():
    """Check if we're in a GitHub repository"""
    print("🔍 Checking GitHub setup...")
    
    if os.path.exists('.git'):
        print("✅ Git repository detected")
    else:
        print("❌ Not a Git repository")
        return False
    
    if os.path.exists('.github/workflows/proxy_checker.yml'):
        print("✅ GitHub Actions workflow file exists")
    else:
        print("❌ GitHub Actions workflow file missing")
        return False
    
    return True

def check_appwrite_config():
    """Check if Appwrite environment variables are set"""
    print("\n🔍 Checking Appwrite configuration...")
    
    required_vars = [
        'APPWRITE_ENDPOINT',
        'APPWRITE_PROJECT_ID', 
        'APPWRITE_API_KEY',
        'APPWRITE_DATABASE_ID',
        'APPWRITE_COLLECTION_ID'
    ]
    
    missing_vars = []
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var} is set")
        else:
            print(f"❌ {var} is missing")
            missing_vars.append(var)
    
    return len(missing_vars) == 0, missing_vars

def test_appwrite_connection():
    """Test connection to Appwrite"""
    print("\n🔍 Testing Appwrite connection...")
    
    try:
        # Import Appwrite SDK
        from appwrite.client import Client
        from appwrite.services.databases import Databases
        
        # Initialize client
        client = Client()
        client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
        client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
        client.set_key(os.getenv('APPWRITE_API_KEY'))
        
        # Test connection
        databases = Databases(client)
        result = databases.list_documents(
            os.getenv('APPWRITE_DATABASE_ID'),
            os.getenv('APPWRITE_COLLECTION_ID'),
            []
        )
        
        print("✅ Appwrite connection successful")
        print(f"✅ Found {result['total']} existing documents")
        return True
        
    except ImportError:
        print("❌ Appwrite SDK not installed")
        print("💡 Run: pip install appwrite")
        return False
    except Exception as e:
        print(f"❌ Appwrite connection failed: {str(e)}")
        return False

def test_proxy_source():
    """Test if we can fetch proxy lists"""
    print("\n🔍 Testing proxy source...")
    
    try:
        url = "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        proxies = [line.strip() for line in response.text.splitlines() if line.strip()]
        print(f"✅ Successfully fetched {len(proxies)} HTTP proxies")
        return True
        
    except Exception as e:
        print(f"❌ Failed to fetch proxies: {str(e)}")
        return False

def print_github_secrets_guide(missing_vars):
    """Print guide for setting up GitHub secrets"""
    print("\n" + "="*60)
    print("📋 GITHUB SECRETS SETUP GUIDE")
    print("="*60)
    print("1. Go to your GitHub repository")
    print("2. Click Settings > Secrets and variables > Actions")
    print("3. Click 'New repository secret' for each:")
    print()
    
    examples = {
        'APPWRITE_ENDPOINT': 'https://cloud.appwrite.io/v1',
        'APPWRITE_PROJECT_ID': '64f1a2b3c4d5e6f7',
        'APPWRITE_API_KEY': 'st-64f1a2b3c4d5...',
        'APPWRITE_DATABASE_ID': '64f1a2b3c4d5e6f8',
        'APPWRITE_COLLECTION_ID': '64f1a2b3c4d5e6f9'
    }
    
    for var in missing_vars:
        print(f"   {var} = {examples.get(var, 'your_value_here')}")
    print()

def main():
    """Main setup verification function"""
    print("🚀 ProxyFinder Setup Verification")
    print("=" * 50)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    all_good = True
    
    # Check GitHub setup
    if not check_github_setup():
        all_good = False
    
    # Check environment variables
    config_ok, missing_vars = check_appwrite_config()
    if not config_ok:
        all_good = False
        print_github_secrets_guide(missing_vars)
    
    # Test Appwrite connection (only if config is OK)
    if config_ok:
        if not test_appwrite_connection():
            all_good = False
    
    # Test proxy source
    if not test_proxy_source():
        all_good = False
    
    print("\n" + "="*50)
    if all_good:
        print("🎉 ALL CHECKS PASSED!")
        print("✅ Your setup is ready to go!")
        print("🚀 You can now run the GitHub Actions workflow")
        print()
        print("Next steps:")
        print("1. Go to GitHub Actions tab")
        print("2. Click 'Daily Proxy Checker'")
        print("3. Click 'Run workflow'")
    else:
        print("❌ SETUP INCOMPLETE")
        print("🔧 Please fix the issues above and run this script again")
        print("📖 See SETUP_GUIDE.md for detailed instructions")
    
    print("="*50)

if __name__ == "__main__":
    main()
