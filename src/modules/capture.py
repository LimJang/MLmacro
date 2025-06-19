"""A module for tracking useful in-game information on macOS."""

import time
import cv2
import threading
import mss
import numpy as np
import Quartz
from AppKit import NSWorkspace, NSRunningApplication
from src.common import config, utils


# The distance between the top of the minimap and the top of the screen
MINIMAP_TOP_BORDER = 5

# The thickness of the other three borders of the minimap
MINIMAP_BOTTOM_BORDER = 9

# macOS doesn't have the same windowed offset as Windows
WINDOWED_OFFSET_TOP = 0
WINDOWED_OFFSET_LEFT = 0

# The top-left and bottom-right corners of the minimap
try:
    MM_TL_TEMPLATE = cv2.imread('assets/minimap_tl_template.png', 0)
    MM_BR_TEMPLATE = cv2.imread('assets/minimap_br_template.png', 0)
    if MM_TL_TEMPLATE is None or MM_BR_TEMPLATE is None:
        print("[WARNING] Template images not found. Creating dummy templates...")
        MM_TL_TEMPLATE = np.ones((20, 20), dtype=np.uint8) * 255
        MM_BR_TEMPLATE = np.ones((20, 20), dtype=np.uint8) * 255
except Exception as e:
    print(f"[WARNING] Error loading templates: {e}")
    MM_TL_TEMPLATE = np.ones((20, 20), dtype=np.uint8) * 255
    MM_BR_TEMPLATE = np.ones((20, 20), dtype=np.uint8) * 255

MMT_HEIGHT = max(MM_TL_TEMPLATE.shape[0], MM_BR_TEMPLATE.shape[0])
MMT_WIDTH = max(MM_TL_TEMPLATE.shape[1], MM_BR_TEMPLATE.shape[1])

# The player's symbol on the minimap
try:
    PLAYER_TEMPLATE = cv2.imread('assets/player_template.png', 0)
    if PLAYER_TEMPLATE is None:
        print("[WARNING] Player template not found. Creating dummy template...")
        PLAYER_TEMPLATE = np.ones((16, 16), dtype=np.uint8) * 255
except Exception as e:
    print(f"[WARNING] Error loading player template: {e}")
    PLAYER_TEMPLATE = np.ones((16, 16), dtype=np.uint8) * 255
PT_HEIGHT, PT_WIDTH = PLAYER_TEMPLATE.shape


def find_window_by_name(window_name):
    """
    Find a window by its name using macOS APIs.
    :param window_name: Name of the window to find
    :return: Window info dictionary or None
    """
    try:
        # Get list of all windows
        window_list = Quartz.CGWindowListCopyWindowInfo(
            Quartz.kCGWindowListOptionOnScreenOnly,
            Quartz.kCGNullWindowID
        )
        
        for window in window_list:
            if window.get('kCGWindowName', '').lower() == window_name.lower():
                bounds = window['kCGWindowBounds']
                return {
                    'left': int(bounds['X']),
                    'top': int(bounds['Y']),
                    'width': int(bounds['Width']),
                    'height': int(bounds['Height'])
                }
    except Exception as e:
        print(f"Error finding window: {e}")
    
    return None


def find_maplestory_window():
    """
    Find MapleStory window with various possible names.
    :return: Window info dictionary or None
    """
    possible_names = [
        'MapleStory',
        'maplestory', 
        'Maple Story',
        'maple story',
        'MapleLand',
        'mapleland',
        'Maple Land',
        'maple land'
    ]
    
    for name in possible_names:
        window = find_window_by_name(name)
        if window:
            return window
    
    # If not found, try to get the frontmost application
    try:
        workspace = NSWorkspace.sharedWorkspace()
        app = workspace.frontmostApplication()
        if app:
            print(f"Using frontmost application: {app.localizedName()}")
            # Return full screen as fallback
            return {
                'left': 0,
                'top': 0,
                'width': 1440,  # Common macOS resolution
                'height': 900
            }
    except Exception as e:
        print(f"Error getting frontmost application: {e}")
    
    return None


class Capture:
    """
    A class that tracks player position and various in-game events. It constantly updates
    the config module with information regarding these events. It also annotates and
    displays the minimap in a pop-up window.
    """

    def __init__(self):
        """Initializes this Capture object's main thread."""

        config.capture = self

        self.frame = None
        self.minimap = {}
        self.minimap_ratio = 1
        self.minimap_sample = None
        self.sct = None
        self.window = {
            'left': 0,
            'top': 0,
            'width': 1440,
            'height': 900
        }

        self.ready = False
        self.calibrated = False
        self.thread = threading.Thread(target=self._main)
        self.thread.daemon = True

    def start(self):
        """Starts this Capture's thread."""

        print('\n[~] Started video capture')
        self.thread.start()

    def _main(self):
        """Constantly monitors the player's position and in-game events."""

        while True:
            # Calibrate screen capture
            window_info = find_maplestory_window()
            if window_info:
                self.window.update(window_info)
            else:
                print("MapleStory window not found, using default screen area")
                # Use default screen area
                self.window = {
                    'left': 0,
                    'top': 0,
                    'width': 1440,
                    'height': 900
                }

            # Ensure minimum dimensions
            self.window['width'] = max(self.window['width'], MMT_WIDTH)
            self.window['height'] = max(self.window['height'], MMT_HEIGHT)

            # Calibrate by finding the top-left and bottom-right corners of the minimap
            with mss.mss() as self.sct:
                self.frame = self.screenshot()
            if self.frame is None:
                continue
                
            tl, _ = utils.single_match(self.frame, MM_TL_TEMPLATE)
            _, br = utils.single_match(self.frame, MM_BR_TEMPLATE)
            
            if tl and br:
                mm_tl = (
                    tl[0] + MINIMAP_BOTTOM_BORDER,
                    tl[1] + MINIMAP_TOP_BORDER
                )
                mm_br = (
                    max(mm_tl[0] + PT_WIDTH, br[0] - MINIMAP_BOTTOM_BORDER),
                    max(mm_tl[1] + PT_HEIGHT, br[1] - MINIMAP_BOTTOM_BORDER)
                )
                self.minimap_ratio = (mm_br[0] - mm_tl[0]) / (mm_br[1] - mm_tl[1])
                self.minimap_sample = self.frame[mm_tl[1]:mm_br[1], mm_tl[0]:mm_br[0]]
                self.calibrated = True

                with mss.mss() as self.sct:
                    while True:
                        if not self.calibrated:
                            break

                        # Take screenshot
                        self.frame = self.screenshot()
                        if self.frame is None:
                            continue

                        # Crop the frame to only show the minimap
                        minimap = self.frame[mm_tl[1]:mm_br[1], mm_tl[0]:mm_br[0]]

                        # Determine the player's position
                        player = utils.multi_match(minimap, PLAYER_TEMPLATE, threshold=0.8)
                        if player:
                            config.player_pos = utils.convert_to_relative(player[0], minimap)

                        # Package display information to be polled by GUI
                        self.minimap = {
                            'minimap': minimap,
                            'rune_active': config.bot.rune_active if config.bot else False,
                            'rune_pos': config.bot.rune_pos if config.bot else (0, 0),
                            'path': config.path,
                            'player_pos': config.player_pos
                        }

                        if not self.ready:
                            self.ready = True
                        time.sleep(0.001)
            else:
                print("Could not find minimap templates, retrying in 1 second...")
                time.sleep(1)

    def screenshot(self, delay=1):
        """Take a screenshot of the specified window area."""
        try:
            return np.array(self.sct.grab(self.window))
        except Exception as e:
            print(f'\n[!] Error while taking screenshot: {e}, retrying in {delay} second'
                  + ('s' if delay != 1 else ''))
            time.sleep(delay)
            return None
