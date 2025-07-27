from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app.services.analytics_service import AnalyticsService

api_analytics_bp = Blueprint('api_analytics', __name__)

@api_analytics_bp.route('/analytics/spending', methods=['GET'])
@login_required
def get_spending_analytics():
    """API endpoint to get monthly spending analytics."""
    try:
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)
        
        # Validate year and month if provided
        if year and (year < 2000 or year > datetime.now().year + 1):
            return jsonify({'error': 'Invalid year provided'}), 400
        
        if month and (month < 1 or month > 12):
            return jsonify({'error': 'Invalid month provided (must be 1-12)'}), 400
        
        analytics_data = AnalyticsService.get_monthly_spending(
            current_user.id, year=year, month=month
        )
        
        return jsonify({
            'success': True,
            'data': analytics_data,
            'filters': {
                'year': year,
                'month': month
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get spending analytics error: {str(e)}")
        return jsonify({'error': 'Failed to get spending analytics'}), 500

@api_analytics_bp.route('/analytics/categories', methods=['GET'])
@login_required
def get_category_analytics():
    """API endpoint to get category-based spending analytics."""
    try:
        # Get date range from query parameters
        period_months = request.args.get('period_months', 12, type=int)
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        # Validate period_months
        if period_months < 1 or period_months > 60:  # Max 5 years
            return jsonify({'error': 'Period months must be between 1 and 60'}), 400
        
        # Parse custom date range if provided
        start_date = None
        end_date = None
        
        if start_date_str:
            try:
                start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid start_date format. Use ISO format (YYYY-MM-DD)'}), 400
        
        if end_date_str:
            try:
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid end_date format. Use ISO format (YYYY-MM-DD)'}), 400
        
        # Use period_months if custom dates not provided
        if not start_date and not end_date:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_months * 30)
        
        # Validate date range
        if start_date and end_date and start_date > end_date:
            return jsonify({'error': 'Start date must be before end date'}), 400
        
        analytics_data = AnalyticsService.get_category_spending_analysis(
            current_user.id, start_date=start_date, end_date=end_date
        )
        
        return jsonify({
            'success': True,
            'data': analytics_data,
            'filters': {
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None,
                'period_months': period_months
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get category analytics error: {str(e)}")
        return jsonify({'error': 'Failed to get category analytics'}), 500

@api_analytics_bp.route('/analytics/stores', methods=['GET'])
@login_required
def get_store_analytics():
    """API endpoint to get store-based spending analytics."""
    try:
        # Get date range from query parameters
        period_months = request.args.get('period_months', 12, type=int)
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        # Validate period_months
        if period_months < 1 or period_months > 60:  # Max 5 years
            return jsonify({'error': 'Period months must be between 1 and 60'}), 400
        
        # Parse custom date range if provided
        start_date = None
        end_date = None
        
        if start_date_str:
            try:
                start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid start_date format. Use ISO format (YYYY-MM-DD)'}), 400
        
        if end_date_str:
            try:
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid end_date format. Use ISO format (YYYY-MM-DD)'}), 400
        
        # Use period_months if custom dates not provided
        if not start_date and not end_date:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_months * 30)
        
        # Validate date range
        if start_date and end_date and start_date > end_date:
            return jsonify({'error': 'Start date must be before end date'}), 400
        
        analytics_data = AnalyticsService.get_store_spending_analysis(
            current_user.id, start_date=start_date, end_date=end_date
        )
        
        return jsonify({
            'success': True,
            'data': analytics_data,
            'filters': {
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None,
                'period_months': period_months
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get store analytics error: {str(e)}")
        return jsonify({'error': 'Failed to get store analytics'}), 500

@api_analytics_bp.route('/analytics/trends', methods=['GET'])
@login_required
def get_trend_analytics():
    """API endpoint to get spending trend analytics."""
    try:
        period_months = request.args.get('period_months', 12, type=int)
        
        # Validate period_months
        if period_months < 1 or period_months > 60:  # Max 5 years
            return jsonify({'error': 'Period months must be between 1 and 60'}), 400
        
        analytics_data = AnalyticsService.get_spending_trends(
            current_user.id, period_months=period_months
        )
        
        return jsonify({
            'success': True,
            'data': analytics_data,
            'filters': {
                'period_months': period_months
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get trend analytics error: {str(e)}")
        return jsonify({'error': 'Failed to get trend analytics'}), 500

@api_analytics_bp.route('/analytics/comprehensive', methods=['GET'])
@login_required
def get_comprehensive_analytics():
    """API endpoint to get comprehensive analytics combining all analysis types."""
    try:
        period_months = request.args.get('period_months', 12, type=int)
        
        # Validate period_months
        if period_months < 1 or period_months > 60:  # Max 5 years
            return jsonify({'error': 'Period months must be between 1 and 60'}), 400
        
        analytics_data = AnalyticsService.get_comprehensive_analytics(
            current_user.id, period_months=period_months
        )
        
        return jsonify({
            'success': True,
            'data': analytics_data,
            'filters': {
                'period_months': period_months
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get comprehensive analytics error: {str(e)}")
        return jsonify({'error': 'Failed to get comprehensive analytics'}), 500

@api_analytics_bp.route('/analytics/summary', methods=['GET'])
@login_required
def get_analytics_summary():
    """API endpoint to get a quick analytics summary."""
    try:
        # Get basic statistics for the current user
        from app.models.purchase import Purchase
        from app.models.product import Product
        from app import db
        from sqlalchemy import func
        
        # Total purchases and spending
        total_stats = db.session.query(
            func.count(Purchase.id).label('total_purchases'),
            func.sum(Product.price).label('total_spending'),
            func.avg(Product.price).label('avg_purchase_price'),
            func.min(Purchase.purchase_date).label('first_purchase'),
            func.max(Purchase.purchase_date).label('last_purchase')
        ).join(Product).filter(Purchase.user_id == current_user.id).first()
        
        # This month's spending
        current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        current_month_stats = db.session.query(
            func.count(Purchase.id).label('month_purchases'),
            func.sum(Product.price).label('month_spending')
        ).join(Product).filter(
            Purchase.user_id == current_user.id,
            Purchase.purchase_date >= current_month_start
        ).first()
        
        # Last month's spending for comparison
        last_month_end = current_month_start - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)
        last_month_stats = db.session.query(
            func.sum(Product.price).label('last_month_spending')
        ).join(Product).filter(
            Purchase.user_id == current_user.id,
            Purchase.purchase_date >= last_month_start,
            Purchase.purchase_date <= last_month_end
        ).first()
        
        # Top category this month
        top_category = db.session.query(
            Product.category,
            func.sum(Product.price).label('category_spending')
        ).join(Purchase).filter(
            Purchase.user_id == current_user.id,
            Purchase.purchase_date >= current_month_start
        ).group_by(Product.category).order_by(
            func.sum(Product.price).desc()
        ).first()
        
        # Calculate month-over-month change
        current_month_spending = float(current_month_stats.month_spending or 0)
        last_month_spending = float(last_month_stats.last_month_spending or 0)
        
        month_change = 0
        month_change_percentage = 0
        if last_month_spending > 0:
            month_change = current_month_spending - last_month_spending
            month_change_percentage = (month_change / last_month_spending) * 100
        
        summary_data = {
            'total_statistics': {
                'total_purchases': total_stats.total_purchases or 0,
                'total_spending': float(total_stats.total_spending or 0),
                'avg_purchase_price': float(total_stats.avg_purchase_price or 0),
                'first_purchase': total_stats.first_purchase.isoformat() if total_stats.first_purchase else None,
                'last_purchase': total_stats.last_purchase.isoformat() if total_stats.last_purchase else None
            },
            'current_month': {
                'purchases': current_month_stats.month_purchases or 0,
                'spending': current_month_spending,
                'top_category': top_category.category if top_category else None,
                'top_category_spending': float(top_category.category_spending) if top_category else 0
            },
            'month_comparison': {
                'last_month_spending': last_month_spending,
                'change_amount': round(month_change, 2),
                'change_percentage': round(month_change_percentage, 2),
                'trend': 'up' if month_change > 0 else 'down' if month_change < 0 else 'stable'
            }
        }
        
        return jsonify({
            'success': True,
            'data': summary_data
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get analytics summary error: {str(e)}")
        return jsonify({'error': 'Failed to get analytics summary'}), 500

@api_analytics_bp.route('/analytics/export', methods=['GET'])
@login_required
def export_analytics():
    """API endpoint to export analytics data in various formats."""
    try:
        export_format = request.args.get('format', 'json').lower()
        period_months = request.args.get('period_months', 12, type=int)
        
        if export_format not in ['json', 'csv']:
            return jsonify({'error': 'Supported formats: json, csv'}), 400
        
        # Validate period_months
        if period_months < 1 or period_months > 60:
            return jsonify({'error': 'Period months must be between 1 and 60'}), 400
        
        # Get comprehensive analytics data
        analytics_data = AnalyticsService.get_comprehensive_analytics(
            current_user.id, period_months=period_months
        )
        
        if export_format == 'json':
            return jsonify({
                'success': True,
                'data': analytics_data,
                'export_info': {
                    'format': 'json',
                    'generated_at': datetime.now().isoformat(),
                    'user_id': current_user.id,
                    'period_months': period_months
                }
            }), 200
        
        elif export_format == 'csv':
            # For CSV export, we'll return the data in a format that can be easily converted to CSV
            # In a real implementation, you might want to use the csv module or pandas
            csv_data = {
                'monthly_spending': analytics_data['monthly_spending']['monthly_spending'],
                'category_analysis': analytics_data['category_analysis']['category_analysis'],
                'store_analysis': analytics_data['store_analysis']['store_analysis'],
                'spending_trends': analytics_data['spending_trends']['trends_data']
            }
            
            return jsonify({
                'success': True,
                'data': csv_data,
                'export_info': {
                    'format': 'csv',
                    'generated_at': datetime.now().isoformat(),
                    'user_id': current_user.id,
                    'period_months': period_months,
                    'note': 'Convert the data arrays to CSV format on the client side'
                }
            }), 200
        
    except Exception as e:
        current_app.logger.error(f"Export analytics error: {str(e)}")
        return jsonify({'error': 'Failed to export analytics'}), 500

@api_analytics_bp.route('/analytics/insights', methods=['GET'])
@login_required
def get_spending_insights():
    """API endpoint to get AI-like spending insights and recommendations."""
    try:
        period_months = request.args.get('period_months', 6, type=int)
        
        # Validate period_months
        if period_months < 1 or period_months > 24:
            return jsonify({'error': 'Period months must be between 1 and 24'}), 400
        
        # Get analytics data for insights
        analytics_data = AnalyticsService.get_comprehensive_analytics(
            current_user.id, period_months=period_months
        )
        
        insights = []
        
        # Analyze spending trends
        trends = analytics_data['spending_trends']['statistics']
        if trends['trend_direction'] == 'increasing':
            insights.append({
                'type': 'trend',
                'level': 'warning',
                'title': 'Increasing Spending Trend',
                'message': f"Your spending has been increasing over the last {period_months} months. "
                          f"Average monthly spending is ${trends['avg_monthly_spending']:.2f}.",
                'recommendation': 'Consider reviewing your budget and identifying areas where you can reduce spending.'
            })
        elif trends['trend_direction'] == 'decreasing':
            insights.append({
                'type': 'trend',
                'level': 'positive',
                'title': 'Decreasing Spending Trend',
                'message': f"Great job! Your spending has been decreasing over the last {period_months} months.",
                'recommendation': 'Keep up the good work with your spending discipline.'
            })
        
        # Analyze top categories
        categories = analytics_data['category_analysis']['category_analysis']
        if categories:
            top_category = categories[0]
            if top_category['percentage'] > 50:
                insights.append({
                    'type': 'category',
                    'level': 'info',
                    'title': 'Dominant Spending Category',
                    'message': f"You spend {top_category['percentage']:.1f}% of your budget on {top_category['category']}.",
                    'recommendation': 'Consider diversifying your spending or finding ways to reduce costs in this category.'
                })
        
        # Analyze store concentration
        stores = analytics_data['store_analysis']['store_analysis']
        if stores:
            top_store = stores[0]
            if top_store['percentage'] > 40:
                insights.append({
                    'type': 'store',
                    'level': 'info',
                    'title': 'Favorite Store',
                    'message': f"You spend {top_store['percentage']:.1f}% of your budget at {top_store['store_name']}.",
                    'recommendation': 'Compare prices with other stores to ensure you\'re getting the best deals.'
                })
        
        # Monthly spending variance insight
        monthly_data = analytics_data['monthly_spending']['monthly_spending']
        if len(monthly_data) >= 3:
            spending_amounts = [month['total_spending'] for month in monthly_data[:6]]  # Last 6 months
            avg_spending = sum(spending_amounts) / len(spending_amounts)
            variance = sum((x - avg_spending) ** 2 for x in spending_amounts) / len(spending_amounts)
            std_dev = variance ** 0.5
            
            if std_dev > avg_spending * 0.3:  # High variance (30% of average)
                insights.append({
                    'type': 'variance',
                    'level': 'warning',
                    'title': 'Irregular Spending Pattern',
                    'message': 'Your monthly spending varies significantly. This might indicate irregular budgeting.',
                    'recommendation': 'Try to establish a more consistent monthly budget to better control your expenses.'
                })
        
        # Budget recommendations based on spending patterns
        if trends['avg_monthly_spending'] > 0:
            suggested_budget = trends['avg_monthly_spending'] * 0.9  # 10% reduction
            insights.append({
                'type': 'budget',
                'level': 'suggestion',
                'title': 'Budget Recommendation',
                'message': f"Based on your spending patterns, consider setting a monthly budget of ${suggested_budget:.2f}.",
                'recommendation': 'This represents a 10% reduction from your current average spending.'
            })
        
        return jsonify({
            'success': True,
            'data': {
                'insights': insights,
                'analysis_period': {
                    'months': period_months,
                    'start_date': analytics_data['period']['start_date'],
                    'end_date': analytics_data['period']['end_date']
                },
                'summary_stats': trends
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get spending insights error: {str(e)}")
        return jsonify({'error': 'Failed to get spending insights'}), 500