# Cache Service - Redis functionality commented out, using simple in-memory cache
# from flask_caching import Cache  # Commented out - Redis dependency
from functools import wraps
import json
import logging
import time

# Configure logging
logger = logging.getLogger(__name__)

# Initialize cache (commented out - Redis dependency)
# cache = Cache()

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

# Initialize simple cache
cache = SimpleCache()

class CacheService:
    """Service class for handling caching operations"""
    
    @staticmethod
    def init_cache(app):
        """Initialize cache with Flask app"""
        # cache.init_app(app)  # Commented out - Redis dependency
        logger.info("Cache service initialized (using simple in-memory cache)")
    
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
            # Clear all parking lots cache
            cache.delete(CacheService.get_parking_lots_cache_key())
            
            if lot_id:
                # Clear specific parking lot cache
                cache.delete(CacheService.get_parking_lot_cache_key(lot_id))
                cache.delete(CacheService.get_parking_spots_cache_key(lot_id))
            
            # Clear dashboard stats cache
            cache.delete(CacheService.get_dashboard_stats_cache_key())
            
            logger.info(f"Parking lot cache invalidated for lot_id: {lot_id}")
        except Exception as e:
            logger.error(f"Failed to invalidate parking lot cache: {str(e)}")
    
    @staticmethod
    def invalidate_user_cache(user_id):
        """Invalidate user-specific cache"""
        try:
            cache.delete(CacheService.get_user_reservations_cache_key(user_id))
            cache.delete(CacheService.get_dashboard_stats_cache_key(user_id))
            logger.info(f"User cache invalidated for user_id: {user_id}")
        except Exception as e:
            logger.error(f"Failed to invalidate user cache: {str(e)}")
    
    @staticmethod
    def cache_parking_lots(data, timeout=300):
        """Cache parking lots data"""
        try:
            cache.set(CacheService.get_parking_lots_cache_key(), data, timeout=timeout)
            logger.debug("Parking lots data cached")
        except Exception as e:
            logger.error(f"Failed to cache parking lots: {str(e)}")
    
    @staticmethod
    def get_cached_parking_lots():
        """Get cached parking lots data"""
        try:
            return cache.get(CacheService.get_parking_lots_cache_key())
        except Exception as e:
            logger.error(f"Failed to get cached parking lots: {str(e)}")
            return None
    
    @staticmethod
    def cache_parking_lot(lot_id, data, timeout=300):
        """Cache specific parking lot data"""
        try:
            cache.set(CacheService.get_parking_lot_cache_key(lot_id), data, timeout=timeout)
            logger.debug(f"Parking lot {lot_id} data cached")
        except Exception as e:
            logger.error(f"Failed to cache parking lot {lot_id}: {str(e)}")
    
    @staticmethod
    def get_cached_parking_lot(lot_id):
        """Get cached parking lot data"""
        try:
            return cache.get(CacheService.get_parking_lot_cache_key(lot_id))
        except Exception as e:
            logger.error(f"Failed to get cached parking lot {lot_id}: {str(e)}")
            return None

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
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    # Default cache key based on function name and arguments
                    cache_key = f"{f.__name__}:{hash(str(args) + str(kwargs))}"
                
                # Try to get cached response
                cached_result = cache.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for key: {cache_key}")
                    return cached_result
                
                # Execute function and cache result
                result = f(*args, **kwargs)
                cache.set(cache_key, result, timeout=timeout)
                logger.debug(f"Cache set for key: {cache_key}")
                
                return result
                
            except Exception as e:
                logger.error(f"Cache decorator error: {str(e)}")
                # If caching fails, still execute the function
                return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def cache_key_with_user(user_id):
    """Helper function to generate cache key with user ID"""
    def key_generator(*args, **kwargs):
        return f"user:{user_id}:args:{hash(str(args) + str(kwargs))}"
    return key_generator

def cache_key_with_params(**params):
    """Helper function to generate cache key with custom parameters"""
    def key_generator(*args, **kwargs):
        param_str = ":".join([f"{k}:{v}" for k, v in params.items()])
        return f"custom:{param_str}:args:{hash(str(args) + str(kwargs))}"
    return key_generator

class CacheStats:
    """Class for tracking cache statistics"""
    
    @staticmethod
    def get_cache_info():
        """Get cache information and statistics"""
        try:
            # Simple cache info
            return {
                "cache_type": "simple_memory",
                "status": "active",
                "note": "Using simple in-memory cache (Redis disabled)"
            }
        except Exception as e:
            logger.error(f"Failed to get cache info: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def clear_all_cache():
        """Clear all cache (use with caution)"""
        try:
            cache.clear()
            logger.info("All cache cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {str(e)}")
            return False

# Performance monitoring decorator
def monitor_performance(func_name=None):
    """Decorator to monitor function performance"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            import time
            start_time = time.time()
            
            try:
                result = f(*args, **kwargs)
                execution_time = time.time() - start_time
                
                logger.info(f"Performance: {func_name or f.__name__} executed in {execution_time:.3f}s")
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"Performance: {func_name or f.__name__} failed in {execution_time:.3f}s - {str(e)}")
                raise
        
        return decorated_function
    return decorator

# Legacy Redis cache code (commented out)
"""
from flask_caching import Cache
# ... all Redis-related cache code commented out ...
""" 