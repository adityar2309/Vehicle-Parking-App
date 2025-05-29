#!/usr/bin/env python3
"""
Simple Redis Connection Test for Redis Cloud

This script tests Redis connection with single database (db 0 only).
"""

import redis
import time
from urllib.parse import urlparse

def test_redis_simple():
    print("🔗 Testing Redis Connection (Single Database)")
    print("=" * 50)
    
    # Your Redis endpoint
    redis_host = "redis-13431.crce179.ap-south-1-1.ec2.redns.redis-cloud.com"
    redis_port = 13431
    
    print(f"Host: {redis_host}")
    print(f"Port: {redis_port}")
    print("\nPlease enter your Redis password:")
    redis_password = input("Password: ").strip()
    
    if not redis_password:
        print("❌ Password is required!")
        return False
    
    try:
        print("\n🔄 Connecting to Redis...")
        
        # Create Redis client for database 0
        r = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            db=0,
            decode_responses=True,
            socket_timeout=10,
            socket_connect_timeout=10
        )
        
        # Test connection
        r.ping()
        print("✅ Successfully connected to Redis!")
        
        # Test operations with key prefixes
        print("\n🔄 Testing Redis operations with key prefixes...")
        
        # Test cache operations
        cache_key = "cache:test_parking_app"
        cache_value = f"cache_test_{int(time.time())}"
        r.set(cache_key, cache_value, ex=60)
        
        retrieved_cache = r.get(cache_key)
        if retrieved_cache == cache_value:
            print("✅ Cache operations working!")
        else:
            print("❌ Cache operations failed!")
            return False
        
        # Test celery operations
        celery_key = "celery:test_parking_app"
        celery_value = f"celery_test_{int(time.time())}"
        r.set(celery_key, celery_value, ex=60)
        
        retrieved_celery = r.get(celery_key)
        if retrieved_celery == celery_value:
            print("✅ Celery operations working!")
        else:
            print("❌ Celery operations failed!")
            return False
        
        # Test Redis info
        print("\n📊 Redis Server Information:")
        info = r.info()
        print(f"Redis Version: {info.get('redis_version', 'Unknown')}")
        print(f"Connected Clients: {info.get('connected_clients', 0)}")
        print(f"Used Memory: {info.get('used_memory_human', 'Unknown')}")
        print(f"Total Commands: {info.get('total_commands_processed', 0)}")
        print(f"Available Databases: {info.get('databases', 'Unknown')}")
        
        # Clean up test keys
        r.delete(cache_key)
        r.delete(celery_key)
        print("🧹 Test keys cleaned up")
        
        print("\n🎉 Redis is ready for your app!")
        
        # Generate the correct Redis URL
        redis_url = f"redis://:{redis_password}@{redis_host}:{redis_port}/0"
        print(f"\n🔗 Your Redis URL: {redis_url}")
        
        return True, redis_url
        
    except redis.ConnectionError as e:
        print(f"❌ Connection failed: {e}")
        return False, None
        
    except redis.AuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        return False, None
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False, None

def update_app_yaml(redis_url):
    """Update app.yaml with the correct Redis URL"""
    print("\n💾 Updating backend/app.yaml with Redis URL...")
    
    try:
        # Read current app.yaml
        with open('backend/app.yaml', 'r') as f:
            content = f.read()
        
        # Replace placeholder with actual Redis URL
        updated_content = content.replace(
            'YOUR_REDIS_PASSWORD@redis-13431.crce179.ap-south-1-1.ec2.redns.redis-cloud.com:13431',
            f'{redis_url.split("@")[1]}'
        )
        updated_content = updated_content.replace(
            'redis://:YOUR_REDIS_PASSWORD@',
            f'redis://:{redis_url.split(":")[2].split("@")[0]}@'
        )
        
        # Write updated content
        with open('backend/app.yaml', 'w') as f:
            f.write(updated_content)
        
        print("✅ backend/app.yaml updated successfully!")
        print("\nNext steps:")
        print("1. Commit and push changes to GitHub")
        print("2. Deploy to Google Cloud App Engine")
        print("3. Test Redis integration")
        
        return True
    except Exception as e:
        print(f"❌ Failed to update app.yaml: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Vehicle Parking App - Simple Redis Test")
    print("=" * 60)
    
    try:
        import redis
        print("✅ Redis package is installed")
    except ImportError:
        print("❌ Redis package not found. Please run: pip install redis")
        exit(1)
    
    success, redis_url = test_redis_simple()
    
    if success and redis_url:
        update_app_yaml(redis_url)
    else:
        print("\n🔧 Troubleshooting tips:")
        print("1. Check your Redis Cloud password")
        print("2. Ensure your Redis instance is running")
        print("3. Verify network connectivity")
        print("4. Contact Redis Cloud support if issues persist") 