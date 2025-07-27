"""
Load testing scenarios for performance optimization validation.
"""

import requests
import time
import threading
import json
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import random

class LoadTester:
    """Load testing utility for the BuyRoll application."""
    
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = []
        
    def authenticate(self, email='test@example.com', password='testpass123'):
        """Authenticate and get session cookie."""
        login_data = {
            'email': email,
            'password': password
        }
        
        response = self.session.post(f'{self.base_url}/auth/login', data=login_data)
        return response.status_code == 200 or response.status_code == 302
    
    def measure_request(self, method, url, **kwargs):
        """Measure request performance."""
        start_time = time.time()
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, **kwargs)
            elif method.upper() == 'POST':
                response = self.session.post(url, **kwargs)
            elif method.upper() == 'PUT':
                response = self.session.put(url, **kwargs)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            end_time = time.time()
            
            result = {
                'url': url,
                'method': method,
                'status_code': response.status_code,
                'response_time': end_time - start_time,
                'content_length': len(response.content),
                'timestamp': datetime.now().isoformat(),
                'success': 200 <= response.status_code < 400
            }
            
            self.results.append(result)
            return result
            
        except Exception as e:
            end_time = time.time()
            result = {
                'url': url,
                'method': method,
                'status_code': 0,
                'response_time': end_time - start_time,
                'content_length': 0,
                'timestamp': datetime.now().isoformat(),
                'success': False,
                'error': str(e)
            }
            
            self.results.append(result)
            return result
    
    def test_homepage_load(self, num_requests=50, concurrent_users=5):
        """Test homepage loading performance."""
        print(f"Testing homepage load with {num_requests} requests, {concurrent_users} concurrent users")
        
        def make_request():
            return self.measure_request('GET', f'{self.base_url}/')
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            
            for future in as_completed(futures):
                result = future.result()
                if not result['success']:
                    print(f"Failed request: {result}")
        
        return self.analyze_results('Homepage Load Test')
    
    def test_dashboard_performance(self, num_requests=30, concurrent_users=3):
        """Test dashboard performance with authenticated users."""
        print(f"Testing dashboard performance with {num_requests} requests, {concurrent_users} concurrent users")
        
        # Authenticate first
        if not self.authenticate():
            print("Authentication failed")
            return None
        
        def make_request():
            return self.measure_request('GET', f'{self.base_url}/dashboard')
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            
            for future in as_completed(futures):
                result = future.result()
                if not result['success']:
                    print(f"Failed request: {result}")
        
        return self.analyze_results('Dashboard Performance Test')
    
    def test_analytics_api_performance(self, num_requests=20, concurrent_users=2):
        """Test analytics API endpoints performance."""
        print(f"Testing analytics API with {num_requests} requests, {concurrent_users} concurrent users")
        
        # Authenticate first
        if not self.authenticate():
            print("Authentication failed")
            return None
        
        api_endpoints = [
            '/api/analytics/spending',
            '/api/analytics/categories',
            '/api/analytics/stores',
            '/api/analytics/trends',
            '/api/analytics/summary'
        ]
        
        def make_request():
            endpoint = random.choice(api_endpoints)
            return self.measure_request('GET', f'{self.base_url}{endpoint}')
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            
            for future in as_completed(futures):
                result = future.result()
                if not result['success']:
                    print(f"Failed request: {result}")
        
        return self.analyze_results('Analytics API Performance Test')
    
    def test_social_feed_performance(self, num_requests=25, concurrent_users=3):
        """Test social feed loading performance."""
        print(f"Testing social feed with {num_requests} requests, {concurrent_users} concurrent users")
        
        # Authenticate first
        if not self.authenticate():
            print("Authentication failed")
            return None
        
        def make_request():
            return self.measure_request('GET', f'{self.base_url}/social/feed')
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            
            for future in as_completed(futures):
                result = future.result()
                if not result['success']:
                    print(f"Failed request: {result}")
        
        return self.analyze_results('Social Feed Performance Test')
    
    def test_static_assets_performance(self, num_requests=40, concurrent_users=8):
        """Test static asset loading performance."""
        print(f"Testing static assets with {num_requests} requests, {concurrent_users} concurrent users")
        
        static_assets = [
            '/static/css/main.css',
            '/static/js/main.js',
            '/static/js/analytics.js',
            '/static/images/placeholder-product.svg'
        ]
        
        def make_request():
            asset = random.choice(static_assets)
            return self.measure_request('GET', f'{self.base_url}{asset}')
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            
            for future in as_completed(futures):
                result = future.result()
                if not result['success']:
                    print(f"Failed request: {result}")
        
        return self.analyze_results('Static Assets Performance Test')
    
    def test_database_intensive_operations(self, num_requests=15, concurrent_users=2):
        """Test database-intensive operations."""
        print(f"Testing database operations with {num_requests} requests, {concurrent_users} concurrent users")
        
        # Authenticate first
        if not self.authenticate():
            print("Authentication failed")
            return None
        
        # Test various database-intensive endpoints
        endpoints = [
            '/api/analytics/comprehensive?period_months=12',
            '/api/purchases/shared',
            '/api/friends/feed?limit=50',
            '/user/purchases?page=1&per_page=20'
        ]
        
        def make_request():
            endpoint = random.choice(endpoints)
            return self.measure_request('GET', f'{self.base_url}{endpoint}')
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            
            for future in as_completed(futures):
                result = future.result()
                if not result['success']:
                    print(f"Failed request: {result}")
        
        return self.analyze_results('Database Intensive Operations Test')
    
    def analyze_results(self, test_name):
        """Analyze test results and provide statistics."""
        if not self.results:
            return None
        
        # Filter results for this test (simple approach - use recent results)
        recent_results = self.results[-50:]  # Last 50 results
        
        response_times = [r['response_time'] for r in recent_results if r['success']]
        success_count = sum(1 for r in recent_results if r['success'])
        total_requests = len(recent_results)
        
        if not response_times:
            print(f"{test_name}: No successful requests")
            return None
        
        analysis = {
            'test_name': test_name,
            'total_requests': total_requests,
            'successful_requests': success_count,
            'success_rate': (success_count / total_requests) * 100,
            'avg_response_time': statistics.mean(response_times),
            'median_response_time': statistics.median(response_times),
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'p95_response_time': self.percentile(response_times, 95),
            'p99_response_time': self.percentile(response_times, 99),
            'requests_per_second': success_count / sum(response_times) if response_times else 0
        }
        
        # Print results
        print(f"\n{test_name} Results:")
        print(f"  Total Requests: {analysis['total_requests']}")
        print(f"  Success Rate: {analysis['success_rate']:.1f}%")
        print(f"  Average Response Time: {analysis['avg_response_time']:.3f}s")
        print(f"  Median Response Time: {analysis['median_response_time']:.3f}s")
        print(f"  95th Percentile: {analysis['p95_response_time']:.3f}s")
        print(f"  99th Percentile: {analysis['p99_response_time']:.3f}s")
        print(f"  Requests/Second: {analysis['requests_per_second']:.2f}")
        
        # Performance thresholds
        warnings = []
        if analysis['avg_response_time'] > 2.0:
            warnings.append("Average response time > 2s")
        if analysis['p95_response_time'] > 5.0:
            warnings.append("95th percentile > 5s")
        if analysis['success_rate'] < 95:
            warnings.append("Success rate < 95%")
        
        if warnings:
            print(f"  ⚠️  Warnings: {', '.join(warnings)}")
        else:
            print("  ✅ Performance within acceptable thresholds")
        
        return analysis
    
    @staticmethod
    def percentile(data, percentile):
        """Calculate percentile of a dataset."""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def run_comprehensive_load_test(self):
        """Run all load tests and provide comprehensive report."""
        print("Starting Comprehensive Load Test Suite")
        print("=" * 50)
        
        all_results = []
        
        # Run all tests
        tests = [
            self.test_homepage_load,
            self.test_dashboard_performance,
            self.test_analytics_api_performance,
            self.test_social_feed_performance,
            self.test_static_assets_performance,
            self.test_database_intensive_operations
        ]
        
        for test in tests:
            try:
                result = test()
                if result:
                    all_results.append(result)
                time.sleep(2)  # Brief pause between tests
            except Exception as e:
                print(f"Test failed: {str(e)}")
        
        # Generate summary report
        print("\n" + "=" * 50)
        print("COMPREHENSIVE LOAD TEST SUMMARY")
        print("=" * 50)
        
        total_requests = sum(r['total_requests'] for r in all_results)
        total_successful = sum(r['successful_requests'] for r in all_results)
        overall_success_rate = (total_successful / total_requests) * 100 if total_requests > 0 else 0
        
        print(f"Total Requests: {total_requests}")
        print(f"Overall Success Rate: {overall_success_rate:.1f}%")
        
        # Find slowest operations
        slowest_tests = sorted(all_results, key=lambda x: x['avg_response_time'], reverse=True)
        print(f"\nSlowest Operations:")
        for i, test in enumerate(slowest_tests[:3], 1):
            print(f"  {i}. {test['test_name']}: {test['avg_response_time']:.3f}s avg")
        
        # Performance recommendations
        print(f"\nPerformance Recommendations:")
        recommendations = []
        
        for result in all_results:
            if result['avg_response_time'] > 1.0:
                recommendations.append(f"Optimize {result['test_name']} (avg: {result['avg_response_time']:.3f}s)")
            if result['success_rate'] < 98:
                recommendations.append(f"Investigate failures in {result['test_name']} ({result['success_rate']:.1f}% success)")
        
        if recommendations:
            for rec in recommendations:
                print(f"  • {rec}")
        else:
            print("  ✅ All tests performing within acceptable thresholds")
        
        return all_results
    
    def save_results(self, filename='load_test_results.json'):
        """Save test results to file."""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"Results saved to {filename}")

def run_stress_test(base_url='http://localhost:5000', duration_minutes=5):
    """Run a stress test for a specified duration."""
    print(f"Running stress test for {duration_minutes} minutes")
    
    tester = LoadTester(base_url)
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    
    request_count = 0
    error_count = 0
    
    while time.time() < end_time:
        try:
            # Random endpoint selection
            endpoints = ['/', '/dashboard', '/api/analytics/summary']
            endpoint = random.choice(endpoints)
            
            if endpoint != '/':
                tester.authenticate()
            
            result = tester.measure_request('GET', f'{base_url}{endpoint}')
            request_count += 1
            
            if not result['success']:
                error_count += 1
            
            # Brief pause to simulate realistic usage
            time.sleep(random.uniform(0.1, 0.5))
            
        except KeyboardInterrupt:
            print("\nStress test interrupted by user")
            break
        except Exception as e:
            error_count += 1
            print(f"Error during stress test: {str(e)}")
    
    duration = time.time() - start_time
    print(f"\nStress Test Results:")
    print(f"  Duration: {duration:.1f} seconds")
    print(f"  Total Requests: {request_count}")
    print(f"  Errors: {error_count}")
    print(f"  Error Rate: {(error_count/request_count)*100:.1f}%")
    print(f"  Requests/Second: {request_count/duration:.2f}")

if __name__ == '__main__':
    # Example usage
    tester = LoadTester()
    
    # Run comprehensive test
    results = tester.run_comprehensive_load_test()
    
    # Save results
    tester.save_results()
    
    # Optional: Run stress test
    # run_stress_test(duration_minutes=2)