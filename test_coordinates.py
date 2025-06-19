"""
Simplified coordinate conversion test
"""

import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
from typing import Tuple, Optional
import sys

class SimpleImageViewer(QLabel):
    """Simplified image viewer for testing coordinate conversion"""
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 600)
        self.setStyleSheet("border: 1px solid gray;")
        self.setAlignment(Qt.AlignCenter)
        
        # State
        self.original_image = None
        self.display_scale = 1.0
        self.display_offset = (0, 0)
        self.selection_start = None
        self.selection_end = None
        self.selecting = False
        
    def set_image(self, image: np.ndarray):
        """Set image with simple scaling"""
        self.original_image = image.copy()
        
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width, channel = rgb_image.shape
        
        # Simple scaling to fit widget
        widget_size = self.size()
        scale_x = (widget_size.width() - 40) / width
        scale_y = (widget_size.height() - 40) / height
        scale = min(scale_x, scale_y, 1.0)  # Don't upscale
        
        # Calculate display size
        display_width = int(width * scale)
        display_height = int(height * scale)
        
        # Create QImage and scale
        bytes_per_line = 3 * width
        q_image = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(display_width, display_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        # Calculate offset (center)
        offset_x = (widget_size.width() - display_width) // 2
        offset_y = (widget_size.height() - display_height) // 2
        
        # Store values
        self.display_scale = scale
        self.display_offset = (offset_x, offset_y)
        
        # Set pixmap
        self.setPixmap(scaled_pixmap)
        
        print(f"🖼️ Image: {width}x{height} -> {display_width}x{display_height}")
        print(f"🖼️ Scale: {scale:.3f}, Offset: ({offset_x}, {offset_y})")
        
    def mousePressEvent(self, event):
        """Start selection"""
        if event.button() == Qt.LeftButton and self.original_image is not None:
            # Convert widget coords to image coords
            widget_x = event.x()
            widget_y = event.y()
            
            image_coords = self.widget_to_image(widget_x, widget_y)
            if image_coords:
                self.selection_start = image_coords
                self.selecting = True
                print(f"🖱️ Start: widget({widget_x}, {widget_y}) -> image{image_coords}")
                
    def mouseMoveEvent(self, event):
        """Update selection"""
        if self.selecting and self.original_image is not None:
            widget_x = event.x()
            widget_y = event.y()
            
            image_coords = self.widget_to_image(widget_x, widget_y)
            if image_coords:
                self.selection_end = image_coords
                self.update()
                
    def mouseReleaseEvent(self, event):
        """Finish selection"""
        if event.button() == Qt.LeftButton and self.selecting:
            self.selecting = False
            
            if self.selection_start and self.selection_end:
                # Calculate rectangle
                x1, y1 = self.selection_start
                x2, y2 = self.selection_end
                
                x = min(x1, x2)
                y = min(y1, y2)
                width = abs(x2 - x1)
                height = abs(y2 - y1)
                
                print(f"✂️ Selection: x={x}, y={y}, width={width}, height={height}")
                
                # Extract and save ROI
                if width > 10 and height > 10:
                    roi = self.original_image[y:y+height, x:x+width]
                    cv2.imwrite("test_roi.png", roi)
                    print(f"💾 ROI saved: {roi.shape}")
                    
    def widget_to_image(self, wx: int, wy: int) -> Optional[Tuple[int, int]]:
        """Convert widget coordinates to image coordinates"""
        if self.original_image is None:
            return None
            
        offset_x, offset_y = self.display_offset
        
        # Check if within display area first
        display_width = int(self.original_image.shape[1] * self.display_scale)
        display_height = int(self.original_image.shape[0] * self.display_scale)
        
        print(f"🔍 Widget click: ({wx}, {wy})")
        print(f"🔍 Display area: offset=({offset_x}, {offset_y}), size=({display_width}, {display_height})")
        print(f"🔍 Display bounds: x=[{offset_x}, {offset_x + display_width}], y=[{offset_y}, {offset_y + display_height}]")
        
        if (wx < offset_x or wy < offset_y or 
            wx > offset_x + display_width or wy > offset_y + display_height):
            print(f"🔍 Click outside display area")
            return None
            
        # Convert to relative coordinates within the display area
        relative_x = wx - offset_x
        relative_y = wy - offset_y
        
        print(f"🔍 Relative coords: ({relative_x}, {relative_y})")
        print(f"🔍 Scale factor: {self.display_scale}")
        
        # Scale back to original image coordinates
        image_x = int(relative_x / self.display_scale)
        image_y = int(relative_y / self.display_scale)
        
        print(f"🔍 Before clamp: image=({image_x}, {image_y})")
        
        # Clamp to image bounds
        image_height, image_width = self.original_image.shape[:2]
        image_x = max(0, min(image_x, image_width - 1))
        image_y = max(0, min(image_y, image_height - 1))
        
        print(f"🔍 Final image coords: ({image_x}, {image_y})")
        
        return (image_x, image_y)
        
    def paintEvent(self, event):
        """Draw selection rectangle"""
        super().paintEvent(event)
        
        if self.selecting and self.selection_start and self.selection_end:
            painter = QPainter(self)
            painter.setPen(QPen(Qt.red, 2, Qt.DashLine))
            
            # Convert image coords back to widget coords for drawing
            start_widget = self.image_to_widget(*self.selection_start)
            end_widget = self.image_to_widget(*self.selection_end)
            
            if start_widget and end_widget:
                x1, y1 = start_widget
                x2, y2 = end_widget
                
                x = min(x1, x2)
                y = min(y1, y2)
                width = abs(x2 - x1)
                height = abs(y2 - y1)
                
                painter.drawRect(x, y, width, height)
                
    def image_to_widget(self, ix: int, iy: int) -> Optional[Tuple[int, int]]:
        """Convert image coordinates to widget coordinates"""
        offset_x, offset_y = self.display_offset
        
        wx = int(ix * self.display_scale + offset_x)
        wy = int(iy * self.display_scale + offset_y)
        
        return (wx, wy)

# Test function
def test_coordinates():
    """Test coordinate conversion with a simple image"""
    app = QApplication(sys.argv)
    
    # Create test image
    test_image = np.zeros((400, 600, 3), dtype=np.uint8)
    cv2.rectangle(test_image, (50, 50), (150, 150), (255, 255, 255), -1)  # White square
    cv2.rectangle(test_image, (200, 200), (300, 300), (0, 255, 0), -1)    # Green square
    cv2.rectangle(test_image, (400, 100), (550, 250), (0, 0, 255), -1)    # Red square
    
    # Create window
    window = QMainWindow()
    viewer = SimpleImageViewer()
    window.setCentralWidget(viewer)
    
    viewer.set_image(test_image)
    
    window.setWindowTitle("Coordinate Test - Drag to select regions")
    window.resize(900, 700)
    window.show()
    
    app.exec_()

if __name__ == "__main__":
    test_coordinates()
