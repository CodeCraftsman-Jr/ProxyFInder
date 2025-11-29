"""
Appwrite Function to clean up old proxy records
Keeps only the last 2 days of data and deletes older records
"""

import os
import json
from datetime import datetime, timedelta


def main(context):
    """
    Main function to clean up old proxy records
    Runs every 2 days to delete records older than 2 days
    """
    
    # Import Appwrite SDK inside the function
    try:
        from appwrite.client import Client
        from appwrite.services.databases import Databases
        from appwrite.query import Query
    except ImportError as e:
        context.error(f"Failed to import Appwrite SDK: {str(e)}")
        return context.res.json({
            "success": False,
            "error": f"Import error: {str(e)}"
        }, 500)
    
    # Initialize Appwrite client
    client = Client()
    
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
    
    client.set_endpoint(endpoint)
    client.set_project(project_id)
    client.set_key(api_key)
    
    databases = Databases(client)
    
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
    
    try:
        # Fetch all documents (paginated)
        offset = 0
        limit = 100
        has_more = True
        
        while has_more:
            try:
                # Get documents
                response = databases.list_documents(
                    database_id=database_id,
                    collection_id=collection_id,
                    queries=[
                        Query.limit(limit),
                        Query.offset(offset)
                    ]
                )
                
                documents = response['documents']
                total_in_batch = len(documents)
                
                if total_in_batch == 0:
                    has_more = False
                    break
                
                context.log(f"Processing batch: {total_in_batch} documents (offset: {offset})")
                
                # Process each document
                for doc in documents:
                    total_checked += 1
                    
                    try:
                        # Parse the tested_at timestamp
                        tested_at_str = doc.get('tested_at', '')
                        
                        # Handle different timestamp formats
                        if 'T' in tested_at_str:
                            # ISO format
                            tested_at = datetime.fromisoformat(tested_at_str.replace('Z', '+00:00'))
                        else:
                            # Try parsing as string timestamp
                            tested_at = datetime.strptime(tested_at_str, '%Y-%m-%d %H:%M:%S')
                        
                        # Check if older than 2 days
                        if tested_at < cutoff_date:
                            # Delete the document
                            databases.delete_document(
                                database_id=database_id,
                                collection_id=collection_id,
                                document_id=doc['$id']
                            )
                            deleted_count += 1
                            
                            if deleted_count % 10 == 0:
                                context.log(f"Deleted {deleted_count} old records so far...")
                    
                    except Exception as e:
                        error_msg = f"Error processing document {doc.get('$id', 'unknown')}: {str(e)}"
                        context.error(error_msg)
                        errors.append(error_msg)
                        continue
                
                # Move to next batch
                offset += limit
                
                # If we got fewer documents than the limit, we've reached the end
                if total_in_batch < limit:
                    has_more = False
            
            except Exception as e:
                context.error(f"Error fetching batch at offset {offset}: {str(e)}")
                errors.append(f"Batch error at offset {offset}: {str(e)}")
                has_more = False
        
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
