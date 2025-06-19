"""
Window detection module for macOS
Handles game window detection and management
"""

import time
import subprocess
import re
from typing import Optional, List, Dict, Tuple
import logging

try:
    from AppKit import NSWorkspace, NSApplicationActivationPolicyRegular
    from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID
    MACOS_LIBS_AVAILABLE = True
except ImportError:
    print("⚠️ AppKit/Quartz not available. Window detection may not work.")
    MACOS_LIBS_AVAILABLE = False

# Configure logging
logger = logging.getLogger(__name__)


class WindowDetector:
    """Detect and manage game windows on macOS"""
    
    def __init__(self):
        self.target_games = [
            "MapleStory",
            "MapleLand", 
            "MapleStory Worlds",
            "Maple",
            # Add more game variations
        ]
        self.last_detected_window = None
        
    def get_all_windows(self) -> List[Dict]:
        """
        Get list of all visible windows
        
        Returns:
            List of window dictionaries with info
        """
        if not MACOS_LIBS_AVAILABLE:
            return []
            
        try:
            window_list = CGWindowListCopyWindowInfo(
                kCGWindowListOptionOnScreenOnly, 
                kCGNullWindowID
            )
            
            windows = []
            for window in window_list:
                # Filter out system windows
                if window.get('kCGWindowName') and window.get('kCGWindowBounds'):
                    bounds = window['kCGWindowBounds']
                    windows.append({
                        'name': window.get('kCGWindowName', ''),
                        'owner': window.get('kCGWindowOwnerName', ''),
                        'pid': window.get('kCGWindowOwnerPID', 0),
                        'bounds': bounds,
                        'width': bounds.get('Width', 0),
                        'height': bounds.get('Height', 0),
                        'x': bounds.get('X', 0),
                        'y': bounds.get('Y', 0)
                    })
                    
            logger.debug(f"Found {len(windows)} windows")
            return windows
            
        except Exception as e:
            logger.error(f"Failed to get window list: {e}")
            return []
    
    def find_game_window(self, debug: bool = False) -> Optional[Dict]:
        """
        Find game window using multiple detection strategies
        
        Args:
            debug: Print debug information
            
        Returns:
            Window info dictionary or None if not found
        """
        windows = self.get_all_windows()
        
        if debug:
            print(f"\n🔍 Searching through {len(windows)} windows...")
            
        # Strategy 1: Exact name match
        for target in self.target_games:
            for window in windows:
                if target.lower() in window['name'].lower():
                    if debug:
                        print(f"✅ Found by exact match: {window['name']}")
                    self.last_detected_window = window
                    return window
                    
        # Strategy 2: Owner/app name match  
        for target in self.target_games:
            for window in windows:
                if target.lower() in window['owner'].lower():
                    if debug:
                        print(f"✅ Found by owner match: {window['owner']} -> {window['name']}")
                    self.last_detected_window = window
                    return window
                    
        # Strategy 3: Pattern matching for game-like windows
        game_patterns = [
            r'maple.*story',
            r'maple.*land', 
            r'maple.*world',
            r'.*maple.*',
        ]
        
        for pattern in game_patterns:
            for window in windows:
                name_lower = window['name'].lower()
                owner_lower = window['owner'].lower()
                
                if re.search(pattern, name_lower) or re.search(pattern, owner_lower):
                    if debug:
                        print(f"✅ Found by pattern '{pattern}': {window['name']}")
                    self.last_detected_window = window
                    return window
                    
        # Strategy 4: Largest game-like window fallback
        game_like_windows = []
        for window in windows:
            # Filter reasonable game window sizes
            if (window['width'] > 800 and window['height'] > 600 and 
                window['width'] < 2000 and window['height'] < 1500):
                game_like_windows.append(window)
                
        if game_like_windows:
            # Sort by size and pick largest
            largest = max(game_like_windows, key=lambda w: w['width'] * w['height'])
            if debug:
                print(f"🎯 Fallback to largest window: {largest['name']} ({largest['width']}x{largest['height']})")
            self.last_detected_window = largest
            return largest
            
        if debug:
            print("❌ No game window found")
            print("\n📋 Available windows:")
            for i, window in enumerate(windows[:10]):  # Show first 10
                print(f"  {i+1}. {window['owner']} - {window['name']} ({window['width']}x{window['height']})")
                
        return None
        
    def bring_window_to_front(self, window: Dict) -> bool:
        """
        Bring specified window to front by clicking its center
        
        Args:
            window: Window info dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Calculate center coordinates
            center_x = window['x'] + window['width'] // 2
            center_y = window['y'] + window['height'] // 2
            
            # Use system click to bring window to front
            cmd = f"cliclick c:{center_x},{center_y}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Brought window to front: {window['name']}")
                time.sleep(0.5)  # Wait for window to stabilize
                return True
            else:
                logger.warning("cliclick not available, trying alternative method")
                return self._alternative_focus_method(window)
                
        except Exception as e:
            logger.error(f"Failed to bring window to front: {e}")
            return False
            
    def _alternative_focus_method(self, window: Dict) -> bool:
        """Alternative window focusing using AppleScript"""
        try:
            # Use AppleScript to activate application
            script = f'''
            tell application "{window['owner']}"
                activate
            end tell
            '''
            
            result = subprocess.run(
                ['osascript', '-e', script], 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"Activated application: {window['owner']}")
                time.sleep(0.5)
                return True
                
        except Exception as e:
            logger.warning(f"Alternative focus method failed: {e}")
            
        return False
        
    def find_and_focus_game_window(self, debug: bool = False) -> Optional[Dict]:
        """
        Find game window and bring it to front
        
        Args:
            debug: Print debug information
            
        Returns:
            Window info if found and focused, None otherwise
        """
        window = self.find_game_window(debug=debug)
        if window:
            if self.bring_window_to_front(window):
                return window
            else:
                logger.warning("Found window but failed to bring to front")
                return window  # Return anyway, might still be usable
        return None
        
    def get_window_bounds(self, window: Optional[Dict] = None) -> Optional[Dict]:
        """
        Get window bounds for screenshot capture
        
        Args:
            window: Window info, uses last detected if None
            
        Returns:
            Dictionary with screenshot bounds or None
        """
        target_window = window or self.last_detected_window
        if not target_window:
            return None
            
        return {
            'top': target_window['y'],
            'left': target_window['x'],
            'width': target_window['width'], 
            'height': target_window['height']
        }


# Test function
def test_window_detection():
    """Test window detection functionality"""
    print("🔍 Testing window detection...")
    
    detector = WindowDetector()
    
    # List all windows
    windows = detector.get_all_windows()
    print(f"\n📋 Found {len(windows)} total windows")
    
    # Show first few windows
    for i, window in enumerate(windows[:5]):
        print(f"  {i+1}. {window['owner']} - {window['name']} ({window['width']}x{window['height']})")
    
    # Try to find game window
    print(f"\n🎯 Looking for game window...")
    game_window = detector.find_game_window(debug=True)
    
    if game_window:
        print(f"\n✅ Game window found:")
        print(f"   Name: {game_window['name']}")
        print(f"   Owner: {game_window['owner']}")
        print(f"   Size: {game_window['width']}x{game_window['height']}")
        print(f"   Position: ({game_window['x']}, {game_window['y']})")
        
        # Test focusing
        print(f"\n🎯 Attempting to bring window to front...")
        if detector.bring_window_to_front(game_window):
            print("✅ Window focused successfully")
        else:
            print("❌ Failed to focus window")
            
    else:
        print("❌ No game window found")


if __name__ == "__main__":
    test_window_detection()
