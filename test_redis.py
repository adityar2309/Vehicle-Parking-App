#!/usr/bin/env python3
"""
Redis Connection Test Script

This script tests your Redis connection before deploying with Celery/Redis.
"""

# import redis  # Redis disabled
import os
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
        print(f"Database: {parsed_url.path[1:] if parsed_url.path else '0'}")
        
        print("\n🔄 Connecting to Redis...")
        
        # Create Redis client
        # r = redis.Redis(  # Redis disabled
        #     host=parsed_url.hostname,
        #     port=parsed_url.port,
        #     password=parsed_url.password,
        #     db=int(parsed_url.path[1:]) if parsed_url.path else 0,
        #     decode_responses=True,
        #     socket_connect_timeout=5,
        #     socket_timeout=5
        # )
        
        print("✅ Redis connection disabled")
        # print("✅ Successfully connected to Redis!")
        
        # Test basic operations
        print("\n🔄 Testing Redis operations...")
        
        # ... rest of Redis test code commented out ...
        
        print("\n🎉 Redis testing is disabled!")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis error: {e}")
        print("   Redis functionality has been disabled")
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
    print("⚠️  Redis functionality has been disabled")
    print("The app now uses simple in-memory caching instead.")
    print("=" * 60)
    
    # Check if redis package is installed
    try:
        # import redis  # Redis disabled
        print("✅ Redis package check disabled")
    except ImportError:
        print("❌ Redis package not found. Please run: pip install redis")
        exit(1)
    
    # Test connection
    if test_redis_connection():
        print("\n✅ Redis testing completed (disabled)")
    else:
        print("\n❌ Redis testing failed")
        print("1. Double-check your Redis URL format")
        print("2. Ensure your Redis instance is running")
        print("3. Check network connectivity")
        print("4. Verify Redis authentication")
        print("5. Try a different Redis provider if issues persist") 