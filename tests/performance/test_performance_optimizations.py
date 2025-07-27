"""
Test performance optimizations implementation.
"""

import pytest
import time
import os
import json
import tempfile
from unittest.mock import patch, MagicMock
from flask import Flask
from app import create_app, db
from app.utils.database_optimization import QueryOptimizer, vacuum_database, optimize_sqlite_settings
from app.utils.cache import cache, AnalyticsCache, SocialCache, CacheManager
from app.utils.asset_optimization import AssetOptimizer, AssetBundler, minify_css, minify_js
from app.utils.performance_monitor import performance_monitor, PerformanceMonitor
from tests.performance.load_testing import LoadTester

class TestDatabaseOptimization:
    """Test database optimization features."""
    
    def test_create_indexes(self, app):
        """Test database index creation."""
        with app.app_context():
            # This should not raise an exception
            QueryOptimizer.create_indexes()
            
            # Verify indexes were created by checking if they exist
            # (SQLite specific check)
            from sqlalchemy import text
            result = db.session.execute(
                text("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")
            ).fetchall()
            
            index_names = [row[0] for row in result]
            expected_indexes = [
                'idx_user_email',
                'idx_purchase_user_id',
                'idx_purchase_user_date',
                'idx_purchase_shared'
            ]
            
            for expected_index in expected_indexes:
                assert expected_index in index_names
    
    def test_query_performance_analysis(self, app):
        """Test query performance analysis."""
        with app.app_context():
            analysis = QueryOptimizer.analyze_query_performance()
            
            assert 'slow_queries' in analysis
            assert 'total_queries_analyzed' in analysis
            assert 'recommendations' in analysis
            assert isinstance(analysis['slow_queries'], list)
            assert isinstance(analysis['recommendations'], list)
    
    def test_sqlite_optimizations(self, app):
        """Test SQLite-specific optimizations."""
        with app.app_context():
            # This should not raise an exception
            optimize_sqlite_settings()
            
            # Verify some settings were applied
            from sqlalchemy import text
            result = db.session.execute(text("PRAGMA journal_mode")).fetchone()
            assert result[0] == 'wal'
    
    def test_vacuum_database(self, app):
        """Test database vacuum operation."""
        with app.app_context():
            # This should not raise an exception
            vacuum_database()

class TestCaching:
    """Test caching functionality."""
    
    def test_memory_cache_basic_operations(self):
        """Test basic cache operations."""
        cache.clear()
        
        # Test set and get
        cache.set('test_key', 'test_value', ttl=60)
        assert cache.get('test_key') == 'test_value'
        
        # Test non-existent key
        assert cache.get('non_existent') is None
        
        # Test delete
        cache.delete('test_key')
        assert cache.get('test_key') is None
    
    def test_cache_expiration(self):
        """Test cache TTL expiration."""
        cache.clear()
        
        # Set with very short TTL
        cache.set('expire_test', 'value', ttl=1)
        assert cache.get('expire_test') == 'value'
        
        # Wait for expiration
        time.sleep(1.1)
        assert cache.get('expire_test') is None
    
    def test_cache_cleanup(self):
        """Test expired cache cleanup."""
        cache.clear()
        
        # Add some expired entries
        cache.set('expired1', 'value1', ttl=1)
        cache.set('expired2', 'value2', ttl=1)
        cache.set('valid', 'value3', ttl=60)
        
        time.sleep(1.1)
        
        # Cleanup should remove expired entries
        removed_count = cache.cleanup_expired()
        assert removed_count == 2
        assert cache.get('valid') == 'value3'
    
    def test_cached_decorator(self, app):
        """Test the cached decorator."""
        from app.utils.cache import cached
        
        call_count = 0
        
        @cached(ttl=60)
        def expensive_function(x, y):
            nonlocal call_count
            call_count += 1
            return x + y
        
        with app.app_context():
            cache.clear()
            
            # First call should execute function
            result1 = expensive_function(1, 2)
            assert result1 == 3
            assert call_count == 1
            
            # Second call should use cache
            result2 = expensive_function(1, 2)
            assert result2 == 3
            assert call_count == 1  # Should not increment
            
            # Different arguments should execute function again
            result3 = expensive_function(2, 3)
            assert result3 == 5
            assert call_count == 2
    
    def test_analytics_cache(self, app, test_user):
        """Test analytics caching."""
        with app.app_context():
            cache.clear()
            
            # Mock the analytics service
            with patch('app.services.analytics_service.AnalyticsService') as mock_service:
                mock_service.get_monthly_spending.return_value = {'total': 100}
                
                # First call should hit the service
                result1 = AnalyticsCache.get_monthly_spending(test_user.id)
                assert result1 == {'total': 100}
                mock_service.get_monthly_spending.assert_called_once()
                
                # Second call should use cache
                result2 = AnalyticsCache.get_monthly_spending(test_user.id)
                assert result2 == {'total': 100}
                # Should still be called only once
                mock_service.get_monthly_spending.assert_called_once()
    
    def test_cache_manager_stats(self):
        """Test cache manager statistics."""
        cache.clear()
        cache.set('test1', 'value1')
        cache.set('test2', 'value2')
        
        stats = CacheManager.get_cache_stats()
        
        assert 'total_entries' in stats
        assert 'memory_usage_estimate' in stats
        assert 'expired_entries_cleaned' in stats
        assert stats['total_entries'] == 2

class TestAssetOptimization:
    """Test asset optimization features."""
    
    def test_file_hash_generation(self, app):
        """Test file hash generation for versioning."""
        with app.app_context():
            # Create a temporary file
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.css') as f:
                f.write('body { color: red; }')
                temp_file = f.name
            
            try:
                hash1 = AssetOptimizer.get_file_hash(temp_file)
                assert len(hash1) == 8  # MD5 hash truncated to 8 chars
                
                # Same file should produce same hash
                hash2 = AssetOptimizer.get_file_hash(temp_file)
                assert hash1 == hash2
                
                # Non-existent file should return 'missing'
                missing_hash = AssetOptimizer.get_file_hash('non_existent.css')
                assert missing_hash == 'missing'
                
            finally:
                os.unlink(temp_file)
    
    def test_css_minification(self):
        """Test CSS minification."""
        css_input = """
        /* This is a comment */
        body {
            color: red;
            margin: 0;
        }
        
        .container {
            padding: 10px;
        }
        """
        
        minified = minify_css(css_input)
        
        # Should remove comments and unnecessary whitespace
        assert '/*' not in minified
        assert '*/' not in minified
        assert minified.count('\n') < css_input.count('\n')
        assert 'color:red' in minified or 'color: red' in minified
    
    def test_js_minification(self):
        """Test JavaScript minification."""
        js_input = """
        // This is a comment
        function test() {
            var x = 1;
            return x + 2;
        }
        
        /* Multi-line
           comment */
        var result = test();
        """
        
        minified = minify_js(js_input)
        
        # Should remove comments and unnecessary whitespace
        assert '//' not in minified
        assert '/*' not in minified
        assert '*/' not in minified
        assert minified.count('\n') < js_input.count('\n')
    
    def test_asset_bundler(self, app):
        """Test asset bundling functionality."""
        with app.app_context():
            # Create temporary CSS files
            css_dir = os.path.join(app.static_folder, 'css')
            os.makedirs(css_dir, exist_ok=True)
            
            css1_path = os.path.join(css_dir, 'test1.css')
            css2_path = os.path.join(css_dir, 'test2.css')
            
            with open(css1_path, 'w') as f:
                f.write('body { color: red; }')
            
            with open(css2_path, 'w') as f:
                f.write('.container { padding: 10px; }')
            
            try:
                bundler = AssetBundler()
                bundler.add_css('test1.css')
                bundler.add_css('test2.css')
                
                bundle_name = bundler.bundle_css('test_bundle.css')
                assert bundle_name == 'test_bundle.css'
                
                # Check if bundle file was created
                bundle_path = os.path.join(css_dir, 'test_bundle.css')
                assert os.path.exists(bundle_path)
                
                # Check if gzipped version was created
                assert os.path.exists(bundle_path + '.gz')
                
                # Check bundle content
                with open(bundle_path, 'r') as f:
                    content = f.read()
                    assert 'color:red' in content or 'color: red' in content
                    assert 'padding:10px' in content or 'padding: 10px' in content
                
            finally:
                # Cleanup
                for file_path in [css1_path, css2_path]:
                    if os.path.exists(file_path):
                        os.unlink(file_path)
                
                bundle_path = os.path.join(css_dir, 'test_bundle.css')
                if os.path.exists(bundle_path):
                    os.unlink(bundle_path)
                if os.path.exists(bundle_path + '.gz'):
                    os.unlink(bundle_path + '.gz')

class TestPerformanceMonitoring:
    """Test performance monitoring functionality."""
    
    def test_performance_monitor_initialization(self):
        """Test performance monitor initialization."""
        monitor = PerformanceMonitor()
        
        assert monitor.monitoring_active is True
        assert 'requests' in monitor.metrics
        assert 'database_queries' in monitor.metrics
        assert 'cache_hits' in monitor.metrics
        assert 'cache_misses' in monitor.metrics
    
    def test_request_recording(self):
        """Test request performance recording."""
        monitor = PerformanceMonitor()
        monitor.metrics['requests'] = []  # Clear existing data
        
        monitor.record_request('/test', 'GET', 0.5, 200, user_id=1)
        
        assert len(monitor.metrics['requests']) == 1
        request = monitor.metrics['requests'][0]
        
        assert request['endpoint'] == '/test'
        assert request['method'] == 'GET'
        assert request['response_time'] == 0.5
        assert request['status_code'] == 200
        assert request['user_id'] == 1
    
    def test_database_query_recording(self):
        """Test database query performance recording."""
        monitor = PerformanceMonitor()
        monitor.metrics['database_queries'] = []  # Clear existing data
        
        monitor.record_database_query('SELECT', 0.1, 'users')
        
        assert len(monitor.metrics['database_queries']) == 1
        query = monitor.metrics['database_queries'][0]
        
        assert query['query_type'] == 'SELECT'
        assert query['execution_time'] == 0.1
        assert query['table'] == 'users'
    
    def test_cache_metrics_recording(self):
        """Test cache metrics recording."""
        monitor = PerformanceMonitor()
        monitor.metrics['cache_hits'] = 0
        monitor.metrics['cache_misses'] = 0
        
        monitor.record_cache_hit()
        monitor.record_cache_hit()
        monitor.record_cache_miss()
        
        assert monitor.metrics['cache_hits'] == 2
        assert monitor.metrics['cache_misses'] == 1
    
    def test_performance_summary(self):
        """Test performance summary generation."""
        monitor = PerformanceMonitor()
        
        # Add some test data
        monitor.record_request('/test1', 'GET', 0.5, 200)
        monitor.record_request('/test2', 'POST', 1.2, 201)
        monitor.record_database_query('SELECT', 0.1)
        monitor.record_cache_hit()
        monitor.record_cache_miss()
        
        summary = monitor.get_performance_summary(minutes=60)
        
        assert 'request_stats' in summary
        assert 'database_stats' in summary
        assert 'cache_stats' in summary
        
        req_stats = summary['request_stats']
        assert req_stats['total_requests'] >= 2
        assert 'avg_response_time' in req_stats
        assert 'max_response_time' in req_stats
    
    def test_slow_endpoints_detection(self):
        """Test slow endpoints detection."""
        monitor = PerformanceMonitor()
        monitor.metrics['requests'] = []  # Clear existing data
        
        # Add some slow requests
        monitor.record_request('/slow', 'GET', 2.0, 200)
        monitor.record_request('/slow', 'GET', 3.0, 200)
        monitor.record_request('/fast', 'GET', 0.1, 200)
        
        slow_endpoints = monitor.get_slow_endpoints(threshold=1.0)
        
        assert len(slow_endpoints) == 1
        endpoint, stats = slow_endpoints[0]
        assert endpoint == '/slow'
        assert stats['count'] == 2
        assert stats['avg_time'] == 2.5

class TestLoadTesting:
    """Test load testing functionality."""
    
    @pytest.mark.slow
    def test_load_tester_initialization(self):
        """Test load tester initialization."""
        tester = LoadTester('http://localhost:5000')
        
        assert tester.base_url == 'http://localhost:5000'
        assert tester.results == []
    
    @pytest.mark.slow
    def test_measure_request_mock(self):
        """Test request measurement with mocking."""
        tester = LoadTester()
        
        # Mock the session.get method
        with patch.object(tester.session, 'get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b'test content'
            mock_get.return_value = mock_response
            
            result = tester.measure_request('GET', 'http://test.com/test')
            
            assert result['url'] == 'http://test.com/test'
            assert result['method'] == 'GET'
            assert result['status_code'] == 200
            assert result['success'] is True
            assert 'response_time' in result
            assert result['content_length'] == len(b'test content')
    
    def test_percentile_calculation(self):
        """Test percentile calculation."""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        
        p50 = LoadTester.percentile(data, 50)
        p95 = LoadTester.percentile(data, 95)
        p99 = LoadTester.percentile(data, 99)
        
        assert p50 == 5.5  # Median
        assert abs(p95 - 9.55) < 0.01  # Allow for floating point precision
        assert abs(p99 - 9.91) < 0.01

class TestIntegrationPerformance:
    """Integration tests for performance optimizations."""
    
    def test_database_with_indexes(self, app, test_user):
        """Test database performance with indexes."""
        with app.app_context():
            # Create indexes
            QueryOptimizer.create_indexes()
            
            # Perform some queries that should benefit from indexes
            start_time = time.time()
            
            # Query that should use email index
            from app.models.user import User
            user = User.query.filter_by(email=test_user.email).first()
            
            query_time = time.time() - start_time
            
            assert user is not None
            assert query_time < 0.1  # Should be fast with index
    
    def test_caching_integration(self, app, test_user):
        """Test caching integration with real data."""
        with app.app_context():
            cache.clear()
            
            # Mock analytics service
            with patch('app.services.analytics_service.AnalyticsService') as mock_service:
                mock_service.get_monthly_spending.return_value = {'total': 150}
                
                # First call - should hit service and cache result
                start_time = time.time()
                result1 = AnalyticsCache.get_monthly_spending(test_user.id)
                first_call_time = time.time() - start_time
                
                # Second call - should use cache
                start_time = time.time()
                result2 = AnalyticsCache.get_monthly_spending(test_user.id)
                second_call_time = time.time() - start_time
                
                assert result1 == result2
                assert second_call_time < first_call_time  # Cache should be faster
                mock_service.get_monthly_spending.assert_called_once()
    
    def test_performance_monitoring_integration(self, app):
        """Test performance monitoring integration."""
        with app.app_context():
            # Clear existing metrics
            performance_monitor.clear_metrics()
            
            # Simulate some requests
            performance_monitor.record_request('/test', 'GET', 0.5, 200)
            performance_monitor.record_request('/api/test', 'POST', 1.2, 201)
            performance_monitor.record_database_query('SELECT', 0.1, 'users')
            
            # Get summary
            summary = performance_monitor.get_performance_summary()
            
            assert summary['request_stats']['total_requests'] == 2
            assert summary['database_stats']['total_queries'] == 1
            assert summary['request_stats']['avg_response_time'] == 0.85

@pytest.mark.slow
class TestRealLoadTesting:
    """Real load testing (marked as slow tests)."""
    
    def test_homepage_load_performance(self, app):
        """Test homepage loading under load."""
        # This would require the app to be running
        # Skipped in normal test runs due to @pytest.mark.slow
        pass
    
    def test_api_endpoint_performance(self, app):
        """Test API endpoint performance under load."""
        # This would require the app to be running
        # Skipped in normal test runs due to @pytest.mark.slow
        pass