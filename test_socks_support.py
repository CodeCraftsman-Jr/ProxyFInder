#!/usr/bin/env python3
"""
Quick test script to verify SOCKS proxy support
Tests a few proxies to ensure the setup works
"""

import requests
import time

# Disable SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_single_proxy(proxy, proxy_type):
    """Test a single proxy"""
    print(f"\nTesting {proxy_type.upper()} proxy: {proxy}")
    
    # Format proxy
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
    
    # Test URLs
    test_urls = [
        'http://httpbin.org/ip',
        'http://ifconfig.me/ip',
        'https://api.ipify.org?format=json'
    ]
    
    for url in test_urls:
        try:
            print(f"  Trying {url}...", end=" ")
            start = time.time()
            response = requests.get(
                url,
                proxies=proxy_dict,
                timeout=10,
                verify=False,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            elapsed = time.time() - start
            
            if response.status_code == 200:
                print(f"✅ SUCCESS ({elapsed:.2f}s) - {response.text[:50]}")
                return True
            else:
                print(f"❌ HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {type(e).__name__}: {str(e)[:50]}")
    
    return False

if __name__ == "__main__":
    print("=" * 60)
    print("SOCKS Proxy Support Test")
    print("=" * 60)
    
    # Fetch a few proxies to test
    print("\nFetching sample proxies...")
    
    try:
        # Get SOCKS4 proxies
        response = requests.get("https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt", timeout=30)
        socks4_proxies = [line.strip() for line in response.text.split('\n') if line.strip()][:5]
        
        # Get SOCKS5 proxies
        response = requests.get("https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt", timeout=30)
        socks5_proxies = [line.strip() for line in response.text.split('\n') if line.strip()][:5]
        
        # Get HTTP proxies
        response = requests.get("https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt", timeout=30)
        http_proxies = [line.strip() for line in response.text.split('\n') if line.strip()][:5]
        
        print(f"Got {len(socks4_proxies)} SOCKS4, {len(socks5_proxies)} SOCKS5, {len(http_proxies)} HTTP proxies")
        
        results = {
            'socks4': 0,
            'socks5': 0,
            'http': 0
        }
        
        # Test SOCKS4
        print("\n" + "=" * 60)
        print("Testing SOCKS4 Proxies")
        print("=" * 60)
        for proxy in socks4_proxies:
            if test_single_proxy(proxy, 'socks4'):
                results['socks4'] += 1
                break  # Found one working, that's enough
        
        # Test SOCKS5
        print("\n" + "=" * 60)
        print("Testing SOCKS5 Proxies")
        print("=" * 60)
        for proxy in socks5_proxies:
            if test_single_proxy(proxy, 'socks5'):
                results['socks5'] += 1
                break
        
        # Test HTTP
        print("\n" + "=" * 60)
        print("Testing HTTP Proxies")
        print("=" * 60)
        for proxy in http_proxies:
            if test_single_proxy(proxy, 'http'):
                results['http'] += 1
                break
        
        print("\n" + "=" * 60)
        print("RESULTS")
        print("=" * 60)
        print(f"SOCKS4: {'✅ WORKING' if results['socks4'] > 0 else '❌ NOT WORKING'}")
        print(f"SOCKS5: {'✅ WORKING' if results['socks5'] > 0 else '❌ NOT WORKING'}")
        print(f"HTTP:   {'✅ WORKING' if results['http'] > 0 else '❌ NOT WORKING'}")
        
        if sum(results.values()) == 0:
            print("\n⚠️  No working proxies found. This could mean:")
            print("   1. The proxy lists are currently dead")
            print("   2. Network/firewall is blocking proxy connections")
            print("   3. Timeout is too short")
        else:
            print("\n✅ SOCKS proxy support is working correctly!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
