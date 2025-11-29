"""
Appwrite Function to clean up old proxy records
Keeps only the last 2 days of data and deletes older records
Uses REST API directly to avoid SDK compatibility issues
"""

import os
import json
import requests
from datetime import datetime, timedelta
from urllib.parse import quote


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
        # Fetch ALL documents using REST API with pagination
        list_url = f"{endpoint}/databases/{database_id}/collections/{collection_id}/documents"
        
        all_documents = []
        offset = 0
        limit = 100  # Max per page
        
        # Fetch all documents with pagination
        while True:
            try:
                # Add pagination parameters using proper Appwrite REST API query format
                query_limit = json.dumps({"method":"limit","values":[limit]})
                query_offset = json.dumps({"method":"offset","values":[offset]})
                
                context.log(f"Building queries - limit: {limit}, offset: {offset}")
                context.log(f"Query limit JSON: {query_limit}")
                context.log(f"Query offset JSON: {query_offset}")
                
                # Use params to let requests handle URL encoding
                params = [
                    ('queries[]', query_limit),
                    ('queries[]', query_offset)
                ]
                
                context.log(f"Making request to: {list_url}")
                context.log(f"With params: {params}")
                
                response = requests.get(list_url, headers=headers, params=params, timeout=30)
                
                context.log(f"Response status: {response.status_code}")
                context.log(f"Response URL: {response.url}")
                
                response.raise_for_status()
                
                data = response.json()
                documents = data.get('documents', [])
                total = data.get('total', 0)
                
                context.log(f"✅ Successfully fetched batch")
                context.log(f"   Documents in this batch: {len(documents)}")
                context.log(f"   Server reports total: {total}")
                context.log(f"   Total fetched so far: {len(all_documents) + len(documents)}")
                
                if not documents:
                    context.log("No more documents found - breaking pagination loop")
                    break  # No more documents
                
                all_documents.extend(documents)
                context.log(f"Added {len(documents)} documents to collection")
                
                # If we got fewer documents than the limit, we've reached the end
                if len(documents) < limit:
                    context.log(f"Got fewer documents ({len(documents)}) than limit ({limit}) - reached end")
                    break
                
                offset += limit
                context.log(f"Moving to next batch with offset: {offset}")
                context.log("="*50)
                
            except Exception as e:
                context.error(f"❌ Error fetching page at offset {offset}: {str(e)}")
                context.error(f"Exception type: {type(e).__name__}")
                import traceback
                context.error(f"Traceback: {traceback.format_exc()}")
                break
        
        total_checked = len(all_documents)
        context.log(f"📊 Pagination complete!")
        context.log(f"Total documents fetched: {total_checked}")
        
        # Process each document
        context.log(f"🔄 Starting to process {total_checked} documents...")
        
        # Collect documents to delete
        docs_to_delete = []
        
        for i, doc in enumerate(all_documents, 1):
                try:
                    if i % 100 == 0:
                        context.log(f"Processing document {i}/{total_checked}...")
                    
                    # Parse the tested_at timestamp
                    tested_at_str = doc.get('tested_at', '')
                    doc_id = doc.get('$id', 'unknown')
                    
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
                        docs_to_delete.append(doc_id)
                
                except Exception as e:
                    error_msg = f"Error processing document {doc_id}: {str(e)}"
                    context.error(error_msg)
                    errors.append(error_msg)
                    continue
        
        context.log(f"📋 Found {len(docs_to_delete)} documents to delete")
        
        # Delete documents in parallel batches
        import concurrent.futures
        
        def delete_document(doc_id):
            """Delete a single document"""
            try:
                delete_url = f"{list_url}/{doc_id}"
                delete_response = requests.delete(delete_url, headers=headers, timeout=30)
                
                if delete_response.status_code in [200, 204]:
                    return ('success', doc_id)
                elif delete_response.status_code == 404:
                    return ('already_deleted', doc_id)
                else:
                    return ('error', doc_id, delete_response.status_code)
            except Exception as e:
                return ('exception', doc_id, str(e))
        
        # Delete in batches using thread pool
        batch_size = 20  # Delete 20 at a time
        context.log(f"🗑️  Starting batch deletion with {batch_size} workers...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=batch_size) as executor:
            futures = {executor.submit(delete_document, doc_id): doc_id for doc_id in docs_to_delete}
            
            for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
                result = future.result()
                
                if result[0] == 'success':
                    deleted_count += 1
                    if deleted_count % 50 == 0:
                        context.log(f"🗑️  Deleted {deleted_count}/{len(docs_to_delete)} old records...")
                elif result[0] == 'already_deleted':
                    # Count as deleted since it's already gone
                    deleted_count += 1
                elif result[0] == 'error':
                    error_msg = f"Failed to delete {result[1]}: HTTP {result[2]}"
                    context.error(error_msg)
                    errors.append(error_msg)
                else:  # exception
                    error_msg = f"Exception deleting {result[1]}: {result[2]}"
                    context.error(error_msg)
                    errors.append(error_msg)
        
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
        
        context.log("="*60)
        context.log(f"✅ Cleanup completed successfully!")
        context.log(f"📋 Summary:")
        context.log(f"   Total documents checked: {total_checked}")
        context.log(f"   Documents deleted: {deleted_count}")
        context.log(f"   Documents retained: {total_checked - deleted_count}")
        context.log(f"   Errors encountered: {len(errors)}")
        context.log("="*60)
        
        if errors:
            context.log(f"⚠️  Encountered {len(errors)} errors during cleanup")
            for i, err in enumerate(errors[:5], 1):
                context.error(f"  Error {i}: {err}")
        
        return context.res.json(summary)
    
    except Exception as e:
        error_summary = {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "total_documents_checked": total_checked,
            "documents_deleted": deleted_count
        }
        
        context.error("="*60)
        context.error(f"❌ Fatal error during cleanup: {str(e)}")
        context.error(f"Exception type: {type(e).__name__}")
        import traceback
        context.error(f"Full traceback:")
        context.error(traceback.format_exc())
        context.error("="*60)
        return context.res.json(error_summary, 500)
