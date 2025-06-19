"""
SUPER SIMPLE - Just two points and rectangle crop
"""

import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
import sys

class TwoPointViewer(QLabel):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 600)
        self.setStyleSheet("border: 1px solid gray;")
        self.setAlignment(Qt.AlignCenter)
        
        self.original_image = None
        self.displayed_pixmap = None
        self.point1 = None  # Start point in WIDGET coordinates
        self.point2 = None  # End point in WIDGET coordinates
        self.dragging = False
        
    def set_image(self, image):
        self.original_image = image.copy()
        
        # Display the image
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qt_image = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        
        # Scale to fit
        scaled = pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.displayed_pixmap = scaled
        self.setPixmap(scaled)
        
        print(f"Original: {w}x{h}, Displayed: {scaled.width()}x{scaled.height()}")
        
    def widget_to_image(self, widget_x, widget_y):
        """Convert widget coordinates to image coordinates"""
        if self.original_image is None or self.displayed_pixmap is None:
            return None, None
            
        # Get sizes
        orig_h, orig_w = self.original_image.shape[:2]
        disp_w = self.displayed_pixmap.width()
        disp_h = self.displayed_pixmap.height()
        
        # Get widget size and calculate offset (centering)
        widget_size = self.size()
        offset_x = (widget_size.width() - disp_w) // 2
        offset_y = (widget_size.height() - disp_h) // 2
        
        # Convert widget coords to display coords
        display_x = widget_x - offset_x
        display_y = widget_y - offset_y
        
        # Scale to original image coords
        scale_x = orig_w / disp_w
        scale_y = orig_h / disp_h
        
        image_x = int(display_x * scale_x)
        image_y = int(display_y * scale_y)
        
        # Clamp
        image_x = max(0, min(image_x, orig_w - 1))
        image_y = max(0, min(image_y, orig_h - 1))
        
        return image_x, image_y
        
    def image_to_widget(self, image_x, image_y):
        """Convert image coordinates to widget coordinates"""
        if self.original_image is None or self.displayed_pixmap is None:
            return None, None
            
        orig_h, orig_w = self.original_image.shape[:2]
        disp_w = self.displayed_pixmap.width()
        disp_h = self.displayed_pixmap.height()
        
        widget_size = self.size()
        offset_x = (widget_size.width() - disp_w) // 2
        offset_y = (widget_size.height() - disp_h) // 2
        
        scale_x = disp_w / orig_w
        scale_y = disp_h / orig_h
        
        widget_x = int(image_x * scale_x + offset_x)
        widget_y = int(image_y * scale_y + offset_y)
        
        return widget_x, widget_y
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.point1 = (event.x(), event.y())
            self.dragging = True
            print(f"Start: widget({event.x()}, {event.y()})")
            
    def mouseMoveEvent(self, event):
        if self.dragging:
            self.point2 = (event.x(), event.y())
            self.update()
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.dragging:
            self.dragging = False
            self.point2 = (event.x(), event.y())
            
            if self.point1 and self.point2:
                # Convert both points to image coordinates
                img_x1, img_y1 = self.widget_to_image(*self.point1)
                img_x2, img_y2 = self.widget_to_image(*self.point2)
                
                print(f"Widget: ({self.point1[0]}, {self.point1[1]}) -> ({self.point2[0]}, {self.point2[1]})")
                print(f"Image: ({img_x1}, {img_y1}) -> ({img_x2}, {img_y2})")
                
                # Calculate rectangle
                x = min(img_x1, img_x2)
                y = min(img_y1, img_y2)
                width = abs(img_x2 - img_x1)
                height = abs(img_y2 - img_y1)
                
                print(f"Rectangle: x={x}, y={y}, w={width}, h={height}")
                
                # Crop and save
                if width > 5 and height > 5:
                    roi = self.original_image[y:y+height, x:x+width]
                    cv2.imwrite("two_point_roi.png", roi)
                    print(f"Saved ROI: {roi.shape}")
                    
    def paintEvent(self, event):
        super().paintEvent(event)
        
        if self.dragging and self.point1 and self.point2:
            painter = QPainter(self)
            painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
            
            x1, y1 = self.point1
            x2, y2 = self.point2
            
            x = min(x1, x2)
            y = min(y1, y2)
            w = abs(x2 - x1)
            h = abs(y2 - y1)
            
            painter.drawRect(x, y, w, h)

def test_two_points():
    app = QApplication(sys.argv)
    
    # Test image
    img = np.zeros((400, 600, 3), dtype=np.uint8)
    cv2.rectangle(img, (100, 100), (200, 200), (255, 255, 255), -1)  # White
    cv2.rectangle(img, (250, 150), (350, 250), (0, 255, 0), -1)      # Green  
    cv2.rectangle(img, (400, 50), (500, 150), (0, 0, 255), -1)       # Red
    
    window = QMainWindow()
    viewer = TwoPointViewer()
    window.setCentralWidget(viewer)
    
    viewer.set_image(img)
    
    window.setWindowTitle("Two Points Test")
    window.resize(900, 700)
    window.show()
    
    print("Drag around the GREEN rectangle - should get: x=250, y=150, w=100, h=100")
    
    app.exec_()

if __name__ == "__main__":
    test_two_points()
