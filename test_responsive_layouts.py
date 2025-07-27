#!/usr/bin/env python3
"""
Test script to verify responsive layout implementation
Tests the CSS grid system, responsive containers, typography, and breakpoints
"""

import os
import re
from pathlib import Path

def test_responsive_css():
    """Test that the responsive CSS contains all required components"""
    css_file = Path("app/static/css/main.css")
    
    if not css_file.exists():
        print("❌ CSS file not found")
        return False
    
    css_content = css_file.read_text()
    
    # Test for responsive grid system
    grid_tests = [
        r"\.grid-cols-1.*grid-template-columns.*repeat\(1",
        r"\.sm\\:grid-cols-2.*grid-template-columns.*repeat\(2",
        r"\.md\\:grid-cols-3.*grid-template-columns.*repeat\(3",
        r"\.lg\\:grid-cols-4.*grid-template-columns.*repeat\(4",
    ]
    
    print("🧪 Testing Responsive Grid System...")
    for i, pattern in enumerate(grid_tests, 1):
        if re.search(pattern, css_content, re.DOTALL):
            print(f"  ✅ Grid test {i} passed")
        else:
            print(f"  ❌ Grid test {i} failed: {pattern}")
            return False
    
    # Test for responsive containers
    container_tests = [
        r"\.container\s*{[^}]*max-width",
        r"\.container-sm\s*{[^}]*max-width:\s*640px",
        r"\.container-md\s*{[^}]*max-width:\s*768px",
        r"\.container-lg\s*{[^}]*max-width:\s*1024px",
    ]
    
    print("🧪 Testing Responsive Containers...")
    for i, pattern in enumerate(container_tests, 1):
        if re.search(pattern, css_content, re.DOTALL):
            print(f"  ✅ Container test {i} passed")
        else:
            print(f"  ❌ Container test {i} failed: {pattern}")
            return False
    
    # Test for responsive typography
    typography_tests = [
        r"\.text-xs.*font-size:\s*0\.75rem",
        r"\.text-sm.*font-size:\s*0\.875rem",
        r"\.text-base.*font-size:\s*1rem",
        r"\.sm\\:text-lg.*font-size:\s*1\.125rem",
        r"h1.*font-size.*1\.875rem",
    ]
    
    print("🧪 Testing Responsive Typography...")
    for i, pattern in enumerate(typography_tests, 1):
        if re.search(pattern, css_content, re.DOTALL):
            print(f"  ✅ Typography test {i} passed")
        else:
            print(f"  ❌ Typography test {i} failed: {pattern}")
            return False
    
    # Test for media query breakpoints
    breakpoint_tests = [
        r"@media \(min-width:\s*640px\)",
        r"@media \(min-width:\s*768px\)",
        r"@media \(min-width:\s*1024px\)",
        r"@media \(min-width:\s*1280px\)",
        r"--breakpoint-sm:\s*640px",
    ]
    
    print("🧪 Testing Media Query Breakpoints...")
    for i, pattern in enumerate(breakpoint_tests, 1):
        if re.search(pattern, css_content):
            print(f"  ✅ Breakpoint test {i} passed")
        else:
            print(f"  ❌ Breakpoint test {i} failed: {pattern}")
            return False
    
    # Test for responsive utilities
    utility_tests = [
        r"\.sm\\:hidden.*display:\s*none",
        r"\.md\\:flex.*display:\s*flex",
        r"\.lg\\:block.*display:\s*block",
        r"\.responsive-card",
        r"\.responsive-form",
    ]
    
    print("🧪 Testing Responsive Utilities...")
    for i, pattern in enumerate(utility_tests, 1):
        if re.search(pattern, css_content, re.DOTALL):
            print(f"  ✅ Utility test {i} passed")
        else:
            print(f"  ❌ Utility test {i} failed: {pattern}")
            return False
    
    return True

def test_demo_template():
    """Test that the responsive layout demo template exists"""
    demo_file = Path("app/templates/examples/responsive_layout_demo.html")
    
    if not demo_file.exists():
        print("❌ Responsive layout demo template not found")
        return False
    
    demo_content = demo_file.read_text()
    
    # Test for key demo sections
    demo_tests = [
        "Container Components",
        "Responsive Grid System",
        "Responsive Typography",
        "Responsive Flexbox Layouts",
        "Breakpoint Reference",
        "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3",
        "text-3xl md:text-4xl lg:text-5xl",
        "flex flex-col md:flex-row",
    ]
    
    print("🧪 Testing Demo Template...")
    for i, test in enumerate(demo_tests, 1):
        if test in demo_content:
            print(f"  ✅ Demo test {i} passed: {test}")
        else:
            print(f"  ❌ Demo test {i} failed: {test}")
            return False
    
    return True

def test_line_clamp_fix():
    """Test that line-clamp warnings are fixed"""
    css_file = Path("app/static/css/main.css")
    css_content = css_file.read_text()
    
    print("🧪 Testing Line-Clamp Fix...")
    
    # Check for both webkit and standard line-clamp properties
    line_clamp_patterns = [
        r"\.line-clamp-1\s*{[^}]*-webkit-line-clamp:\s*1[^}]*line-clamp:\s*1",
        r"\.line-clamp-2\s*{[^}]*-webkit-line-clamp:\s*2[^}]*line-clamp:\s*2",
        r"\.line-clamp-3\s*{[^}]*-webkit-line-clamp:\s*3[^}]*line-clamp:\s*3",
    ]
    
    for i, pattern in enumerate(line_clamp_patterns, 1):
        if re.search(pattern, css_content, re.DOTALL):
            print(f"  ✅ Line-clamp test {i} passed")
        else:
            print(f"  ❌ Line-clamp test {i} failed")
            return False
    
    return True

def main():
    """Run all responsive layout tests"""
    print("🚀 Testing Responsive Layout Implementation")
    print("=" * 50)
    
    tests = [
        ("Responsive CSS Components", test_responsive_css),
        ("Demo Template", test_demo_template),
        ("Line-Clamp Fix", test_line_clamp_fix),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                print(f"✅ {test_name} - PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All responsive layout tests passed!")
        print("\n📝 Implementation Summary:")
        print("  ✅ Responsive grid system with breakpoints")
        print("  ✅ Container components for different screen sizes")
        print("  ✅ Responsive typography with mobile-first scaling")
        print("  ✅ Media query breakpoints (640px, 768px, 1024px, 1280px)")
        print("  ✅ Responsive utilities for spacing, visibility, and layout")
        print("  ✅ Demo template showcasing all features")
        print("  ✅ Fixed line-clamp CSS warnings")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)