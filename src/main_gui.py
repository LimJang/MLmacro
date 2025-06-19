"""
Main GUI for Auto Maple Bot
Cross-platform Tkinter interface
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
from pathlib import Path
import sys
import os

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__)))

from screen_capture import ScreenCapture
from window_detector import WindowDetector
from template_matcher import TemplateMatcher

try:
    from pyqt_template_manager import PyQtTemplateManager
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False
    print("⚠️ PyQt5 not available. Advanced template features disabled.")


class AutoMapleGUI:
    """Main GUI application for Auto Maple Bot"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_variables()
        self.setup_widgets()
        
        # Initialize core modules
        self.screen_capture = ScreenCapture()
        self.window_detector = WindowDetector()
        self.template_matcher = TemplateMatcher()
        
        # Initialize PyQt5 template manager if available
        if PYQT5_AVAILABLE:
            try:
                self.pyqt_template_manager = PyQtTemplateManager()
            except Exception as e:
                self.log_debug(f"⚠️ Failed to initialize PyQt5 template manager: {e}")
                self.pyqt_template_manager = None
        else:
            self.pyqt_template_manager = None
        
        # Bot state
        self.bot_running = False
        self.bot_thread = None
        
    def setup_window(self):
        """Configure main window"""
        self.root.title("Auto Maple Bot v2.0 - macOS")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Set minimum size
        self.root.minsize(600, 500)
        
        # Center window on screen
        self.center_window()
        
    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    def setup_variables(self):
        """Initialize GUI variables"""
        self.status_var = tk.StringVar(value="Ready")
        self.game_window_var = tk.StringVar(value="No game window detected")
        self.template_count_var = tk.StringVar(value="Templates: 0")
        
    def setup_widgets(self):
        """Create and arrange GUI widgets"""
        # Create main frame with scrollbar
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Status bar at top
        self.create_status_bar(main_frame)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Create tabs
        self.create_bot_control_tab(notebook)
        self.create_template_tab(notebook)
        self.create_settings_tab(notebook)
        self.create_debug_tab(notebook)
        
    def create_status_bar(self, parent):
        """Create status bar section"""
        status_frame = ttk.LabelFrame(parent, text="System Status", padding=10)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Status indicators
        ttk.Label(status_frame, text="Bot Status:").grid(row=0, column=0, sticky="w")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, foreground="green")
        status_label.grid(row=0, column=1, sticky="w", padx=(10, 0))
        
        ttk.Label(status_frame, text="Game Window:").grid(row=1, column=0, sticky="w")
        game_label = ttk.Label(status_frame, textvariable=self.game_window_var)
        game_label.grid(row=1, column=1, sticky="w", padx=(10, 0))
        
        ttk.Label(status_frame, textvariable=self.template_count_var).grid(row=2, column=0, sticky="w")
        
        # Refresh button
        ttk.Button(status_frame, text="🔄 Refresh", command=self.refresh_status).grid(row=0, column=2, padx=(20, 0))
        
    def create_bot_control_tab(self, notebook):
        """Create bot control tab"""
        bot_frame = ttk.Frame(notebook)
        notebook.add(bot_frame, text="Bot Control")
        
        # Bot control section
        control_frame = ttk.LabelFrame(bot_frame, text="Bot Control", padding=20)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack()
        
        self.start_button = ttk.Button(
            button_frame, 
            text="▶️ START BOT", 
            command=self.start_bot,
            style="Accent.TButton"
        )
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(
            button_frame, 
            text="⏹️ STOP BOT", 
            command=self.stop_bot,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.pause_button = ttk.Button(
            button_frame, 
            text="⏸️ PAUSE", 
            command=self.pause_bot,
            state=tk.DISABLED
        )
        self.pause_button.pack(side=tk.LEFT)
        
        # Quick actions
        quick_frame = ttk.LabelFrame(bot_frame, text="Quick Actions", padding=20)
        quick_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(quick_frame, text="📸 Test Screenshot", command=self.test_screenshot).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(quick_frame, text="🎯 Find Game Window", command=self.find_game_window).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(quick_frame, text="🖼️ Open Templates Folder", command=self.open_templates_folder).pack(side=tk.LEFT)
        
    def create_template_tab(self, notebook):
        """Create template management tab"""
        template_frame = ttk.Frame(notebook)
        notebook.add(template_frame, text="Templates")
        
        # Template creation section
        creation_frame = ttk.LabelFrame(template_frame, text="Template Creation", padding=20)
        creation_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # PyQt5 template capture (preferred)
        if PYQT5_AVAILABLE:
            ttk.Button(
                creation_frame, 
                text="📸 CAPTURE (PyQt5)", 
                command=self.capture_screen_pyqt5,
                style="Accent.TButton"
            ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Fallback Tkinter capture
        ttk.Button(
            creation_frame, 
            text="📸 CAPTURE (Basic)", 
            command=self.capture_screen_basic
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(creation_frame, text="🔍 TEST MATCH", command=self.test_template_match).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(creation_frame, text="🎯 QUICK TEST", command=self.quick_template_test).pack(side=tk.LEFT, padx=(0, 10))
        
        # Template type selection
        type_frame = ttk.Frame(creation_frame)
        type_frame.pack(side=tk.RIGHT)
        
        ttk.Label(type_frame, text="Type:").pack(side=tk.LEFT)
        self.template_type = tk.StringVar(value="player")
        ttk.Radiobutton(type_frame, text="Player", variable=self.template_type, value="player").pack(side=tk.LEFT, padx=(5, 0))
        ttk.Radiobutton(type_frame, text="Monster", variable=self.template_type, value="monster").pack(side=tk.LEFT, padx=(5, 0))
        
        # Template list section
        list_frame = ttk.LabelFrame(template_frame, text="Template Library", padding=20)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Template listbox with scrollbar
        listbox_frame = ttk.Frame(list_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        self.template_listbox = tk.Listbox(listbox_frame)
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.template_listbox.yview)
        self.template_listbox.config(yscrollcommand=scrollbar.set)
        
        self.template_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Template management buttons
        template_buttons = ttk.Frame(list_frame)
        template_buttons.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(template_buttons, text="🔄 Refresh List", command=self.refresh_template_list).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(template_buttons, text="🗑️ Delete Selected", command=self.delete_template).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(template_buttons, text="📁 Open Folder", command=self.open_templates_folder).pack(side=tk.LEFT)
        
    def create_settings_tab(self, notebook):
        """Create settings tab"""
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="Settings")
        
        # Placeholder for settings
        ttk.Label(settings_frame, text="Settings will be implemented in Phase 4", font=("Arial", 12)).pack(pady=50)
        
    def create_debug_tab(self, notebook):
        """Create debug tab"""
        debug_frame = ttk.Frame(notebook)
        notebook.add(debug_frame, text="Debug")
        
        # Debug log area
        log_frame = ttk.LabelFrame(debug_frame, text="Debug Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Text widget with scrollbar
        text_frame = ttk.Frame(log_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.debug_text = tk.Text(text_frame, wrap=tk.WORD, height=15)
        debug_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.debug_text.yview)
        self.debug_text.config(yscrollcommand=debug_scrollbar.set)
        
        self.debug_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        debug_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Debug buttons
        debug_buttons = ttk.Frame(log_frame)
        debug_buttons.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(debug_buttons, text="🧪 Run Tests", command=self.run_system_tests).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(debug_buttons, text="🗑️ Clear Log", command=self.clear_debug_log).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(debug_buttons, text="💾 Save Log", command=self.save_debug_log).pack(side=tk.LEFT)
        
    # Event handlers
    def start_bot(self):
        """Start bot operation"""
        self.bot_running = True
        self.status_var.set("Bot Starting...")
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.NORMAL)
        
        # Start bot in separate thread
        self.bot_thread = threading.Thread(target=self.bot_main_loop, daemon=True)
        self.bot_thread.start()
        
        self.log_debug("🤖 Bot started")
        
    def stop_bot(self):
        """Stop bot operation"""
        self.bot_running = False
        self.status_var.set("Bot Stopping...")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.DISABLED)
        
        self.log_debug("🛑 Bot stopped")
        
    def pause_bot(self):
        """Pause/resume bot operation"""
        # Placeholder for pause functionality
        self.log_debug("⏸️ Pause functionality will be implemented in Phase 3")
        
    def bot_main_loop(self):
        """Main bot loop (placeholder)"""
        while self.bot_running:
            try:
                # Placeholder bot logic
                self.status_var.set("Bot Running...")
                time.sleep(1)  # Placeholder delay
                
            except Exception as e:
                self.log_debug(f"❌ Bot error: {e}")
                break
                
        self.status_var.set("Bot Stopped")
        
    def test_screenshot(self):
        """Test screenshot functionality"""
        self.log_debug("📸 Testing screenshot...")
        
        try:
            img = self.screen_capture.capture_screen()
            if img is not None:
                filename = f"test_screenshot_{int(time.time())}.png"
                if self.screen_capture.save_screenshot(img, filename):
                    self.log_debug(f"✅ Screenshot saved: {filename}")
                    messagebox.showinfo("Success", f"Screenshot saved as {filename}")
                else:
                    self.log_debug("❌ Failed to save screenshot")
            else:
                self.log_debug("❌ Failed to capture screenshot")
                
        except Exception as e:
            self.log_debug(f"❌ Screenshot error: {e}")
            
    def find_game_window(self):
        """Find and focus game window"""
        self.log_debug("🎯 Searching for game window...")
        
        try:
            window = self.window_detector.find_and_focus_game_window(debug=True)
            if window:
                self.game_window_var.set(f"Found: {window['name']} ({window['width']}x{window['height']})")
                self.log_debug(f"✅ Game window found: {window['name']}")
                messagebox.showinfo("Success", f"Game window found:\n{window['name']}")
            else:
                self.game_window_var.set("No game window detected")
                self.log_debug("❌ No game window found")
                messagebox.showwarning("Not Found", "No game window detected")
                
        except Exception as e:
            self.log_debug(f"❌ Window detection error: {e}")
            
    def capture_screen_pyqt5(self):
        """Launch PyQt5 template capture"""
        if not self.pyqt_template_manager:
            self.log_debug("⚠️ PyQt5 template manager not available")
            messagebox.showwarning("Not Available", "PyQt5 template manager not available")
            return
            
        self.log_debug("📸 Starting PyQt5 template capture...")
        
        try:
            success = self.pyqt_template_manager.capture_and_create_template()
            if success:
                self.log_debug("✅ Template created successfully!")
                self.refresh_template_list()
                messagebox.showinfo("Success", "Template created successfully!")
            else:
                self.log_debug("⚠️ Template creation cancelled")
        except Exception as e:
            self.log_debug(f"❌ Template capture error: {e}")
            messagebox.showerror("Error", f"Template capture failed: {e}")
            
    def capture_screen_basic(self):
        """Basic screen capture (fallback method)"""
        self.log_debug("📸 Basic template capture will be enhanced in future updates")
        messagebox.showinfo("Basic Capture", "Basic template capture will be enhanced in future updates\n\nPlease use PyQt5 capture for full functionality.")
        
    def test_template_match(self):
        """Test template matching with PyQt5 manager"""
        if not self.pyqt_template_manager:
            self.log_debug("⚠️ PyQt5 template manager not available")
            messagebox.showwarning("Not Available", "PyQt5 template manager not available")
            return
            
        self.log_debug("🔍 Starting template matching test...")
        
        try:
            success = self.pyqt_template_manager.test_template_matching()
            if success:
                self.log_debug("✅ Template matching test completed!")
            else:
                self.log_debug("⚠️ Template matching test failed")
        except Exception as e:
            self.log_debug(f"❌ Template matching error: {e}")
            messagebox.showerror("Error", f"Template matching failed: {e}")
            
    def quick_template_test(self):
        """Quick template test without GUI"""
        self.log_debug("🎯 Running quick template test...")
        
        try:
            # Get current templates
            templates = self.template_matcher.get_template_list()
            if not templates:
                self.log_debug("⚠️ No templates found")
                messagebox.showwarning("No Templates", "No templates found. Create templates first.")
                return
                
            self.log_debug(f"📋 Found {len(templates)} templates")
            
            # Capture current screen
            window = self.window_detector.find_and_focus_game_window()
            if not window:
                self.log_debug("❌ No game window found")
                messagebox.showwarning("No Window", "Game window not found")
                return
                
            bounds = self.window_detector.get_window_bounds(window)
            screenshot = self.screen_capture.capture_screen(bounds)
            
            if screenshot is None:
                self.log_debug("❌ Screenshot capture failed")
                messagebox.showerror("Error", "Failed to capture screenshot")
                return
                
            # Test matching
            matches = self.template_matcher.match_templates(screenshot)
            
            self.log_debug(f"🎯 Found {len(matches)} matches:")
            for match in matches[:5]:  # Top 5 matches
                self.log_debug(f"  • {match.template_name} ({match.template_type}): {match.confidence:.3f}")
                
            if matches:
                # Save debug image
                debug_image = self.template_matcher.visualize_matches(screenshot, matches)
                timestamp = int(time.time())
                filename = f"quick_test_{timestamp}.png"
                if self.screen_capture.save_screenshot(debug_image, filename):
                    self.log_debug(f"💾 Debug image saved: {filename}")
                    
                messagebox.showinfo(
                    "Test Results", 
                    f"Found {len(matches)} matches!\n\n" +
                    "\n".join([f"• {m.template_name}: {m.confidence:.3f}" for m in matches[:5]]) +
                    f"\n\nDebug image saved: {filename}"
                )
            else:
                self.log_debug("⚠️ No matches found")
                messagebox.showinfo("Test Results", "No template matches found")
                
        except Exception as e:
            self.log_debug(f"❌ Quick test error: {e}")
            messagebox.showerror("Error", f"Quick test failed: {e}")
        
    def refresh_status(self):
        """Refresh system status"""
        self.find_game_window()
        self.refresh_template_list()
        
    def refresh_template_list(self):
        """Refresh template list"""
        try:
            # Force reload templates from disk
            self.template_matcher.load_all_templates()
            
            # Get templates from matcher
            templates = self.template_matcher.get_template_list()
            
            # Debug info
            print(f"📋 Template directory: {self.template_matcher.templates_dir}")
            print(f"📋 Found {len(templates)} templates in cache")
            
            # List actual files in directory
            template_files = list(self.template_matcher.templates_dir.glob("*.png"))
            print(f"📋 Found {len(template_files)} .png files on disk:")
            for f in template_files:
                print(f"  - {f.name}")
            
            # Update count
            self.template_count_var.set(f"Templates: {len(templates)}")
            
            # Clear and populate listbox
            self.template_listbox.delete(0, tk.END)
            
            for template in templates:
                name = template['name']
                template_type = template['type']
                size = template.get('size', 'unknown')
                confidence = template.get('confidence_threshold', 0.7)
                
                display_text = f"{name} ({template_type}) - {size} - {confidence:.2f}"
                self.template_listbox.insert(tk.END, display_text)
                
            self.log_debug(f"📋 Refreshed template list: {len(templates)} templates")
            
        except Exception as e:
            self.log_debug(f"❌ Failed to refresh template list: {e}")
            self.template_count_var.set("Templates: Error")
        
    def delete_template(self):
        """Delete selected template"""
        selection = self.template_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a template to delete")
            return
            
        try:
            # Get selected template name
            selected_text = self.template_listbox.get(selection[0])
            template_name = selected_text.split(' (')[0]  # Extract name before type
            
            # Confirm deletion
            result = messagebox.askyesno(
                "Confirm Deletion", 
                f"Are you sure you want to delete template '{template_name}'?"
            )
            
            if result:
                if self.template_matcher.delete_template(template_name):
                    self.log_debug(f"🗑️ Template deleted: {template_name}")
                    self.refresh_template_list()
                    messagebox.showinfo("Success", f"Template '{template_name}' deleted")
                else:
                    self.log_debug(f"❌ Failed to delete template: {template_name}")
                    messagebox.showerror("Error", f"Failed to delete template '{template_name}'")
                    
        except Exception as e:
            self.log_debug(f"❌ Template deletion error: {e}")
            messagebox.showerror("Error", f"Failed to delete template: {e}")
        
    def open_templates_folder(self):
        """Open templates folder"""
        templates_path = Path(__file__).parent.parent / "templates"
        templates_path.mkdir(exist_ok=True)
        
        try:
            os.system(f"open '{templates_path}'")
            self.log_debug(f"📁 Opened templates folder: {templates_path}")
        except Exception as e:
            self.log_debug(f"❌ Failed to open templates folder: {e}")
            
    def run_system_tests(self):
        """Run system tests"""
        self.log_debug("🧪 Running system tests...")
        
        # Test screen capture
        try:
            img = self.screen_capture.capture_screen()
            if img is not None:
                self.log_debug("✅ Screen capture: OK")
            else:
                self.log_debug("❌ Screen capture: FAILED")
        except Exception as e:
            self.log_debug(f"❌ Screen capture test error: {e}")
            
        # Test window detection
        try:
            windows = self.window_detector.get_all_windows()
            self.log_debug(f"✅ Window detection: OK ({len(windows)} windows)")
        except Exception as e:
            self.log_debug(f"❌ Window detection test error: {e}")
            
        self.log_debug("🧪 System tests completed")
        
    def log_debug(self, message):
        """Add message to debug log"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.debug_text.insert(tk.END, log_message)
        self.debug_text.see(tk.END)
        
        # Keep log size manageable
        if int(self.debug_text.index('end-1c').split('.')[0]) > 1000:
            self.debug_text.delete('1.0', '500.0')
            
    def clear_debug_log(self):
        """Clear debug log"""
        self.debug_text.delete('1.0', tk.END)
        self.log_debug("🗑️ Debug log cleared")
        
    def save_debug_log(self):
        """Save debug log to file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                content = self.debug_text.get('1.0', tk.END)
                with open(filename, 'w') as f:
                    f.write(content)
                self.log_debug(f"💾 Debug log saved: {filename}")
        except Exception as e:
            self.log_debug(f"❌ Failed to save log: {e}")
            
    def run(self):
        """Start the GUI application"""
        self.log_debug("🚀 Auto Maple Bot v2.0 started")
        self.log_debug("📋 Phase 1: Basic Framework - Ready")
        self.refresh_status()
        self.root.mainloop()
        

def main():
    """Main entry point"""
    app = AutoMapleGUI()
    app.run()


if __name__ == "__main__":
    main()
