#!/usr/bin/env python3
"""
Auto Maple Bot v2.0 - Main Entry Point
Cross-platform game automation for MapleStory-like games
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def check_dependencies():
    """Check if required dependencies are installed"""
    missing_deps = []
    
    try:
        import cv2
    except ImportError:
        missing_deps.append("opencv-python")
        
    try:
        import numpy
    except ImportError:
        missing_deps.append("numpy")
        
    try:
        import mss
    except ImportError:
        missing_deps.append("mss")
        
    try:
        from AppKit import NSWorkspace
        from Quartz import CGWindowListCopyWindowInfo
    except ImportError:
        missing_deps.append("pyobjc-framework-Cocoa and pyobjc-framework-Quartz")
        
    if missing_deps:
        print("❌ Missing dependencies:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\n📦 Please install dependencies:")
        print("   pip install -r requirements.txt")
        return False
        
    print("✅ All dependencies available")
    return True

def main():
    """Main entry point"""
    print("🍁 Auto Maple Bot v2.0 - macOS Edition")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
        
    # Import and run GUI
    try:
        from main_gui import AutoMapleGUI
        
        print("🚀 Starting GUI...")
        app = AutoMapleGUI()
        app.run()
        
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
