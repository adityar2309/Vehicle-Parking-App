# MongoDB Migration - Vehicle Parking App

## Overview

This document outlines the migration from Redis/PostgreSQL to MongoDB for the Vehicle Parking App backend.

## Changes Made

### 1. Database Migration
- **From**: PostgreSQL with SQLAlchemy ORM
- **To**: MongoDB with MongoEngine ODM
- **Impact**: All database models and queries updated

### 2. Caching System
- **From**: Redis-based caching with Flask-Caching
- **To**: Simple in-memory caching
- **Impact**: Reduced external dependencies, simplified deployment

### 3. Background Jobs
- **From**: Celery with Redis broker (async)
- **To**: Synchronous job execution
- **Impact**: Simplified architecture, no separate worker process needed

### 4. Dependencies Updated

#### Removed Dependencies
```
Flask-Caching==2.1.0  # Redis dependency
redis==5.0.1          # Redis client
celery==5.3.4         # Background job processing
```

#### Added Dependencies
```
pymongo==4.6.0        # MongoDB driver
flask-pymongo==2.3.0  # Flask-MongoDB integration
mongoengine==0.27.0   # MongoDB ODM
```

### 5. Configuration Changes

#### MongoDB Configuration (config.py)
```python
# MongoDB configuration
MONGODB_SETTINGS = {
    'host': os.environ.get('MONGODB_URI') or 'mongodb://localhost:27017/parking_app',
    'connect': False
}
```

#### Commented Out Redis Configuration
```python
# Redis/Celery configurations commented out
# CACHE_TYPE = 'redis'
# CACHE_REDIS_URL = 'redis://localhost:6379/0'
# CELERY_BROKER_URL = 'redis://localhost:6379/1'
```

### 6. Model Changes (models.py)

#### Before (SQLAlchemy)
```python
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
```

#### After (MongoEngine)
```python
from mongoengine import Document, StringField, IntField, DateTimeField

class User(Document):
    meta = {'collection': 'users'}
    username = StringField(max_length=80, unique=True, required=True)
```

### 7. Query Changes

#### Before (SQLAlchemy)
```python
users = User.query.filter_by(role='user').all()
user = User.query.get(user_id)
```

#### After (MongoDB)
```python
users = User.objects(role='user')
user = User.objects(id=user_id).first()
```

### 8. Cache Service Changes

#### Before (Redis)
```python
from flask_caching import Cache
cache = Cache()
cache.init_app(app)
```

#### After (Simple Memory)
```python
class SimpleCache:
    def __init__(self):
        self._cache = {}
        self._expiry = {}
```

### 9. Background Jobs Changes

#### Before (Celery)
```python
@celery.task
def daily_reminder_job():
    # Async execution
    pass

# Usage
daily_reminder_job.delay()
```

#### After (Synchronous)
```python
def daily_reminder_job():
    # Direct execution
    pass

# Usage
daily_reminder_job()
```

## Setup Instructions

### 1. Install MongoDB
```bash
# Ubuntu/Debian
sudo apt-get install mongodb

# macOS
brew install mongodb-community

# Windows
# Download from https://www.mongodb.com/try/download/community
```

### 2. Start MongoDB
```bash
mongod
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp env_example.txt .env
# Edit .env with your MongoDB URI
```

### 5. Run Application
```bash
python app.py
```

## Benefits of Migration

### 1. Simplified Architecture
- No Redis server required
- No separate Celery worker process
- Single database system (MongoDB)

### 2. Reduced Infrastructure
- One less service to manage (Redis)
- Simplified deployment
- Lower resource requirements

### 3. Development Benefits
- Faster local development setup
- No need to manage multiple services
- Simplified testing

### 4. MongoDB Advantages
- Flexible schema
- JSON-like documents
- Built-in replication and sharding
- Better handling of complex data structures

## Trade-offs

### 1. Caching Performance
- **Before**: Redis (persistent, distributed)
- **After**: In-memory (process-local, non-persistent)
- **Impact**: Cache lost on restart, not shared across instances

### 2. Background Jobs
- **Before**: Async processing, scalable
- **After**: Synchronous, blocking
- **Impact**: Longer response times for export operations

### 3. Scalability
- **Before**: Horizontal scaling with Redis cluster
- **After**: Vertical scaling limitations
- **Impact**: May need different approach for high-traffic scenarios

## Migration Checklist

- [x] Update dependencies in requirements.txt
- [x] Replace SQLAlchemy models with MongoEngine
- [x] Update all database queries
- [x] Replace Redis caching with simple cache
- [x] Convert Celery tasks to synchronous functions
- [x] Update configuration files
- [x] Update all route handlers
- [x] Update authentication system
- [x] Test all functionality
- [x] Update documentation

## Testing

### 1. Database Operations
- [x] User registration/login
- [x] Parking lot CRUD operations
- [x] Reservation management
- [x] Admin dashboard

### 2. Background Jobs
- [x] Daily reminder execution
- [x] Monthly report generation
- [x] CSV export functionality
- [x] File cleanup operations

### 3. Caching
- [x] Cache hit/miss functionality
- [x] Cache invalidation
- [x] Performance monitoring

## Production Considerations

### 1. MongoDB Setup
- Use MongoDB Atlas for managed hosting
- Configure proper authentication
- Set up backups and monitoring

### 2. Caching Strategy
- Consider Redis for production if needed
- Implement distributed caching for multiple instances
- Monitor cache performance

### 3. Background Jobs
- Consider job queues for production (RQ, Celery)
- Implement proper error handling
- Add job monitoring and alerting

### 4. Performance
- Add database indexes
- Monitor query performance
- Implement connection pooling

## Rollback Plan

If needed, rollback involves:
1. Restore original requirements.txt
2. Restore SQLAlchemy models
3. Restore Redis configuration
4. Restore Celery tasks
5. Migrate data from MongoDB to PostgreSQL

## Support

For issues or questions:
1. Check MongoDB documentation
2. Review MongoEngine documentation
3. Test with sample data
4. Monitor application logs 