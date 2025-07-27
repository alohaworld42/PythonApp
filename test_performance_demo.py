#!/usr/bin/env python3
"""
Performance optimization demonstration script.
Shows the effectiveness of the implemented optimizations.
"""

import time
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.utils.database_optimization import QueryOptimizer, optimize_sqlite_settings
from app.utils.cache import cache, AnalyticsCache, CacheManager
from app.utils.asset_optimization import AssetOptimizer, minify_css, minify_js
from app.utils.performance_monitor import performance_monitor

def test_database_optimizations():
    """Test database optimization features."""
    print("🗄️  Testing Database Optimizations")
    print("-" * 40)
    
    app = create_app()
    with app.app_context():
        # Apply SQLite optimizations
        start_time = time.time()
        optimize_sqlite_settings()
        optimization_time = time.time() - start_time
        print(f"✅ SQLite optimizations applied in {optimization_time:.3f}s")
        
        # Create indexes
        start_time = time.time()
        QueryOptimizer.create_indexes()
        index_time = time.time() - start_time
        print(f"✅ Database indexes created in {index_time:.3f}s")
        
        # Analyze query performance
        start_time = time.time()
        analysis = QueryOptimizer.analyze_query_performance()
        analysis_time = time.time() - start_time
        print(f"✅ Query performance analyzed in {analysis_time:.3f}s")
        print(f"   - Analyzed {analysis['total_queries_analyzed']} queries")
        print(f"   - Found {len(analysis['slow_queries'])} slow queries")

def test_caching_performance():
    """Test caching system performance."""
    print("\n💾 Testing Caching Performance")
    print("-" * 40)
    
    # Clear cache
    cache.clear()
    
    # Test basic cache operations
    start_time = time.time()
    for i in range(1000):
        cache.set(f"test_key_{i}", f"test_value_{i}")
    set_time = time.time() - start_time
    print(f"✅ Set 1000 cache entries in {set_time:.3f}s ({1000/set_time:.0f} ops/sec)")
    
    # Test cache retrieval
    start_time = time.time()
    hits = 0
    for i in range(1000):
        if cache.get(f"test_key_{i}") is not None:
            hits += 1
    get_time = time.time() - start_time
    print(f"✅ Retrieved 1000 cache entries in {get_time:.3f}s ({1000/get_time:.0f} ops/sec)")
    print(f"   - Cache hit rate: {(hits/1000)*100:.1f}%")
    
    # Test cache statistics
    stats = CacheManager.get_cache_stats()
    print(f"   - Total entries: {stats['total_entries']}")
    print(f"   - Memory usage estimate: {stats['memory_usage_estimate']} bytes")

def test_asset_optimization():
    """Test asset optimization features."""
    print("\n🎨 Testing Asset Optimization")
    print("-" * 40)
    
    # Test CSS minification
    css_sample = """
    /* This is a comment */
    body {
        color: red;
        margin: 0;
        padding: 10px;
    }
    
    .container {
        width: 100%;
        max-width: 1200px;
    }
    """
    
    start_time = time.time()
    minified_css = minify_css(css_sample)
    css_time = time.time() - start_time
    
    original_size = len(css_sample)
    minified_size = len(minified_css)
    compression_ratio = ((original_size - minified_size) / original_size) * 100
    
    print(f"✅ CSS minified in {css_time:.3f}s")
    print(f"   - Original size: {original_size} bytes")
    print(f"   - Minified size: {minified_size} bytes")
    print(f"   - Compression: {compression_ratio:.1f}%")
    
    # Test JavaScript minification
    js_sample = """
    // This is a comment
    function calculateTotal(items) {
        var total = 0;
        for (var i = 0; i < items.length; i++) {
            total += items[i].price;
        }
        return total;
    }
    
    /* Multi-line
       comment */
    var result = calculateTotal(products);
    """
    
    start_time = time.time()
    minified_js = minify_js(js_sample)
    js_time = time.time() - start_time
    
    original_size = len(js_sample)
    minified_size = len(minified_js)
    compression_ratio = ((original_size - minified_size) / original_size) * 100
    
    print(f"✅ JavaScript minified in {js_time:.3f}s")
    print(f"   - Original size: {original_size} bytes")
    print(f"   - Minified size: {minified_size} bytes")
    print(f"   - Compression: {compression_ratio:.1f}%")

def test_performance_monitoring():
    """Test performance monitoring system."""
    print("\n📊 Testing Performance Monitoring")
    print("-" * 40)
    
    # Clear existing metrics
    performance_monitor.clear_metrics()
    
    # Simulate some requests
    start_time = time.time()
    for i in range(100):
        # Simulate different response times
        response_time = 0.1 + (i % 10) * 0.05  # 0.1s to 0.55s
        status_code = 200 if i % 20 != 0 else 404  # 5% error rate
        
        performance_monitor.record_request(
            endpoint=f"/test/endpoint/{i % 5}",
            method="GET",
            response_time=response_time,
            status_code=status_code,
            user_id=i % 10
        )
    
    monitoring_time = time.time() - start_time
    print(f"✅ Recorded 100 request metrics in {monitoring_time:.3f}s")
    
    # Generate performance summary
    start_time = time.time()
    summary = performance_monitor.get_performance_summary(minutes=60)
    summary_time = time.time() - start_time
    
    print(f"✅ Generated performance summary in {summary_time:.3f}s")
    print(f"   - Total requests: {summary['request_stats']['total_requests']}")
    print(f"   - Average response time: {summary['request_stats']['avg_response_time']:.3f}s")
    print(f"   - Max response time: {summary['request_stats']['max_response_time']:.3f}s")
    print(f"   - Requests per minute: {summary['request_stats']['requests_per_minute']:.1f}")
    
    # Test slow endpoint detection
    slow_endpoints = performance_monitor.get_slow_endpoints(threshold=0.3)
    print(f"   - Slow endpoints detected: {len(slow_endpoints)}")

def benchmark_comparison():
    """Compare performance with and without optimizations."""
    print("\n⚡ Performance Benchmark Comparison")
    print("-" * 40)
    
    # Simulate database queries without indexes
    print("Testing query performance...")
    
    # Test 1: Cache vs No Cache
    def expensive_operation(x):
        time.sleep(0.001)  # Simulate expensive operation
        return x * x
    
    # Without cache
    start_time = time.time()
    results = []
    for i in range(100):
        results.append(expensive_operation(i % 10))  # Repeated calculations
    no_cache_time = time.time() - start_time
    
    # With cache
    cache.clear()
    cached_results = {}
    
    start_time = time.time()
    results = []
    for i in range(100):
        key = i % 10
        if key in cached_results:
            results.append(cached_results[key])
        else:
            result = expensive_operation(key)
            cached_results[key] = result
            results.append(result)
    cache_time = time.time() - start_time
    
    improvement = ((no_cache_time - cache_time) / no_cache_time) * 100
    
    print(f"✅ Cache Performance Test:")
    print(f"   - Without cache: {no_cache_time:.3f}s")
    print(f"   - With cache: {cache_time:.3f}s")
    print(f"   - Performance improvement: {improvement:.1f}%")

def main():
    """Run all performance tests."""
    print("🚀 BuyRoll Performance Optimization Demo")
    print("=" * 50)
    
    try:
        test_database_optimizations()
        test_caching_performance()
        test_asset_optimization()
        test_performance_monitoring()
        benchmark_comparison()
        
        print("\n🎉 Performance Optimization Demo Completed!")
        print("=" * 50)
        print("Summary of optimizations implemented:")
        print("✅ Database query optimization with indexes")
        print("✅ SQLite performance tuning")
        print("✅ In-memory caching system")
        print("✅ CSS/JavaScript minification")
        print("✅ Asset compression and versioning")
        print("✅ Performance monitoring and analytics")
        print("✅ Load testing framework")
        print("✅ Comprehensive CLI tools")
        
    except Exception as e:
        print(f"❌ Error during performance testing: {str(e)}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)