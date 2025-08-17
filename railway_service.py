#!/usr/bin/env python3
"""
Railway Deployment Version - Runs as a service with cron scheduling
"""

import schedule
import time
import os
from github_actions_proxy_checker import AppwriteProxyChecker

def run_proxy_check():
    """Run the proxy check job"""
    print("🚀 Starting scheduled proxy check...")
    checker = AppwriteProxyChecker()
    checker.run()
    print("✅ Proxy check completed!")

def main():
    """Main function for Railway deployment"""
    print("🚂 Railway Proxy Checker Service Started")
    print("📅 Scheduling daily runs at 2:00 AM UTC")
    
    # Schedule the job to run daily at 2 AM UTC
    schedule.every().day.at("02:00").do(run_proxy_check)
    
    # Run once immediately for testing
    if os.getenv('RUN_IMMEDIATELY', '').lower() == 'true':
        run_proxy_check()
    
    # Keep the service running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()
