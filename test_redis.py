#!/usr/bin/env python3
"""
Redis Connection Test Script

This script tests your Redis connection before deploying with Celery/Redis.
"""

import redis
import time
from urllib.parse import urlparse

def test_redis_connection():
    print("🔗 Testing Redis Connection")
    print("=" * 50)
    
    # Get Redis URL from user
    print("\nPlease enter your Redis URL:")
    print("Format: redis://:password@host:port/db")
    print("Example: redis://:mypass123@redis-12345.redis-cloud.com:12345/0")
    print("\n(Paste your Redis URL here)")
    
    redis_url = input("Redis URL: ").strip()
    
    if not redis_url:
        print("❌ No Redis URL provided!")
        return False
    
    try:
        print("\n🔄 Parsing Redis URL...")
        parsed_url = urlparse(redis_url)
        
        print(f"Host: {parsed_url.hostname}")
        print(f"Port: {parsed_url.port}")
        print(f"Password: {'***' if parsed_url.password else 'None'}")
        
        print("\n🔄 Connecting to Redis...")
        
        # Create Redis client
        r = redis.Redis(
            host=parsed_url.hostname,
            port=parsed_url.port,
            password=parsed_url.password,
            decode_responses=True,
            socket_timeout=10,
            socket_connect_timeout=10
        )
        
        # Test connection
        r.ping()
        print("✅ Successfully connected to Redis!")
        
        # Test basic operations
        print("\n🔄 Testing Redis operations...")
        
        # Test SET/GET
        test_key = "test_parking_app"
        test_value = f"test_value_{int(time.time())}"
        r.set(test_key, test_value, ex=60)  # Expire in 60 seconds
        
        retrieved_value = r.get(test_key)
        if retrieved_value == test_value:
            print("✅ SET/GET operations working!")
        else:
            print("❌ SET/GET operations failed!")
            return False
        
        # Test different databases
        print("\n🔄 Testing multiple databases...")
        
        # Test db 0 (cache)
        r0 = redis.Redis(
            host=parsed_url.hostname,
            port=parsed_url.port,
            password=parsed_url.password,
            db=0,
            decode_responses=True
        )
        r0.set("cache_test", "cache_working")
        
        # Test db 1 (celery broker)
        r1 = redis.Redis(
            host=parsed_url.hostname,
            port=parsed_url.port,
            password=parsed_url.password,
            db=1,
            decode_responses=True
        )
        r1.set("celery_test", "celery_working")
        
        # Verify separation
        if r0.get("cache_test") == "cache_working" and r1.get("celery_test") == "celery_working":
            print("✅ Multiple databases working!")
        else:
            print("❌ Multiple databases failed!")
            return False
        
        # Test Redis info
        print("\n📊 Redis Server Information:")
        info = r.info()
        print(f"Redis Version: {info.get('redis_version', 'Unknown')}")
        print(f"Connected Clients: {info.get('connected_clients', 0)}")
        print(f"Used Memory: {info.get('used_memory_human', 'Unknown')}")
        print(f"Total Commands: {info.get('total_commands_processed', 0)}")
        
        # Clean up test keys
        r.delete(test_key)
        r0.delete("cache_test")
        r1.delete("celery_test")
        print("🧹 Test keys cleaned up")
        
        print("\n🎉 Redis is ready for your app!")
        print("\nNext steps:")
        print("1. Update backend/app.yaml with this Redis URL")
        print("2. Deploy your backend to Google Cloud")
        print("3. Test the integrated application")
        
        return True
        
    except redis.ConnectionError as e:
        print(f"❌ Connection failed: {e}")
        print("   Check your Redis URL and network connectivity")
        return False
        
    except redis.AuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("   Check your Redis password")
        return False
        
    except redis.ResponseError as e:
        print(f"❌ Redis error: {e}")
        print("   Check your Redis configuration")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def generate_app_yaml_config():
    """Generate app.yaml configuration with Redis URLs"""
    print("\n💾 Would you like to generate app.yaml Redis configuration? (y/n): ", end="")
    choice = input().lower().strip()
    
    if choice == 'y':
        redis_url = input("\nEnter your Redis URL again: ").strip()
        
        # Parse to extract components
        parsed_url = urlparse(redis_url)
        base_url = f"redis://:{parsed_url.password}@{parsed_url.hostname}:{parsed_url.port}"
        
        config = f"""
# Add these lines to your backend/app.yaml env_variables section:

env_variables:
  # Redis Configuration
  REDIS_URL: "{base_url}/0"
  CACHE_REDIS_URL: "{base_url}/0"
  CELERY_BROKER_URL: "{base_url}/1"
  CELERY_RESULT_BACKEND: "{base_url}/1"
"""
        
        # Save to file
        with open('redis_config_for_app_yaml.txt', 'w') as f:
            f.write(config)
        
        print("✅ Configuration saved to 'redis_config_for_app_yaml.txt'")
        print("⚠️  Copy these lines to your backend/app.yaml file")

if __name__ == "__main__":
    print("🚀 Vehicle Parking App - Redis Connection Test")
    print("=" * 60)
    
    # Check if redis package is installed
    try:
        import redis
        print("✅ Redis package is installed")
    except ImportError:
        print("❌ Redis package not found. Please run: pip install redis")
        exit(1)
    
    # Test connection
    if test_redis_connection():
        generate_app_yaml_config()
    else:
        print("\n🔧 Troubleshooting tips:")
        print("1. Double-check your Redis URL format")
        print("2. Ensure your Redis instance is running")
        print("3. Check firewall/network settings")
        print("4. Verify Redis authentication")
        print("5. Try a different Redis provider if issues persist") 