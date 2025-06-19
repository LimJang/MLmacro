#!/bin/bash
# Auto Maple macOS Quick Start Script

echo "Auto Maple macOS Quick Start"
echo "============================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running installation..."
    ./install.sh
    if [ $? -ne 0 ]; then
        echo "Installation failed. Please check the error messages above."
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if templates exist
if [ ! -f "assets/player_template.png" ]; then
    echo "Creating template images..."
    python3 create_templates.py
fi

# Run system test first
echo "Running system test..."
python3 test_system.py

echo ""
echo "If all tests passed, Auto Maple is ready to run!"
echo "Starting Auto Maple..."
echo ""

# Start Auto Maple
python3 main.py
