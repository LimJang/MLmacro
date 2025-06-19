"""The central program that ties all the modules together - macOS version."""

import time
import sys
import os
import subprocess

# Check for required permissions on macOS
def check_permissions():
    """Check if the app has accessibility permissions on macOS."""
    try:
        import Quartz
        # Try to get window list - this requires accessibility permissions
        Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionOnScreenOnly, Quartz.kCGNullWindowID)
        return True
    except Exception:
        return False

def request_permissions():
    """Request accessibility permissions on macOS."""
    print("\n" + "="*60)
    print("ACCESSIBILITY PERMISSIONS REQUIRED")
    print("="*60)
    print("Auto Maple needs accessibility permissions to:")
    print("  • Control keyboard and mouse")
    print("  • Take screenshots")
    print("  • Detect game windows")
    print("\nTo grant permissions:")
    print("  1. Open System Preferences > Security & Privacy")
    print("  2. Click the 'Privacy' tab")
    print("  3. Select 'Accessibility' from the left sidebar")
    print("  4. Click the lock icon and enter your password")
    print("  5. Add Terminal or your Python app to the list")
    print("  6. Restart this program")
    print("="*60)
    
    # Try to open System Preferences
    try:
        subprocess.run(['open', '/System/Library/PreferencePanes/Security.prefPane'], check=False)
    except:
        pass
    
    input("\nPress Enter after granting permissions...")
    return check_permissions()

def main():
    """Main function to start Auto Maple."""
    print("Starting Auto Maple for macOS...")
    
    # Check permissions first
    if not check_permissions():
        print("Accessibility permissions not granted.")
        if not request_permissions():
            print("Cannot continue without accessibility permissions. Exiting...")
            sys.exit(1)
    
    print("Permissions OK, starting Auto Maple...")
    
    try:
        from src.modules.bot import Bot
        from src.modules.capture import Capture
        from src.modules.notifier import Notifier
        from src.modules.listener import Listener
        from src.modules.gui import GUI
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)

    # Initialize modules
    bot = Bot()
    capture = Capture()
    notifier = Notifier()
    listener = Listener()

    # Start modules
    print("Starting bot...")
    bot.start()
    while not bot.ready:
        time.sleep(0.01)

    print("Starting capture...")
    capture.start()
    while not capture.ready:
        time.sleep(0.01)

    print("Starting notifier...")
    notifier.start()
    while not notifier.ready:
        time.sleep(0.01)

    print("Starting listener...")
    listener.start()
    while not listener.ready:
        time.sleep(0.01)

    print('\n[~] Successfully initialized Auto Maple for macOS')

    # Start GUI
    try:
        gui = GUI()
        gui.start()
    except Exception as e:
        print(f"GUI error: {e}")
        print("Running in headless mode...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")

if __name__ == '__main__':
    main()
