#!/usr/bin/env python3
"""
Script to create dummy template images for testing.
These should be replaced with actual game templates.
"""

import cv2
import numpy as np
import os

def create_dummy_template(name, width, height, color=(255, 255, 255)):
    """Create a dummy template image."""
    img = np.full((height, width, 3), color, dtype=np.uint8)
    
    # Add some pattern to make it recognizable
    cv2.rectangle(img, (5, 5), (width-5, height-5), (0, 0, 0), 2)
    cv2.putText(img, name[:8], (10, height//2), cv2.FONT_HERSHEY_SIMPLEX, 
                0.5, (0, 0, 0), 1, cv2.LINE_AA)
    
    return img

def main():
    """Create all required dummy templates."""
    os.makedirs('assets', exist_ok=True)
    os.makedirs('assets/alerts', exist_ok=True)
    
    templates = {
        'minimap_tl_template.png': (20, 20, (100, 100, 255)),  # Blue for top-left
        'minimap_br_template.png': (20, 20, (255, 100, 100)),  # Red for bottom-right
        'player_template.png': (16, 16, (0, 255, 0)),          # Green for player
        'rune_template.png': (32, 32, (255, 255, 0)),          # Yellow for rune
        'rune_buff_template.jpg': (24, 24, (255, 0, 255)),     # Magenta for rune buff
        'elite_template.jpg': (40, 40, (0, 255, 255)),         # Cyan for elite
        'other_template.png': (30, 30, (128, 128, 128)),       # Gray for other
        'icon.png': (64, 64, (255, 165, 0)),                   # Orange for icon
    }
    
    for filename, (width, height, color) in templates.items():
        img = create_dummy_template(filename.split('.')[0], width, height, color)
        filepath = os.path.join('assets', filename)
        cv2.imwrite(filepath, img)
        print(f"Created dummy template: {filepath}")
    
    # Create a simple text file for label_map
    with open('assets/label_map.pbtxt', 'w') as f:
        f.write("""item {
  id: 1
  name: 'up'
}
item {
  id: 2
  name: 'down'
}
item {
  id: 3
  name: 'left'
}
item {
  id: 4
  name: 'right'
}
""")
    print("Created label_map.pbtxt")
    
    print("\nDummy templates created successfully!")
    print("Note: Replace these with actual game templates for proper functionality.")

if __name__ == '__main__':
    main()
