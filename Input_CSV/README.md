# CSV Input Files

This folder contains sample CSV files for the microplate application.

## File Descriptions

### 📄 **Step_Source_Destination.csv**
- **Description**: Complete step format example with source and destination
- **Format**: Step, Source, Destination three-column format
- **Purpose**: Demonstrates standard three-column CSV format with explicit source and destination well definitions
- **Sample Content**:
  ```csv
  Step,Source,Destination
  1,A1,B1
  1,A2,B2
  2,A3,B3
  2,A4,B4
  3,C1,D1
  3,C2,D2
  3,C3,D3
  ```

### 📄 **Step_Source.csv**  
- **Description**: Source-only step format
- **Format**: Step, Source format (no destination wells)
- **Purpose**: For experiments that only require source well identification (e.g., detection, sampling operations)
- **Sample Content**:
  ```csv
  Step,Source
  1,A1
  1,A2
  1,A3
  2,B1
  2,B2
  3,C1
  3,C2
  3,C3
  3,C4
  ```

## CSV File Format Specifications

### Step Format - Complete Version (Recommended)
Contains complete operation definition with source and destination wells:
```csv
Step,Source,Destination
1,A01,B02
1,C03,D04
2,E05,F06
```

### Step Format - Source-Only Version
Only defines source wells, suitable for detection or sampling operations:
```csv
Step,Source
1,A01
1,C03
2,E05
```

## Usage Instructions

1. Click the "Load CSV" button in the application
2. Select any CSV file from this folder
3. The application will automatically detect the file format and load it
4. Use Next/Previous buttons to navigate through steps

## Important Notes

- Well formats support both A1 and A01 notation
- Multiple wells can be separated with semicolons (;)
- The application will automatically standardize well format to A01 form
