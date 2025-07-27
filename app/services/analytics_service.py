from app import db
from app.models.purchase import Purchase
from app.models.product import Product
from app.utils.cache import cached
from app.utils.performance_monitor import monitor_database_query
from sqlalchemy import func, extract, and_
from datetime import datetime, timedelta
from collections import defaultdict
import calendar

class AnalyticsService:
    """Service for generating spending analytics and insights."""
    
    @staticmethod
    @cached(ttl=600, key_prefix='analytics_monthly_')
    @monitor_database_query('SELECT', 'purchase')
    def get_monthly_spending(user_id, year=None, month=None):
        """
        Calculate monthly spending for a user.
        
        Args:
            user_id (int): User ID
            year (int, optional): Specific year to analyze
            month (int, optional): Specific month to analyze
            
        Returns:
            dict: Monthly spending data
        """
        query = db.session.query(
            extract('year', Purchase.purchase_date).label('year'),
            extract('month', Purchase.purchase_date).label('month'),
            func.sum(Product.price).label('total_spending'),
            func.count(Purchase.id).label('purchase_count')
        ).join(Product).filter(Purchase.user_id == user_id)
        
        if year:
            query = query.filter(extract('year', Purchase.purchase_date) == year)
        if month:
            query = query.filter(extract('month', Purchase.purchase_date) == month)
            
        query = query.group_by(
            extract('year', Purchase.purchase_date),
            extract('month', Purchase.purchase_date)
        ).order_by(
            extract('year', Purchase.purchase_date).desc(),
            extract('month', Purchase.purchase_date).desc()
        )
        
        results = query.all()
        
        monthly_data = []
        for result in results:
            month_name = calendar.month_name[int(result.month)]
            monthly_data.append({
                'year': int(result.year),
                'month': int(result.month),
                'month_name': month_name,
                'total_spending': float(result.total_spending or 0),
                'purchase_count': result.purchase_count,
                'period': f"{month_name} {int(result.year)}"
            })
            
        return {
            'monthly_spending': monthly_data,
            'total_months': len(monthly_data)
        }
    
    @staticmethod
    @cached(ttl=900, key_prefix='analytics_category_')
    @monitor_database_query('SELECT', 'purchase')
    def get_category_spending_analysis(user_id, start_date=None, end_date=None):
        """
        Analyze spending by product category.
        
        Args:
            user_id (int): User ID
            start_date (datetime, optional): Start date for analysis
            end_date (datetime, optional): End date for analysis
            
        Returns:
            dict: Category spending analysis
        """
        query = db.session.query(
            Product.category,
            func.sum(Product.price).label('total_spending'),
            func.count(Purchase.id).label('purchase_count'),
            func.avg(Product.price).label('avg_price')
        ).join(Purchase).filter(Purchase.user_id == user_id)
        
        if start_date:
            query = query.filter(Purchase.purchase_date >= start_date)
        if end_date:
            query = query.filter(Purchase.purchase_date <= end_date)
            
        query = query.group_by(Product.category).order_by(
            func.sum(Product.price).desc()
        )
        
        results = query.all()
        
        # Calculate total spending for percentage calculation
        total_spending = sum(float(result.total_spending or 0) for result in results)
        
        category_data = []
        for result in results:
            category_spending = float(result.total_spending or 0)
            percentage = (category_spending / total_spending * 100) if total_spending > 0 else 0
            
            category_data.append({
                'category': result.category or 'Uncategorized',
                'total_spending': category_spending,
                'purchase_count': result.purchase_count,
                'avg_price': float(result.avg_price or 0),
                'percentage': round(percentage, 2)
            })
            
        return {
            'category_analysis': category_data,
            'total_spending': total_spending,
            'total_categories': len(category_data)
        }
    
    @staticmethod
    @cached(ttl=900, key_prefix='analytics_store_')
    @monitor_database_query('SELECT', 'purchase')
    def get_store_spending_analysis(user_id, start_date=None, end_date=None):
        """
        Analyze spending by store.
        
        Args:
            user_id (int): User ID
            start_date (datetime, optional): Start date for analysis
            end_date (datetime, optional): End date for analysis
            
        Returns:
            dict: Store spending analysis
        """
        query = db.session.query(
            Purchase.store_name,
            func.sum(Product.price).label('total_spending'),
            func.count(Purchase.id).label('purchase_count'),
            func.avg(Product.price).label('avg_price'),
            func.max(Purchase.purchase_date).label('last_purchase')
        ).join(Product).filter(Purchase.user_id == user_id)
        
        if start_date:
            query = query.filter(Purchase.purchase_date >= start_date)
        if end_date:
            query = query.filter(Purchase.purchase_date <= end_date)
            
        query = query.group_by(Purchase.store_name).order_by(
            func.sum(Product.price).desc()
        )
        
        results = query.all()
        
        # Calculate total spending for percentage calculation
        total_spending = sum(float(result.total_spending or 0) for result in results)
        
        store_data = []
        for result in results:
            store_spending = float(result.total_spending or 0)
            percentage = (store_spending / total_spending * 100) if total_spending > 0 else 0
            
            store_data.append({
                'store_name': result.store_name,
                'total_spending': store_spending,
                'purchase_count': result.purchase_count,
                'avg_price': float(result.avg_price or 0),
                'percentage': round(percentage, 2),
                'last_purchase': result.last_purchase.isoformat() if result.last_purchase else None
            })
            
        return {
            'store_analysis': store_data,
            'total_spending': total_spending,
            'total_stores': len(store_data)
        }
    
    @staticmethod
    @cached(ttl=1800, key_prefix='analytics_trends_')
    @monitor_database_query('SELECT', 'purchase')
    def get_spending_trends(user_id, period_months=12):
        """
        Generate time-series spending trends.
        
        Args:
            user_id (int): User ID
            period_months (int): Number of months to analyze (default: 12)
            
        Returns:
            dict: Spending trends data
        """
        # Calculate start date
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_months * 30)  # Approximate months
        
        # Get monthly spending data
        query = db.session.query(
            extract('year', Purchase.purchase_date).label('year'),
            extract('month', Purchase.purchase_date).label('month'),
            func.sum(Product.price).label('total_spending'),
            func.count(Purchase.id).label('purchase_count')
        ).join(Product).filter(
            and_(
                Purchase.user_id == user_id,
                Purchase.purchase_date >= start_date,
                Purchase.purchase_date <= end_date
            )
        ).group_by(
            extract('year', Purchase.purchase_date),
            extract('month', Purchase.purchase_date)
        ).order_by(
            extract('year', Purchase.purchase_date),
            extract('month', Purchase.purchase_date)
        )
        
        results = query.all()
        
        # Create time series data
        trends_data = []
        monthly_totals = []
        
        for result in results:
            month_name = calendar.month_name[int(result.month)]
            spending = float(result.total_spending or 0)
            
            trends_data.append({
                'year': int(result.year),
                'month': int(result.month),
                'month_name': month_name,
                'period': f"{month_name[:3]} {int(result.year)}",
                'total_spending': spending,
                'purchase_count': result.purchase_count
            })
            monthly_totals.append(spending)
        
        # Calculate trend statistics
        avg_monthly_spending = sum(monthly_totals) / len(monthly_totals) if monthly_totals else 0
        max_spending = max(monthly_totals) if monthly_totals else 0
        min_spending = min(monthly_totals) if monthly_totals else 0
        
        # Calculate trend direction (simple linear trend)
        trend_direction = 'stable'
        if len(monthly_totals) >= 2:
            recent_avg = sum(monthly_totals[-3:]) / min(3, len(monthly_totals))
            earlier_avg = sum(monthly_totals[:3]) / min(3, len(monthly_totals))
            
            if recent_avg > earlier_avg * 1.1:  # 10% increase threshold
                trend_direction = 'increasing'
            elif recent_avg < earlier_avg * 0.9:  # 10% decrease threshold
                trend_direction = 'decreasing'
        
        return {
            'trends_data': trends_data,
            'period_months': period_months,
            'statistics': {
                'avg_monthly_spending': round(avg_monthly_spending, 2),
                'max_monthly_spending': max_spending,
                'min_monthly_spending': min_spending,
                'total_spending': sum(monthly_totals),
                'trend_direction': trend_direction
            }
        }
    
    @staticmethod
    def get_comprehensive_analytics(user_id, period_months=12):
        """
        Get comprehensive analytics combining all analysis types.
        
        Args:
            user_id (int): User ID
            period_months (int): Number of months for trend analysis
            
        Returns:
            dict: Comprehensive analytics data
        """
        # Calculate date range for filtered analysis
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_months * 30)
        
        return {
            'monthly_spending': AnalyticsService.get_monthly_spending(user_id),
            'category_analysis': AnalyticsService.get_category_spending_analysis(
                user_id, start_date, end_date
            ),
            'store_analysis': AnalyticsService.get_store_spending_analysis(
                user_id, start_date, end_date
            ),
            'spending_trends': AnalyticsService.get_spending_trends(user_id, period_months),
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'months': period_months
            }
        }