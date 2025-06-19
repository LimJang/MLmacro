"""
Template matching module for player and monster detection
Uses OpenCV for high-performance template matching
"""

import os
import cv2
import numpy as np
import json
import time
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
import logging

logger = logging.getLogger(__name__)


class TemplateMatch:
    """Represents a single template match result"""
    
    def __init__(self, x: int, y: int, width: int, height: int, confidence: float, template_name: str, template_type: str):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.confidence = confidence
        self.template_name = template_name
        self.template_type = template_type
        self.center_x = x + width // 2
        self.center_y = y + height // 2
        
    def __repr__(self):
        return f"TemplateMatch({self.template_name}: {self.confidence:.3f} at ({self.x}, {self.y}))"


class TemplateMatcher:
    """High-performance template matching for game objects"""
    
    def __init__(self, templates_dir: str = "templates"):
        # Ensure absolute path
        if not os.path.isabs(templates_dir):
            self.templates_dir = Path(__file__).parent.parent / templates_dir
        else:
            self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(exist_ok=True)
        
        print(f"📁 TemplateMatcher using directory: {self.templates_dir}")
        
        # Template cache for performance
        self.template_cache: Dict[str, Dict[str, Any]] = {}
        self.load_all_templates()
        
        # Matching parameters
        self.confidence_threshold = 0.7
        self.nms_threshold = 0.3  # Non-maximum suppression
        self.scale_factors = [1.0]  # Multi-scale matching if needed
        
    def load_all_templates(self):
        """Load all templates from templates directory"""
        self.template_cache.clear()
        
        for template_file in self.templates_dir.glob("*.png"):
            try:
                self.load_template(template_file.stem)
            except Exception as e:
                logger.warning(f"Failed to load template {template_file}: {e}")
                
        logger.info(f"Loaded {len(self.template_cache)} templates")
        
    def load_template(self, template_name: str) -> bool:
        """
        Load a single template with metadata
        
        Args:
            template_name: Name of template (without .png extension)
            
        Returns:
            True if loaded successfully
        """
        try:
            # Load image
            img_path = self.templates_dir / f"{template_name}.png"
            if not img_path.exists():
                logger.warning(f"Template image not found: {img_path}")
                return False
                
            template_img = cv2.imread(str(img_path), cv2.IMREAD_COLOR)
            if template_img is None:
                logger.warning(f"Failed to load template image: {img_path}")
                return False
                
            # Load metadata
            meta_path = self.templates_dir / f"{template_name}.json"
            metadata = {}
            if meta_path.exists():
                with open(meta_path, 'r') as f:
                    metadata = json.load(f)
            else:
                # Default metadata
                metadata = {
                    'name': template_name,
                    'type': 'unknown',
                    'created': time.time(),
                    'confidence_threshold': 0.7
                }
                
            # Store in cache
            self.template_cache[template_name] = {
                'image': template_img,
                'metadata': metadata,
                'height': template_img.shape[0],
                'width': template_img.shape[1]
            }
            
            logger.debug(f"Loaded template: {template_name} ({template_img.shape})")
            return True
            
        except Exception as e:
            logger.error(f"Error loading template {template_name}: {e}")
            return False
            
    def match_templates(self, screen_image: np.ndarray, template_types: Optional[List[str]] = None) -> List[TemplateMatch]:
        """
        Match all templates against screen image
        
        Args:
            screen_image: Screenshot to search in
            template_types: Filter by template types (e.g., ['player', 'monster'])
            
        Returns:
            List of template matches sorted by confidence
        """
        if screen_image is None:
            return []
            
        matches = []
        
        for template_name, template_data in self.template_cache.items():
            metadata = template_data['metadata']
            template_type = metadata.get('type', 'unknown')
            
            # Filter by type if specified
            if template_types and template_type not in template_types:
                continue
                
            # Get confidence threshold for this template
            threshold = metadata.get('confidence_threshold', self.confidence_threshold)
            
            # Perform template matching
            template_matches = self._match_single_template(
                screen_image, 
                template_data['image'], 
                template_name, 
                template_type,
                threshold
            )
            
            matches.extend(template_matches)
            
        # Sort by confidence and apply non-maximum suppression
        matches.sort(key=lambda m: m.confidence, reverse=True)
        matches = self._apply_nms(matches)
        
        return matches
        
    def _match_single_template(self, screen_image: np.ndarray, template: np.ndarray, 
                              name: str, template_type: str, threshold: float) -> List[TemplateMatch]:
        """
        Match single template against screen image
        
        Args:
            screen_image: Screenshot to search in
            template: Template image
            name: Template name
            template_type: Template type
            threshold: Confidence threshold
            
        Returns:
            List of matches for this template
        """
        matches = []
        
        try:
            # Convert to grayscale for better matching
            screen_gray = cv2.cvtColor(screen_image, cv2.COLOR_BGR2GRAY)
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            
            # Template matching
            result = cv2.matchTemplate(screen_gray, template_gray, cv2.TM_CCOEFF_NORMED)
            
            # Find matches above threshold
            locations = np.where(result >= threshold)
            
            for pt in zip(*locations[::-1]):  # Switch x and y coordinates
                confidence = result[pt[1], pt[0]]
                
                match = TemplateMatch(
                    x=int(pt[0]),
                    y=int(pt[1]),
                    width=template.shape[1],
                    height=template.shape[0],
                    confidence=float(confidence),
                    template_name=name,
                    template_type=template_type
                )
                
                matches.append(match)
                
        except Exception as e:
            logger.error(f"Error matching template {name}: {e}")
            
        return matches
        
    def _apply_nms(self, matches: List[TemplateMatch]) -> List[TemplateMatch]:
        """
        Apply Non-Maximum Suppression to remove overlapping matches
        
        Args:
            matches: List of template matches
            
        Returns:
            Filtered list without overlapping matches
        """
        if not matches:
            return []
            
        # Group matches by template type for separate NMS
        grouped_matches = {}
        for match in matches:
            if match.template_type not in grouped_matches:
                grouped_matches[match.template_type] = []
            grouped_matches[match.template_type].append(match)
            
        final_matches = []
        
        for template_type, type_matches in grouped_matches.items():
            if not type_matches:
                continue
                
            # Convert to format for OpenCV NMS
            boxes = []
            scores = []
            
            for match in type_matches:
                boxes.append([match.x, match.y, match.width, match.height])
                scores.append(match.confidence)
                
            boxes = np.array(boxes, dtype=np.float32)
            scores = np.array(scores, dtype=np.float32)
            
            # Apply NMS
            indices = cv2.dnn.NMSBoxes(boxes, scores, self.confidence_threshold, self.nms_threshold)
            
            if len(indices) > 0:
                for i in indices.flatten():
                    final_matches.append(type_matches[i])
                    
        return final_matches
        
    def save_template(self, image: np.ndarray, name: str, template_type: str, 
                     confidence_threshold: float = 0.7) -> bool:
        """
        Save template image with metadata
        
        Args:
            image: Template image
            name: Template name
            template_type: Type (player, monster, etc.)
            confidence_threshold: Matching threshold
            
        Returns:
            True if saved successfully
        """
        try:
            # Save image
            img_path = self.templates_dir / f"{name}.png"
            cv2.imwrite(str(img_path), image)
            
            # Save metadata
            metadata = {
                'name': name,
                'type': template_type,
                'created': time.time(),
                'confidence_threshold': confidence_threshold,
                'width': image.shape[1],
                'height': image.shape[0]
            }
            
            meta_path = self.templates_dir / f"{name}.json"
            with open(meta_path, 'w') as f:
                json.dump(metadata, f, indent=2)
                
            # Add to cache
            self.template_cache[name] = {
                'image': image,
                'metadata': metadata,
                'height': image.shape[0],
                'width': image.shape[1]
            }
            
            logger.info(f"Template saved: {name} ({template_type})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save template {name}: {e}")
            return False
            
    def delete_template(self, name: str) -> bool:
        """Delete template and its metadata"""
        try:
            img_path = self.templates_dir / f"{name}.png"
            meta_path = self.templates_dir / f"{name}.json"
            
            if img_path.exists():
                img_path.unlink()
            if meta_path.exists():
                meta_path.unlink()
                
            if name in self.template_cache:
                del self.template_cache[name]
                
            logger.info(f"Template deleted: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete template {name}: {e}")
            return False
            
    def get_template_list(self) -> List[Dict[str, Any]]:
        """Get list of all available templates with metadata"""
        templates = []
        
        for name, data in self.template_cache.items():
            metadata = data['metadata'].copy()
            metadata['size'] = f"{data['width']}x{data['height']}"
            templates.append(metadata)
            
        return sorted(templates, key=lambda t: t.get('created', 0), reverse=True)
        
    def set_confidence_threshold(self, threshold: float):
        """Set global confidence threshold"""
        self.confidence_threshold = max(0.1, min(1.0, threshold))
        
    def visualize_matches(self, image: np.ndarray, matches: List[TemplateMatch]) -> np.ndarray:
        """
        Draw bounding boxes around matches for visualization
        
        Args:
            image: Original image
            matches: List of template matches
            
        Returns:
            Image with bounding boxes drawn
        """
        result_image = image.copy()
        
        colors = {
            'player': (0, 255, 0),    # Green
            'monster': (0, 0, 255),   # Red  
            'unknown': (255, 0, 255)  # Magenta
        }
        
        for match in matches:
            color = colors.get(match.template_type, colors['unknown'])
            
            # Draw bounding box
            cv2.rectangle(
                result_image,
                (match.x, match.y),
                (match.x + match.width, match.y + match.height),
                color,
                2
            )
            
            # Draw label
            label = f"{match.template_name}: {match.confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
            
            cv2.rectangle(
                result_image,
                (match.x, match.y - label_size[1] - 5),
                (match.x + label_size[0], match.y),
                color,
                -1
            )
            
            cv2.putText(
                result_image,
                label,
                (match.x, match.y - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1
            )
            
        return result_image


# Test function
def test_template_matching():
    """Test template matching functionality"""
    print("🔍 Testing template matching...")
    
    matcher = TemplateMatcher()
    
    # Check for existing templates
    templates = matcher.get_template_list()
    print(f"📋 Found {len(templates)} templates:")
    for template in templates:
        print(f"  - {template['name']} ({template['type']}) - {template['size']}")
        
    if not templates:
        print("⚠️ No templates found. Use the GUI to create templates first.")
        return
        
    # Test with a dummy image
    test_image = np.zeros((600, 800, 3), dtype=np.uint8)
    cv2.rectangle(test_image, (100, 100), (200, 200), (255, 255, 255), -1)
    
    matches = matcher.match_templates(test_image)
    print(f"🎯 Found {len(matches)} matches in test image")
    
    for match in matches:
        print(f"  {match}")


if __name__ == "__main__":
    test_template_matching()
