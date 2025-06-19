"""
PyQt5 Template Manager for ROI selection and template creation
Provides drag-and-drop interface for creating game object templates
"""

import sys
import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import time
import logging

try:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                                QComboBox, QScrollArea, QMessageBox, QDialog,
                                QSpinBox, QDoubleSpinBox, QGroupBox)
    from PyQt5.QtCore import Qt, QRect, pyqtSignal
    from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QFont
    PYQT5_AVAILABLE = True
except ImportError:
    print("⚠️ PyQt5 not available. Template manager will use fallback mode.")
    PYQT5_AVAILABLE = False

# Add src directory for imports
sys.path.append(str(Path(__file__).parent))

if PYQT5_AVAILABLE:
    from screen_capture import ScreenCapture
    from window_detector import WindowDetector
    from template_matcher import TemplateMatcher

logger = logging.getLogger(__name__)


class ImageViewer(QLabel):
    """Custom QLabel for image display with ROI selection"""
    
    roi_selected = pyqtSignal(int, int, int, int)  # x, y, width, height
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 600)
        self.setStyleSheet("border: 1px solid gray;")
        self.setAlignment(Qt.AlignCenter)
        
        # Simple state - just two points
        self.original_image = None
        self.displayed_pixmap = None
        self.point1 = None  # Start point in widget coordinates
        self.point2 = None  # End point in widget coordinates
        self.dragging = False
        
    def set_image(self, image: np.ndarray):
        """Set image to display - SIMPLE version"""
        try:
            if image is None or image.size == 0:
                self.setText("No image data")
                return
                
            self.original_image = image.copy()
            
            # Convert BGR to RGB for display
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            height, width, channel = rgb_image.shape
            
            # Create QImage and QPixmap
            bytes_per_line = 3 * width
            q_image = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            
            # Scale to fit widget
            widget_size = self.size()
            scaled_pixmap = pixmap.scaled(widget_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            self.displayed_pixmap = scaled_pixmap
            self.setPixmap(scaled_pixmap)
            
            logger.debug(f"Image set: original={width}x{height}, scaled={scaled_pixmap.width()}x{scaled_pixmap.height()}")
            
        except Exception as e:
            logger.error(f"Failed to set image: {e}")
            self.setText(f"Error loading image: {e}")
            # Reset state
            self.original_image = None
            self.displayed_pixmap = None
            self.point1 = None
            self.point2 = None
            self.dragging = False
            
    def mousePressEvent(self, event):
        """Start ROI selection"""
        if event.button() == Qt.LeftButton and self.original_image is not None:
            self.point1 = (event.x(), event.y())
            self.dragging = True
            logger.debug(f"Start drag: widget({event.x()}, {event.y()})")
                
    def mouseMoveEvent(self, event):
        """Update ROI selection"""
        if self.dragging and self.original_image is not None:
            self.point2 = (event.x(), event.y())
            self.update()  # Trigger repaint
                
    def mouseReleaseEvent(self, event):
        """Finish ROI selection"""
        if event.button() == Qt.LeftButton and self.dragging:
            self.dragging = False
            self.point2 = (event.x(), event.y())
            
            if self.point1 and self.point2:
                # Convert both points to image coordinates
                img_x1, img_y1 = self.widget_to_image(*self.point1)
                img_x2, img_y2 = self.widget_to_image(*self.point2)
                
                if img_x1 is not None and img_y1 is not None and img_x2 is not None and img_y2 is not None:
                    # Calculate rectangle
                    x = min(img_x1, img_x2)
                    y = min(img_y1, img_y2)
                    width = abs(img_x2 - img_x1)
                    height = abs(img_y2 - img_y1)
                    
                    logger.debug(f"ROI selected: x={x}, y={y}, width={width}, height={height}")
                    
                    # Minimum size check
                    if width > 10 and height > 10:
                        self.roi_selected.emit(x, y, width, height)
                    
    def widget_to_image(self, widget_x, widget_y):
        """Convert widget coordinates to image coordinates - SIMPLE version"""
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
        
        # Check bounds
        if display_x < 0 or display_y < 0 or display_x >= disp_w or display_y >= disp_h:
            return None, None
        
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
        """Convert image coordinates to widget coordinates - SIMPLE version"""
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
                    
    def paintEvent(self, event):
        """Draw selection rectangle - SAFE version"""
        super().paintEvent(event)
        
        # Only draw if we have valid state
        if (self.dragging and 
            self.point1 is not None and 
            self.point2 is not None and 
            hasattr(self, 'displayed_pixmap') and 
            self.displayed_pixmap is not None):
            
            try:
                painter = QPainter(self)
                painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
                
                x1, y1 = self.point1
                x2, y2 = self.point2
                
                # Calculate rectangle coordinates
                x = min(x1, x2)
                y = min(y1, y2)
                w = abs(x2 - x1)
                h = abs(y2 - y1)
                
                # Only draw if rectangle has reasonable size
                if w > 1 and h > 1:
                    painter.drawRect(x, y, w, h)
                    
                painter.end()  # Explicitly end painting
                
            except Exception as e:
                logger.error(f"Paint error: {e}")
                pass  # Fail silently to avoid crash



class TemplateCreatorDialog(QDialog):
    """Dialog for creating new templates"""
    
    def __init__(self, screenshot: np.ndarray, parent=None):
        super().__init__(parent)
        self.screenshot = screenshot
        self.selected_roi = None
        self.template_matcher = TemplateMatcher()
        
        self.setup_ui()
        self.setModal(True)
        self.resize(1000, 800)
        
    def setup_ui(self):
        """Setup dialog UI"""
        self.setWindowTitle("Create Template")
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel("📸 Drag to select a region for template creation")
        instructions.setFont(QFont("Arial", 12))
        instructions.setStyleSheet("padding: 10px; background-color: #e6f3ff; border-radius: 5px;")
        layout.addWidget(instructions)
        
        # Image viewer
        self.image_viewer = ImageViewer()
        self.image_viewer.set_image(self.screenshot)
        self.image_viewer.roi_selected.connect(self.on_roi_selected)
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.image_viewer)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        # Template settings
        settings_group = QGroupBox("Template Settings")
        settings_layout = QVBoxLayout(settings_group)
        
        # Name input
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter template name (e.g., 'slime', 'player_knight')")
        name_layout.addWidget(self.name_input)
        settings_layout.addLayout(name_layout)
        
        # Type selection
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["player", "monster", "npc", "item", "ui", "other"])
        type_layout.addWidget(self.type_combo)
        settings_layout.addLayout(type_layout)
        
        # Confidence threshold
        confidence_layout = QHBoxLayout()
        confidence_layout.addWidget(QLabel("Confidence Threshold:"))
        self.confidence_spin = QDoubleSpinBox()
        self.confidence_spin.setRange(0.1, 1.0)
        self.confidence_spin.setValue(0.7)
        self.confidence_spin.setSingleStep(0.05)
        self.confidence_spin.setDecimals(2)
        confidence_layout.addWidget(self.confidence_spin)
        settings_layout.addLayout(confidence_layout)
        
        # ROI info
        self.roi_label = QLabel("No region selected")
        self.roi_label.setStyleSheet("color: #666; padding: 5px;")
        settings_layout.addWidget(self.roi_label)
        
        layout.addWidget(settings_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.create_button = QPushButton("✅ Create Template")
        self.create_button.setEnabled(False)
        self.create_button.clicked.connect(self.create_template)
        
        self.test_button = QPushButton("🔍 Test Match")
        self.test_button.setEnabled(False)
        self.test_button.clicked.connect(self.test_template)
        
        cancel_button = QPushButton("❌ Cancel")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.create_button)
        button_layout.addWidget(self.test_button)
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
    def on_roi_selected(self, x: int, y: int, width: int, height: int):
        """Handle ROI selection"""
        # Debug: Print received coordinates
        print(f"🎯 ROI selected: x={x}, y={y}, width={width}, height={height}")
        
        # Validate coordinates before saving
        img_height, img_width = self.screenshot.shape[:2]
        print(f"🎯 Image dimensions: {img_width}x{img_height}")
        
        # Check bounds
        if x < 0 or y < 0 or x + width > img_width or y + height > img_height:
            print(f"❌ ROI out of bounds: ({x}, {y}, {width}, {height}) for {img_width}x{img_height}")
            return
            
        # Show preview of what will be extracted
        preview_roi = self.screenshot[y:y+height, x:x+width]
        print(f"🎯 Preview ROI shape: {preview_roi.shape}")
        
        self.selected_roi = (x, y, width, height)
        self.roi_label.setText(f"Selected region: {width}x{height} at ({x}, {y})")
        
        # Enable buttons
        self.create_button.setEnabled(True)
        self.test_button.setEnabled(True)
        
        # Auto-generate name if empty
        if not self.name_input.text():
            template_type = self.type_combo.currentText()
            timestamp = int(time.time())
            self.name_input.setText(f"{template_type}_{timestamp}")
            
    def create_template(self):
        """Create and save template"""
        if not self.selected_roi or not self.name_input.text():
            QMessageBox.warning(self, "Error", "Please select a region and enter a name")
            return
            
        try:
            # Extract ROI from screenshot
            x, y, width, height = self.selected_roi
            
            # Debug info
            print(f"📐 Creating template with ROI: x={x}, y={y}, width={width}, height={height}")
            print(f"📐 Original image shape: {self.screenshot.shape}")
            
            # Validate coordinates
            img_height, img_width = self.screenshot.shape[:2]
            if x < 0 or y < 0 or x + width > img_width or y + height > img_height:
                QMessageBox.warning(self, "Error", f"Invalid ROI coordinates: ({x}, {y}, {width}, {height}) for image {img_width}x{img_height}")
                return
                
            roi_image = self.screenshot[y:y+height, x:x+width]
            
            if roi_image.size == 0:
                QMessageBox.warning(self, "Error", "Invalid region selected")
                return
                
            print(f"📐 Extracted ROI shape: {roi_image.shape}")
                
            # Save template
            name = self.name_input.text().strip()
            template_type = self.type_combo.currentText()
            confidence = self.confidence_spin.value()
            
            if self.template_matcher.save_template(roi_image, name, template_type, confidence):
                print(f"✅ Template '{name}' saved successfully!")
                QMessageBox.information(self, "Success", f"Template '{name}' created successfully!")
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Failed to save template")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create template: {e}")
            
    def test_template(self):
        """Test template matching"""
        if not self.selected_roi:
            return
            
        try:
            # Extract ROI as template
            x, y, width, height = self.selected_roi
            template_image = self.screenshot[y:y+height, x:x+width]
            
            # Create temporary matcher
            temp_matcher = TemplateMatcher()
            temp_matcher.save_template(template_image, "_temp_test", "test", self.confidence_spin.value())
            
            # Test match
            matches = temp_matcher.match_templates(self.screenshot, ["test"])
            
            if matches:
                QMessageBox.information(
                    self, 
                    "Test Result", 
                    f"Found {len(matches)} matches!\n"
                    f"Best match: {matches[0].confidence:.3f} confidence"
                )
            else:
                QMessageBox.warning(
                    self, 
                    "Test Result", 
                    "No matches found. Try lowering the confidence threshold."
                )
                
            # Clean up temp template
            temp_matcher.delete_template("_temp_test")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Test failed: {e}")


class PyQtTemplateManager:
    """Main template manager using PyQt5"""
    
    def __init__(self):
        if not PYQT5_AVAILABLE:
            raise ImportError("PyQt5 not available")
            
        self.screen_capture = ScreenCapture()
        self.window_detector = WindowDetector()
        self.template_matcher = TemplateMatcher()
        
    def capture_and_create_template(self) -> bool:
        """
        Capture game screen and launch template creation dialog
        
        Returns:
            True if template was created successfully
        """
        try:
            # Find and focus game window
            print("🎯 Finding game window...")
            game_window = self.window_detector.find_and_focus_game_window(debug=True)
            
            if not game_window:
                print("❌ No game window found")
                return False
                
            print(f"✅ Found game window: {game_window['name']}")
            
            # Capture screenshot
            print("📸 Capturing screenshot...")
            bounds = self.window_detector.get_window_bounds(game_window)
            screenshot = self.screen_capture.capture_screen(bounds)
            
            if screenshot is None:
                print("❌ Failed to capture screenshot")
                return False
                
            print(f"✅ Screenshot captured: {screenshot.shape}")
            
            # Launch template creation dialog
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)
                
            dialog = TemplateCreatorDialog(screenshot)
            result = dialog.exec_()
            
            return result == QDialog.Accepted
            
        except Exception as e:
            print(f"❌ Template creation failed: {e}")
            return False
            
    def test_template_matching(self) -> bool:
        """
        Test template matching on current game screen
        
        Returns:
            True if test completed successfully
        """
        try:
            # Find game window
            print("🎯 Finding game window for testing...")
            game_window = self.window_detector.find_and_focus_game_window()
            
            if not game_window:
                print("❌ No game window found")
                return False
                
            # Capture screenshot
            print("📸 Capturing test screenshot...")
            bounds = self.window_detector.get_window_bounds(game_window)
            screenshot = self.screen_capture.capture_screen(bounds)
            
            if screenshot is None:
                print("❌ Failed to capture screenshot")
                return False
                
            # Test matching
            print("🔍 Testing template matching...")
            matches = self.template_matcher.match_templates(screenshot)
            
            print(f"✅ Found {len(matches)} matches:")
            for match in matches[:5]:  # Show top 5
                print(f"  - {match.template_name} ({match.template_type}): {match.confidence:.3f}")
                
            # Save debug image
            if matches:
                debug_image = self.template_matcher.visualize_matches(screenshot, matches)
                timestamp = int(time.time())
                filename = f"template_test_{timestamp}.png"
                cv2.imwrite(filename, debug_image)
                print(f"💾 Debug image saved: {filename}")
                
            return True
            
        except Exception as e:
            print(f"❌ Template test failed: {e}")
            return False


# Test functions
def test_template_capture():
    """Test template capture functionality"""
    if not PYQT5_AVAILABLE:
        print("❌ PyQt5 not available")
        return
        
    print("🧪 Testing PyQt5 template capture...")
    
    try:
        manager = PyQtTemplateManager()
        
        print("📸 Starting template capture...")
        success = manager.capture_and_create_template()
        
        if success:
            print("✅ Template creation completed!")
        else:
            print("❌ Template creation cancelled or failed")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")


def test_template_matching():
    """Test template matching functionality"""
    if not PYQT5_AVAILABLE:
        print("❌ PyQt5 not available")
        return
        
    print("🧪 Testing template matching...")
    
    try:
        manager = PyQtTemplateManager()
        manager.test_template_matching()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "capture":
            test_template_capture()
        elif sys.argv[1] == "test":
            test_template_matching()
    else:
        print("Usage:")
        print("  python pyqt_template_manager.py capture  # Test template capture")
        print("  python pyqt_template_manager.py test     # Test template matching")
