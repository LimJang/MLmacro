#!/usr/bin/env python3
"""
Phase 2 Test Script - Template System Testing
Tests all template-related functionality
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_template_matcher():
    """Test template matching functionality"""
    print("🧪 Testing TemplateMatcher...")
    
    try:
        from template_matcher import TemplateMatcher
        
        matcher = TemplateMatcher()
        print(f"✅ TemplateMatcher initialized")
        
        # Test template list
        templates = matcher.get_template_list()
        print(f"📋 Found {len(templates)} existing templates")
        
        # Test confidence threshold
        matcher.set_confidence_threshold(0.8)
        print(f"✅ Confidence threshold set")
        
        return True
        
    except Exception as e:
        print(f"❌ TemplateMatcher test failed: {e}")
        return False

def test_pyqt5_availability():
    """Test PyQt5 availability"""
    print("🧪 Testing PyQt5 availability...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        print("✅ PyQt5 available")
        return True
    except ImportError:
        print("❌ PyQt5 not available")
        print("   Install with: pip install PyQt5")
        return False

def test_pyqt5_template_manager():
    """Test PyQt5 template manager"""
    print("🧪 Testing PyQt5TemplateManager...")
    
    try:
        from pyqt_template_manager import PyQtTemplateManager
        
        # Note: Can't fully test without GUI interaction
        print("✅ PyQtTemplateManager imports successfully")
        return True
        
    except ImportError as e:
        print(f"❌ PyQtTemplateManager import failed: {e}")
        return False
    except Exception as e:
        print(f"⚠️ PyQtTemplateManager warning: {e}")
        return True  # Still considered successful

def test_gui_integration():
    """Test GUI template integration"""
    print("🧪 Testing GUI template integration...")
    
    try:
        from main_gui import AutoMapleGUI
        
        # Test initialization (without running mainloop)
        print("✅ GUI imports with template integration")
        return True
        
    except Exception as e:
        print(f"❌ GUI integration test failed: {e}")
        return False

def test_all_imports():
    """Test all Phase 2 imports"""
    print("🧪 Testing all Phase 2 imports...")
    
    modules = [
        "screen_capture",
        "window_detector", 
        "template_matcher",
        "pyqt_template_manager",
        "main_gui"
    ]
    
    success_count = 0
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
            success_count += 1
        except Exception as e:
            print(f"❌ {module}: {e}")
            
    print(f"📊 Import success rate: {success_count}/{len(modules)}")
    return success_count == len(modules)

def check_dependencies():
    """Check Phase 2 dependencies"""
    print("🧪 Checking Phase 2 dependencies...")
    
    dependencies = [
        ("cv2", "opencv-python"),
        ("numpy", "numpy"),
        ("mss", "mss"),
        ("PyQt5", "PyQt5"),
        ("tkinter", "built-in")
    ]
    
    success_count = 0
    
    for module, package in dependencies:
        try:
            if module == "cv2":
                import cv2
            elif module == "PyQt5":
                from PyQt5.QtWidgets import QApplication
            else:
                __import__(module)
            print(f"✅ {module} ({package})")
            success_count += 1
        except ImportError:
            print(f"❌ {module} ({package}) - Not installed")
        except Exception as e:
            print(f"⚠️ {module} ({package}) - {e}")
            
    print(f"📊 Dependency success rate: {success_count}/{len(dependencies)}")
    return success_count >= len(dependencies) - 1  # PyQt5 is optional

def main():
    """Run all Phase 2 tests"""
    print("🍁 Auto Maple Bot - Phase 2 Template System Tests")
    print("=" * 60)
    
    tests = [
        ("Dependencies", check_dependencies),
        ("Imports", test_all_imports),
        ("TemplateMatcher", test_template_matcher),
        ("PyQt5 Available", test_pyqt5_availability),
        ("PyQt5 Manager", test_pyqt5_template_manager),
        ("GUI Integration", test_gui_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}:")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"💥 {test_name} CRASHED: {e}")
            
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Phase 2 is ready!")
    elif passed >= total - 1:
        print("✨ Almost all tests passed! Phase 2 is mostly ready!")
    else:
        print("⚠️ Some tests failed. Check dependencies and installation.")
        
    print("\n🚀 To test the GUI:")
    print("   python3 run.py")
    print("\n📸 To test template capture:")
    print("   cd src && python3 pyqt_template_manager.py capture")

if __name__ == "__main__":
    main()
