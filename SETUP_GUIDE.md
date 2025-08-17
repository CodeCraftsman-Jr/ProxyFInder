# 🚀 Complete Setup Guide - Proxy Finder with Appwrite

## Overview
This guide will help you set up an automated proxy checker that:
- ✅ Runs daily on GitHub Actions (FREE)
- ✅ Tests proxies from TheSpeedX/PROXY-List repo
- ✅ Stores only working proxies in Appwrite
- ✅ Provides easy API access to working proxies

---

## 📋 Prerequisites
- GitHub account
- Appwrite account (free at cloud.appwrite.io)

---

## 🏗️ Step 1: Set up Appwrite Database

### 1.1 Create Appwrite Account
1. Go to [cloud.appwrite.io](https://cloud.appwrite.io)
2. Sign up for a free account
3. Verify your email

### 1.2 Create Project
1. Click "Create Project"
2. Name: `ProxyFinder`
3. Click "Create"
4. **Copy the Project ID** (you'll need this later)

### 1.3 Create Database
1. Go to "Databases" in the left sidebar
2. Click "Create Database"
3. Name: `ProxyDatabase`
4. Click "Create"
5. **Copy the Database ID** (you'll need this later)

### 1.4 Create Collection
1. Inside your database, click "Create Collection"
2. Name: `WorkingProxies`
3. Click "Create"
4. **Copy the Collection ID** (you'll need this later)

### 1.5 Add Attributes to Collection
Click "Add Attribute" for each:

| Attribute | Type | Size | Required |
|-----------|------|------|----------|
| `proxy` | String | 50 | Yes |
| `type` | String | 20 | Yes |
| `response_time` | Float | - | Yes |
| `tested_at` | String | 50 | Yes |
| `status` | String | 20 | Yes |

### 1.6 Create API Key
1. Go to "Settings" → "API Keys"
2. Click "Create API Key"
3. Name: `ProxyChecker`
4. Select these scopes:
   - `databases.read`
   - `databases.write`
   - `documents.read` 
   - `documents.write`
5. Click "Create"
6. **Copy the API Key** (you'll need this later)

---

## 🔐 Step 2: Configure GitHub Secrets

### 2.1 Go to Repository Settings
1. In your GitHub repository, click "Settings"
2. Go to "Secrets and variables" → "Actions"

### 2.2 Add Required Secrets
Click "New repository secret" for each:

| Secret Name | Value | Example |
|-------------|-------|---------|
| `APPWRITE_ENDPOINT` | `https://cloud.appwrite.io/v1` | (exactly as shown) |
| `APPWRITE_PROJECT_ID` | Your Project ID from Step 1.2 | `64f1a2b3c4d5e6f7` |
| `APPWRITE_API_KEY` | Your API Key from Step 1.6 | `st-64f1a2b3c4d5...` |
| `APPWRITE_DATABASE_ID` | Your Database ID from Step 1.3 | `64f1a2b3c4d5e6f8` |
| `APPWRITE_COLLECTION_ID` | Your Collection ID from Step 1.4 | `64f1a2b3c4d5e6f9` |

---

## 🚀 Step 3: Test the Setup

### 3.1 Manual Test Run
1. Go to your GitHub repository
2. Click "Actions" tab
3. Click "Daily Proxy Checker" workflow
4. Click "Run workflow" → "Run workflow"
5. Wait for it to complete (5-15 minutes)

### 3.2 Check Results
**In GitHub:**
- Go to the completed workflow run
- Check the logs for statistics
- Download artifacts (working proxy files)

**In Appwrite:**
- Go to your Appwrite console
- Navigate to Databases → ProxyDatabase → WorkingProxies
- You should see working proxies with details

---

## 🔄 Step 4: Automatic Daily Runs

The workflow is already configured to run daily at 2:00 AM UTC. No additional setup needed!

---

## 📊 Step 5: Access Your Working Proxies

### 5.1 Via Appwrite Console
1. Login to Appwrite console
2. Go to Databases → ProxyDatabase → WorkingProxies
3. View all working proxies with response times

### 5.2 Via API (Python Example)
```python
from appwrite.client import Client
from appwrite.services.databases import Databases

# Initialize client
client = Client()
client.set_endpoint('https://cloud.appwrite.io/v1')
client.set_project('YOUR_PROJECT_ID')
client.set_key('YOUR_API_KEY')

# Get working proxies
databases = Databases(client)
result = databases.list_documents('YOUR_DB_ID', 'YOUR_COLLECTION_ID')

# Use the proxies
for doc in result['documents']:
    proxy = doc['proxy']
    proxy_type = doc['type']
    response_time = doc['response_time']
    print(f"{proxy_type.upper()}: {proxy} ({response_time}s)")
```

### 5.3 Via REST API
```bash
curl -X GET \
  'https://cloud.appwrite.io/v1/databases/YOUR_DB_ID/collections/YOUR_COLLECTION_ID/documents' \
  -H 'X-Appwrite-Project: YOUR_PROJECT_ID' \
  -H 'X-Appwrite-Key: YOUR_API_KEY'
```

---

## 🛠️ Step 6: Local Testing (Optional)

### 6.1 Install Dependencies
```bash
pip install -r requirements.txt
```

### 6.2 Set Environment Variables
Create `.env` file:
```env
APPWRITE_ENDPOINT=https://cloud.appwrite.io/v1
APPWRITE_PROJECT_ID=your_project_id
APPWRITE_API_KEY=your_api_key
APPWRITE_DATABASE_ID=your_database_id
APPWRITE_COLLECTION_ID=your_collection_id
```

### 6.3 Run Local Test
```bash
python github_actions_proxy_checker.py
```

---

## 🔧 Troubleshooting

### Common Issues:

**1. GitHub Actions fails with "401 Unauthorized"**
- Check if all GitHub secrets are set correctly
- Verify Appwrite API key has correct permissions

**2. No proxies found**
- Check if the PROXY-List repo is accessible
- Verify internet connection in GitHub Actions

**3. Appwrite connection fails**
- Verify Project ID and endpoint are correct
- Check API key permissions

**4. Local testing fails**
- Install required packages: `pip install appwrite requests python-socks`
- Check environment variables

---

## 📈 Expected Results

After setup, you should see:
- **Daily workflow runs** in GitHub Actions
- **Working proxies** stored in Appwrite (typically 10-50 per day)
- **Performance data** (response times)
- **Multiple proxy types** (HTTP, SOCKS4, SOCKS5)

---

## 🎯 Next Steps

1. **Monitor daily runs** in GitHub Actions
2. **Build applications** using the working proxy API
3. **Set up alerts** for workflow failures (optional)
4. **Scale up** testing frequency if needed

---

## 💡 Pro Tips

- **Free Usage**: GitHub Actions gives 2000 minutes/month free
- **Storage**: Appwrite free tier includes generous database storage
- **API Access**: Use Appwrite SDKs for easy integration
- **Backup**: Workflow artifacts provide local file backups

---

## 🆘 Need Help?

If you encounter issues:
1. Check GitHub Actions logs for detailed error messages
2. Verify all secrets are set correctly in GitHub
3. Test Appwrite connection manually
4. Check the troubleshooting section above

Happy proxy hunting! 🎯
