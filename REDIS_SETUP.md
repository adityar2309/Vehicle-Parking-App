# 🔗 Redis Cloud Setup Guide

This guide will help you set up Redis Cloud for your Vehicle Parking App to enable Redis caching and Celery background jobs.

## 📋 Option 1: Redis Cloud (Recommended)

### Step 1: Create Redis Cloud Account

1. **Go to Redis Cloud**: https://redis.com/try-free/
2. **Sign up** for a free account
3. **Verify your email**

### Step 2: Create a Free Database

1. **After login**, click "New Subscription"
2. **Choose Plan**: Select "Fixed" plan (Free tier)
3. **Cloud Provider**: Choose "AWS" 
4. **Region**: Select closest to your App Engine region (e.g., us-east-1)
5. **Subscription Name**: `parking-app-redis`
6. **Click "Create Subscription"**

### Step 3: Create Database

1. **In your subscription**, click "New Database"
2. **Database Name**: `parking-app-cache`
3. **Keep default settings** (30MB memory, no persistence needed for cache)
4. **Click "Create Database"**

### Step 4: Get Connection Details

1. **Click on your database** to open details
2. **Copy the following**:
   - **Endpoint**: `redis-xxxxx.xxx.redis-cloud.com`
   - **Port**: `xxxxx`
   - **Password**: Click "Show" to reveal

### Step 5: Format Your Redis URL

Your Redis URL should look like:
```
redis://:PASSWORD@ENDPOINT:PORT/0
```

Example:
```
redis://:mypassword123@redis-12345.c1.us-east-1-1.ec2.redis-cloud.com:12345/0
```

## 📋 Option 2: Upstash Redis (Alternative)

### Step 1: Create Upstash Account

1. **Go to Upstash**: https://upstash.com/
2. **Sign up** with GitHub or email
3. **Create a new Redis database**

### Step 2: Configure Database

1. **Name**: `parking-app-redis`
2. **Region**: Choose closest to your deployment
3. **Type**: Regional (free tier)
4. **Click "Create"**

### Step 3: Get Connection String

1. **In database dashboard**, find "Connect your database"
2. **Copy the Redis URL** (starts with `redis://`)

## 🚀 Update Your App Engine Configuration

Once you have your Redis URL, update your backend configuration:

### Step 1: Update app.yaml

Replace the Redis URLs in your `backend/app.yaml`:

```yaml
env_variables:
  # Replace with your actual Redis Cloud URL
  REDIS_URL: "redis://:your_password@your-redis-endpoint:port/0"
  CACHE_REDIS_URL: "redis://:your_password@your-redis-endpoint:port/0"
  CELERY_BROKER_URL: "redis://:your_password@your-redis-endpoint:port/1"
  CELERY_RESULT_BACKEND: "redis://:your_password@your-redis-endpoint:port/1"
```

### Step 2: Test Redis Connection

Use this script to test your Redis connection:

```python
import redis
from urllib.parse import urlparse

redis_url = "your_redis_url_here"
parsed_url = urlparse(redis_url)

r = redis.Redis(
    host=parsed_url.hostname,
    port=parsed_url.port,
    password=parsed_url.password,
    decode_responses=True
)

try:
    r.ping()
    print("✅ Redis connection successful!")
    
    # Test set/get
    r.set("test_key", "test_value")
    value = r.get("test_key")
    print(f"✅ Test value: {value}")
    
except Exception as e:
    print(f"❌ Redis connection failed: {e}")
```

## 🔄 Deploy Updated Backend

After setting up Redis:

1. **Update your app.yaml** with the real Redis URLs
2. **Commit and push** changes to GitHub
3. **Redeploy to App Engine**:
   ```bash
   cd backend
   gcloud app deploy
   ```

## ✅ Verify Redis Integration

After deployment, check:

1. **Health Check**: Visit `https://your-app.appspot.com/health`
   - Should show `"cache": "redis"`
   - Should show `"celery": "active"`

2. **Cache Info**: Visit `https://your-app.appspot.com/admin/cache/info`
   - Should show Redis statistics

3. **Job Status**: Visit `https://your-app.appspot.com/admin/jobs`
   - Should show `"celery_available": true`

## 🎯 Benefits of Redis + Celery

With Redis and Celery enabled, your app will have:

- ✅ **Fast Redis Caching** - Sub-millisecond data access
- ✅ **Async Background Jobs** - CSV exports, email sending, reports
- ✅ **Better Performance** - Cached API responses
- ✅ **Scalability** - Background task processing
- ✅ **Reliability** - Job persistence and retry mechanisms

## 🔧 Troubleshooting

### Common Issues:

1. **Connection Timeout**:
   - Check Redis URL format
   - Verify firewall/security groups

2. **Authentication Failed**:
   - Double-check password
   - Ensure URL encoding if special characters

3. **Celery Not Starting**:
   - Check Redis connectivity
   - Verify broker URL format

4. **Cache Not Working**:
   - Check logs for Redis connection errors
   - Verify cache configuration

### Debug Commands:

```bash
# Check app logs
gcloud app logs tail -s default

# Test Redis connection locally
python test_redis.py

# View cache statistics
curl https://your-app.appspot.com/admin/cache/info
```

## 📞 Support

If you need help:
- Redis Cloud: https://redis.com/support/
- Upstash: https://docs.upstash.com/
- App Engine: https://cloud.google.com/appengine/docs/ 