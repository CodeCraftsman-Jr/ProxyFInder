#!/usr/bin/env python3
"""
Proxy Finder Script
Fetches proxy lists from TheSpeedX/PROXY-List repository,
tests them against Google sites, and stores only working proxies.
"""

import requests
import concurrent.futures
import time
import os
from datetime import datetime
from typing import List, Dict, Tuple
import json
import socks
import socket
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ProxyFinder:
    def __init__(self):
        self.base_url = "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master"
        self.proxy_files = {
            'http': f"{self.base_url}/http.txt",
            'socks4': f"{self.base_url}/socks4.txt", 
            'socks5': f"{self.base_url}/socks5.txt"
        }
        self.test_urls = [
            "http://httpbin.org/ip",
            "http://ifconfig.me/ip",
            "https://api.ipify.org?format=json"
        ]
        self.working_proxies = {'http': [], 'socks4': [], 'socks5': []}
        self.timeout = 10  # seconds
        self.max_workers = 50  # concurrent threads
        
    def fetch_proxy_list(self, proxy_type: str) -> List[str]:
        """Fetch proxy list from GitHub repository"""
        try:
            print(f"Fetching {proxy_type.upper()} proxies...")
            response = requests.get(self.proxy_files[proxy_type], timeout=30)
            response.raise_for_status()
            
            proxies = [line.strip() for line in response.text.split('\n') if line.strip()]
            print(f"Found {len(proxies)} {proxy_type.upper()} proxies")
            return proxies
            
        except Exception as e:
            print(f"Error fetching {proxy_type} proxies: {e}")
            return []
    
    def test_proxy(self, proxy: str, proxy_type: str) -> Tuple[bool, str, float]:
        """Test a single proxy against test sites"""
        try:
            start_time = time.time()
            
            # Format proxy for requests with proper SOCKS support
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
            else:  # socks5
                proxy_dict = {
                    'http': f'socks5://{proxy}',
                    'https': f'socks5://{proxy}'
                }
            
            # Test against multiple URLs
            for test_url in self.test_urls:
                try:
                    response = requests.get(
                        test_url,
                        proxies=proxy_dict,
                        timeout=self.timeout,
                        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
                        verify=False  # Skip SSL verification for faster testing
                    )
                    
                    # Check if request was successful
                    if response.status_code == 200:
                        response_time = time.time() - start_time
                        return True, proxy, response_time
                        
                except requests.exceptions.RequestException:
                    continue
            
            return False, proxy, 0
            
        except Exception:
            return False, proxy, 0
    
    def test_proxies_batch(self, proxies: List[str], proxy_type: str) -> List[Dict]:
        """Test a batch of proxies concurrently"""
        working_proxies = []
        
        print(f"Testing {len(proxies)} {proxy_type.upper()} proxies with {self.max_workers} threads...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all proxy tests
            future_to_proxy = {
                executor.submit(self.test_proxy, proxy, proxy_type): proxy 
                for proxy in proxies
            }
            
            completed = 0
            for future in concurrent.futures.as_completed(future_to_proxy):
                completed += 1
                
                # Print progress every 100 proxies
                if completed % 100 == 0:
                    print(f"Progress: {completed}/{len(proxies)} proxies tested for {proxy_type.upper()}")
                
                try:
                    is_working, proxy, response_time = future.result()
                    if is_working:
                        working_proxies.append({
                            'proxy': proxy,
                            'type': proxy_type,
                            'response_time': round(response_time, 2),
                            'tested_at': datetime.now().isoformat()
                        })
                        print(f"✓ Working {proxy_type.upper()} proxy found: {proxy} (Response time: {response_time:.2f}s)")
                        
                except Exception as e:
                    print(f"Error testing proxy: {e}")
        
        return working_proxies
    
    def save_working_proxies(self, working_proxies: List[Dict], proxy_type: str):
        """Save working proxies to files"""
        if not working_proxies:
            print(f"No working {proxy_type.upper()} proxies found")
            return
        
        # Create output directory
        output_dir = "working_proxies"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save as text file (simple format)
        txt_file = os.path.join(output_dir, f"working_{proxy_type}_{timestamp}.txt")
        with open(txt_file, 'w') as f:
            for proxy_info in working_proxies:
                f.write(f"{proxy_info['proxy']}\n")
        
        # Save as JSON file (detailed format)
        json_file = os.path.join(output_dir, f"working_{proxy_type}_{timestamp}.json")
        with open(json_file, 'w') as f:
            json.dump(working_proxies, f, indent=2)
        
        # Save to latest file (overwrite previous)
        latest_txt = os.path.join(output_dir, f"working_{proxy_type}_latest.txt")
        latest_json = os.path.join(output_dir, f"working_{proxy_type}_latest.json")
        
        with open(latest_txt, 'w') as f:
            for proxy_info in working_proxies:
                f.write(f"{proxy_info['proxy']}\n")
        
        with open(latest_json, 'w') as f:
            json.dump(working_proxies, f, indent=2)
        
        print(f"Saved {len(working_proxies)} working {proxy_type.upper()} proxies to:")
        print(f"  - {txt_file}")
        print(f"  - {json_file}")
        print(f"  - {latest_txt}")
        print(f"  - {latest_json}")
    
    def generate_summary_report(self):
        """Generate a summary report of all working proxies"""
        output_dir = "working_proxies"
        summary_file = os.path.join(output_dir, f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        summary = {
            'generated_at': datetime.now().isoformat(),
            'total_working_proxies': sum(len(proxies) for proxies in self.working_proxies.values()),
            'by_type': {
                proxy_type: len(proxies) 
                for proxy_type, proxies in self.working_proxies.items()
            },
            'fastest_proxies': {},
            'source': 'https://github.com/TheSpeedX/SOCKS-List'
        }
        
        # Find fastest proxies for each type
        for proxy_type, proxies in self.working_proxies.items():
            if proxies:
                fastest = min(proxies, key=lambda x: x['response_time'])
                summary['fastest_proxies'][proxy_type] = fastest
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\nSummary report saved to: {summary_file}")
        return summary
    
    def run(self, proxy_types: List[str] = None):
        """Main execution function"""
        if proxy_types is None:
            proxy_types = ['http', 'socks4', 'socks5']
        
        print("=" * 60)
        print("🔍 PROXY FINDER - Finding Working Proxies")
        print("=" * 60)
        print(f"Source: https://github.com/TheSpeedX/SOCKS-List")
        print(f"Testing against: {', '.join(self.test_urls)}")
        print(f"Timeout: {self.timeout}s per proxy")
        print(f"Max concurrent threads: {self.max_workers}")
        print("=" * 60)
        
        start_time = time.time()
        
        for proxy_type in proxy_types:
            print(f"\n🔎 Processing {proxy_type.upper()} proxies...")
            
            # Fetch proxy list
            proxies = self.fetch_proxy_list(proxy_type)
            if not proxies:
                continue
            
            # Test proxies
            working_proxies = self.test_proxies_batch(proxies, proxy_type)
            self.working_proxies[proxy_type] = working_proxies
            
            # Save results
            self.save_working_proxies(working_proxies, proxy_type)
        
        # Generate summary
        summary = self.generate_summary_report()
        
        total_time = time.time() - start_time
        print("\n" + "=" * 60)
        print("📊 FINAL SUMMARY")
        print("=" * 60)
        print(f"Total execution time: {total_time:.2f} seconds")
        print(f"Total working proxies found: {summary['total_working_proxies']}")
        for proxy_type, count in summary['by_type'].items():
            print(f"  - {proxy_type.upper()}: {count} working proxies")
        
        if summary['fastest_proxies']:
            print("\n🏃 Fastest proxies by type:")
            for proxy_type, fastest in summary['fastest_proxies'].items():
                print(f"  - {proxy_type.upper()}: {fastest['proxy']} ({fastest['response_time']}s)")
        
        print("=" * 60)


def main():
    """Main function"""
    proxy_finder = ProxyFinder()
    
    # You can specify which proxy types to test
    # proxy_finder.run(['http'])  # Test only HTTP proxies
    # proxy_finder.run(['socks5'])  # Test only SOCKS5 proxies
    proxy_finder.run()  # Test all proxy types


if __name__ == "__main__":
    main()
