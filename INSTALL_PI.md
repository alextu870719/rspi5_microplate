# Raspberry Pi 5 安裝指南

本指南將協助你在Raspberry Pi 5上安裝並運行Microplate Light Guide應用程式。

## 🚀 一鍵自動安裝

### 方法1: 完整自動安裝（推薦）
```bash
curl -sSL https://raw.githubusercontent.com/alextu870719/rspi5_microplate/main/install.sh | bash
```

這個腳本會自動：
- 更新系統
- 安裝所有必要套件
- 下載專案
- 設定觸控螢幕
- 設定開機自動啟動
- 創建桌面捷徑

### 方法2: 快速安裝（適合已有基本環境）
```bash
curl -sSL https://raw.githubusercontent.com/alextu870719/rspi5_microplate/main/quick_install.sh | bash
```

## 📋 系統需求

### 硬體需求
- Raspberry Pi 5 (推薦) 或 Pi 4
- 7吋官方觸控螢幕 (800×480)
- MicroSD卡 (至少16GB，推薦32GB)
- USB序列埠轉換器（用於硬體通訊）

### 軟體需求
- Raspberry Pi OS (Bullseye或更新版本)
- Python 3.7+
- X11桌面環境

## 🛠️ 手動安裝步驟

如果自動安裝失敗，可以手動執行以下步驟：

### 1. 更新系統
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. 安裝Python依賴
```bash
sudo apt install -y python3-pyqt5 python3-pandas python3-serial python3-pip git
```

### 3. 下載專案
```bash
cd ~
git clone https://github.com/alextu870719/rspi5_microplate.git
cd rspi5_microplate
```

### 4. 安裝額外依賴
```bash
pip3 install --user -r requirements.txt
```

### 5. 測試運行
```bash
python3 main.py
```

## ⚙️ 觸控螢幕設定

### 啟用7吋觸控螢幕
編輯 `/boot/config.txt`:
```bash
sudo nano /boot/config.txt
```

添加以下行：
```
# 7-inch touchscreen support
dtoverlay=rpi-ft5406
dtoverlay=rpi-backlight
```

### 校準觸控（如果需要）
```bash
xinput_calibrator
```

## 🔧 開機自動啟動

### 使用systemd服務（推薦）
創建服務檔案：
```bash
sudo nano /etc/systemd/system/microplate.service
```

內容：
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

啟用服務：
```bash
sudo systemctl enable microplate.service
sudo systemctl start microplate.service
```

### 使用autostart（替代方法）
```bash
mkdir -p ~/.config/autostart
nano ~/.config/autostart/microplate.desktop
```

內容：
```ini
[Desktop Entry]
Type=Application
Name=Microplate Light Guide
Exec=python3 /home/pi/rspi5_microplate/main.py
Hidden=false
X-GNOME-Autostart-enabled=true
```

## 📁 專案結構

```
rspi5_microplate/
├── main.py                    # 主程式
├── Input_CSV/                 # CSV範例檔案
│   ├── test.csv
│   ├── 384DNA.csv
│   └── ...
├── install.sh                 # 完整安裝腳本
├── quick_install.sh           # 快速安裝腳本
├── run_microplate.sh          # 快速啟動腳本
└── requirements.txt           # Python依賴
```

## 🎯 使用方式

### 基本操作
1. 點擊「Load CSV」載入協議檔案
2. 使用孔板類型按鈕切換格式（384→96→48→24）
3. 使用「Next/Previous」導航步驟
4. 使用「All Light」功能測試所有孔位

### CSV檔案格式
範例檔案在 `Input_CSV/` 資料夾中：
- `test.csv` - 基本測試
- `384DNA.csv` - 384孔板實驗
- `multi_wells.csv` - 多孔位操作

## 🔍 故障排除

### 程式無法啟動
```bash
# 檢查Python依賴
python3 -c "import PyQt5; print('PyQt5 OK')"
python3 -c "import pandas; print('pandas OK')"
python3 -c "import serial; print('serial OK')"
```

### 觸控不響應
```bash
# 檢查觸控設備
xinput list
# 重新校準
xinput_calibrator
```

### 串列埠問題
```bash
# 檢查串列埠
ls /dev/ttyUSB*
ls /dev/ttyACM*
# 設定權限
sudo usermod -a -G dialout $USER
```

### 檢查服務狀態
```bash
sudo systemctl status microplate
sudo journalctl -u microplate -f
```

## 🛡️ 生產環境設定

### 1. 關閉開發模式
編輯 `main.py`：
```python
DEV_MODE = False  # 啟用實際硬體通訊
```

### 2. 設定串列埠
```python
SERIAL_PORT_SOURCE = '/dev/ttyUSB0'  # 根據實際設備調整
SERIAL_PORT_DEST = '/dev/ttyUSB1'
```

### 3. 設定看門狗（可選）
```bash
sudo apt install watchdog
sudo systemctl enable watchdog
```

## 📞 支援

如果遇到問題，請檢查：
1. 硬體連接是否正確
2. 系統日誌：`sudo journalctl -xe`
3. 程式日誌：`sudo journalctl -u microplate -f`

更多資訊請參考主要README.md檔案。
