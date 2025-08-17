@echo off
echo 🚀 ProxyFinder Setup Helper
echo ============================
echo.

echo 📦 Installing required packages...
pip install -r requirements.txt

echo.
echo 🔍 Running setup verification...
python setup_verification.py

echo.
echo 📖 Setup complete! Check SETUP_GUIDE.md for next steps.
pause
