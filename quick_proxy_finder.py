#!/usr/bin/env python3
"""
Quick Proxy Finder - Simplified version for quick testing
"""

import sys
import argparse
from proxy_finder import ProxyFinder

def main():
    parser = argparse.ArgumentParser(description='Find working proxies from PROXY-List repository')
    parser.add_argument('--type', '-t', 
                       choices=['http', 'socks4', 'socks5', 'all'],
                       default='all',
                       help='Type of proxies to test (default: all)')
    parser.add_argument('--workers', '-w',
                       type=int,
                       default=50,
                       help='Number of concurrent workers (default: 50)')
    parser.add_argument('--timeout',
                       type=int,
                       default=10,
                       help='Timeout in seconds for each proxy test (default: 10)')
    parser.add_argument('--quick', '-q',
                       action='store_true',
                       help='Quick mode - test fewer proxies for faster results')
    
    args = parser.parse_args()
    
    # Create ProxyFinder instance
    finder = ProxyFinder()
    finder.max_workers = args.workers
    finder.timeout = args.timeout
    
    # Determine which proxy types to test
    if args.type == 'all':
        proxy_types = ['http', 'socks4', 'socks5']
    else:
        proxy_types = [args.type]
    
    # Quick mode - reduce workers and timeout for faster testing
    if args.quick:
        finder.max_workers = min(finder.max_workers, 20)
        finder.timeout = min(finder.timeout, 5)
        print("🚀 Quick mode enabled - faster but less thorough testing")
    
    # Run the proxy finder
    finder.run(proxy_types)

if __name__ == "__main__":
    main()
