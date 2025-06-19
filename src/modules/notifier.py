"""Notification system for macOS."""

import threading
import time
import os
import subprocess
from src.common import config


class Notifier:
    """A class that handles notifications and alerts."""

    def __init__(self):
        config.notifier = self
        self.ready = False
        self.thread = threading.Thread(target=self._main)
        self.thread.daemon = True

    def start(self):
        """Starts the notifier thread."""
        print('\n[~] Started notifier')
        self.thread.start()

    def _main(self):
        """Main notifier loop."""
        self.ready = True
        
        while True:
            # Basic notifier loop
            time.sleep(1)

    def notify(self, title, message, sound=False):
        """Send a macOS notification."""
        try:
            script = f'''
            display notification "{message}" with title "{title}"
            '''
            subprocess.run(['osascript', '-e', script], check=False)
            
            if sound:
                # Play system sound
                subprocess.run(['afplay', '/System/Library/Sounds/Glass.aiff'], check=False)
        except Exception as e:
            print(f"Notification error: {e}")

    def alert_rune(self):
        """Alert when a rune appears."""
        self.notify("Auto Maple", "Rune appeared!", sound=True)

    def alert_death(self):
        """Alert when character dies."""
        self.notify("Auto Maple", "Character died!", sound=True)
