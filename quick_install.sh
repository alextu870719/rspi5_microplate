#!/bin/bash

# 快速安裝腳本 - 用於已有基本環境的Pi
# 使用方式: curl -sSL https://raw.githubusercontent.com/alextu870719/rspi5_microplate/main/quick_install.sh | bash

echo "🚀 Microplate Light Guide 快速安裝"
echo "=================================="

# 下載專案
echo "📥 下載專案..."
cd ~
if [ -d "rspi5_microplate" ]; then
    echo "⚠️  發現現有目錄，創建備份..."
    mv rspi5_microplate rspi5_microplate.backup.$(date +%Y%m%d_%H%M%S)
fi

git clone https://github.com/alextu870719/rspi5_microplate.git
cd rspi5_microplate

# 安裝依賴
echo "📦 安裝Python依賴..."
sudo apt update -y
sudo apt install -y python3-pyqt5 python3-pandas python3-serial python3-pip

# 安裝額外依賴（如果需要）
pip3 install --user -r requirements.txt

# 設定執行權限
chmod +x install.sh

echo "✅ 快速安裝完成！"
echo ""
echo "🎯 下一步："
echo "1. 完整安裝: ./install.sh"
echo "2. 直接運行: python3 main.py"
echo "3. 範例CSV: ls Input_CSV/"
