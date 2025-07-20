# Microplate Light Guide for Raspberry Pi 5

A PyQt5-based application for controlling microplate lighting on laboratory equipment using a 7-inch touchscreen display.

## Features

- Support for multiple microplate formats: 384, 96, 48, and 24-well plates
- Full-screen interface optimized for 7-inch touchscreens
- Pure black background for minimal light interference
- CSV-based step protocols for automated procedures
- Serial communication for hardware control
- Precise 1:1 physical dimension mapping
- Touch-friendly interface design

## Hardware Requirements

- Raspberry Pi 5 (recommended) or Pi 4
- 7-inch touchscreen display (152.4mm × 91.4mm active area)
- USB serial adapters for hardware communication
- Compatible microplate hardware

## Software Requirements

- Python 3.7+
- PyQt5
- pandas
- pyserial

## Installation

### On Raspberry Pi OS

1. Update your system:
```bash
sudo apt update && sudo apt upgrade -y
```

2. Install Python dependencies:
```bash
sudo apt install python3-pip python3-pyqt5 python3-pandas python3-serial
```

3. Clone this repository:
```bash
git clone <your-repository-url>
cd rspi5_microplate
```

4. Run the application:
```bash
python3 main.py
```

### Development Mode

The application includes a development mode that disables serial communication for testing:
- Set `DEV_MODE = True` in `main.py` to disable serial communication
- Set `DEV_MODE = False` for production use with hardware

## Usage

1. **Select Plate Type**: Use the plate type button to cycle through 384→96→48→24 well formats
2. **Load Protocol**: Click "Select File" to load a CSV protocol file
3. **Execute Steps**: Use Next/Previous buttons to navigate through protocol steps
4. **Reset**: Click "Reset" to return to the beginning of the protocol

## CSV Protocol Format

Create CSV files with the following structure:
- Column headers: Well positions (A1, A2, B1, etc.)
- Each row represents a protocol step
- Values: 1 for light on, 0 for light off

Example:
```csv
A1,A2,B1,B2,C1,C2
1,0,1,0,1,0
0,1,0,1,0,1
1,1,0,0,1,1
```

## Microplate Specifications

### Physical Dimensions
- **384-well**: 127.76mm × 85.48mm, A1 at (12.13, 8.99)mm, 4.5mm spacing
- **96-well**: 127.76mm × 85.48mm, A1 at (14.38, 11.24)mm, 9mm spacing  
- **48-well**: 127.76mm × 85.48mm, A1 at (17.26, 13.62)mm, 13.5mm spacing
- **24-well**: 127.76mm × 85.48mm, A1 at (21.02, 17.25)mm, 19.3mm spacing

### Screen Mapping
- Screen size: 152.4mm × 91.4mm
- Plate area: 127.76mm × 85.48mm
- Centering offset: X=12.32mm, Y=2.96mm

## Serial Communication

The application communicates via two USB serial ports:
- **Source Port** (`/dev/ttyUSB0`): Commands to hardware
- **Destination Port** (`/dev/ttyUSB1`): Responses from hardware
- **Baud Rate**: 9600

## Raspberry Pi Setup

### Enable Touch Screen
Add to `/boot/config.txt`:
```
dtoverlay=rpi-ft5406
dtoverlay=rpi-backlight
```

### Auto-start Application
Create `/etc/systemd/system/microplate.service`:
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

Enable the service:
```bash
sudo systemctl enable microplate.service
sudo systemctl start microplate.service
```

## Development

### Project Structure
```
rspi5_microplate/
├── main.py          # Main application file
├── test.csv         # Example protocol file
├── README.md        # This documentation
└── .gitignore       # Git ignore file
```

### Key Components
- `MicroplateApp`: Main application class
- `PlateWidget`: Custom widget for drawing microplate layouts
- `cycle_plate_type()`: Handles plate format switching
- `update_plate_parameters()`: Updates physical dimensions
- `draw_plate()`: Renders well positions with precise mapping

## Troubleshooting

### Serial Port Issues
- Check USB connections: `ls /dev/ttyUSB*`
- Verify permissions: `sudo usermod -a -G dialout $USER`
- Test communication: `python3 -c "import serial; print('Serial OK')"`

### Display Issues
- Ensure proper screen resolution in `/boot/config.txt`
- Check touch calibration: `xinput_calibrator`
- Verify Qt display: `export QT_QPA_PLATFORM=linuxfb`

### Dependencies
- PyQt5 installation: `pip3 install PyQt5`
- pandas: `pip3 install pandas`
- pyserial: `pip3 install pyserial`

## License

This project is open source and available under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test on Raspberry Pi hardware
5. Submit a pull request

## Version History

- v1.0: Initial release with 4-plate support and full-screen interface
- Added precise physical dimension mapping for laboratory accuracy
- Implemented pure black theme for minimal light interference
