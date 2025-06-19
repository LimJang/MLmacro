"""Keyboard listener for macOS."""

import threading
import time
from pynput import keyboard
from src.common import config


class Listener:
    """A class that listens for keyboard input."""

    def __init__(self):
        config.listener = self
        self.enabled = False
        self.ready = False
        self.thread = threading.Thread(target=self._main)
        self.thread.daemon = True

    def start(self):
        """Starts the listener thread."""
        print('\n[~] Started keyboard listener')
        self.thread.start()

    def _main(self):
        """Main listener loop."""
        def on_press(key):
            try:
                if hasattr(key, 'char') and key.char:
                    # Handle character keys
                    if key.char == '`':  # Toggle bot with backtick
                        self.toggle_bot()
                elif key == keyboard.Key.f1:  # Toggle bot with F1
                    self.toggle_bot()
            except AttributeError:
                pass

        def on_release(key):
            if key == keyboard.Key.esc:
                # ESC to exit
                return False

        self.ready = True
        
        # Start the listener
        with keyboard.Listener(
                on_press=on_press,
                on_release=on_release) as listener:
            listener.join()

    def toggle_bot(self):
        """Toggle bot enabled state."""
        config.enabled = not config.enabled
        state = "ENABLED" if config.enabled else "DISABLED"
        print(f"\n[~] Bot {state}")
