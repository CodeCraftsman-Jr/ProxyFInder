#!/usr/bin/env python3
"""
GitHub Actions Proxy Checker with Appwrite Integration
Fetches proxies from PROXY-List repo, tests them, and stores working ones in Appwrite
"""

import requests
import time
import os
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID

class AppwriteProxyChecker:
    def __init__(self):
        # Appwrite configuration
        self.client = Client()
        self.client.set_endpoint(os.getenv('APPWRITE_ENDPOINT', 'https://cloud.appwrite.io/v1'))
        self.client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
        self.client.set_key(os.getenv('APPWRITE_API_KEY'))
        
        self.databases = Databases(self.client)
        self.database_id = os.getenv('APPWRITE_DATABASE_ID')
        self.collection_id = os.getenv('APPWRITE_COLLECTION_ID')
        
        # Test configuration - Use a mix of simple and popular sites
        self.test_urls = [
            'http://httpbin.org/get',          # Simple HTTP service
            'https://api.ipify.org',           # Simple IP service
            'https://www.google.com',          # Google
            'https://www.youtube.com',         # YouTube
        ]
        self.timeout = 15  # Increased timeout for popular sites
        self.max_workers = 25  # Reduced for better success rate
        
        # Statistics
        self.stats = {
            'total_tested': 0,
            'working': 0,
            'failed': 0,
            'start_time': datetime.now(),
            'proxy_types': {}
        }

    def fetch_proxy_list(self, proxy_type):
        """Fetch proxy list from GitHub repository"""
        url = f"https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/{proxy_type}.txt"
        try:
            print(f"Fetching {proxy_type} proxies from GitHub...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            proxies = [line.strip() for line in response.text.splitlines() if line.strip()]
            print(f"Found {len(proxies)} {proxy_type} proxies")
            return proxies
        except Exception as e:
            print(f"Error fetching {proxy_type} proxies: {e}")
            return []

    def test_proxy(self, proxy, proxy_type):
        """Test a single proxy with multiple URLs"""
        try:
            # Configure proxy settings
            if proxy_type == 'http':
                proxy_dict = {
                    'http': f'http://{proxy}',
                    'https': f'http://{proxy}'
                }
            elif proxy_type == 'socks4':
                proxy_dict = {
                    'http': f'socks4://{proxy}',
                    'https': f'socks4://{proxy}'
                }
            elif proxy_type == 'socks5':
                proxy_dict = {
                    'http': f'socks5://{proxy}',
                    'https': f'socks5://{proxy}'
                }
            else:
                return False, f"Unknown proxy type: {proxy_type}"

            # Test proxy with multiple URLs - try each one
            successful_urls = []
            for i, test_url in enumerate(self.test_urls, 1):
                try:
                    response = requests.get(
                        test_url,
                        proxies=proxy_dict,
                        timeout=self.timeout,
                        allow_redirects=True,
                        headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                        }
                    )
                    
                    if response.status_code == 200:
                        site_name = test_url.split('//')[1].split('/')[0]
                        successful_urls.append(site_name)
                        
                        # Return success after first working URL for speed
                        return True, f"Works with {site_name} ({response.status_code})"
                        
                except requests.exceptions.RequestException as e:
                    # Continue to next URL
                    continue
                    
            return False, f"Failed all sites: {', '.join([url.split('//')[1].split('/')[0] for url in self.test_urls])}"
            
        except Exception as e:
            return False, f"Error: {str(e)}"

    def save_to_appwrite(self, proxy, proxy_type, response_time):
        """Save working proxy to Appwrite database"""
        try:
            document_data = {
                'proxy': proxy,
                'type': proxy_type,
                'response_time': response_time,
                'tested_at': datetime.now().isoformat(),
                'status': 'working'
            }
            
            self.databases.create_document(
                database_id=self.database_id,
                collection_id=self.collection_id,
                document_id=ID.unique(),
                data=document_data
            )
            return True
        except Exception as e:
            print(f"Error saving to Appwrite: {e}")
            return False

    def save_to_local_file(self, working_proxies, proxy_type):
        """Save working proxies to local files as backup"""
        os.makedirs('working_proxies', exist_ok=True)
        
        filename = f"working_proxies/working_{proxy_type}_proxies.txt"
        with open(filename, 'w') as f:
            for proxy_data in working_proxies:
                f.write(f"{proxy_data['proxy']}\n")
        
        # Save detailed info as JSON
        json_filename = f"working_proxies/working_{proxy_type}_proxies_detailed.json"
        with open(json_filename, 'w') as f:
            json.dump(working_proxies, f, indent=2)

    def test_proxies_batch(self, proxies, proxy_type):
        """Test a batch of proxies concurrently"""
        working_proxies = []
        
        print(f"\nTesting {len(proxies)} {proxy_type} proxies...")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_proxy = {
                executor.submit(self.test_proxy, proxy, proxy_type): proxy 
                for proxy in proxies
            }
            
            for i, future in enumerate(as_completed(future_to_proxy), 1):
                proxy = future_to_proxy[future]
                self.stats['total_tested'] += 1
                
                try:
                    start_time = time.time()
                    is_working, message = future.result()
                    response_time = time.time() - start_time
                    
                    if is_working:
                        self.stats['working'] += 1
                        proxy_data = {
                            'proxy': proxy,
                            'type': proxy_type,
                            'response_time': round(response_time, 2),
                            'tested_at': datetime.now().isoformat()
                        }
                        working_proxies.append(proxy_data)
                        
                        # Save to Appwrite
                        self.save_to_appwrite(proxy, proxy_type, round(response_time, 2))
                        
                        print(f"✅ {proxy} - {message} ({response_time:.2f}s)")
                    else:
                        self.stats['failed'] += 1
                        # Only show failed proxies occasionally to reduce noise
                        if i % 20 == 0:
                            print(f"❌ {proxy} - {message}")
                        
                except Exception as e:
                    self.stats['failed'] += 1
                    # Only show exceptions occasionally
                    if i % 20 == 0:
                        print(f"❌ {proxy} - Exception: {e}")
                
                # Enhanced progress update
                if i % 25 == 0:
                    success_rate = (self.stats['working'] / i * 100) if i > 0 else 0
                    print(f"📊 Progress: {i}/{len(proxies)} tested | Working: {self.stats['working']} | Success Rate: {success_rate:.1f}%")
        
        return working_proxies

    def run(self):
        """Main execution function"""
        print("🚀 Starting GitHub Actions Proxy Checker with Appwrite Integration")
        print(f"Test URLs: {', '.join(self.test_urls)}")
        print(f"Timeout: {self.timeout}s")
        print(f"Max workers: {self.max_workers}")
        print("-" * 60)
        
        proxy_types = ['http', 'socks4', 'socks5']
        all_working_proxies = {}
        
        for proxy_type in proxy_types:
            # Fetch proxies
            proxies = self.fetch_proxy_list(proxy_type)
            if not proxies:
                continue
                
            self.stats['proxy_types'][proxy_type] = len(proxies)
            
            # Test proxies
            working_proxies = self.test_proxies_batch(proxies, proxy_type)
            all_working_proxies[proxy_type] = working_proxies
            
            # Save to local files
            self.save_to_local_file(working_proxies, proxy_type)
            
            print(f"\n{proxy_type.upper()} Results:")
            print(f"  Total tested: {len(proxies)}")
            print(f"  Working: {len(working_proxies)}")
            print(f"  Success rate: {len(working_proxies)/len(proxies)*100:.1f}%")
        
        # Final statistics
        self.print_final_stats(all_working_proxies)
        
        return all_working_proxies

    def print_final_stats(self, all_working_proxies):
        """Print final statistics"""
        end_time = datetime.now()
        duration = end_time - self.stats['start_time']
        
        total_working = sum(len(proxies) for proxies in all_working_proxies.values())
        
        print("\n" + "="*60)
        print("📊 FINAL STATISTICS")
        print("="*60)
        print(f"Start time: {self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duration: {duration}")
        print(f"Total proxies tested: {self.stats['total_tested']}")
        print(f"Working proxies found: {total_working}")
        print(f"Failed proxies: {self.stats['failed']}")
        print(f"Overall success rate: {total_working/self.stats['total_tested']*100:.1f}%")
        
        print("\nBreakdown by type:")
        for proxy_type, working_proxies in all_working_proxies.items():
            total = self.stats['proxy_types'].get(proxy_type, 0)
            working = len(working_proxies)
            rate = working/total*100 if total > 0 else 0
            print(f"  {proxy_type.upper()}: {working}/{total} ({rate:.1f}%)")

if __name__ == "__main__":
    checker = AppwriteProxyChecker()
    checker.run()
