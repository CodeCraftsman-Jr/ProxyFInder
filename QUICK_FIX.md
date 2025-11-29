# Quick Fix for Cleanup Function

## ⚠️ Current Issue
The function is deployed but missing the API key environment variable.

## ✅ Quick Solution

### Option 1: Automated Setup Script (Recommended)
```powershell
.\setup-cleanup-function.ps1
```

### Option 2: Manual Setup

**Step 1: Create API Key**
```bash
appwrite projects create-key \
  --project-id 68a227de003201ae2463 \
  --name "Cleanup Function Key" \
  --scopes databases.read databases.write
```

**Step 2: Copy the API key from the output**

**Step 3: Set Environment Variable**
```bash
appwrite functions update-variables \
  --function-id cleanup-old-proxies \
  --variables "APPWRITE_API_KEY=YOUR_API_KEY_HERE"
```

### Option 3: Using Appwrite Console

1. Go to: https://fra.cloud.appwrite.io/console/project-68a227de003201ae2463
2. **Overview** → **API Keys** → **Create API Key**
3. Name: "Cleanup Function Key"
4. Scopes: Select `databases.read` and `databases.write`
5. Copy the generated key
6. Go to **Functions** → **cleanup-old-proxies** → **Settings**
7. Under **Variables**, add:
   - Key: `APPWRITE_API_KEY`
   - Value: [paste your API key]
8. Save

## 🧪 Test After Setup

```bash
# Execute the function
appwrite functions create-execution --function-id cleanup-old-proxies --async

# Check executions
appwrite functions list-executions --function-id cleanup-old-proxies

# View specific execution (replace EXECUTION_ID)
appwrite functions get-execution --function-id cleanup-old-proxies --execution-id EXECUTION_ID
```

## 📋 What the Function Does

- Runs automatically every 2 days at midnight (UTC)
- Deletes proxy records older than 2 days
- Keeps database clean and performant
- Logs detailed execution results

## 🔧 Function Details

- **Function ID**: `cleanup-old-proxies`
- **Schedule**: `0 0 */2 * *` (every 2 days)
- **Timeout**: 300 seconds
- **Runtime**: Python 3.12
- **Database**: ProxyDatabase (68a227fb00180c4a541a)
- **Collection**: WorkingProxies (68a2280e0039af9b6a24)

---

**After setting up the API key, the function will work automatically!** 🚀
