#!/usr/bin/env python3
"""
Check total document count in Appwrite database
"""

import requests

# Configuration
endpoint = "https://fra.cloud.appwrite.io/v1"
project_id = "68a227de003201ae2463"
api_key = "standard_07fb15b720e462b3836f463480a1806e1bdff6395d21e97cb0d835c7403329923073329e7fb76ee8de3f42e732d391583be826c2a91afe6014c7e248cf14b64880e9597257eec3ad82c78bf1b13b99b9ecb8bc7357fab9284afa73e8e245788449418dcc468499870fd5da6ebbd5b1148370260ab2dc82431cd5ad5b2df32621"
database_id = "68a227fb00180c4a541a"
collection_id = "68a2280e0039af9b6a24"

headers = {
    'X-Appwrite-Project': project_id,
    'X-Appwrite-Key': api_key,
}

print("Fetching document count...")
print("=" * 60)

# Fetch all documents with pagination
all_docs = []
offset = 0
limit = 5000  # Appwrite max limit per page
page = 1

while True:
    # Use queries parameter for Appwrite with proper JSON format
    url = f"{endpoint}/databases/{database_id}/collections/{collection_id}/documents"
    
    # Build proper query strings according to Appwrite REST API docs
    import json as json_module
    query_limit = json_module.dumps({"method":"limit","values":[limit]})
    query_offset = json_module.dumps({"method":"offset","values":[offset]})
    
    # Construct URL with multiple queries[] parameters
    full_url = f"{url}?queries[]={query_limit}&queries[]={query_offset}"
    
    print(f"Fetching page {page} (offset: {offset}, limit: {limit})...")
    response = requests.get(full_url, headers=headers)
    
    if response.status_code != 200:
        print(f"Error: HTTP {response.status_code}")
        print(response.text)
        break
    
    data = response.json()
    documents = data.get('documents', [])
    total = data.get('total', 0)
    
    if not documents:
        print(f"No more documents found at offset {offset}")
        break
    
    all_docs.extend(documents)
    print(f"  Page {page}: Got {len(documents)} documents | Total so far: {len(all_docs)} | Server reports total: {total}")
    
    # Check if we've fetched all documents
    if len(all_docs) >= total or len(documents) < limit:
        break
    
    offset += limit
    page += 1

print("=" * 60)
print(f"Total documents in database: {len(all_docs)}")
print("=" * 60)

if all_docs:
    print("\nSample document timestamps:")
    for i, doc in enumerate(all_docs[:5]):
        print(f"  {i+1}. {doc.get('proxy', 'N/A')} - Tested: {doc.get('tested_at', 'N/A')}")
