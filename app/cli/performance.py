"""
CLI commands for performance optimization.
"""

import click
from flask import current_app
from flask.cli import with_appcontext
from app.utils.database_optimization import QueryOptimizer, vacuum_database
from app.utils.asset_optimization import AssetOptimizer, AssetBundler, create_asset_manifest
from app.utils.cache import CacheManager
from app.utils.performance_monitor import performance_monitor, get_performance_recommendations

@click.group()
def performance():
    """Performance optimization commands."""
    pass

@performance.command()
@with_appcontext
def create_indexes():
    """Create database indexes for better query performance."""
    click.echo("Creating database indexes...")
    try:
        QueryOptimizer.create_indexes()
        click.echo("✅ Database indexes created successfully")
    except Exception as e:
        click.echo(f"❌ Error creating indexes: {str(e)}")

@performance.command()
@with_appcontext
def analyze_queries():
    """Analyze database query performance."""
    click.echo("Analyzing query performance...")
    try:
        analysis = QueryOptimizer.analyze_query_performance()
        
        if 'error' in analysis:
            click.echo(f"❌ Error: {analysis['error']}")
            return
        
        click.echo(f"📊 Analyzed {analysis['total_queries_analyzed']} queries")
        
        if analysis['slow_queries']:
            click.echo("\n🐌 Slow queries detected:")
            for query in analysis['slow_queries']:
                click.echo(f"  • {query['query']}: {query['time']:.3f}s")
                click.echo(f"    Recommendation: {query['recommendation']}")
        else:
            click.echo("✅ No slow queries detected")
        
        click.echo("\n💡 General recommendations:")
        for rec in analysis['recommendations']:
            click.echo(f"  • {rec}")
            
    except Exception as e:
        click.echo(f"❌ Error analyzing queries: {str(e)}")

@performance.command()
@with_appcontext
def vacuum_db():
    """Perform database maintenance (VACUUM)."""
    click.echo("Performing database maintenance...")
    try:
        vacuum_database()
        click.echo("✅ Database maintenance completed")
    except Exception as e:
        click.echo(f"❌ Error during database maintenance: {str(e)}")

@performance.command()
@with_appcontext
def compress_assets():
    """Compress static assets for better performance."""
    click.echo("Compressing static assets...")
    try:
        compressed_files = AssetOptimizer.compress_static_files()
        click.echo(f"✅ Compressed {len(compressed_files)} files")
        
        for file in compressed_files[:10]:  # Show first 10
            click.echo(f"  • {file}")
        
        if len(compressed_files) > 10:
            click.echo(f"  ... and {len(compressed_files) - 10} more files")
            
    except Exception as e:
        click.echo(f"❌ Error compressing assets: {str(e)}")

@performance.command()
@with_appcontext
def bundle_assets():
    """Bundle CSS and JavaScript assets."""
    click.echo("Bundling assets...")
    try:
        bundler = AssetBundler()
        
        # Add CSS files to bundle
        bundler.add_css('main.css')
        
        # Add JS files to bundle
        bundler.add_js('main.js')
        bundler.add_js('analytics.js')
        
        # Create bundles
        css_bundle = bundler.bundle_css('bundle.min.css')
        js_bundle = bundler.bundle_js('bundle.min.js')
        
        click.echo(f"✅ Created CSS bundle: {css_bundle}")
        click.echo(f"✅ Created JS bundle: {js_bundle}")
        
    except Exception as e:
        click.echo(f"❌ Error bundling assets: {str(e)}")

@performance.command()
@with_appcontext
def create_manifest():
    """Create asset manifest for versioning."""
    click.echo("Creating asset manifest...")
    try:
        manifest = create_asset_manifest()
        click.echo(f"✅ Created manifest with {len(manifest)} assets")
        
        # Show some examples
        for asset, versioned in list(manifest.items())[:5]:
            click.echo(f"  • {asset} → {versioned}")
            
    except Exception as e:
        click.echo(f"❌ Error creating manifest: {str(e)}")

@performance.command()
@with_appcontext
def cache_stats():
    """Show cache statistics."""
    click.echo("Cache Statistics:")
    try:
        stats = CacheManager.get_cache_stats()
        
        click.echo(f"  Total entries: {stats['total_entries']}")
        click.echo(f"  Memory usage estimate: {stats['memory_usage_estimate']} bytes")
        click.echo(f"  Expired entries cleaned: {stats['expired_entries_cleaned']}")
        
    except Exception as e:
        click.echo(f"❌ Error getting cache stats: {str(e)}")

@performance.command()
@with_appcontext
def clear_cache():
    """Clear application cache."""
    click.echo("Clearing cache...")
    try:
        from app.utils.cache import cache
        cache.clear()
        click.echo("✅ Cache cleared successfully")
        
    except Exception as e:
        click.echo(f"❌ Error clearing cache: {str(e)}")

@performance.command()
@click.option('--minutes', default=60, help='Time period in minutes to analyze')
@with_appcontext
def monitor_summary(minutes):
    """Show performance monitoring summary."""
    click.echo(f"Performance Summary (last {minutes} minutes):")
    try:
        summary = performance_monitor.get_performance_summary(minutes)
        
        # Request statistics
        req_stats = summary['request_stats']
        click.echo(f"\n📊 Request Statistics:")
        click.echo(f"  Total requests: {req_stats['total_requests']}")
        click.echo(f"  Average response time: {req_stats['avg_response_time']:.3f}s")
        click.echo(f"  Max response time: {req_stats['max_response_time']:.3f}s")
        click.echo(f"  Requests per minute: {req_stats['requests_per_minute']:.1f}")
        
        # Database statistics
        db_stats = summary['database_stats']
        click.echo(f"\n🗄️  Database Statistics:")
        click.echo(f"  Total queries: {db_stats['total_queries']}")
        click.echo(f"  Average query time: {db_stats['avg_query_time']:.3f}s")
        click.echo(f"  Max query time: {db_stats['max_query_time']:.3f}s")
        
        # Cache statistics
        cache_stats = summary['cache_stats']
        click.echo(f"\n💾 Cache Statistics:")
        click.echo(f"  Cache hits: {cache_stats['cache_hits']}")
        click.echo(f"  Cache misses: {cache_stats['cache_misses']}")
        click.echo(f"  Hit rate: {cache_stats['cache_hit_rate']:.1f}%")
        
        # System statistics
        if summary['system_stats']:
            sys_stats = summary['system_stats']
            click.echo(f"\n🖥️  System Statistics:")
            click.echo(f"  CPU usage: {sys_stats['cpu_percent']:.1f}%")
            click.echo(f"  Memory usage: {sys_stats['memory_percent']:.1f}%")
            click.echo(f"  Disk usage: {sys_stats['disk_percent']:.1f}%")
        
    except Exception as e:
        click.echo(f"❌ Error getting performance summary: {str(e)}")

@performance.command()
@with_appcontext
def recommendations():
    """Get performance optimization recommendations."""
    click.echo("Performance Recommendations:")
    try:
        recs = get_performance_recommendations()
        
        if not recs:
            click.echo("✅ No performance issues detected")
            return
        
        for rec in recs:
            severity_icon = {
                'high': '🔴',
                'medium': '🟡',
                'low': '🟢'
            }.get(rec['severity'], '⚪')
            
            click.echo(f"\n{severity_icon} {rec['type'].upper()}: {rec['message']}")
            click.echo(f"   💡 {rec['suggestion']}")
            
    except Exception as e:
        click.echo(f"❌ Error getting recommendations: {str(e)}")

@performance.command()
@click.option('--threshold', default=1.0, help='Response time threshold in seconds')
@click.option('--minutes', default=60, help='Time period in minutes to analyze')
@with_appcontext
def slow_endpoints(threshold, minutes):
    """Show slow endpoints."""
    click.echo(f"Slow Endpoints (>{threshold}s in last {minutes} minutes):")
    try:
        slow = performance_monitor.get_slow_endpoints(threshold, minutes)
        
        if not slow:
            click.echo("✅ No slow endpoints detected")
            return
        
        for endpoint, stats in slow:
            click.echo(f"\n🐌 {endpoint}")
            click.echo(f"   Count: {stats['count']}")
            click.echo(f"   Average: {stats['avg_time']:.3f}s")
            click.echo(f"   Maximum: {stats['max_time']:.3f}s")
            
    except Exception as e:
        click.echo(f"❌ Error getting slow endpoints: {str(e)}")

@performance.command()
@with_appcontext
def table_stats():
    """Show database table statistics."""
    click.echo("Database Table Statistics:")
    try:
        from app.utils.database_optimization import analyze_table_statistics
        stats = analyze_table_statistics()
        
        if not stats:
            click.echo("No table statistics available")
            return
        
        # Sort tables by row count
        sorted_tables = sorted(stats.items(), key=lambda x: x[1]['row_count'], reverse=True)
        
        click.echo(f"\n{'Table':<20} {'Rows':<10} {'Columns':<8} {'Indexes':<8} {'Est. Size (KB)':<15}")
        click.echo("-" * 70)
        
        for table_name, table_stats in sorted_tables:
            click.echo(f"{table_name:<20} {table_stats['row_count']:<10} "
                      f"{table_stats['column_count']:<8} {table_stats['index_count']:<8} "
                      f"{table_stats['estimated_size_kb']:<15.1f}")
        
        # Summary
        total_rows = sum(stats[table]['row_count'] for table in stats)
        total_size = sum(stats[table]['estimated_size_kb'] for table in stats)
        
        click.echo(f"\nTotal rows: {total_rows:,}")
        click.echo(f"Estimated total size: {total_size:.1f} KB")
        
    except Exception as e:
        click.echo(f"❌ Error getting table statistics: {str(e)}")

@performance.command()
@click.argument('query')
@with_appcontext
def explain_query(query):
    """Explain query execution plan."""
    click.echo(f"Query execution plan for: {query}")
    try:
        from app.utils.database_optimization import get_query_execution_plan
        plan = get_query_execution_plan(query)
        
        if not plan:
            click.echo("No execution plan available")
            return
        
        click.echo("\nExecution Plan:")
        for step in plan:
            click.echo(f"  ID: {step['id']}, Parent: {step['parent']}")
            click.echo(f"  Detail: {step['detail']}")
            click.echo()
        
    except Exception as e:
        click.echo(f"❌ Error explaining query: {str(e)}")

@performance.command()
@with_appcontext
def optimize_all():
    """Run all performance optimizations."""
    click.echo("Running comprehensive performance optimization...")
    
    # Apply SQLite optimizations
    click.echo("\n1. Applying SQLite optimizations...")
    try:
        from app.utils.database_optimization import optimize_sqlite_settings
        optimize_sqlite_settings()
        click.echo("✅ SQLite optimizations applied")
    except Exception as e:
        click.echo(f"❌ Error applying SQLite optimizations: {str(e)}")
    
    # Create database indexes
    click.echo("\n2. Creating database indexes...")
    try:
        QueryOptimizer.create_indexes()
        click.echo("✅ Database indexes created")
    except Exception as e:
        click.echo(f"❌ Error creating indexes: {str(e)}")
    
    # Vacuum database
    click.echo("\n3. Performing database maintenance...")
    try:
        vacuum_database()
        click.echo("✅ Database maintenance completed")
    except Exception as e:
        click.echo(f"❌ Error during maintenance: {str(e)}")
    
    # Compress assets
    click.echo("\n4. Compressing static assets...")
    try:
        compressed_files = AssetOptimizer.compress_static_files()
        click.echo(f"✅ Compressed {len(compressed_files)} files")
    except Exception as e:
        click.echo(f"❌ Error compressing assets: {str(e)}")
    
    # Create asset manifest
    click.echo("\n5. Creating asset manifest...")
    try:
        manifest = create_asset_manifest()
        click.echo(f"✅ Created manifest with {len(manifest)} assets")
    except Exception as e:
        click.echo(f"❌ Error creating manifest: {str(e)}")
    
    # Clean up cache
    click.echo("\n6. Cleaning up cache...")
    try:
        cleaned = CacheManager.schedule_cache_cleanup()
        click.echo(f"✅ Cleaned {cleaned} expired cache entries")
    except Exception as e:
        click.echo(f"❌ Error cleaning cache: {str(e)}")
    
    click.echo("\n🎉 Performance optimization completed!")

def init_performance_cli(app):
    """Initialize performance CLI commands."""
    app.cli.add_command(performance)