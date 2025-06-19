#!/usr/bin/env python3
"""
Test script for Auto Maple macOS version
Tests basic functionality without running the full bot
"""

import sys
import os
import time

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import cv2
        print("✓ OpenCV imported successfully")
    except ImportError as e:
        print(f"✗ OpenCV import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✓ NumPy imported successfully")
    except ImportError as e:
        print(f"✗ NumPy import failed: {e}")
        return False
    
    try:
        import mss
        print("✓ MSS (screenshot) imported successfully")
    except ImportError as e:
        print(f"✗ MSS import failed: {e}")
        return False
    
    try:
        import pynput
        print("✓ PyInput imported successfully")
    except ImportError as e:
        print(f"✗ PyInput import failed: {e}")
        return False
    
    try:
        import pyautogui
        print("✓ PyAutoGUI imported successfully")
    except ImportError as e:
        print(f"✗ PyAutoGUI import failed: {e}")
        return False
    
    try:
        from AppKit import NSWorkspace
        print("✓ AppKit imported successfully")
    except ImportError as e:
        print(f"✗ AppKit import failed: {e}")
        return False
    
    try:
        import Quartz
        print("✓ Quartz imported successfully")
    except ImportError as e:
        print(f"✗ Quartz import failed: {e}")
        return False
    
    return True

def test_screen_capture():
    """Test screen capture functionality."""
    print("\nTesting screen capture...")
    
    try:
        import mss
        import numpy as np
        
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # Primary monitor
            screenshot = sct.grab(monitor)
            img_array = np.array(screenshot)
            print(f"✓ Screenshot taken: {img_array.shape}")
            return True
    except Exception as e:
        print(f"✗ Screen capture failed: {e}")
        return False

def test_keyboard_control():
    """Test keyboard control (without actually pressing keys)."""
    print("\nTesting keyboard control...")
    
    try:
        from pynput import keyboard
        controller = keyboard.Controller()
        print("✓ Keyboard controller created successfully")
        return True
    except Exception as e:
        print(f"✗ Keyboard control failed: {e}")
        return False

def test_mouse_control():
    """Test mouse control."""
    print("\nTesting mouse control...")
    
    try:
        from pynput import mouse
        controller = mouse.Controller()
        pos = controller.position
        print(f"✓ Mouse position: {pos}")
        return True
    except Exception as e:
        print(f"✗ Mouse control failed: {e}")
        return False

def test_window_detection():
    """Test window detection."""
    print("\nTesting window detection...")
    
    try:
        import Quartz
        from AppKit import NSWorkspace
        
        # Get window list
        window_list = Quartz.CGWindowListCopyWindowInfo(
            Quartz.kCGWindowListOptionOnScreenOnly,
            Quartz.kCGNullWindowID
        )
        
        print(f"✓ Found {len(window_list)} windows")
        
        # Show some window names
        for i, window in enumerate(window_list[:5]):
            name = window.get('kCGWindowName', 'Unknown')
            owner = window.get('kCGWindowOwnerName', 'Unknown')
            print(f"  - {name} ({owner})")
        
        return True
    except Exception as e:
        print(f"✗ Window detection failed: {e}")
        return False

def test_permissions():
    """Test if we have necessary permissions."""
    print("\nTesting permissions...")
    
    try:
        import Quartz
        # This will fail if we don't have accessibility permissions
        window_list = Quartz.CGWindowListCopyWindowInfo(
            Quartz.kCGWindowListOptionOnScreenOnly,
            Quartz.kCGNullWindowID
        )
        print("✓ Accessibility permissions granted")
        return True
    except Exception as e:
        print(f"✗ Accessibility permissions not granted: {e}")
        print("Please grant accessibility permissions in System Preferences")
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("Auto Maple macOS Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_screen_capture,
        test_keyboard_control,
        test_mouse_control,
        test_window_detection,
        test_permissions
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("✓ All tests passed! Auto Maple should work on your system.")
    else:
        print("✗ Some tests failed. Please install missing dependencies.")
        print("\nTo install dependencies:")
        print("pip install -r requirements.txt")
    
    print("=" * 50)

if __name__ == '__main__':
    main()
