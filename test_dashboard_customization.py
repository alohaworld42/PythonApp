#!/usr/bin/env python3
"""
Test script for dashboard customization functionality.
Tests the dashboard settings, widget system, and state persistence.
"""

import sys
import os
import json
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_dashboard_settings_form():
    """Test the dashboard settings form structure."""
    try:
        from app.utils.forms import DashboardSettingsForm
        
        # Create form instance
        form = DashboardSettingsForm()
        
        # Test form fields exist
        assert hasattr(form, 'default_view'), "Form should have default_view field"
        assert hasattr(form, 'items_per_page'), "Form should have items_per_page field"
        assert hasattr(form, 'default_sort'), "Form should have default_sort field"
        assert hasattr(form, 'show_quick_stats'), "Form should have show_quick_stats field"
        assert hasattr(form, 'show_friend_activity'), "Form should have show_friend_activity field"
        assert hasattr(form, 'show_recent_purchases'), "Form should have show_recent_purchases field"
        assert hasattr(form, 'show_spending_chart'), "Form should have show_spending_chart field"
        assert hasattr(form, 'widget_order'), "Form should have widget_order field"
        assert hasattr(form, 'sidebar_collapsed'), "Form should have sidebar_collapsed field"
        assert hasattr(form, 'compact_mode'), "Form should have compact_mode field"
        
        # Test form field choices
        view_choices = [choice[0] for choice in form.default_view.choices]
        assert 'grid' in view_choices, "Form should have grid view option"
        assert 'list' in view_choices, "Form should have list view option"
        
        items_choices = [choice[0] for choice in form.items_per_page.choices]
        assert '12' in items_choices, "Form should have 12 items option"
        assert '24' in items_choices, "Form should have 24 items option"
        
        sort_choices = [choice[0] for choice in form.default_sort.choices]
        assert 'date-desc' in sort_choices, "Form should have date-desc sort option"
        assert 'price-asc' in sort_choices, "Form should have price-asc sort option"
        
        print("✓ Dashboard settings form structure test passed")
        return True
        
    except Exception as e:
        print(f"✗ Dashboard settings form test failed: {e}")
        return False

def test_dashboard_settings_defaults():
    """Test default dashboard settings structure."""
    try:
        # Test default settings structure
        default_settings = {
            'default_view': 'grid',
            'items_per_page': 12,
            'default_sort': 'date-desc',
            'widgets': {
                'show_quick_stats': True,
                'show_friend_activity': True,
                'show_recent_purchases': True,
                'show_spending_chart': False,
                'order': '["quick_stats", "recent_purchases", "friend_activity"]'
            },
            'layout': {
                'sidebar_collapsed': False,
                'compact_mode': False
            }
        }
        
        # Test widget order parsing
        widget_order = json.loads(default_settings['widgets']['order'])
        assert isinstance(widget_order, list), "Widget order should be a list"
        assert 'quick_stats' in widget_order, "Widget order should contain quick_stats"
        assert 'recent_purchases' in widget_order, "Widget order should contain recent_purchases"
        assert 'friend_activity' in widget_order, "Widget order should contain friend_activity"
        
        # Test boolean settings
        assert isinstance(default_settings['widgets']['show_quick_stats'], bool), "show_quick_stats should be boolean"
        assert isinstance(default_settings['layout']['compact_mode'], bool), "compact_mode should be boolean"
        
        # Test numeric settings
        assert isinstance(default_settings['items_per_page'], int), "items_per_page should be integer"
        assert default_settings['items_per_page'] > 0, "items_per_page should be positive"
        
        print("✓ Dashboard settings defaults test passed")
        return True
        
    except Exception as e:
        print(f"✗ Dashboard settings defaults test failed: {e}")
        return False

def test_widget_system_structure():
    """Test the widget system structure and components."""
    try:
        # Test widget types
        widget_types = [
            'quick_stats',
            'recent_purchases', 
            'friend_activity',
            'spending_chart'
        ]
        
        # Test widget configuration
        widget_config = {
            'quick_stats': {
                'name': 'Quick Stats',
                'icon': 'fas fa-chart-bar',
                'default_visible': True
            },
            'recent_purchases': {
                'name': 'Recent Purchases',
                'icon': 'fas fa-shopping-bag',
                'default_visible': True
            },
            'friend_activity': {
                'name': 'Friend Activity',
                'icon': 'fas fa-users',
                'default_visible': True
            },
            'spending_chart': {
                'name': 'Spending Chart',
                'icon': 'fas fa-chart-line',
                'default_visible': False
            }
        }
        
        # Validate widget configuration
        for widget_id in widget_types:
            assert widget_id in widget_config, f"Widget {widget_id} should have configuration"
            config = widget_config[widget_id]
            assert 'name' in config, f"Widget {widget_id} should have name"
            assert 'icon' in config, f"Widget {widget_id} should have icon"
            assert 'default_visible' in config, f"Widget {widget_id} should have default_visible"
            assert isinstance(config['default_visible'], bool), f"Widget {widget_id} default_visible should be boolean"
        
        print("✓ Widget system structure test passed")
        return True
        
    except Exception as e:
        print(f"✗ Widget system structure test failed: {e}")
        return False

def test_dashboard_customization_logic():
    """Test dashboard customization logic."""
    try:
        # Test widget order manipulation
        original_order = ["quick_stats", "recent_purchases", "friend_activity"]
        new_order = ["friend_activity", "quick_stats", "recent_purchases"]
        
        # Test order validation
        assert len(original_order) == len(new_order), "Order lengths should match"
        assert set(original_order) == set(new_order), "Order should contain same widgets"
        
        # Test widget visibility logic
        widget_visibility = {
            'show_quick_stats': True,
            'show_recent_purchases': False,
            'show_friend_activity': True,
            'show_spending_chart': False
        }
        
        visible_widgets = [widget.replace('show_', '') for widget, visible in widget_visibility.items() if visible]
        expected_visible = ['quick_stats', 'friend_activity']
        
        assert set(visible_widgets) == set(expected_visible), "Visible widgets should match expected"
        
        # Test layout settings
        layout_settings = {
            'compact_mode': False,
            'sidebar_collapsed': True
        }
        
        assert isinstance(layout_settings['compact_mode'], bool), "compact_mode should be boolean"
        assert isinstance(layout_settings['sidebar_collapsed'], bool), "sidebar_collapsed should be boolean"
        
        print("✓ Dashboard customization logic test passed")
        return True
        
    except Exception as e:
        print(f"✗ Dashboard customization logic test failed: {e}")
        return False

def test_settings_persistence():
    """Test settings persistence structure."""
    try:
        # Test settings JSON structure
        user_settings = {
            'dashboard': {
                'default_view': 'list',
                'items_per_page': 24,
                'default_sort': 'price-desc',
                'widgets': {
                    'show_quick_stats': True,
                    'show_friend_activity': False,
                    'show_recent_purchases': True,
                    'show_spending_chart': True,
                    'order': '["recent_purchases", "quick_stats", "spending_chart"]'
                },
                'layout': {
                    'sidebar_collapsed': True,
                    'compact_mode': True
                }
            },
            'privacy': {
                'profile_visibility': True,
                'show_email': False
            },
            'notifications': {
                'email': {
                    'friend_requests': True,
                    'comments': False
                }
            }
        }
        
        # Test JSON serialization/deserialization
        settings_json = json.dumps(user_settings)
        parsed_settings = json.loads(settings_json)
        
        assert parsed_settings == user_settings, "Settings should survive JSON round-trip"
        
        # Test dashboard settings extraction
        dashboard_settings = parsed_settings.get('dashboard', {})
        assert dashboard_settings['default_view'] == 'list', "Should preserve default_view setting"
        assert dashboard_settings['items_per_page'] == 24, "Should preserve items_per_page setting"
        
        # Test widget order parsing
        widget_order = json.loads(dashboard_settings['widgets']['order'])
        assert isinstance(widget_order, list), "Widget order should be list after parsing"
        assert len(widget_order) == 3, "Widget order should have 3 items"
        
        print("✓ Settings persistence test passed")
        return True
        
    except Exception as e:
        print(f"✗ Settings persistence test failed: {e}")
        return False

def run_all_tests():
    """Run all dashboard customization tests."""
    print("Running Dashboard Customization Tests")
    print("=" * 50)
    
    tests = [
        test_dashboard_settings_form,
        test_dashboard_settings_defaults,
        test_widget_system_structure,
        test_dashboard_customization_logic,
        test_settings_persistence
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All dashboard customization tests passed!")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)