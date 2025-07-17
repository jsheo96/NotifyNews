#!/usr/bin/env python3
"""
Simple test script to verify webserver functionality
"""

import requests
import json
import time
import sys
import os

def test_webserver():
    """Test webserver endpoints"""
    base_url = "http://localhost:5000"
    
    print("Testing webserver endpoints...")
    
    # Test config endpoint
    try:
        response = requests.get(f"{base_url}/api/config", timeout=5)
        if response.status_code == 200:
            config = response.json()
            print(f"✓ Config endpoint working: {config}")
        else:
            print(f"✗ Config endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Config endpoint error: {e}")
    
    # Test history endpoint
    try:
        response = requests.get(f"{base_url}/api/history", timeout=5)
        if response.status_code == 200:
            history = response.json()
            print(f"✓ History endpoint working: {history['total_links']} links")
        else:
            print(f"✗ History endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"✗ History endpoint error: {e}")
    
    # Test news endpoint (may fail without secret.json)
    try:
        response = requests.get(f"{base_url}/api/news", timeout=5)
        if response.status_code == 200:
            news = response.json()
            if 'error' in news:
                print(f"✓ News endpoint working (expected error without secret.json): {news['error']}")
            else:
                print(f"✓ News endpoint working: {news}")
        else:
            print(f"✗ News endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"✗ News endpoint error: {e}")
    
    # Test web interface
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200 and "NotifyNews Dashboard" in response.text:
            print("✓ Web interface working")
        else:
            print(f"✗ Web interface failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Web interface error: {e}")

if __name__ == '__main__':
    test_webserver()