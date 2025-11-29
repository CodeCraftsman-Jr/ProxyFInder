"""
Appwrite Function to clean up old proxy records
Keeps only the last 2 days of data and deletes older records
Uses REST API directly to avoid SDK compatibility issues
"""

import os
import json
import requests
from datetime import datetime, timedelta


def main(context):
    """
    Main function to clean up old proxy records
    Runs every 2 days to delete records older than 2 days
    """
    
    context.log("🚀 Starting cleanup process...")
    
    # Get environment variables
    endpoint = os.environ.get('APPWRITE_FUNCTION_API_ENDPOINT', 'https://fra.cloud.appwrite.io/v1')
    project_id = os.environ.get('APPWRITE_FUNCTION_PROJECT_ID')
    api_key = os.environ.get('APPWRITE_API_KEY', '')
    
    if not api_key:
        context.error("APPWRITE_API_KEY environment variable is not set")
        return context.res.json({
            "success": False,
            "error": "API key not configured"
        }, 500)
    
    context.log(f"Endpoint: {endpoint}")
    context.log(f"Project ID: {project_id}")
    
    # Database and collection IDs
    database_id = "68a227fb00180c4a541a"  # ProxyDatabase
    collection_id = "68a2280e0039af9b6a24"  # WorkingProxies
    
    # Calculate cutoff date (2 days ago)
    cutoff_date = datetime.now() - timedelta(days=2)
    cutoff_iso = cutoff_date.isoformat()
    
    context.log(f"Starting cleanup process...")
    context.log(f"Cutoff date: {cutoff_iso}")
    context.log(f"Will delete all records older than 2 days")
    
    deleted_count = 0
    total_checked = 0
    errors = []
    
    # Headers for API requests
    headers = {
        'X-Appwrite-Project': project_id,
        'X-Appwrite-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    try:
        # Fetch documents using REST API directly
        list_url = f"{endpoint}/databases/{database_id}/collections/{collection_id}/documents"
        
        try:
            response = requests.get(list_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            documents = data.get('documents', [])
            total_checked = len(documents)
            
            context.log(f"Found {total_checked} documents to check")
            
            # Process each document
            for doc in documents:
                try:
                    # Parse the tested_at timestamp
                    tested_at_str = doc.get('tested_at', '')
                    
                    # Handle different timestamp formats
                    if 'T' in tested_at_str:
                        # ISO format - strip microseconds and timezone
                        tested_at_str_clean = tested_at_str.split('.')[0] if '.' in tested_at_str else tested_at_str
                        tested_at_str_clean = tested_at_str_clean.replace('Z', '')
                        tested_at = datetime.fromisoformat(tested_at_str_clean)
                    else:
                        # Try parsing as string timestamp
                        tested_at = datetime.strptime(tested_at_str, '%Y-%m-%d %H:%M:%S')
                    
                    # Check if older than 2 days
                    if tested_at < cutoff_date:
                        # Delete the document using REST API
                        delete_url = f"{list_url}/{doc['$id']}"
                        delete_response = requests.delete(delete_url, headers=headers, timeout=30)
                        
                        if delete_response.status_code in [200, 204]:
                            deleted_count += 1
                            if deleted_count % 10 == 0:
                                context.log(f"Deleted {deleted_count} old records so far...")
                        else:
                            errors.append(f"Failed to delete {doc['$id']}: HTTP {delete_response.status_code}")
                
                except Exception as e:
                    error_msg = f"Error processing document {doc.get('$id', 'unknown')}: {str(e)}"
                    context.error(error_msg)
                    errors.append(error_msg)
                    continue
            
        except requests.exceptions.RequestException as e:
            context.error(f"Error fetching documents: {str(e)}")
            errors.append(f"Fetch error: {str(e)}")
        
        # Generate summary
        summary = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "cutoff_date": cutoff_iso,
            "total_documents_checked": total_checked,
            "documents_deleted": deleted_count,
            "documents_retained": total_checked - deleted_count,
            "errors_count": len(errors),
            "errors": errors[:10] if errors else []  # Include first 10 errors if any
        }
        
        context.log(f"Cleanup completed successfully!")
        context.log(f"Total documents checked: {total_checked}")
        context.log(f"Documents deleted: {deleted_count}")
        context.log(f"Documents retained: {total_checked - deleted_count}")
        
        if errors:
            context.log(f"Encountered {len(errors)} errors during cleanup")
        
        return context.res.json(summary)
    
    except Exception as e:
        error_summary = {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "total_documents_checked": total_checked,
            "documents_deleted": deleted_count
        }
        
        context.error(f"Fatal error during cleanup: {str(e)}")
        return context.res.json(error_summary, 500)
