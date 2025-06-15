# Cache Service - Redis and Flask-Caching integration with fallback
# This module provides caching functionality with Redis backend and fallback to simple cache
import os
import logging
from typing import Any, Optional, Dict
# import redis  # Redis disabled
from flask import Flask
from flask_caching import Cache
from urllib.parse import urlparse
import traceback
from functools import wraps
import json
import time
# import redis  # Redis disabled

# Configure logging
logger = logging.getLogger(__name__)

# Initialize cache
cache = Cache()

# Simple in-memory cache as fallback
class SimpleCache:
    """Simple in-memory cache implementation"""
    def __init__(self):
        self._cache = {}
        self._expiry = {}
    
    def get(self, key):
        """Get value from cache"""
        if key in self._cache:
            if key in self._expiry and time.time() > self._expiry[key]:
                # Expired
                del self._cache[key]
                del self._expiry[key]
                return None
            return self._cache[key]
        return None
    
    def set(self, key, value, timeout=300):
        """Set value in cache with timeout"""
        self._cache[key] = value
        if timeout:
            self._expiry[key] = time.time() + timeout
    
    def delete(self, key):
        """Delete key from cache"""
        if key in self._cache:
            del self._cache[key]
        if key in self._expiry:
            del self._expiry[key]
    
    def clear(self):
        """Clear all cache"""
        self._cache.clear()
        self._expiry.clear()

# Initialize simple cache as fallback
simple_cache = SimpleCache()

class CacheService:
    """Centralized cache service with Redis backend and simple cache fallback"""
    
    _cache_instance = None
    _initialized = False
    # _redis_available = False  # Redis disabled
    
    @classmethod
    def init_app(cls, app: Flask):
        """Initialize cache with the Flask app"""
        if cls._initialized:
            return cls._cache_instance
            
        logger = logging.getLogger(__name__)
        
        try:
            # Try to initialize Redis cache
            # cache_type = app.config.get('CACHE_TYPE', 'redis')
            cache_type = app.config.get('CACHE_TYPE', 'simple')  # Default to simple cache instead of Redis
            
            # Test Redis connection
            # redis_url = app.config.get('CACHE_REDIS_URL')
            # if redis_url:
            #     # Parse Redis URL and test connection
            #     parsed_url = urlparse(redis_url)
            #     r = redis.Redis(
            #         host=parsed_url.hostname,
            #         port=parsed_url.port,
            #         password=parsed_url.password,
            #         db=int(parsed_url.path[1:]) if parsed_url.path else 0,
            #         decode_responses=True
            #     )
            #     r.ping()  # Test connection
            #     CacheService._redis_available = True
            #     
            #     logger.info("Redis cache initialized successfully")
            # else:
            #     raise Exception("No Redis URL configured")
        except Exception as e:
            # logger.warning(f"Redis cache initialization failed: {str(e)}")
            logger.info("Redis cache disabled - using simple cache")
            app.config['CACHE_TYPE'] = 'simple'
            # CacheService._redis_available = False
            
        # Initialize Flask-Caching
        cls._cache_instance = Cache()
        cls._cache_instance.init_app(app)
        cls._initialized = True
        
        return cls._cache_instance
    
    # @classmethod
    # def is_redis_available(cls):
    #     """Check if Redis is available"""
    #     return CacheService._redis_available

    @staticmethod
    def get_cache():
        """Get the active cache instance"""
        return CacheService._cache_instance or simple_cache
    
    @staticmethod
    def get_parking_lots_cache_key():
        """Get cache key for parking lots"""
        return "parking_lots:all"
    
    @staticmethod
    def get_parking_lot_cache_key(lot_id):
        """Get cache key for specific parking lot"""
        return f"parking_lot:{lot_id}"
    
    @staticmethod
    def get_user_reservations_cache_key(user_id):
        """Get cache key for user reservations"""
        return f"user_reservations:{user_id}"
    
    @staticmethod
    def get_parking_spots_cache_key(lot_id):
        """Get cache key for parking spots of a lot"""
        return f"parking_spots:lot:{lot_id}"
    
    @staticmethod
    def get_dashboard_stats_cache_key(user_id=None):
        """Get cache key for dashboard statistics"""
        if user_id:
            return f"dashboard_stats:user:{user_id}"
        return "dashboard_stats:admin"
    
    @staticmethod
    def invalidate_parking_lot_cache(lot_id=None):
        """Invalidate parking lot related cache"""
        try:
            active_cache = CacheService.get_cache()
            
            # Clear all parking lots cache
            active_cache.delete(CacheService.get_parking_lots_cache_key())
            
            if lot_id:
                # Clear specific parking lot cache
                active_cache.delete(CacheService.get_parking_lot_cache_key(lot_id))
                active_cache.delete(CacheService.get_parking_spots_cache_key(lot_id))
            
            # Clear dashboard stats cache
            active_cache.delete(CacheService.get_dashboard_stats_cache_key())
            
            logger.info(f"Parking lot cache invalidated for lot_id: {lot_id}")
        except Exception as e:
            logger.error(f"Failed to invalidate parking lot cache: {str(e)}")
    
    @staticmethod
    def invalidate_user_cache(user_id):
        """Invalidate user-specific cache"""
        try:
            active_cache = CacheService.get_cache()
            active_cache.delete(CacheService.get_user_reservations_cache_key(user_id))
            active_cache.delete(CacheService.get_dashboard_stats_cache_key(user_id))
            logger.info(f"User cache invalidated for user_id: {user_id}")
        except Exception as e:
            logger.error(f"Failed to invalidate user cache: {str(e)}")
    
    @staticmethod
    def cache_parking_lots(data, timeout=300):
        """Cache parking lots data"""
        try:
            active_cache = CacheService.get_cache()
            active_cache.set(CacheService.get_parking_lots_cache_key(), data, timeout=timeout)
            logger.debug("Parking lots data cached")
        except Exception as e:
            logger.error(f"Failed to cache parking lots: {str(e)}")
    
    @staticmethod
    def get_cached_parking_lots():
        """Get cached parking lots data"""
        try:
            active_cache = CacheService.get_cache()
            return active_cache.get(CacheService.get_parking_lots_cache_key())
        except Exception as e:
            logger.error(f"Failed to get cached parking lots: {str(e)}")
            return None
    
    @staticmethod
    def cache_parking_lot(lot_id, data, timeout=300):
        """Cache specific parking lot data"""
        try:
            active_cache = CacheService.get_cache()
            active_cache.set(CacheService.get_parking_lot_cache_key(lot_id), data, timeout=timeout)
            logger.debug(f"Parking lot {lot_id} data cached")
        except Exception as e:
            logger.error(f"Failed to cache parking lot {lot_id}: {str(e)}")
    
    @staticmethod
    def get_cached_parking_lot(lot_id):
        """Get cached parking lot data"""
        try:
            active_cache = CacheService.get_cache()
            return active_cache.get(CacheService.get_parking_lot_cache_key(lot_id))
        except Exception as e:
            logger.error(f"Failed to get cached parking lot {lot_id}: {str(e)}")
            return None

    @classmethod
    def get_cache_info(cls) -> Dict[str, Any]:
        """Get cache information and statistics"""
        if not cls._initialized:
            return {'error': 'Cache not initialized'}
            
        try:
            stats = {
                'initialized': cls._initialized,
                'type': cls._cache_instance.config.get('CACHE_TYPE', 'unknown'),
                'timeout': cls._cache_instance.config.get('CACHE_DEFAULT_TIMEOUT', 300),
            }
            
            # cache_type = "Redis" if CacheService.is_redis_available() else "Simple"
            cache_type = "Simple"  # Redis disabled
            stats['cache_type'] = cache_type
            stats['status'] = 'active'
            # stats['redis_available'] = CacheService.is_redis_available()
            stats['redis_available'] = False  # Redis disabled
            
            # Get cache-specific information
            # if CacheService.is_redis_available():
            #     # Get Redis-specific stats if available
            #     try:
            #         redis_url = CacheService._cache_instance.config.get('CACHE_REDIS_URL')
            #         if redis_url:
            #             parsed_url = urlparse(redis_url)
            #             r = redis.Redis(
            #                 host=parsed_url.hostname,
            #                 port=parsed_url.port,
            #                 password=parsed_url.password,
            #                 db=int(parsed_url.path[1:]) if parsed_url.path else 0
            #             )
            #             stats['redis_info'] = {
            #                 'connected_clients': r.info().get('connected_clients', 0),
            #                 'used_memory_human': r.info().get('used_memory_human', '0B'),
            #                 'keyspace_hits': r.info().get('keyspace_hits', 0),
            #                 'keyspace_misses': r.info().get('keyspace_misses', 0)
            #             }
            #     except Exception as e:
            #         stats['redis_error'] = str(e)
            
            return stats
            
        except Exception as e:
            return {'error': f'Failed to get cache info: {str(e)}'}

def cached_response(timeout=300, key_func=None):
    """
    Decorator for caching API responses
    
    Args:
        timeout (int): Cache timeout in seconds (default: 5 minutes)
        key_func (function): Function to generate cache key
    
    Usage:
        @cached_response(timeout=600, key_func=lambda: f"api:parking_lots")
        def get_parking_lots():
            # Your API logic here
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                active_cache = CacheService.get_cache()
                
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    # Default cache key based on function name and arguments
                    cache_key = f"{f.__name__}:{hash(str(args) + str(kwargs))}"
                
                # Try to get cached response
                cached_result = active_cache.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for key: {cache_key}")
                    return cached_result
                
                # Execute function and cache result
                result = f(*args, **kwargs)
                active_cache.set(cache_key, result, timeout=timeout)
                logger.debug(f"Cache set for key: {cache_key}")
                
                return result
                
            except Exception as e:
                logger.error(f"Cache decorator error: {str(e)}")
                # If caching fails, still execute the function
                return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def cache_key_with_user(user_id):
    """Generate cache key function with user ID"""
    def key_generator(*args, **kwargs):
        return f"user:{user_id}:{args}:{kwargs}"
    return key_generator

def cache_key_with_params(**params):
    """Generate cache key function with custom parameters"""
    def key_generator(*args, **kwargs):
        param_str = ':'.join([f"{k}:{v}" for k, v in params.items()])
        return f"params:{param_str}:{args}:{kwargs}"
    return key_generator

def monitor_performance(func_name=None):
    """Decorator to monitor function performance"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            try:
                result = f(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(f"Function {func_name or f.__name__} executed in {execution_time:.3f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"Function {func_name or f.__name__} failed after {execution_time:.3f}s: {str(e)}")
                raise
        return decorated_function
    return decorator 