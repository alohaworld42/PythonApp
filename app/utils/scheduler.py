import threading
import time
import logging
from datetime import datetime, timedelta

try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False
    schedule = None
from flask import current_app
from app import db
from app.models.store_integration import StoreIntegration
from app.integrations.shopify import ShopifyClient
from app.integrations.woocommerce import sync_woocommerce_orders
from app.models.user import User

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global flag to control the scheduler thread
scheduler_running = False
scheduler_thread = None

def sync_all_integrations():
    """Sync all store integrations that need updating."""
    with current_app.app_context():
        # Get integrations that haven't been synced in the last 6 hours
        six_hours_ago = datetime.utcnow() - timedelta(hours=6)
        integrations = StoreIntegration.query.filter(
            (StoreIntegration.last_sync == None) | 
            (StoreIntegration.last_sync < six_hours_ago)
        ).all()
        
        logger.info(f"Found {len(integrations)} integrations to sync")
        
        for integration in integrations:
            try:
                if integration.platform == 'shopify':
                    logger.info(f"Syncing Shopify integration {integration.id}")
                    user = User.query.get(integration.user_id)
                    if user:
                        client = ShopifyClient(integration)
                        client.sync_orders_for_user(user)
                    else:
                        logger.error(f"User not found for integration: {integration.id}")
                elif integration.platform == 'woocommerce':
                    logger.info(f"Syncing WooCommerce integration {integration.id}")
                    sync_woocommerce_orders(integration.id)
                else:
                    logger.warning(f"Unknown platform: {integration.platform}")
            except Exception as e:
                logger.error(f"Error syncing integration {integration.id}: {e}")

def sync_integration(integration_id):
    """Sync a specific integration."""
    with current_app.app_context():
        integration = StoreIntegration.query.get(integration_id)
        if not integration:
            logger.error(f"Integration not found: {integration_id}")
            return False
        
        try:
            if integration.platform == 'shopify':
                logger.info(f"Syncing Shopify integration {integration.id}")
                user = User.query.get(integration.user_id)
                if user:
                    client = ShopifyClient(integration)
                    count = client.sync_orders_for_user(user)
                    return count > 0
                else:
                    logger.error(f"User not found for integration: {integration.id}")
                    return False
            elif integration.platform == 'woocommerce':
                logger.info(f"Syncing WooCommerce integration {integration.id}")
                return sync_woocommerce_orders(integration.id)
            else:
                logger.warning(f"Unknown platform: {integration.platform}")
                return False
        except Exception as e:
            logger.error(f"Error syncing integration {integration.id}: {e}")
            return False

def run_scheduler():
    """Run the scheduler in a loop."""
    global scheduler_running
    
    if not SCHEDULE_AVAILABLE:
        logger.warning("Schedule module not available, scheduler disabled")
        return
    
    logger.info("Starting scheduler thread")
    
    # Schedule the sync job to run every hour
    schedule.every(1).hours.do(sync_all_integrations)
    
    # Run the scheduler loop
    while scheduler_running:
        schedule.run_pending()
        time.sleep(60)  # Check every minute
    
    logger.info("Scheduler thread stopped")

def start_scheduler(app):
    """Start the scheduler thread."""
    global scheduler_running, scheduler_thread
    
    if scheduler_thread and scheduler_thread.is_alive():
        logger.warning("Scheduler is already running")
        return
    
    scheduler_running = True
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    # Run an initial sync
    with app.app_context():
        sync_all_integrations()
    
    logger.info("Scheduler started")

def stop_scheduler():
    """Stop the scheduler thread."""
    global scheduler_running, scheduler_thread
    
    if not scheduler_thread or not scheduler_thread.is_alive():
        logger.warning("Scheduler is not running")
        return
    
    scheduler_running = False
    scheduler_thread.join(timeout=5)
    
    if scheduler_thread.is_alive():
        logger.warning("Scheduler thread did not stop gracefully")
    else:
        logger.info("Scheduler stopped")
        scheduler_thread = None

def init_scheduler(app):
    """Initialize the scheduler for the Flask app."""
    if not SCHEDULE_AVAILABLE:
        logger.warning("Schedule module not available, scheduler initialization skipped")
        return
    
    start_scheduler(app)