#!/usr/bin/env python3
"""
Simple health check script for local testing.
Run after docker-compose up to verify the API is responding.
"""
import requests
import sys
import time

def check_health(max_retries=30, delay=2):
    """Check if the API health endpoint is responding."""
    url = "http://localhost:8000/health"
    
    print(f"Checking health endpoint: {url}")
    
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Health check passed!")
                print(f"  Status: {data.get('status')}")
                print(f"  Service: {data.get('service')}")
                print(f"  Version: {data.get('version')}")
                return True
            else:
                print(f"✗ Attempt {attempt}/{max_retries}: Got status code {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"✗ Attempt {attempt}/{max_retries}: Connection refused (API may still be starting)")
        except requests.exceptions.Timeout:
            print(f"✗ Attempt {attempt}/{max_retries}: Request timed out")
        except Exception as e:
            print(f"✗ Attempt {attempt}/{max_retries}: {str(e)}")
        
        if attempt < max_retries:
            time.sleep(delay)
    
    print(f"\n✗ Health check failed after {max_retries} attempts")
    return False

if __name__ == "__main__":
    success = check_health()
    sys.exit(0 if success else 1)
