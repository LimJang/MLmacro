"""An interpreter that reads and executes user-created routines - macOS version."""

import threading
import time
import os
import cv2
import numpy as np
from src.common import config, utils
from src.common.vkeys import press, click
from src.common.interfaces import Configurable


# The rune's buff icon
RUNE_BUFF_TEMPLATE = cv2.imread('assets/rune_buff_template.jpg', 0) if os.path.exists('assets/rune_buff_template.jpg') else None


class Bot(Configurable):
    """A class that interprets and executes user-defined routines."""

    DEFAULT_CONFIG = {
        'Interact': 'y',
        'Feed pet': '9'
    }

    def __init__(self):
        """Loads a user-defined routine on start up and initializes this Bot's main thread."""

        super().__init__('keybindings')
        config.bot = self

        self.rune_active = False
        self.rune_pos = (0, 0)
        self.rune_closest_pos = (0, 0)      # Location of the Point closest to rune
        self.submodules = []
        self.command_book = None            # CommandBook instance

        # Initialize with empty routine
        class EmptyRoutine:
            def __init__(self):
                self.index = 0
                self.sequence = []
            
            def __len__(self):
                return len(self.sequence)
            
            def __getitem__(self, index):
                return self.sequence[index] if index < len(self.sequence) else None
            
            def step(self):
                if len(self.sequence) > 0:
                    self.index = (self.index + 1) % len(self.sequence)

        config.routine = EmptyRoutine()

        self.ready = False
        self.thread = threading.Thread(target=self._main)
        self.thread.daemon = True

    def start(self):
        """
        Starts this Bot object's thread.
        :return:    None
        """

        print('\n[~] Started main bot loop')
        self.thread.start()

    def _main(self):
        """
        The main body of Bot that executes the user's routine.
        :return:    None
        """

        print('\n[~] Bot ready (detection algorithm disabled for now)')
        self.ready = True
        
        if hasattr(config, 'listener'):
            config.listener.enabled = True
        
        last_fed = time.time()
        
        while True:
            if config.enabled and len(config.routine) > 0:
                # Basic bot loop - simplified for initial testing
                if hasattr(self, 'command_book') and self.command_book:
                    # Execute buffing if available
                    try:
                        if hasattr(self.command_book, 'buff'):
                            self.command_book.buff.main()
                    except:
                        pass

                # Pet feeding logic
                now = time.time()
                if now - last_fed > 120:  # Feed every 2 minutes as default
                    try:
                        press(self.config['Feed pet'], 1)
                        last_fed = now
                    except:
                        pass

                # Execute routine if available
                if len(config.routine) > 0:
                    try:
                        element = config.routine[config.routine.index]
                        if element and hasattr(element, 'execute'):
                            element.execute()
                        config.routine.step()
                    except:
                        pass
            else:
                time.sleep(0.01)

    def load_commands(self, file):
        """Load command book - simplified for testing."""
        print(f"[~] Command book loading requested: {file}")
        # This will be implemented when we add the command book system
        pass

    def update_submodules(self, force=False):
        """Update submodules - simplified for macOS."""
        print('[~] Submodule update requested (simplified for macOS)')
        pass
