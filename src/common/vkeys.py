"""A module for simulating low-level keyboard and mouse key presses on macOS."""

import time
import pyautogui
from pynput import keyboard, mouse
from pynput.keyboard import Key, KeyCode
from random import random
from src.common import utils


# macOS Key mappings
KEY_MAP = {
    'left': Key.left,   # Arrow keys
    'up': Key.up,
    'right': Key.right,
    'down': Key.down,

    'backspace': Key.backspace,      # Special keys
    'tab': Key.tab,
    'enter': Key.enter,
    'shift': Key.shift,
    'ctrl': Key.ctrl,
    'alt': Key.alt,
    'cmd': Key.cmd,
    # 'caps_lock': Key.caps_lock,  # Use caps instead on macOS
    'caps': Key.caps_lock,
    'esc': Key.esc,
    'space': Key.space,
    'page_up': Key.page_up,
    'page_down': Key.page_down,
    'end': Key.end,
    'home': Key.home,
    # 'insert': Key.insert,  # Not available on macOS
    'delete': Key.delete,

    '0': KeyCode.from_char('0'),      # Numbers
    '1': KeyCode.from_char('1'),
    '2': KeyCode.from_char('2'),
    '3': KeyCode.from_char('3'),
    '4': KeyCode.from_char('4'),
    '5': KeyCode.from_char('5'),
    '6': KeyCode.from_char('6'),
    '7': KeyCode.from_char('7'),
    '8': KeyCode.from_char('8'),
    '9': KeyCode.from_char('9'),

    'a': KeyCode.from_char('a'),      # Letters
    'b': KeyCode.from_char('b'),
    'c': KeyCode.from_char('c'),
    'd': KeyCode.from_char('d'),
    'e': KeyCode.from_char('e'),
    'f': KeyCode.from_char('f'),
    'g': KeyCode.from_char('g'),
    'h': KeyCode.from_char('h'),
    'i': KeyCode.from_char('i'),
    'j': KeyCode.from_char('j'),
    'k': KeyCode.from_char('k'),
    'l': KeyCode.from_char('l'),
    'm': KeyCode.from_char('m'),
    'n': KeyCode.from_char('n'),
    'o': KeyCode.from_char('o'),
    'p': KeyCode.from_char('p'),
    'q': KeyCode.from_char('q'),
    'r': KeyCode.from_char('r'),
    's': KeyCode.from_char('s'),
    't': KeyCode.from_char('t'),
    'u': KeyCode.from_char('u'),
    'v': KeyCode.from_char('v'),
    'w': KeyCode.from_char('w'),
    'x': KeyCode.from_char('x'),
    'y': KeyCode.from_char('y'),
    'z': KeyCode.from_char('z'),

    'f1': Key.f1,     # Functional keys
    'f2': Key.f2,
    'f3': Key.f3,
    'f4': Key.f4,
    'f5': Key.f5,
    'f6': Key.f6,
    'f7': Key.f7,
    'f8': Key.f8,
    'f9': Key.f9,
    'f10': Key.f10,
    'f11': Key.f11,
    'f12': Key.f12,

    ';': KeyCode.from_char(';'),      # Special characters
    '=': KeyCode.from_char('='),
    ',': KeyCode.from_char(','),
    '-': KeyCode.from_char('-'),
    '.': KeyCode.from_char('.'),
    '/': KeyCode.from_char('/'),
    '`': KeyCode.from_char('`'),
    '[': KeyCode.from_char('['),
    '\\': KeyCode.from_char('\\'),
    ']': KeyCode.from_char(']'),
    "'": KeyCode.from_char("'")
}

# Global controller instances
_keyboard_controller = keyboard.Controller()
_mouse_controller = mouse.Controller()


#################################
#           Functions           #
#################################
@utils.run_if_enabled
def key_down(key):
    """
    Simulates a key-down action. Can be cancelled by Bot.toggle_enabled.
    :param key:     The key to press.
    :return:        None
    """

    key = key.lower()
    if key not in KEY_MAP.keys():
        print(f"Invalid keyboard input: '{key}'.")
    else:
        _keyboard_controller.press(KEY_MAP[key])


def key_up(key):
    """
    Simulates a key-up action. Cannot be cancelled by Bot.toggle_enabled.
    This is to ensure no keys are left in the 'down' state when the program pauses.
    :param key:     The key to press.
    :return:        None
    """

    key = key.lower()
    if key not in KEY_MAP.keys():
        print(f"Invalid keyboard input: '{key}'.")
    else:
        _keyboard_controller.release(KEY_MAP[key])


@utils.run_if_enabled
def press(key, n, down_time=0.05, up_time=0.1):
    """
    Presses KEY N times, holding it for DOWN_TIME seconds, and releasing for UP_TIME seconds.
    :param key:         The keyboard input to press.
    :param n:           Number of times to press KEY.
    :param down_time:   Duration of down-press (in seconds).
    :param up_time:     Duration of release (in seconds).
    :return:            None
    """

    for _ in range(n):
        key_down(key)
        time.sleep(down_time * (0.8 + 0.4 * random()))
        key_up(key)
        time.sleep(up_time * (0.8 + 0.4 * random()))


@utils.run_if_enabled
def click(position, button='left'):
    """
    Simulate a mouse click with BUTTON at POSITION.
    :param position:    The (x, y) position at which to click.
    :param button:      Either the left or right mouse button.
    :return:            None
    """

    if button not in ['left', 'right']:
        print(f"'{button}' is not a valid mouse button.")
    else:
        # Move mouse to position
        _mouse_controller.position = position
        time.sleep(0.01)  # Small delay for mouse movement
        
        # Click
        if button == 'left':
            _mouse_controller.click(mouse.Button.left)
        else:
            _mouse_controller.click(mouse.Button.right)


@utils.run_if_enabled
def move_mouse(position):
    """
    Move mouse to the specified position.
    :param position:    The (x, y) position to move to.
    :return:            None
    """
    _mouse_controller.position = position


def get_mouse_position():
    """
    Get current mouse position.
    :return:    Current (x, y) position of the mouse.
    """
    return _mouse_controller.position


# Compatibility functions for pyautogui integration
def get_screen_size():
    """Get screen dimensions."""
    return pyautogui.size()


def screenshot():
    """Take a screenshot using pyautogui."""
    return pyautogui.screenshot()
