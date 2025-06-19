#!/usr/bin/env python3
"""Test which keys are available on macOS"""

from pynput.keyboard import Key

print("Testing available keys on macOS:")
test_keys = [
    'backspace', 'tab', 'enter', 'shift', 'ctrl', 'alt', 'cmd',
    'caps_lock', 'esc', 'space', 'page_up', 'page_down', 
    'end', 'home', 'insert', 'delete', 'left', 'up', 'right', 'down',
    'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12'
]

available = []
unavailable = []

for key_name in test_keys:
    try:
        key = getattr(Key, key_name)
        available.append(key_name)
        print(f"✓ {key_name}")
    except AttributeError:
        unavailable.append(key_name)
        print(f"✗ {key_name}")

print(f"\nAvailable: {len(available)}")
print(f"Unavailable: {len(unavailable)}")
if unavailable:
    print(f"Missing keys: {', '.join(unavailable)}")
