#!/bin/bash

# =============================================================================
# Microplate Light Guide - Raspberry Pi 5 自動安裝腳本
# =============================================================================
# 
# 這個腳本會自動：
# 1. 更新系統
# 2. 安裝必要的系統套件
# 3. 從GitHub下載專案
# 4. 安裝Python依賴
# 5. 設定開機自動啟動
# 6. 設定觸控螢幕
#
# 使用方式：
# curl -sSL https://raw.githubusercontent.com/alextu870719/rspi5_microplate/main/install.sh | bash
#
# =============================================================================

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 專案設定
PROJECT_NAME="rspi5_microplate"
GITHUB_REPO="https://github.com/alextu870719/rspi5_microplate.git"
INSTALL_DIR="/home/$USER/$PROJECT_NAME"
SERVICE_NAME="microplate"

# 印出彩色訊息的函數
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${GREEN}"
    echo "=================================================================="
    echo "  Microplate Light Guide - Raspberry Pi 5 自動安裝程式"
    echo "=================================================================="
    echo -e "${NC}"
}

# 檢查是否為root用戶
check_user() {
    if [[ $EUID -eq 0 ]]; then
        print_error "請不要使用root權限運行此腳本"
        print_status "請使用一般使用者帳戶運行: bash install.sh"
        exit 1
    fi
}

# 檢查網路連線
check_internet() {
    print_status "檢查網路連線..."
    if ping -c 1 google.com &> /dev/null; then
        print_success "網路連線正常"
    else
        print_error "無法連接到網路，請檢查網路連線"
        exit 1
    fi
}

# 更新系統
update_system() {
    print_status "更新系統套件..."
    sudo apt update -y
    sudo apt upgrade -y
    print_success "系統更新完成"
}

# 安裝基本套件
install_system_packages() {
    print_status "安裝系統必要套件..."
    
    # 基本開發工具和Python相關
    sudo apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        git \
        curl \
        wget \
        build-essential
    
    # PyQt5相關套件
    sudo apt install -y \
        python3-pyqt5 \
        python3-pyqt5.qtcore \
        python3-pyqt5.qtgui \
        python3-pyqt5.qtwidgets \
        python3-pyqt5.qtsvg
    
    # 其他Python套件
    sudo apt install -y \
        python3-pandas \
        python3-serial \
        python3-numpy
    
    # 觸控螢幕相關
    sudo apt install -y \
        xserver-xorg-input-evdev \
        xinput-calibrator \
        x11-apps
        
    print_success "系統套件安裝完成"
}

# 下載專案
download_project() {
    print_status "從GitHub下載專案..."
    
    # 如果目錄已存在，先備份
    if [ -d "$INSTALL_DIR" ]; then
        print_warning "發現現有安裝，創建備份..."
        sudo mv "$INSTALL_DIR" "${INSTALL_DIR}.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    # Clone專案
    git clone "$GITHUB_REPO" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    print_success "專案下載完成"
}

# 安裝Python依賴
install_python_dependencies() {
    print_status "安裝Python依賴套件..."
    
    cd "$INSTALL_DIR"
    
    # 使用pip安裝（如果系統套件不夠新）
    pip3 install --user -r requirements.txt
    
    print_success "Python依賴安裝完成"
}

# 設定觸控螢幕
setup_touchscreen() {
    print_status "設定觸控螢幕支援..."
    
    # 檢查是否為7吋螢幕
    print_status "設定DSI觸控螢幕..."
    
    # 備份config.txt
    sudo cp /boot/config.txt /boot/config.txt.backup
    
    # 添加觸控螢幕設定
    if ! grep -q "dtoverlay=rpi-ft5406" /boot/config.txt; then
        echo "# Microplate 7-inch touchscreen" | sudo tee -a /boot/config.txt
        echo "dtoverlay=rpi-ft5406" | sudo tee -a /boot/config.txt
        echo "dtoverlay=rpi-backlight" | sudo tee -a /boot/config.txt
    fi
    
    print_success "觸控螢幕設定完成"
}

# 設定自動啟動服務
setup_autostart() {
    print_status "設定開機自動啟動..."
    
    # 創建systemd服務檔
    sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null <<EOF
[Unit]
Description=Microplate Light Guide Application
After=graphical-session.target
Wants=graphical-session.target

[Service]
Type=simple
User=$USER
Group=$USER
Environment=DISPLAY=:0
Environment=QT_QPA_PLATFORM=xcb
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/python3 $INSTALL_DIR/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=graphical-session.target
EOF

    # 重新載入systemd
    sudo systemctl daemon-reload
    
    # 啟用服務
    sudo systemctl enable ${SERVICE_NAME}.service
    
    print_success "自動啟動設定完成"
}

# 創建桌面捷徑
create_desktop_shortcut() {
    print_status "創建桌面捷徑..."
    
    # 確保Desktop目錄存在
    mkdir -p ~/Desktop
    
    # 創建桌面捷徑
    tee ~/Desktop/Microplate.desktop > /dev/null <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Microplate Light Guide
Comment=Laboratory microplate light guide application
Icon=applications-science
Exec=python3 $INSTALL_DIR/main.py
Terminal=false
Categories=Science;Education;
StartupNotify=true
EOF

    # 設定執行權限
    chmod +x ~/Desktop/Microplate.desktop
    
    print_success "桌面捷徑創建完成"
}

# 設定快速啟動腳本
create_run_script() {
    print_status "創建快速啟動腳本..."
    
    tee "$INSTALL_DIR/run_microplate.sh" > /dev/null <<'EOF'
#!/bin/bash

# Microplate Light Guide 快速啟動腳本

cd "$(dirname "$0")"

echo "啟動 Microplate Light Guide..."
echo "按 Ctrl+C 結束程式"
echo ""

# 檢查Python和依賴
if ! python3 -c "import PyQt5" 2>/dev/null; then
    echo "錯誤: PyQt5未安裝，請運行安裝腳本"
    exit 1
fi

# 設定環境變數
export DISPLAY=:0
export QT_QPA_PLATFORM=xcb

# 啟動程式
python3 main.py
EOF

    chmod +x "$INSTALL_DIR/run_microplate.sh"
    
    print_success "快速啟動腳本創建完成"
}

# 測試安裝
test_installation() {
    print_status "測試安裝..."
    
    cd "$INSTALL_DIR"
    
    # 測試Python導入
    if python3 -c "import PyQt5.QtWidgets; import pandas; import serial; print('所有依賴套件正常')"; then
        print_success "依賴套件測試通過"
    else
        print_error "依賴套件測試失敗"
        return 1
    fi
    
    # 檢查主程式檔案
    if [ -f "main.py" ]; then
        print_success "主程式檔案存在"
    else
        print_error "主程式檔案不存在"
        return 1
    fi
    
    print_success "安裝測試完成"
}

# 顯示安裝完成資訊
show_completion_info() {
    print_success "安裝完成！"
    echo ""
    echo -e "${GREEN}=================================================================="
    echo "  安裝完成資訊"
    echo "==================================================================${NC}"
    echo ""
    echo "📁 安裝目錄: $INSTALL_DIR"
    echo "🖥️  桌面捷徑: ~/Desktop/Microplate.desktop"
    echo "🚀 快速啟動: $INSTALL_DIR/run_microplate.sh"
    echo "⚙️  系統服務: $SERVICE_NAME.service"
    echo ""
    echo -e "${YELLOW}下一步操作:${NC}"
    echo "1. 重新啟動系統以啟用所有設定"
    echo "2. 手動測試: cd $INSTALL_DIR && ./run_microplate.sh"
    echo "3. 檢查服務: sudo systemctl status $SERVICE_NAME"
    echo "4. 查看日誌: sudo journalctl -u $SERVICE_NAME -f"
    echo ""
    echo -e "${BLUE}使用說明:${NC}"
    echo "• 程式會在開機後自動啟動"
    echo "• CSV範例檔案在 Input_CSV/ 資料夾"
    echo "• 支援384/96/48/24孔板格式"
    echo "• 觸控操作已優化"
    echo ""
    echo -e "${RED}注意事項:${NC}"
    echo "• 請確保7吋觸控螢幕正確連接"
    echo "• 第一次啟動可能需要校準觸控"
    echo "• 生產環境請修改 DEV_MODE = False"
    echo ""
}

# 主要安裝流程
main() {
    print_header
    
    # 前置檢查
    check_user
    check_internet
    
    print_status "開始安裝程序..."
    
    # 執行安裝步驟
    update_system
    install_system_packages
    download_project
    install_python_dependencies
    setup_touchscreen
    setup_autostart
    create_desktop_shortcut
    create_run_script
    
    # 測試安裝
    if test_installation; then
        show_completion_info
        echo ""
        print_status "建議現在重新啟動系統: sudo reboot"
    else
        print_error "安裝過程中發生錯誤，請檢查上述訊息"
        exit 1
    fi
}

# 錯誤處理
trap 'print_error "安裝過程中發生錯誤，腳本已中止"; exit 1' ERR

# 執行主程式
main "$@"
