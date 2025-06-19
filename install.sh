#!/bin/bash
# Auto Maple macOS Installation Script

echo "=================================="
echo "Auto Maple macOS Installation"
echo "=================================="

# Check Python version
echo "Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "Error: Python 3 is required but not installed."
    echo "Please install Python 3.8 or later from https://python.org"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "Error: Failed to create virtual environment."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies."
    echo "Please check the requirements.txt file and try again."
    exit 1
fi

# Create dummy templates
echo "Creating dummy template images..."
python3 create_templates.py

# Create resources directory structure
echo "Creating resources directory structure..."
mkdir -p resources/command_books
mkdir -p resources/keybindings
mkdir -p resources/routines
mkdir -p layouts
mkdir -p .settings

# Create example files
echo "Creating example files..."

# Example command book
cat > resources/command_books/example.py << 'EOF'
"""Example command book for Auto Maple macOS."""

from src.routine.components import Command


class Key:
    """Key bindings for this character."""
    # Movement
    up = 'up'
    down = 'down'
    left = 'left'
    right = 'right'
    
    # Skills
    attack = 'space'
    skill1 = 'a'
    skill2 = 's'
    skill3 = 'd'
    
    # Items
    potion = '1'
    mana = '2'


class Move(Command):
    """Basic movement command."""
    def __init__(self, x, y, max_steps=15):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.max_steps = int(max_steps)

    def main(self):
        # Basic movement implementation
        print(f"Moving to ({self.x}, {self.y})")


class Adjust(Command):
    """Fine-tune position."""
    def __init__(self, x, y, max_steps=5):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.max_steps = int(max_steps)

    def main(self):
        print(f"Adjusting to ({self.x}, {self.y})")


class Buff(Command):
    """Buff command."""
    def main(self):
        print("Casting buffs...")


class Attack(Command):
    """Basic attack."""
    def main(self):
        from src.common.vkeys import press
        press(Key.attack, 1)
EOF

# Example routine
cat > resources/routines/example.csv << 'EOF'
# Example routine for Auto Maple macOS
# Format: command, x, y, options

# Move to first position and attack
point, 0.3, 0.5
    attack
    
# Move to second position and attack
point, 0.7, 0.5
    attack

# Jump back to start
jump, start

# Label for looping
label, start
EOF

echo "Installation completed successfully!"
echo ""
echo "Next steps:"
echo "1. Grant accessibility permissions:"
echo "   System Preferences > Security & Privacy > Privacy > Accessibility"
echo "2. Run the test script:"
echo "   python3 test_system.py"
echo "3. Start Auto Maple:"
echo "   python3 main.py"
echo ""
echo "For more information, see README.md"
