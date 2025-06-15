#!/usr/bin/env python3
"""
Simple Redis Connection Test for Redis Cloud

This script tests Redis connection with single database (db 0 only).
"""

# import redis  # Redis disabled
import os

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
        print("❌ No password provided!")
        return False
    
    try:
        print("\n🔄 Connecting to Redis...")
        
        # Create Redis client for database 0
        # r = redis.Redis(  # Redis disabled
        #     host=redis_host,
        #     port=redis_port,
        #     password=redis_password,
        #     db=0,  # Only use database 0
        #     decode_responses=True,
        #     socket_timeout=10,
        #     socket_connect_timeout=10
        # )
        
        # Test connection
        # r.ping()
        print("✅ Redis connection disabled")
        
        # Test basic operations
        print("\n🔄 Testing Redis operations...")
        
        # ... rest of Redis test code commented out ...
        
        print("\n🎉 Redis testing is disabled!")
        
        # Generate the correct Redis URL
        # redis_url = f"redis://:{redis_password}@{redis_host}:{redis_port}/0"
        
        print(f"\n🔗 Redis URL disabled")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis error: {e}")
        print("   Redis functionality has been disabled")
        return False

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
    if test_redis_simple():
        print("\n✅ Redis testing completed (disabled)")
    else:
        print("\n❌ Redis testing failed")
        print("1. Check your Redis Cloud password")
        print("2. Ensure your Redis instance is running")
        print("3. Check network connectivity")
        print("4. Contact Redis Cloud support if issues persist") 