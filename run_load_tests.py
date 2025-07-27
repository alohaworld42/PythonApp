#!/usr/bin/env python3
"""
Standalone load testing script for BuyRoll application.
Run this script to perform comprehensive load testing.
"""

import sys
import os
import argparse
import time
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tests.performance.load_testing import LoadTester, run_stress_test

def main():
    parser = argparse.ArgumentParser(description='BuyRoll Load Testing Tool')
    parser.add_argument('--url', default='http://localhost:5000', 
                       help='Base URL of the application (default: http://localhost:5000)')
    parser.add_argument('--test-type', choices=['comprehensive', 'stress', 'specific'], 
                       default='comprehensive', help='Type of test to run')
    parser.add_argument('--duration', type=int, default=5, 
                       help='Duration for stress test in minutes (default: 5)')
    parser.add_argument('--output', help='Output file for results (optional)')
    parser.add_argument('--concurrent-users', type=int, default=5, 
                       help='Number of concurrent users (default: 5)')
    parser.add_argument('--requests', type=int, default=50, 
                       help='Number of requests per test (default: 50)')
    
    args = parser.parse_args()
    
    print("BuyRoll Load Testing Tool")
    print("=" * 40)
    print(f"Target URL: {args.url}")
    print(f"Test Type: {args.test_type}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize load tester
    tester = LoadTester(args.url)
    
    try:
        if args.test_type == 'comprehensive':
            print("Running comprehensive load test suite...")
            results = tester.run_comprehensive_load_test()
            
        elif args.test_type == 'stress':
            print(f"Running stress test for {args.duration} minutes...")
            run_stress_test(args.url, args.duration)
            results = None
            
        elif args.test_type == 'specific':
            print("Running specific performance tests...")
            results = []
            
            # Homepage test
            print("\n1. Testing homepage performance...")
            result = tester.test_homepage_load(args.requests, args.concurrent_users)
            if result:
                results.append(result)
            
            # Dashboard test (requires authentication)
            print("\n2. Testing dashboard performance...")
            result = tester.test_dashboard_performance(args.requests // 2, args.concurrent_users)
            if result:
                results.append(result)
            
            # API tests
            print("\n3. Testing API performance...")
            result = tester.test_analytics_api_performance(args.requests // 3, args.concurrent_users)
            if result:
                results.append(result)
        
        # Save results if output file specified
        if args.output and hasattr(tester, 'results'):
            tester.save_results(args.output)
            print(f"\nResults saved to: {args.output}")
        
        # Performance recommendations
        if args.test_type in ['comprehensive', 'specific'] and results:
            print("\n" + "=" * 50)
            print("PERFORMANCE RECOMMENDATIONS")
            print("=" * 50)
            
            # Analyze results and provide recommendations
            slow_tests = [r for r in results if r['avg_response_time'] > 1.0]
            error_tests = [r for r in results if r['success_rate'] < 95]
            
            if slow_tests:
                print("\n🐌 Slow Operations (>1s average):")
                for test in slow_tests:
                    print(f"  • {test['test_name']}: {test['avg_response_time']:.3f}s")
                    print("    Recommendations:")
                    print("      - Add caching for frequently accessed data")
                    print("      - Optimize database queries")
                    print("      - Consider CDN for static assets")
            
            if error_tests:
                print("\n❌ Operations with Errors (<95% success):")
                for test in error_tests:
                    print(f"  • {test['test_name']}: {test['success_rate']:.1f}% success")
                    print("    Recommendations:")
                    print("      - Investigate error logs")
                    print("      - Add better error handling")
                    print("      - Increase server resources")
            
            if not slow_tests and not error_tests:
                print("\n✅ All tests performing within acceptable thresholds!")
                print("Consider these optimizations for even better performance:")
                print("  • Implement HTTP/2 server push")
                print("  • Add service worker for offline functionality")
                print("  • Optimize images with WebP format")
                print("  • Implement lazy loading for non-critical resources")
        
    except KeyboardInterrupt:
        print("\n\nLoad testing interrupted by user")
        return 1
    
    except Exception as e:
        print(f"\nError during load testing: {str(e)}")
        return 1
    
    print(f"\nLoad testing completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return 0

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)