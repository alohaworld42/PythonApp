#!/usr/bin/env python3
"""
Demo script to showcase the Analytics Service functionality.
This script creates sample data and demonstrates all analytics features.
"""

from datetime import datetime, timedelta
from app import create_app, db
from app.models.user import User
from app.models.product import Product
from app.models.purchase import Purchase
from app.services.analytics_service import AnalyticsService
import json

def create_sample_data():
    """Create sample data for analytics demonstration."""
    
    # Create a test user
    user = User(
        email='demo@buyroll.com',
        name='Demo User',
        password_hash=User.hash_password('password123')
    )
    db.session.add(user)
    db.session.commit()
    
    # Create sample products across different categories and price ranges
    products = [
        # Electronics
        Product(title='MacBook Pro', source='shopify', price=2499.99, currency='USD', category='Electronics'),
        Product(title='iPhone 15', source='shopify', price=999.99, currency='USD', category='Electronics'),
        Product(title='AirPods Pro', source='shopify', price=249.99, currency='USD', category='Electronics'),
        Product(title='iPad Air', source='shopify', price=599.99, currency='USD', category='Electronics'),
        
        # Clothing
        Product(title='Designer Jeans', source='woocommerce', price=189.99, currency='USD', category='Clothing'),
        Product(title='Wool Sweater', source='woocommerce', price=129.99, currency='USD', category='Clothing'),
        Product(title='Running Shoes', source='shopify', price=159.99, currency='USD', category='Clothing'),
        Product(title='Winter Jacket', source='woocommerce', price=299.99, currency='USD', category='Clothing'),
        
        # Home & Garden
        Product(title='Coffee Machine', source='shopify', price=399.99, currency='USD', category='Home'),
        Product(title='Smart Thermostat', source='shopify', price=249.99, currency='USD', category='Home'),
        Product(title='Kitchen Knife Set', source='woocommerce', price=149.99, currency='USD', category='Home'),
        Product(title='Vacuum Cleaner', source='shopify', price=299.99, currency='USD', category='Home'),
        
        # Books & Media
        Product(title='Programming Book', source='woocommerce', price=49.99, currency='USD', category='Books'),
        Product(title='Cookbook', source='woocommerce', price=29.99, currency='USD', category='Books'),
        Product(title='Novel Set', source='woocommerce', price=39.99, currency='USD', category='Books'),
        
        # Health & Beauty
        Product(title='Skincare Set', source='shopify', price=89.99, currency='USD', category='Beauty'),
        Product(title='Vitamins', source='woocommerce', price=34.99, currency='USD', category='Health'),
        Product(title='Fitness Tracker', source='shopify', price=199.99, currency='USD', category='Health'),
    ]
    
    for product in products:
        db.session.add(product)
    db.session.commit()
    
    # Create purchases spread across different months and stores
    now = datetime.now()
    stores = ['Apple Store', 'Amazon', 'Best Buy', 'Target', 'Walmart', 'Fashion Boutique', 'Home Depot']
    
    purchases = []
    
    # Create purchases for the last 12 months with varying patterns
    for i, product in enumerate(products):
        # Vary the purchase dates to create interesting trends
        days_ago = (i * 15) + (i % 3) * 10  # Spread purchases over time
        purchase_date = now - timedelta(days=days_ago)
        
        store_name = stores[i % len(stores)]
        
        purchase = Purchase(
            user_id=user.id,
            product_id=product.id,
            purchase_date=purchase_date,
            store_name=store_name,
            order_id=f'ORDER{1000 + i}',
            is_shared=(i % 3 == 0)  # Share every third purchase
        )
        purchases.append(purchase)
        db.session.add(purchase)
    
    db.session.commit()
    
    return user, products, purchases

def demonstrate_analytics(user_id):
    """Demonstrate all analytics functionality."""
    
    print("=" * 60)
    print("BuyRoll Analytics Service Demonstration")
    print("=" * 60)
    
    # 1. Monthly Spending Analysis
    print("\n1. MONTHLY SPENDING ANALYSIS")
    print("-" * 40)
    monthly_data = AnalyticsService.get_monthly_spending(user_id)
    
    print(f"Total months with purchases: {monthly_data['total_months']}")
    print("\nMonthly breakdown:")
    for month in monthly_data['monthly_spending'][:6]:  # Show last 6 months
        print(f"  {month['period']}: ${month['total_spending']:.2f} ({month['purchase_count']} purchases)")
    
    # 2. Category Spending Analysis
    print("\n2. CATEGORY SPENDING ANALYSIS")
    print("-" * 40)
    category_data = AnalyticsService.get_category_spending_analysis(user_id)
    
    print(f"Total spending: ${category_data['total_spending']:.2f}")
    print(f"Categories analyzed: {category_data['total_categories']}")
    print("\nSpending by category:")
    for category in category_data['category_analysis']:
        print(f"  {category['category']}: ${category['total_spending']:.2f} "
              f"({category['percentage']:.1f}%) - {category['purchase_count']} items")
    
    # 3. Store Spending Analysis
    print("\n3. STORE SPENDING ANALYSIS")
    print("-" * 40)
    store_data = AnalyticsService.get_store_spending_analysis(user_id)
    
    print(f"Total stores: {store_data['total_stores']}")
    print("\nSpending by store:")
    for store in store_data['store_analysis'][:5]:  # Show top 5 stores
        print(f"  {store['store_name']}: ${store['total_spending']:.2f} "
              f"({store['percentage']:.1f}%) - {store['purchase_count']} purchases")
        print(f"    Average: ${store['avg_price']:.2f}")
    
    # 4. Spending Trends
    print("\n4. SPENDING TRENDS ANALYSIS")
    print("-" * 40)
    trends_data = AnalyticsService.get_spending_trends(user_id, period_months=6)
    
    stats = trends_data['statistics']
    print(f"Trend direction: {stats['trend_direction'].upper()}")
    print(f"Average monthly spending: ${stats['avg_monthly_spending']:.2f}")
    print(f"Highest month: ${stats['max_monthly_spending']:.2f}")
    print(f"Lowest month: ${stats['min_monthly_spending']:.2f}")
    print(f"Total spending (6 months): ${stats['total_spending']:.2f}")
    
    print("\nMonthly trend:")
    for trend in trends_data['trends_data']:
        print(f"  {trend['period']}: ${trend['total_spending']:.2f} ({trend['purchase_count']} purchases)")
    
    # 5. Comprehensive Analytics
    print("\n5. COMPREHENSIVE ANALYTICS SUMMARY")
    print("-" * 40)
    comprehensive = AnalyticsService.get_comprehensive_analytics(user_id, period_months=12)
    
    print(f"Analysis period: {comprehensive['period']['months']} months")
    print(f"From: {comprehensive['period']['start_date'][:10]}")
    print(f"To: {comprehensive['period']['end_date'][:10]}")
    
    # Summary statistics
    monthly_total = sum(month['total_spending'] for month in comprehensive['monthly_spending']['monthly_spending'])
    category_total = comprehensive['category_analysis']['total_spending']
    store_total = comprehensive['store_analysis']['total_spending']
    
    print(f"\nTotal spending: ${monthly_total:.2f}")
    print(f"Categories: {comprehensive['category_analysis']['total_categories']}")
    print(f"Stores: {comprehensive['store_analysis']['total_stores']}")
    print(f"Months active: {comprehensive['monthly_spending']['total_months']}")
    
    return comprehensive

def main():
    """Main demonstration function."""
    
    # Create Flask app and database
    app = create_app('config.DevelopmentConfig')
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if demo data already exists
        existing_user = User.query.filter_by(email='demo@buyroll.com').first()
        
        if existing_user:
            print("Using existing demo data...")
            user = existing_user
        else:
            print("Creating sample data...")
            user, products, purchases = create_sample_data()
            print(f"Created {len(products)} products and {len(purchases)} purchases")
        
        # Demonstrate analytics
        comprehensive_data = demonstrate_analytics(user.id)
        
        # Save comprehensive data to JSON file for reference
        with open('analytics_demo_output.json', 'w') as f:
            json.dump(comprehensive_data, f, indent=2, default=str)
        
        print(f"\n{'='*60}")
        print("Demo completed! Comprehensive analytics saved to 'analytics_demo_output.json'")
        print("You can now test the API endpoints at:")
        print("  GET /api/analytics/spending")
        print("  GET /api/analytics/categories")
        print("  GET /api/analytics/stores")
        print("  GET /api/analytics/trends")
        print("  GET /api/analytics/comprehensive")
        print(f"{'='*60}")

if __name__ == '__main__':
    main()