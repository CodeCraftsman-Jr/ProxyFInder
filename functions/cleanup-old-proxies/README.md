# Cleanup Old Proxies Function

This Appwrite function automatically deletes proxy records older than 2 days from your ProxyDatabase.

## Features

- 🗑️ Automatically deletes records older than 2 days
- ⏰ Runs on a schedule (every 2 days)
- 📊 Provides detailed cleanup reports
- 🔄 Handles pagination for large datasets
- 🛡️ Error handling and logging

## How It Works

1. Calculates the cutoff date (2 days ago from current time)
2. Fetches all documents from the WorkingProxies collection
3. Checks each document's `tested_at` timestamp
4. Deletes documents older than the cutoff date
5. Returns a summary report

## Setup & Deployment

### 1. Deploy the Function

```bash
# From the project root directory
appwrite deploy function
```

When prompted:
- Select "Create a new function"
- Name: `cleanup-old-proxies`
- Runtime: `python-3.12` (or latest available Python runtime)
- Execute access: Select your preference
- Events: Leave empty (we'll use schedule)

### 2. Configure the Schedule

After deployment, set up the schedule to run every 2 days:

```bash
# Set the function to run every 2 days (172800 seconds = 2 days)
appwrite functions updateSchedule \
  --functionId [YOUR_FUNCTION_ID] \
  --schedule "0 0 */2 * *"
```

Or use the Appwrite Console:
1. Go to Functions → cleanup-old-proxies
2. Click on "Settings"
3. Set "Schedule" to: `0 0 */2 * *` (runs at midnight every 2 days)
4. Save changes

### 3. Set Required Environment Variables

The function needs an API key with database permissions:

```bash
appwrite functions updateVariables \
  --functionId [YOUR_FUNCTION_ID] \
  --variables '{"APPWRITE_API_KEY":"[YOUR_API_KEY]"}'
```

Or in the Console:
1. Go to Functions → cleanup-old-proxies → Settings
2. Add environment variable:
   - Key: `APPWRITE_API_KEY`
   - Value: Your API key with `databases.read` and `databases.write` permissions

### 4. Test the Function

Test manually before the scheduled run:

```bash
appwrite functions createExecution \
  --functionId [YOUR_FUNCTION_ID]
```

Or use the Console:
1. Go to Functions → cleanup-old-proxies
2. Click "Execute now"
3. Check the execution logs

## Response Format

Successful execution returns:

```json
{
  "success": true,
  "timestamp": "2025-11-29T10:30:00.000000",
  "cutoff_date": "2025-11-27T10:30:00.000000",
  "total_documents_checked": 1500,
  "documents_deleted": 800,
  "documents_retained": 700,
  "errors_count": 0,
  "errors": []
}
```

## Schedule Format

The cron schedule format: `minute hour day month weekday`

Examples:
- `0 0 */2 * *` - Every 2 days at midnight
- `0 2 */2 * *` - Every 2 days at 2 AM
- `0 0 * * 0,3` - Every Sunday and Wednesday at midnight
- `0 12 */2 * *` - Every 2 days at noon

## Monitoring

Check function executions:
```bash
appwrite functions listExecutions --functionId [YOUR_FUNCTION_ID]
```

Or in the Console:
1. Go to Functions → cleanup-old-proxies
2. View "Executions" tab for history and logs

## Troubleshooting

### No documents deleted
- Check if you have proxy records older than 2 days
- Verify the `tested_at` field format in your documents

### Permission errors
- Ensure the API key has proper database permissions
- Check that the function has the correct environment variables

### Timeout issues
- For very large datasets, consider adjusting the function timeout in settings
- The function uses pagination to handle large collections efficiently

## Cost Considerations

- Function executions: Charged per execution
- Each scheduled run counts as 1 execution
- Running every 2 days = ~15 executions per month
- Check Appwrite pricing for your plan's limits
