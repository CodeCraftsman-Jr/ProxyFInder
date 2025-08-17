# GitHub Actions + Appwrite Setup Guide

## Overview
This setup uses **GitHub Actions** to run the heavy proxy testing work (for free!) and stores only the working proxies in **Appwrite** for easy access.

## Why GitHub Actions?
- ✅ **Free**: 2000 minutes/month on public repos
- ✅ **Powerful**: Can handle thousands of proxy tests
- ✅ **Scheduled**: Runs automatically daily
- ✅ **Reliable**: GitHub's infrastructure
- ✅ **No server needed**: Completely serverless

## Setup Instructions

### 1. Set up Appwrite

1. **Create Appwrite Account**: Go to [cloud.appwrite.io](https://cloud.appwrite.io)
2. **Create Project**: Name it "ProxyFinder"
3. **Create Database**: 
   - Name: "ProxyDatabase"
   - Copy the Database ID
4. **Create Collection**: 
   - Name: "WorkingProxies"
   - Copy the Collection ID
   - Add these attributes:
     - `proxy` (String, 50 chars)
     - `type` (String, 10 chars) 
     - `response_time` (Float)
     - `tested_at` (String, 50 chars)
     - `status` (String, 20 chars)
5. **Create API Key**:
   - Go to Settings > API Keys
   - Create new key with Database permissions
   - Copy the API Key

### 2. Configure GitHub Secrets

In your GitHub repository, go to **Settings > Secrets and variables > Actions** and add:

```
APPWRITE_ENDPOINT = https://cloud.appwrite.io/v1
APPWRITE_PROJECT_ID = [Your Project ID]
APPWRITE_API_KEY = [Your API Key]
APPWRITE_DATABASE_ID = [Your Database ID]
APPWRITE_COLLECTION_ID = [Your Collection ID]
```

### 3. Test the Workflow

1. **Manual Test**: Go to Actions tab > "Daily Proxy Checker" > "Run workflow"
2. **Check Results**: 
   - Working proxies will be saved to Appwrite
   - Artifacts with proxy files will be available for download
   - Check the logs for statistics

### 4. Access Working Proxies

**From Appwrite Console:**
- Go to your database > WorkingProxies collection
- View all working proxies with details

**Programmatically:**
```python
from appwrite.client import Client
from appwrite.services.databases import Databases

client = Client()
client.set_endpoint('https://cloud.appwrite.io/v1')
client.set_project('your-project-id')
client.set_key('your-api-key')

databases = Databases(client)
result = databases.list_documents('your-db-id', 'your-collection-id')
working_proxies = result['documents']
```

## Alternative Platforms

### 1. **Railway** (Recommended for Python)
```bash
# Deploy to Railway
railway login
railway new
railway add
railway up
```

### 2. **Render** (Easy deployment)
- Connect GitHub repo
- Add cron job service
- Set environment variables

### 3. **Google Cloud Functions + Scheduler**
```bash
gcloud functions deploy proxy-checker --runtime python310 --trigger-http
gcloud scheduler jobs create http daily-proxy-check --schedule="0 2 * * *" --uri=[function-url]
```

### 4. **Vercel Functions** (For lighter workloads)
```javascript
// api/check-proxies.js
export default async function handler(req, res) {
  // Your proxy checking logic
}
```

## Cost Comparison

| Platform | Free Tier | Best For |
|----------|-----------|----------|
| GitHub Actions | 2000 min/month | Heavy testing |
| Railway | $5/month | Full Python apps |
| Render | 750 hours/month | Simple deployments |
| Google Cloud | 2M invocations | Enterprise |
| Vercel | 100GB-hours | Light workloads |

## Recommendation

**Use GitHub Actions** - it's the best choice because:
- Completely free for public repos
- Can handle thousands of proxy tests
- Built-in scheduling
- No server management needed
- Just push code and it works!
