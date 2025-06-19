# MLmacro - Auto Maple macOS for MapleLand-like Games

An intelligent macro bot for 2D side-scrolling MMORPG games, ported to macOS with enhanced template-based monster detection and smart combat system.

## 🚀 Features

### Phase 1: Completed
- ✅ **macOS Compatibility**: Fully ported from Windows-only version
- ✅ **Minimap-based Movement**: Intelligent waypoint navigation
- ✅ **Accessibility Integration**: macOS permission handling
- ✅ **Real-time Screen Capture**: Optimized for game detection

### Phase 2: In Development
- 🔄 **Template-based Monster Detection**: Real-time enemy recognition
- 🔄 **Smart Combat System**: Direction-aware skill usage
- 🔄 **Hybrid Movement + Combat**: Interrupt movement for combat
- 🔄 **Anti-detection Measures**: Random timing and human-like behavior

## 🎯 System Requirements

- macOS 10.14+
- Python 3.8+
- Accessibility permissions enabled
- 4GB+ RAM recommended

## 📦 Installation

### Quick Start
```bash
git clone https://github.com/LimJang/MLmacro.git
cd MLmacro
./install.sh
```

### Manual Installation
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create templates
python create_templates.py

# Run system test
python test_system.py
```

## 🎮 Usage

### Basic Execution
```bash
source venv/bin/activate
python main.py
```

### Controls
- **F1** or **`**: Toggle bot on/off
- **ESC**: Exit program
- **GUI**: Load routines and command books

### Game Setup
1. Launch your MapleLand-like game in windowed mode
2. Start MLmacro
3. Load character command book (skills configuration)
4. Load hunting routine (waypoint sequence)
5. Enable bot with F1 or GUI

## 🛠️ Configuration

### Command Books
Define character skills and key bindings:
```python
# resources/command_books/my_character.py
class Key:
    attack = 'space'
    skill1 = 'a'
    skill2 = 's'

class Attack(Command):
    def main(self):
        press(Key.attack, 1)
```

### Routines
Set up hunting waypoints:
```csv
# resources/routines/my_routine.csv
point, 0.3, 0.5
    attack
point, 0.7, 0.5  
    skill1
jump, start
label, start
```

## 🔧 Advanced Features

### Template-based Detection (Phase 2)
- **Player Detection**: Nickname tag template matching
- **Monster Detection**: Multiple monster type templates
- **Real-time Processing**: 100ms cycle with anti-detection jitter

### Smart Combat System
- **X-axis Distance Calculation**: Horizontal attack prioritization
- **Direction-aware Combat**: Automatic facing and skill usage
- **Multi-target Management**: Closest-first targeting
- **Buff Management**: Automated skill rotation

## 🚨 Important Notes

### Legal & Ethical Use
- Check game terms of service before use
- Use responsibly and at your own risk
- Respect other players and game balance

### Performance
- Optimized for sub-100ms operation
- Template matching with ~27-67ms cycle time
- Memory efficient with minimal system impact

## 📁 Project Structure

```
MLmacro/
├── main.py              # Entry point
├── requirements.txt     # Python dependencies
├── src/
│   ├── modules/         # Core system modules
│   ├── common/          # Shared utilities
│   └── tools/           # Development tools
├── resources/           # Game configurations
├── assets/              # Template images
└── memory-bank/         # Project tracking
```

## 🐛 Troubleshooting

### Permission Issues
```bash
# Grant accessibility permissions
System Preferences > Security & Privacy > Accessibility
```

### Installation Problems
```bash
# Test system compatibility
python test_system.py

# Reset virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📋 Development Status

- [x] Phase 1: macOS Porting & Basic Functionality
- [ ] Phase 2: Template-based Monster Detection
- [ ] Phase 3: Smart Combat Integration
- [ ] Phase 4: Advanced Anti-detection Features
- [ ] Phase 5: Multi-character Support

## 📜 License

This project is for educational purposes. Use responsibly and in accordance with applicable game terms of service.

## 🙏 Acknowledgments

Based on the original Auto Maple project by [tanjeffreyz](https://github.com/tanjeffreyz/auto-maple)
- Enhanced for macOS compatibility
- Extended with intelligent combat system
- Optimized for MapleLand-like games

---

**Made with ❤️ for the MapleStory community**
