"""
Screen capture module for macOS
Handles game window detection and screenshot capture
"""

import mss
import numpy as np
import cv2
import time
from typing import Optional, Tuple, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScreenCapture:
    """Handle screen capture operations for game window"""
    
    def __init__(self):
        self.sct = mss.mss()
        self.last_capture_time = 0
        self.capture_cooldown = 0.01  # 10ms minimum between captures
        
    def capture_screen(self, monitor: Optional[Dict[str, int]] = None) -> Optional[np.ndarray]:
        """
        Capture screenshot of specified monitor or full screen
        
        Args:
            monitor: Dictionary with 'top', 'left', 'width', 'height' keys
                    If None, captures primary monitor
                    
        Returns:
            numpy array of captured image in BGR format, or None if failed
        """
        try:
            # Respect capture cooldown
            current_time = time.time()
            if current_time - self.last_capture_time < self.capture_cooldown:
                time.sleep(self.capture_cooldown)
                
            # Use primary monitor if none specified
            if monitor is None:
                monitor = self.sct.monitors[1]  # Primary monitor
                
            # Capture screenshot
            screenshot = self.sct.grab(monitor)
            
            # Convert to numpy array
            img_array = np.array(screenshot)
            
            # Convert BGRA to BGR (remove alpha channel)
            if img_array.shape[2] == 4:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_BGRA2BGR)
            elif img_array.shape[2] == 3:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                
            self.last_capture_time = time.time()
            logger.debug(f"Screenshot captured: {img_array.shape}")
            
            return img_array
            
        except Exception as e:
            logger.error(f"Failed to capture screen: {e}")
            return None
            
    def capture_region(self, x: int, y: int, width: int, height: int) -> Optional[np.ndarray]:
        """
        Capture specific region of screen
        
        Args:
            x, y: Top-left coordinates
            width, height: Region dimensions
            
        Returns:
            numpy array of captured region or None if failed
        """
        monitor = {
            "top": y,
            "left": x, 
            "width": width,
            "height": height
        }
        return self.capture_screen(monitor)
        
    def save_screenshot(self, image: np.ndarray, filename: str) -> bool:
        """
        Save screenshot to file
        
        Args:
            image: Image array to save
            filename: Output filename
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            cv2.imwrite(filename, image)
            logger.info(f"Screenshot saved: {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to save screenshot: {e}")
            return False
            
    def get_primary_monitor_info(self) -> Dict[str, int]:
        """Get primary monitor dimensions"""
        return self.sct.monitors[1]
        
    def get_all_monitors(self) -> list:
        """Get information for all monitors"""
        return self.sct.monitors


# Test function
def test_screen_capture():
    """Test screen capture functionality"""
    print("Testing screen capture...")
    
    capturer = ScreenCapture()
    
    # Test full screen capture
    img = capturer.capture_screen()
    if img is not None:
        print(f"✅ Full screen capture successful: {img.shape}")
        capturer.save_screenshot(img, "test_fullscreen.png")
    else:
        print("❌ Full screen capture failed")
        
    # Test region capture
    img_region = capturer.capture_region(100, 100, 400, 300)
    if img_region is not None:
        print(f"✅ Region capture successful: {img_region.shape}")
        capturer.save_screenshot(img_region, "test_region.png")
    else:
        print("❌ Region capture failed")
        
    # Print monitor info
    monitors = capturer.get_all_monitors()
    print(f"📺 Available monitors: {len(monitors)}")
    for i, monitor in enumerate(monitors):
        print(f"  Monitor {i}: {monitor}")


if __name__ == "__main__":
    test_screen_capture()
