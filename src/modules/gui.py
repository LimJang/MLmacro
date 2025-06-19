"""Simplified GUI for macOS version."""

import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from src.common import config


class GUI:
    """A simplified GUI for Auto Maple macOS."""

    def __init__(self):
        config.gui = self
        self.root = None
        self.status_label = None
        self.enabled_var = None

    def start(self):
        """Start the GUI."""
        self.root = tk.Tk()
        self.root.title("Auto Maple - macOS")
        self.root.geometry("500x400")
        
        self.setup_ui()
        self.update_loop()
        self.root.mainloop()

    def setup_ui(self):
        """Setup the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Auto Maple - macOS", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Status section
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="5")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text="Bot: DISABLED")
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Control section
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="5")
        control_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Enable/Disable button
        self.enabled_var = tk.BooleanVar()
        enable_check = ttk.Checkbutton(control_frame, text="Enable Bot", 
                                     variable=self.enabled_var,
                                     command=self.toggle_bot)
        enable_check.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Load routine button
        load_routine_btn = ttk.Button(control_frame, text="Load Routine", 
                                    command=self.load_routine)
        load_routine_btn.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # Load command book button
        load_commands_btn = ttk.Button(control_frame, text="Load Command Book", 
                                     command=self.load_commands)
        load_commands_btn.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        # Information section
        info_frame = ttk.LabelFrame(main_frame, text="Information", padding="5")
        info_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        info_text = tk.Text(info_frame, height=10, width=50)
        info_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=info_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        info_text.configure(yscrollcommand=scrollbar.set)
        
        # Add initial information
        info_text.insert(tk.END, "Auto Maple macOS Version\n")
        info_text.insert(tk.END, "=" * 30 + "\n\n")
        info_text.insert(tk.END, "Controls:\n")
        info_text.insert(tk.END, "• F1 or ` (backtick): Toggle bot\n")
        info_text.insert(tk.END, "• ESC: Exit program\n\n")
        info_text.insert(tk.END, "Status:\n")
        info_text.insert(tk.END, "• Bot initialized and ready\n")
        info_text.insert(tk.END, "• Load a routine and command book to start\n\n")
        info_text.insert(tk.END, "Requirements:\n")
        info_text.insert(tk.END, "• Accessibility permissions enabled\n")
        info_text.insert(tk.END, "• Game window visible\n")
        info_text.config(state=tk.DISABLED)
        
        self.info_text = info_text
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        info_frame.columnconfigure(0, weight=1)
        info_frame.rowconfigure(0, weight=1)

    def toggle_bot(self):
        """Toggle bot enabled state."""
        config.enabled = self.enabled_var.get()
        self.update_status()

    def update_status(self):
        """Update the status display."""
        if self.status_label:
            state = "ENABLED" if config.enabled else "DISABLED"
            self.status_label.config(text=f"Bot: {state}")

    def load_routine(self):
        """Load a routine file."""
        filename = filedialog.askopenfilename(
            title="Select Routine File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.log_message(f"Loading routine: {filename}")
            # TODO: Implement routine loading
            messagebox.showinfo("Info", "Routine loading not yet implemented")

    def load_commands(self):
        """Load a command book file."""
        filename = filedialog.askopenfilename(
            title="Select Command Book",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        if filename:
            self.log_message(f"Loading command book: {filename}")
            # TODO: Implement command book loading
            messagebox.showinfo("Info", "Command book loading not yet implemented")

    def log_message(self, message):
        """Log a message to the info text area."""
        if hasattr(self, 'info_text'):
            self.info_text.config(state=tk.NORMAL)
            self.info_text.insert(tk.END, f"{message}\n")
            self.info_text.see(tk.END)
            self.info_text.config(state=tk.DISABLED)

    def update_loop(self):
        """Update loop for the GUI."""
        self.update_status()
        if self.root:
            self.root.after(100, self.update_loop)

    # Compatibility methods for the original codebase
    def set_routine(self, routine_display):
        """Set routine display (compatibility)."""
        pass

    def clear_routine_info(self):
        """Clear routine info (compatibility)."""
        pass

    class ViewClass:
        def __init__(self):
            pass
        
        class StatusClass:
            def set_routine(self, name):
                pass
            
            def set_cb(self, name):
                pass
        
        class DetailsClass:
            def display_info(self, index):
                pass
            
            def update_details(self):
                pass
        
        class RoutineClass:
            def select(self, index):
                pass
        
        status = StatusClass()
        details = DetailsClass()
        routine = RoutineClass()

    class MenuClass:
        class FileClass:
            def enable_routine_state(self):
                pass
        
        file = FileClass()

    class SettingsClass:
        def update_class_bindings(self):
            pass

    view = ViewClass()
    menu = MenuClass()
    settings = SettingsClass()
