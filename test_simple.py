"""
SIMPLE coordinate conversion - no complex calculations
"""

import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
from typing import Tuple, Optional
import sys

class SuperSimpleViewer(QLabel):
    """Super simple image viewer - KISS principle"""
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 600)
        self.setStyleSheet("border: 1px solid gray;")
        self.setAlignment(Qt.AlignCenter)
        
        # Only store what we need
        self.original_image = None
        self.scale_ratio = 1.0  # display_width / original_width
        self.offset_x = 0
        self.offset_y = 0
        self.start_x = None
        self.start_y = None
        self.end_x = None 
        self.end_y = None
        self.dragging = False
        
    def set_image(self, image: np.ndarray):
        """Set image - SIMPLE version"""
        self.original_image = image.copy()
        
        # Get original size
        orig_height, orig_width = image.shape[:2]
        
        # Convert to Qt format
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        
        # Scale to fit widget
        widget_size = self.size()
        scaled_pixmap = pixmap.scaled(widget_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        # Calculate scale and offset
        self.scale_ratio = scaled_pixmap.width() / orig_width
        self.offset_x = (widget_size.width() - scaled_pixmap.width()) // 2
        self.offset_y = (widget_size.height() - scaled_pixmap.height()) // 2
        
        self.setPixmap(scaled_pixmap)
        
        print(f"📐 Original: {orig_width}x{orig_height}")
        print(f"📐 Display: {scaled_pixmap.width()}x{scaled_pixmap.height()}")
        print(f"📐 Scale: {self.scale_ratio:.3f}")
        print(f"📐 Offset: ({self.offset_x}, {self.offset_y})")
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.original_image is not None:
            # Convert widget coordinates to original image coordinates
            widget_x = event.x()
            widget_y = event.y()
            
            # Simple conversion: (widget_coord - offset) / scale_ratio
            image_x = int((widget_x - self.offset_x) / self.scale_ratio)
            image_y = int((widget_y - self.offset_y) / self.scale_ratio)
            
            # Clamp to image bounds
            orig_height, orig_width = self.original_image.shape[:2]
            image_x = max(0, min(image_x, orig_width - 1))
            image_y = max(0, min(image_y, orig_height - 1))
            
            self.start_x = image_x
            self.start_y = image_y
            self.dragging = True
            
            print(f"🖱️ START: widget({widget_x}, {widget_y}) -> image({image_x}, {image_y})")
            
    def mouseMoveEvent(self, event):
        if self.dragging and self.original_image is not None:
            widget_x = event.x()
            widget_y = event.y()
            
            # Same simple conversion
            image_x = int((widget_x - self.offset_x) / self.scale_ratio)
            image_y = int((widget_y - self.offset_y) / self.scale_ratio)
            
            # Clamp to image bounds
            orig_height, orig_width = self.original_image.shape[:2]
            image_x = max(0, min(image_x, orig_width - 1))
            image_y = max(0, min(image_y, orig_height - 1))
            
            self.end_x = image_x
            self.end_y = image_y
            self.update()  # Redraw
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.dragging:
            self.dragging = False
            
            if self.start_x is not None and self.end_x is not None:
                # Calculate rectangle in image coordinates
                x1, y1 = self.start_x, self.start_y
                x2, y2 = self.end_x, self.end_y
                
                x = min(x1, x2)
                y = min(y1, y2) 
                width = abs(x2 - x1)
                height = abs(y2 - y1)
                
                print(f"✂️ FINAL: x={x}, y={y}, w={width}, h={height}")
                
                # Extract ROI and save
                if width > 5 and height > 5:
                    roi = self.original_image[y:y+height, x:x+width]
                    cv2.imwrite("simple_roi.png", roi)
                    print(f"💾 Saved ROI: {roi.shape}")
                    
    def paintEvent(self, event):
        super().paintEvent(event)
        
        if (self.dragging and self.start_x is not None and 
            self.end_x is not None and self.original_image is not None):
            
            painter = QPainter(self)
            painter.setPen(QPen(Qt.red, 3, Qt.SolidLine))
            
            # Convert image coordinates back to widget coordinates for drawing
            start_widget_x = int(self.start_x * self.scale_ratio + self.offset_x)
            start_widget_y = int(self.start_y * self.scale_ratio + self.offset_y)
            end_widget_x = int(self.end_x * self.scale_ratio + self.offset_x)
            end_widget_y = int(self.end_y * self.scale_ratio + self.offset_y)
            
            x = min(start_widget_x, end_widget_x)
            y = min(start_widget_y, end_widget_y)
            width = abs(end_widget_x - start_widget_x)
            height = abs(end_widget_y - start_widget_y)
            
            painter.drawRect(x, y, width, height)

def test_simple():
    app = QApplication(sys.argv)
    
    # Create test image with clear regions
    test_image = np.zeros((400, 600, 3), dtype=np.uint8)
    
    # Draw colored rectangles at known positions
    cv2.rectangle(test_image, (100, 100), (200, 200), (255, 255, 255), -1)  # White: 100,100 to 200,200
    cv2.rectangle(test_image, (250, 150), (350, 250), (0, 255, 0), -1)      # Green: 250,150 to 350,250  
    cv2.rectangle(test_image, (400, 50), (500, 150), (0, 0, 255), -1)       # Red: 400,50 to 500,150
    
    # Add coordinate labels
    cv2.putText(test_image, "White(100,100)", (105, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    cv2.putText(test_image, "Green(250,150)", (255, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    cv2.putText(test_image, "Red(400,50)", (405, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    window = QMainWindow()
    viewer = SuperSimpleViewer()
    window.setCentralWidget(viewer)
    
    viewer.set_image(test_image)
    
    window.setWindowTitle("SIMPLE Test - Drag exactly around colored rectangles")
    window.resize(900, 700)
    window.show()
    
    print("🎯 Test: Drag exactly around GREEN rectangle")
    print("🎯 Expected result: x=250, y=150, w=100, h=100")
    
    app.exec_()

if __name__ == "__main__":
    test_simple()
