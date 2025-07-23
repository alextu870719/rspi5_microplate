import sys
import pandas as pd
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QLabel, QGridLayout, QHBoxLayout
)
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt
import serial

DEV_MODE = True  # 開發模式，不啟用 Serial
SERIAL_PORT_SOURCE = '/dev/ttyUSB0'
SERIAL_PORT_DEST = '/dev/ttyUSB1'
BAUDRATE = 9600

class MicroplateGUI(QWidget):
    def __init__(self):
        super().__init__()
        
        # Remove window title and make it frameless for fullscreen experience
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # Set black background for the entire application
        self.setStyleSheet("""
            QWidget {
                background-color: #000000;
                color: #FFFFFF;
            }
            QLabel {
                background-color: transparent;
                color: #FFFFFF;
            }
        """)
        
        self.csvData = pd.DataFrame()
        self.currentIndex = 0
        self.plate_type = "384"  # Default to 384-well mode
        self.all_light_mode = False  # All light mode status
        self.current_csv_file = ""  # Store current CSV file name
        
        # Physical dimension calculation (based on 7-inch screen 16:9 ratio)
        # Actual screen size: 154.9mm × 87.1mm
        # Microplate actual size: 127.76mm × 85.48mm (shared by 96 and 384)
        self.screen_width_mm = 154.9
        self.screen_height_mm = 87.1
        self.plate_width_mm = 127.76
        self.plate_height_mm = 85.48
        
        # Default screen resolution for calculations (will be updated dynamically)
        self.default_screen_width = 800
        self.default_screen_height = 480
        
        # 96-well specifications
        self.well_96_diameter_mm = 7.0
        self.well_96_spacing_mm = 9.0
        self.edge_96_to_first_col_mm = 14.4  # Left edge to column 1 center
        self.edge_96_to_first_row_mm = 11.2  # Top edge to row 1 center
        
        # 24-well specifications
        self.well_24_diameter_mm = 16.5
        self.well_24_spacing_mm = 19.0
        self.edge_24_to_first_col_mm = 16.4  # Left edge to column 1 center
        self.edge_24_to_first_row_mm = 14.2  # Top edge to row 1 center
        
        # 48-well specifications
        self.well_48_diameter_mm = 10.7
        self.well_48_spacing_mm = 13.0
        self.edge_48_to_first_col_mm = 18.4  # Left edge to column 1 center
        self.edge_48_to_first_row_mm = 10.2  # Top edge to row 1 center
        
        # 384-well specifications
        self.well_384_diameter_mm = 3.63
        self.well_384_spacing_mm = 4.50
        self.edge_384_to_first_col_mm = 12.12  # Left edge to column 1 center
        self.edge_384_to_first_row_mm = 8.99   # Top edge to row 1 center
        
        # Convert to pixels - will be updated dynamically based on current window size
        self.update_pixel_conversion()
        
        # Calculate actual plate size (127.76mm × 85.48mm)
        self.plate_outline_width_px = int(self.plate_width_mm * self.mm_to_pixel_x)
        self.plate_outline_height_px = int(self.plate_height_mm * self.mm_to_pixel_y)
        
        # Use precise plate outline size as container size to avoid over-scaling
        self.plate_width_px = self.plate_outline_width_px
        self.plate_height_px = self.plate_outline_height_px
        
        # Initialize with 384-well parameters
        self.update_plate_parameters()
        
        # Define plate type cycle order
        self.plate_types = ["384", "96", "48", "24"]
        self.current_plate_index = 0  # Start with 384-well

        # Serial Init
        if not DEV_MODE:
            self.ser_source = serial.Serial(SERIAL_PORT_SOURCE, BAUDRATE)
            self.ser_dest = serial.Serial(SERIAL_PORT_DEST, BAUDRATE)

        # GUI Layout
        main_layout = QHBoxLayout()  # Main horizontal layout
        
        # Left control panel (wider buttons for better touch operation)
        left_panel = QVBoxLayout()
        left_panel.setSpacing(8)  # Increase spacing for better touch targets
        
        self.label = QLabel("Please select cherrypick file")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setFixedWidth(100)  # Reduce width for narrower buttons
        left_panel.addWidget(self.label)
        
        # Add flexible space at top to push buttons down
        left_panel.addStretch()
        
        # Add plate selection button (single button that cycles through formats)
        self.btn_plate_type = QPushButton("384-Well")
        
        self.btn_select = QPushButton("Load CSV")
        self.btn_prev = QPushButton("Previous")
        self.btn_next = QPushButton("Next")
        self.btn_all_light = QPushButton("All Light OFF")
        
        # Set wide rectangular button style for better touch operation
        button_style = """
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 8px 10px;
                text-align: center;
                font-size: 11px;
                margin: 2px 2px;
                border-radius: 6px;
                font-weight: bold;
                min-height: 32px;
                max-height: 36px;
                min-width: 80px;
                max-width: 100px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """
        
        self.btn_plate_type.setStyleSheet(self.get_button_style(True))   # Plate type button
        self.btn_select.setStyleSheet(self.get_button_style(False))
        self.btn_prev.setStyleSheet(self.get_button_style(False))
        self.btn_next.setStyleSheet(self.get_button_style(False))
        self.btn_all_light.setStyleSheet(self.get_button_style(False))
        
        self.btn_plate_type.clicked.connect(self.cycle_plate_type)
        self.btn_select.clicked.connect(self.load_csv)
        self.btn_prev.clicked.connect(self.go_prev)
        self.btn_next.clicked.connect(self.go_next)
        self.btn_all_light.clicked.connect(self.toggle_all_light)
        
        left_panel.addWidget(self.btn_plate_type)
        left_panel.addWidget(self.btn_select)
        left_panel.addWidget(self.btn_prev)
        left_panel.addWidget(self.btn_next)
        left_panel.addWidget(self.btn_all_light)
        
        # Right microplate area
        right_panel = QVBoxLayout()
        
        # Create microplate container suitable for screen
        plate_container = QWidget()
        plate_container.setFixedSize(self.plate_width_px, self.plate_height_px)
        
        self.grid = QGridLayout(plate_container)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(0)  # Use precise positioning, not relying on automatic spacing
        right_panel.addWidget(plate_container, alignment=Qt.AlignCenter)
        
        # Add left and right panels to main layout (give more space to plate)
        main_layout.addLayout(left_panel)
        main_layout.addLayout(right_panel)
        main_layout.setStretchFactor(left_panel, 1)   # Left side takes less space
        main_layout.setStretchFactor(right_panel, 8)  # Right side takes most space
        
        self.setLayout(main_layout)
        self.well_buttons = {}
        
        # Initialize with empty 384-well plate
        self.draw_plate()

    def update_pixel_conversion(self):
        """Update pixel conversion ratios based on current window size"""
        # Always use the actual physical screen mapping for fullscreen
        self.mm_to_pixel_x = self.default_screen_width / self.screen_width_mm
        self.mm_to_pixel_y = self.default_screen_height / self.screen_height_mm

    def update_plate_parameters(self):
        """Update parameters based on current plate type"""
        if self.plate_type == "96":
            self.well_diameter_mm = self.well_96_diameter_mm
            self.well_spacing_mm = self.well_96_spacing_mm
            self.edge_to_first_col_mm = self.edge_96_to_first_col_mm
            self.edge_to_first_row_mm = self.edge_96_to_first_row_mm
            self.rows = 8
            self.cols = 12
        elif self.plate_type == "48":
            self.well_diameter_mm = self.well_48_diameter_mm
            self.well_spacing_mm = self.well_48_spacing_mm
            self.edge_to_first_col_mm = self.edge_48_to_first_col_mm
            self.edge_to_first_row_mm = self.edge_48_to_first_row_mm
            self.rows = 6
            self.cols = 8
        elif self.plate_type == "24":
            self.well_diameter_mm = self.well_24_diameter_mm
            self.well_spacing_mm = self.well_24_spacing_mm
            self.edge_to_first_col_mm = self.edge_24_to_first_col_mm
            self.edge_to_first_row_mm = self.edge_24_to_first_row_mm
            self.rows = 4
            self.cols = 6
        else:  # 384-well
            self.well_diameter_mm = self.well_384_diameter_mm
            self.well_spacing_mm = self.well_384_spacing_mm
            self.edge_to_first_col_mm = self.edge_384_to_first_col_mm
            self.edge_to_first_row_mm = self.edge_384_to_first_row_mm
            self.rows = 16
            self.cols = 24
            
        # Calculate pixel values
        self.well_diameter_px = int(self.well_diameter_mm * self.mm_to_pixel_x)
        self.well_spacing_x_px = int(self.well_spacing_mm * self.mm_to_pixel_x)
        self.well_spacing_y_px = int(self.well_spacing_mm * self.mm_to_pixel_y)
        self.edge_to_first_col_px = int(self.edge_to_first_col_mm * self.mm_to_pixel_x)
        self.edge_to_first_row_px = int(self.edge_to_first_row_mm * self.mm_to_pixel_y)

    def cycle_plate_type(self):
        """Cycle through different plate types"""
        self.current_plate_index = (self.current_plate_index + 1) % len(self.plate_types)
        new_plate_type = self.plate_types[self.current_plate_index]
        self.switch_plate_type(new_plate_type)

    def switch_plate_type(self, plate_type):
        """Switch plate type"""
        self.plate_type = plate_type
        self.update_plate_parameters()
        
        # Update button text to show current plate type
        self.btn_plate_type.setText(f"{plate_type}-Well")
        
        # Update current plate index to match the plate type
        if plate_type in self.plate_types:
            self.current_plate_index = self.plate_types.index(plate_type)
            
        # Redraw plate (regardless of whether CSV is loaded)
        self.draw_plate()
        
        # If previously in all light mode, maintain all light state
        if self.all_light_mode:
            self.light_all_wells()

    def get_button_style(self, is_active):
        """Get button style, distinguishing selected and unselected states"""
        if is_active:
            return """
                QPushButton {
                    background-color: #2196F3;
                    border: none;
                    color: white;
                    padding: 8px 12px;
                    text-align: center;
                    font-size: 11px;
                    margin: 2px 2px;
                    border-radius: 6px;
                    font-weight: bold;
                    min-height: 32px;
                    max-height: 36px;
                    min-width: 100px;
                    max-width: 120px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #0D47A1;
                }
            """
        else:
            return """
                QPushButton {
                    background-color: #4CAF50;
                    border: none;
                    color: white;
                    padding: 8px 12px;
                    text-align: center;
                    font-size: 11px;
                    margin: 2px 2px;
                    border-radius: 6px;
                    font-weight: bold;
                    min-height: 32px;
                    max-height: 36px;
                    min-width: 100px;
                    max-width: 120px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QPushButton:pressed {
                    background-color: #3d8b40;
                }
            """

    def keyPressEvent(self, event):
        """Handle key press events"""
        # Pass through to parent for standard key handling
        super().keyPressEvent(event)

    def load_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "CSV Files (*.csv)")
        if file_path:
            # Store the CSV file name (without path)
            self.current_csv_file = os.path.basename(file_path)
            
            raw_data = pd.read_csv(file_path)
            
            # Check CSV format and convert
            if 'Step' in raw_data.columns:
                # New format: group by Step
                self.csvData = self.convert_step_format(raw_data)
            else:
                # Old format: use directly
                self.csvData = raw_data
                
            self.currentIndex = 0
            # If in all light mode, turn off all light mode
            if self.all_light_mode:
                self.all_light_mode = False
                self.btn_all_light.setText("All Light OFF")
                self.btn_all_light.setStyleSheet(self.get_all_light_button_style(False))
            self.draw_plate()

    def convert_step_format(self, raw_data):
        """Convert Step format CSV to internal format"""
        converted_data = []
        
        # Group by Step
        for step in sorted(raw_data['Step'].unique()):
            step_data = raw_data[raw_data['Step'] == step]
            
            # Collect all Source and Destination for this step
            sources = []
            destinations = []
            
            for _, row in step_data.iterrows():
                # Standardize well format (ensure two digits)
                source = self.standardize_well_format(str(row['Source']))
                sources.append(source)
                
                if 'Destination' in raw_data.columns and pd.notna(row['Destination']):
                    dest = self.standardize_well_format(str(row['Destination']))
                    destinations.append(dest)
                else:
                    destinations.append(source)  # If no destination, use source
            
            # Connect multiple wells with semicolons
            source_str = ';'.join(sources)
            dest_str = ';'.join(destinations)
            
            converted_data.append({
                'Source_well': source_str,
                'Destination_well': dest_str
            })
        
        return pd.DataFrame(converted_data)

    def standardize_well_format(self, well):
        """Standardize well format to A01 form"""
        well = well.strip()
        if len(well) >= 2:
            row = well[0].upper()
            col = well[1:]
            try:
                col_num = int(col)
                return f"{row}{col_num:02d}"
            except ValueError:
                return well
        return well

    def draw_plate(self):
        # Clear existing widgets
        for i in reversed(range(self.grid.count())):
            widget = self.grid.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        self.well_buttons.clear()
        
        # Create an absolutely positioned container
        container = self.grid.parent()
        
        # Clear all existing child elements in container (including plate outline, labels, wells)
        for child in container.findChildren(QLabel):
            child.deleteLater()
        for child in container.findChildren(QPushButton):
            child.deleteLater()
        
        # Calculate plate outline position (centered display)
        plate_x = (self.plate_width_px - self.plate_outline_width_px) // 2
        plate_y = (self.plate_height_px - self.plate_outline_height_px) // 2
        
        # Create plate outline border
        plate_outline = QLabel("")
        plate_outline.setFixedSize(self.plate_outline_width_px, self.plate_outline_height_px)
        plate_outline.setStyleSheet("""
            QLabel {
                border: 3px solid #FFFFFF;
                border-radius: 8px;
                background-color: #000000;
            }
        """)
        plate_outline.setParent(container)
        plate_outline.move(plate_x, plate_y)
        plate_outline.show()
        
        # Add plate size label
        size_label = QLabel(f"127.76mm × 85.48mm")
        size_label.setAlignment(Qt.AlignCenter)
        size_label.setFont(QFont("Arial", 8, QFont.Bold))
        size_label.setStyleSheet("color: #FFFFFF; background: transparent;")
        size_label.setFixedSize(120, 15)
        size_label.setParent(container)
        size_label.move(plate_x + (self.plate_outline_width_px - 120) // 2, plate_y + self.plate_outline_height_px + 5)
        size_label.show()
        
        # Calculate precise position of first well (A1) (based on edge distance)
        # A1 position = plate start position + edge to first well center distance - well radius
        first_well_x = plate_x + self.edge_to_first_col_px - (self.well_diameter_px // 2)
        first_well_y = plate_y + self.edge_to_first_row_px - (self.well_diameter_px // 2)
        
        # Add row labels (A-H or A-P) - based on precise first well position
        for r in range(self.rows):
            row_label = QLabel(chr(65 + r))
            row_label.setAlignment(Qt.AlignCenter)
            if self.plate_type == "384":
                font_size = 6
            elif self.plate_type == "48":
                font_size = 10
            elif self.plate_type == "24":
                font_size = 12
            else:  # 96-well
                font_size = 8
            row_label.setFont(QFont("Arial", font_size, QFont.Bold))
            row_label.setFixedSize(15, self.well_diameter_px)
            row_label.setStyleSheet("color: #FFFFFF; background: transparent;")
            row_label.setParent(container)
            y_pos = first_well_y + r * self.well_spacing_y_px
            row_label.move(first_well_x - 18, y_pos)
            row_label.show()
        
        # Add column labels (1-12 or 1-24) - based on precise first well position
        for c in range(self.cols):
            col_label = QLabel(f"{c+1}")
            col_label.setAlignment(Qt.AlignCenter)
            if self.plate_type == "384":
                font_size = 6
            elif self.plate_type == "48":
                font_size = 10
            elif self.plate_type == "24":
                font_size = 12
            else:  # 96-well
                font_size = 8
            col_label.setFont(QFont("Arial", font_size, QFont.Bold))
            col_label.setFixedSize(self.well_diameter_px, 12)
            col_label.setStyleSheet("color: #FFFFFF; background: transparent;")
            col_label.setParent(container)
            x_pos = first_well_x + c * self.well_spacing_x_px
            col_label.move(x_pos, first_well_y - 15)
            col_label.show()
        
        # Create well buttons (based on precise edge distance calculation)
        for r in range(self.rows):  # Rows A–H (96) 或 A–P (384)
            for c in range(self.cols):  # Columns 1–12 (96) 或 1–24 (384)
                well = f"{chr(65 + r)}{c+1:02d}"
                btn = QPushButton("")
                btn.setFixedSize(self.well_diameter_px, self.well_diameter_px)
                btn.setToolTip(well)
                btn.setParent(container)
                
                # Set circular style
                border_radius = self.well_diameter_px // 2
                btn.setStyleSheet(f"""
                    QPushButton {{
                        border-radius: {border_radius}px;
                        background-color: #000000;
                        border: 1px solid #808080;
                        color: transparent;
                    }}
                    QPushButton:hover {{
                        background-color: #202020;
                        border: 2px solid #A0A0A0;
                    }}
                """)
                
                # Calculate precise position (based on edge distance and well spacing)
                x_pos = first_well_x + c * self.well_spacing_x_px
                y_pos = first_well_y + r * self.well_spacing_y_px
                
                btn.move(x_pos, y_pos)
                btn.show()
                self.well_buttons[well] = btn
        
        self.update_highlight()

    def update_highlight(self):
        # Calculate dynamic border radius
        border_radius = self.well_diameter_px // 2
        
        # Reset all button styles to default circular style
        default_style = f"""
            QPushButton {{
                border-radius: {border_radius}px;
                background-color: #000000;
                border: 1px solid #808080;
                color: transparent;
            }}
            QPushButton:hover {{
                background-color: #202020;
                border: 2px solid #A0A0A0;
            }}
        """
        for btn in self.well_buttons.values():
            btn.setStyleSheet(default_style)
            
        if not self.csvData.empty:
            src_wells_str = str(self.csvData.at[self.currentIndex, 'Source_well'])
            
            # Check if Destination_well column exists
            if 'Destination_well' in self.csvData.columns:
                dest_wells_str = str(self.csvData.at[self.currentIndex, 'Destination_well'])
            else:
                dest_wells_str = src_wells_str  # If no destination, use source
            
            # Split multiple wells (support semicolon separation)
            src_wells = [w.strip() for w in src_wells_str.split(';') if w.strip()]
            dest_wells = [w.strip() for w in dest_wells_str.split(';') if w.strip()]
            
            # Source wells style (red, bright and prominent)
            src_style = f"""
                QPushButton {{
                    border-radius: {border_radius}px;
                    background-color: #FF0000;
                    border: 3px solid #AA0000;
                    color: transparent;
                }}
                QPushButton:hover {{
                    background-color: #FF3333;
                    border: 3px solid #DD0000;
                }}
            """
            
            # Destination wells style (green, bright and prominent)
            dest_style = f"""
                QPushButton {{
                    border-radius: {border_radius}px;
                    background-color: #00FF00;
                    border: 3px solid #00AA00;
                    color: transparent;
                }}
                QPushButton:hover {{
                    background-color: #33FF33;
                    border: 3px solid #00DD00;
                }}
            """
            
            # If source and destination are the same well, use red style (same as source)
            mixed_style = f"""
                QPushButton {{
                    border-radius: {border_radius}px;
                    background-color: #FF0000;
                    border: 3px solid #AA0000;
                    color: transparent;
                }}
                QPushButton:hover {{
                    background-color: #FF3333;
                    border: 3px solid #DD0000;
                }}
            """
            
            # First mark all destination wells
            dest_wells_set = set(dest_wells)
            for dest in dest_wells:
                if dest in self.well_buttons:
                    self.well_buttons[dest].setStyleSheet(dest_style)
                    self.send_command(dest, "destination")
            
            # Then mark source wells, if overlapping with destination use mixed style
            for src in src_wells:
                if src in self.well_buttons:
                    if src in dest_wells_set:
                        # Source and destination are the same well, use red style
                        self.well_buttons[src].setStyleSheet(mixed_style)
                    else:
                        # Pure source well - check if this is source-only mode
                        if 'Destination_well' not in self.csvData.columns or set(src_wells) == set(dest_wells):
                            # Source only mode, use red (same as source style)
                            self.well_buttons[src].setStyleSheet(src_style)
                        else:
                            # Normal source with different destination, use red
                            self.well_buttons[src].setStyleSheet(src_style)
                    self.send_command(src, "source")
            
            # Update label display - show CSV file name and step information
            if self.current_csv_file:
                self.label.setText(f"File: {self.current_csv_file}\nStep {self.currentIndex + 1}/{len(self.csvData)}")
            else:
                self.label.setText(f"Step {self.currentIndex + 1}/{len(self.csvData)}")

    def toggle_all_light(self):
        """Toggle all light mode"""
        self.all_light_mode = not self.all_light_mode
        
        if self.all_light_mode:
            # Turn on all light mode
            self.light_all_wells()
            self.btn_all_light.setText("All Light ON")
            self.btn_all_light.setStyleSheet(self.get_all_light_button_style(True))
        else:
            # Turn off all light mode
            self.turn_off_all_wells()
            self.btn_all_light.setText("All Light OFF")
            self.btn_all_light.setStyleSheet(self.get_all_light_button_style(False))

    def get_all_light_button_style(self, is_on):
        """Get all light button style"""
        if is_on:
            return """
                QPushButton {
                    background-color: #FF9800;
                    border: none;
                    color: white;
                    padding: 8px 10px;
                    text-align: center;
                    font-size: 11px;
                    margin: 2px 2px;
                    border-radius: 6px;
                    font-weight: bold;
                    min-height: 32px;
                    max-height: 36px;
                    min-width: 80px;
                    max-width: 100px;
                }
                QPushButton:hover {
                    background-color: #F57C00;
                }
                QPushButton:pressed {
                    background-color: #E65100;
                }
            """
        else:
            return self.get_button_style(False)

    def light_all_wells(self):
        """Light up all wells"""
        # Calculate dynamic border radius
        border_radius = self.well_diameter_px // 2
        
        # All light style (red, bright and prominent)
        all_light_style = f"""
            QPushButton {{
                border-radius: {border_radius}px;
                background-color: #FF0000;
                border: 3px solid #CC0000;
                color: transparent;
            }}
            QPushButton:hover {{
                background-color: #FF3333;
                border: 3px solid #AA0000;
            }}
        """
        
        # Apply all light style to all well buttons
        for btn in self.well_buttons.values():
            btn.setStyleSheet(all_light_style)
            
        # Update label display
        total_wells = self.rows * self.cols
        if self.current_csv_file:
            self.label.setText(f"File: {self.current_csv_file}\nAll Light Mode\nTotal {total_wells} wells")
        else:
            self.label.setText(f"All Light Mode\nTotal {total_wells} wells")
        
        # Send all light command (will display in terminal in dev mode)
        if not DEV_MODE:
            # Here can send special all light command to hardware
            for r in range(self.rows):
                for c in range(self.cols):
                    well = f"{chr(65 + r)}{c+1:02d}"
                    self.send_command(well, "all_light")
        else:
            print(f"[DEV] All light mode: Light up all {total_wells} wells ({self.plate_type}-well)")

    def turn_off_all_wells(self):
        """Turn off all wells"""
        # Return to normal state
        if not self.csvData.empty:
            # If CSV is loaded, return to current step highlight state
            self.update_highlight()
        else:
            # If no CSV loaded, return to default style
            border_radius = self.well_diameter_px // 2
            default_style = f"""
                QPushButton {{
                    border-radius: {border_radius}px;
                    background-color: #000000;
                    border: 1px solid #808080;
                    color: transparent;
                }}
                QPushButton:hover {{
                    background-color: #202020;
                    border: 2px solid #A0A0A0;
                }}
            """
            for btn in self.well_buttons.values():
                btn.setStyleSheet(default_style)
            
            # Restore label display
            if self.current_csv_file:
                self.label.setText(f"File: {self.current_csv_file}\nPlease select cherrypick file")
            else:
                self.label.setText("Please select cherrypick file")
        
        # Send turn off command (will display in terminal in dev mode)
        if not DEV_MODE:
            # Here can send turn off command to hardware
            for r in range(self.rows):
                for c in range(self.cols):
                    well = f"{chr(65 + r)}{c+1:02d}"
                    self.send_command(well, "turn_off")
        else:
            print(f"[DEV] Turn off all light mode ({self.plate_type}-well)")

    def send_command(self, well, panel_type):
        row = well[0]
        col = well[1:].zfill(2)
        if panel_type == "all_light":
            command = f"all_light <{row},{col},S,>"
        elif panel_type == "turn_off":
            command = f"turn_off <{row},{col},S,>"
        else:
            command = f"{panel_type} <{row},{col},S,>"
            
        if not DEV_MODE:
            port = self.ser_source if panel_type == "source" else self.ser_dest
            port.write(bytes(command, 'us-ascii'))
        else:
            print(f"[DEV] 送出指令：{command}")

    def go_next(self):
        if not self.csvData.empty and self.currentIndex < len(self.csvData) - 1:
            self.currentIndex += 1
            self.update_highlight()

    def go_prev(self):
        if not self.csvData.empty and self.currentIndex > 0:
            self.currentIndex -= 1
            self.update_highlight()

    def closeEvent(self, event):
        if not DEV_MODE:
            self.ser_source.close()
            self.ser_dest.close()
        print("Close program and serial connection!")
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MicroplateGUI()
    window.showFullScreen()  # Use Qt5's built-in fullscreen method
    sys.exit(app.exec_())
