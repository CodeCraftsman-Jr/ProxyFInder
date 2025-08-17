#!/usr/bin/env python3
"""
Test script to verify the proxy finder setup
"""

import sys
import os
import requests
from datetime import datetime

def test_requirements():
    """Test if all required packages are installed"""
    print("🔧 Testing requirements...")
    
    try:
        import requests
        print("✓ requests module found")
    except ImportError:
        print("✗ requests module missing - run: pip install requests")
        return False
    
    try:
        import concurrent.futures
        print("✓ concurrent.futures module found")
    except ImportError:
        print("✗ concurrent.futures module missing")
        return False
    
    return True

def test_internet_connection():
    """Test internet connectivity"""
    print("\n🌐 Testing internet connection...")
    
    try:
        response = requests.get("https://www.google.com", timeout=10)
        if response.status_code == 200:
            print("✓ Internet connection working")
            return True
        else:
            print(f"✗ Unexpected response code: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Internet connection failed: {e}")
        return False

def test_proxy_source():
    """Test if proxy source is accessible"""
    print("\n📡 Testing proxy source accessibility...")
    
    try:
        # Test HTTP proxy list
        response = requests.get("https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt", timeout=15)
        if response.status_code == 200:
            proxy_count = len([line for line in response.text.split('\n') if line.strip()])
            print(f"✓ HTTP proxy source accessible ({proxy_count} proxies)")
            return True
        else:
            print(f"✗ Proxy source returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Failed to access proxy source: {e}")
        return False

def test_output_directory():
    """Test if output directory can be created"""
    print("\n📁 Testing output directory creation...")
    
    try:
        output_dir = "working_proxies"
        os.makedirs(output_dir, exist_ok=True)
        
        # Test file creation
        test_file = os.path.join(output_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        
        # Clean up
        os.remove(test_file)
        print("✓ Output directory creation successful")
        return True
    except Exception as e:
        print(f"✗ Failed to create output directory: {e}")
        return False

def test_proxy_finder_import():
    """Test if proxy finder module can be imported"""
    print("\n🔍 Testing proxy finder import...")
    
    try:
        from proxy_finder import ProxyFinder
        finder = ProxyFinder()
        print("✓ ProxyFinder class imported successfully")
        print(f"  - Timeout: {finder.timeout}s")
        print(f"  - Max workers: {finder.max_workers}")
        print(f"  - Test URLs: {len(finder.test_urls)}")
        return True
    except Exception as e:
        print(f"✗ Failed to import ProxyFinder: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 PROXY FINDER - SYSTEM TEST")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python version: {sys.version}")
    print("=" * 60)
    
    tests = [
        ("Requirements Check", test_requirements),
        ("Internet Connection", test_internet_connection),
        ("Proxy Source Access", test_proxy_source),
        ("Output Directory", test_output_directory),
        ("ProxyFinder Import", test_proxy_finder_import)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:<25} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("🎉 ALL TESTS PASSED! The proxy finder is ready to use.")
        print("\nTo run the proxy finder:")
        print("  python proxy_finder.py")
        print("  or")
        print("  python quick_proxy_finder.py --quick")
    else:
        print("❌ SOME TESTS FAILED! Please fix the issues above before running the proxy finder.")
        return 1
    
    print("=" * 60)
    return 0

if __name__ == "__main__":
    sys.exit(main())
