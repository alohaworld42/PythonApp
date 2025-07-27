"""
Caching utilities for improved application performance.
"""

import json
import time
from functools import wraps
from flask import current_app
from typing import Any, Optional, Callable
import hashlib

class MemoryCache:
    """Simple in-memory cache implementation."""
    
    def __init__(self):
        self._cache = {}
        self._timestamps = {}
        self._default_ttl = 300  # 5 minutes default TTL
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key not in self._cache:
            return None
        
        # Check if expired
        if key in self._timestamps:
            if time.time() - self._timestamps[key]['created'] > self._timestamps[key]['ttl']:
                self.delete(key)
                return None
        
        return self._cache[key]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL."""
        self._cache[key] = value
        self._timestamps[key] = {
            'created': time.time(),
            'ttl': ttl or self._default_ttl
        }
    
    def delete(self, key: str) -> None:
        """Delete value from cache."""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._timestamps.clear()
    
    def size(self) -> int:
        """Get current cache size."""
        return len(self._cache)
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count of removed items."""
        current_time = time.time()
        expired_keys = []
        
        for key, timestamp_info in self._timestamps.items():
            if current_time - timestamp_info['created'] > timestamp_info['ttl']:
                expired_keys.append(key)
        
        for key in expired_keys:
            self.delete(key)
        
        return len(expired_keys)

# Global cache instance
cache = MemoryCache()

def cache_key(*args, **kwargs) -> str:
    """Generate a cache key from function arguments."""
    # Create a string representation of all arguments
    key_data = {
        'args': args,
        'kwargs': sorted(kwargs.items())
    }
    key_string = json.dumps(key_data, sort_keys=True, default=str)
    
    # Create a hash of the key string for consistent length
    return hashlib.md5(key_string.encode()).hexdigest()

def cached(ttl: int = 300, key_prefix: str = ''):
    """
    Decorator to cache function results.
    
    Args:
        ttl: Time to live in seconds (default: 5 minutes)
        key_prefix: Prefix for cache key
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            func_key = f"{key_prefix}{func.__name__}_{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = cache.get(func_key)
            if cached_result is not None:
                current_app.logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(func_key, result, ttl)
            current_app.logger.debug(f"Cache miss for {func.__name__}, result cached")
            
            return result
        return wrapper
    return decorator

class AnalyticsCache:
    """Specialized cache for analytics data."""
    
    @staticmethod
    @cached(ttl=600, key_prefix='analytics_')  # 10 minutes TTL
    def get_monthly_spending(user_id: int, year: Optional[int] = None, month: Optional[int] = None):
        """Cached version of monthly spending analytics."""
        from app.services.analytics_service import AnalyticsService
        return AnalyticsService.get_monthly_spending(user_id, year, month)
    
    @staticmethod
    @cached(ttl=900, key_prefix='analytics_')  # 15 minutes TTL
    def get_category_analysis(user_id: int, start_date=None, end_date=None):
        """Cached version of category spending analysis."""
        from app.services.analytics_service import AnalyticsService
        return AnalyticsService.get_category_spending_analysis(user_id, start_date, end_date)
    
    @staticmethod
    @cached(ttl=900, key_prefix='analytics_')  # 15 minutes TTL
    def get_store_analysis(user_id: int, start_date=None, end_date=None):
        """Cached version of store spending analysis."""
        from app.services.analytics_service import AnalyticsService
        return AnalyticsService.get_store_spending_analysis(user_id, start_date, end_date)
    
    @staticmethod
    @cached(ttl=1800, key_prefix='analytics_')  # 30 minutes TTL
    def get_spending_trends(user_id: int, period_months: int = 12):
        """Cached version of spending trends."""
        from app.services.analytics_service import AnalyticsService
        return AnalyticsService.get_spending_trends(user_id, period_months)

class SocialCache:
    """Specialized cache for social features."""
    
    @staticmethod
    @cached(ttl=180, key_prefix='social_')  # 3 minutes TTL
    def get_friends_feed(user_id: int, limit: Optional[int] = None):
        """Cached version of friends feed."""
        from app.services.purchase_sharing_service import PurchaseSharingService
        return PurchaseSharingService.get_friends_shared_purchases(user_id, limit)
    
    @staticmethod
    @cached(ttl=300, key_prefix='social_')  # 5 minutes TTL
    def get_user_shared_purchases(user_id: int, limit: Optional[int] = None):
        """Cached version of user's shared purchases."""
        from app.services.purchase_sharing_service import PurchaseSharingService
        return PurchaseSharingService.get_user_shared_purchases(user_id, limit)
    
    @staticmethod
    @cached(ttl=600, key_prefix='social_')  # 10 minutes TTL
    def get_sharing_stats(user_id: int):
        """Cached version of sharing statistics."""
        from app.services.purchase_sharing_service import PurchaseSharingService
        return PurchaseSharingService.get_sharing_stats(user_id)

def invalidate_user_cache(user_id: int):
    """Invalidate all cache entries for a specific user."""
    # This is a simple implementation - in a real system you might want
    # to use cache tags or a more sophisticated invalidation strategy
    keys_to_remove = []
    
    for key in cache._cache.keys():
        if f"_{user_id}_" in key or key.endswith(f"_{user_id}"):
            keys_to_remove.append(key)
    
    for key in keys_to_remove:
        cache.delete(key)
    
    current_app.logger.info(f"Invalidated {len(keys_to_remove)} cache entries for user {user_id}")

def invalidate_analytics_cache(user_id: int):
    """Invalidate analytics cache for a specific user."""
    keys_to_remove = []
    
    for key in cache._cache.keys():
        if key.startswith('analytics_') and f"_{user_id}_" in key:
            keys_to_remove.append(key)
    
    for key in keys_to_remove:
        cache.delete(key)
    
    current_app.logger.info(f"Invalidated {len(keys_to_remove)} analytics cache entries for user {user_id}")

def invalidate_social_cache(user_id: int):
    """Invalidate social cache for a specific user."""
    keys_to_remove = []
    
    for key in cache._cache.keys():
        if key.startswith('social_') and f"_{user_id}_" in key:
            keys_to_remove.append(key)
    
    for key in keys_to_remove:
        cache.delete(key)
    
    current_app.logger.info(f"Invalidated {len(keys_to_remove)} social cache entries for user {user_id}")

class CacheManager:
    """Manage cache operations and maintenance."""
    
    @staticmethod
    def get_cache_stats():
        """Get cache statistics."""
        return {
            'total_entries': cache.size(),
            'memory_usage_estimate': len(str(cache._cache)),  # Rough estimate
            'expired_entries_cleaned': cache.cleanup_expired()
        }
    
    @staticmethod
    def warm_cache_for_user(user_id: int):
        """Pre-populate cache with commonly accessed data for a user."""
        try:
            # Warm up analytics cache
            AnalyticsCache.get_monthly_spending(user_id)
            AnalyticsCache.get_category_analysis(user_id)
            AnalyticsCache.get_store_analysis(user_id)
            AnalyticsCache.get_spending_trends(user_id)
            
            # Warm up social cache
            SocialCache.get_friends_feed(user_id, 20)
            SocialCache.get_user_shared_purchases(user_id, 20)
            SocialCache.get_sharing_stats(user_id)
            
            current_app.logger.info(f"Cache warmed up for user {user_id}")
            
        except Exception as e:
            current_app.logger.error(f"Error warming cache for user {user_id}: {str(e)}")
    
    @staticmethod
    def schedule_cache_cleanup():
        """Schedule periodic cache cleanup."""
        # This would typically be called by a background task
        expired_count = cache.cleanup_expired()
        current_app.logger.info(f"Cache cleanup completed, removed {expired_count} expired entries")
        
        return expired_count

# Context processor to add cache stats to templates (for debugging)
def cache_stats_context_processor():
    """Add cache statistics to template context."""
    if current_app.debug:
        return {
            'cache_stats': CacheManager.get_cache_stats()
        }
    return {}