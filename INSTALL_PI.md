# Raspberry Pi 5 Installation Guide

This guide will help you install and run the Microplate Light Guide application on Raspberry Pi 5.

## 🚀 One-Click Automated Installation

### Method 1: Complete Automated Installation (Recommended)
```bash
curl -sSL https://raw.githubusercontent.com/alextu870719/rspi5_microplate/main/install.sh | bash
```

This script will automatically:
- Update the system
- Install all necessary packages
- Download the project
- Configure touchscreen
- Set up auto-startup
- Create desktop shortcuts

### Method 2: Quick Installation (For existing basic environments)
```bash
curl -sSL https://raw.githubusercontent.com/alextu870719/rspi5_microplate/main/quick_install.sh | bash
```

## 📋 System Requirements

### Hardware Requirements
- Raspberry Pi 5 (recommended) or Pi 4
- 7-inch official touchscreen (800×480)
- MicroSD card (minimum 16GB, recommended 32GB)
- USB serial converters (for hardware communication)

### Software Requirements
- Raspberry Pi OS (Bullseye or newer)
- Python 3.7+
- X11 desktop environment

## 🛠️ Manual Installation Steps

If automatic installation fails, you can manually execute the following steps:

### 1. Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Python Dependencies
```bash
sudo apt install -y python3-pyqt5 python3-pandas python3-serial python3-pip git
```

### 3. Download Project
```bash
cd ~
git clone https://github.com/alextu870719/rspi5_microplate.git
cd rspi5_microplate
```

### 4. Install Additional Dependencies
```bash
pip3 install --user -r requirements.txt
```

### 5. Test Run
```bash
python3 main.py
```

## ⚙️ Touchscreen Configuration

### Enable 7-inch Touchscreen
Edit `/boot/config.txt`:
```bash
sudo nano /boot/config.txt
```

Add the following lines:
```
# 7-inch touchscreen support
dtoverlay=rpi-ft5406
dtoverlay=rpi-backlight
```

### Calibrate Touch (if needed)
```bash
xinput_calibrator
```

## 🔧 Auto-startup Configuration

### Using systemd Service (Recommended)
Create service file:
```bash
sudo nano /etc/systemd/system/microplate.service
```

Content:
```ini
[Unit]
Description=Microplate Light Guide
After=graphical-session.target

[Service]
Type=simple
User=pi
Environment=DISPLAY=:0
WorkingDirectory=/home/pi/rspi5_microplate
ExecStart=/usr/bin/python3 /home/pi/rspi5_microplate/main.py
Restart=always

[Install]
WantedBy=graphical-session.target
```

Enable service:
```bash
sudo systemctl enable microplate.service
sudo systemctl start microplate.service
```

### Using autostart (Alternative method)
```bash
mkdir -p ~/.config/autostart
nano ~/.config/autostart/microplate.desktop
```

Content:
```ini
[Desktop Entry]
Type=Application
Name=Microplate Light Guide
Exec=python3 /home/pi/rspi5_microplate/main.py
Hidden=false
X-GNOME-Autostart-enabled=true
```

## 📁 Project Structure

```
rspi5_microplate/
├── main.py                       # Main application
├── Input_CSV/                    # CSV sample files
│   ├── Step_Source_Destination.csv  # Complete step format
│   ├── Step_Source.csv              # Source-only format
│   └── README.md                    # CSV documentation
├── install.sh                    # Complete installation script
├── quick_install.sh              # Quick installation script  
├── run_microplate.sh             # Quick launch script
├── INSTALL_PI.md                 # This installation guide
└── requirements.txt              # Python dependencies
```

## 🎯 Usage Instructions

### Basic Operations
1. Click "Load CSV" to load protocol files
2. Use plate type button to switch formats (384→96→48→24)
3. Use "Next/Previous" to navigate steps
4. Use "All Light" function to test all wells

### CSV File Formats
Sample files in the `Input_CSV/` folder:
- `Step_Source_Destination.csv` - Complete step format with source and destination
- `Step_Source.csv` - Source-only format for detection/sampling operations

### Supported CSV Formats
1. **Complete Step Format** (Recommended):
   ```csv
   Step,Source,Destination
   1,A1,B1
   2,A2,B2
   ```

2. **Source-Only Step Format**:
   ```csv
   Step,Source
   1,A1
   2,B1
   ```

## 🔍 Troubleshooting

### Application Won't Start
```bash
# Check Python dependencies
python3 -c "import PyQt5; print('PyQt5 OK')"
python3 -c "import pandas; print('pandas OK')"
python3 -c "import serial; print('serial OK')"
```

### Touch Not Responding
```bash
# Check touch devices
xinput list
# Recalibrate
xinput_calibrator
```

### Serial Port Issues
```bash
# Check serial ports
ls /dev/ttyUSB*
ls /dev/ttyACM*
# Set permissions
sudo usermod -a -G dialout $USER
```

### Check Service Status
```bash
sudo systemctl status microplate
sudo journalctl -u microplate -f
```

## 🛡️ Production Environment Setup

### 1. Disable Development Mode
Edit `main.py`:
```python
DEV_MODE = False  # Enable actual hardware communication
```

### 2. Configure Serial Ports
```python
SERIAL_PORT_SOURCE = '/dev/ttyUSB0'  # Adjust according to actual devices
SERIAL_PORT_DEST = '/dev/ttyUSB1'
```

### 3. Configure Watchdog (Optional)
```bash
sudo apt install watchdog
sudo systemctl enable watchdog
```

## 📞 Support

If you encounter problems, please check:
1. Hardware connections are correct
2. System logs: `sudo journalctl -xe`
3. Application logs: `sudo journalctl -u microplate -f`

For more information, please refer to the main README.md file.

## 📚 Additional Resources

- **Main Documentation**: See the project's main README.md
- **CSV Format Guide**: Check Input_CSV/README.md for detailed CSV format specifications
- **GitHub Repository**: [https://github.com/alextu870719/rspi5_microplate](https://github.com/alextu870719/rspi5_microplate)
