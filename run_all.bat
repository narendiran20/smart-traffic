@echo off
echo Starting Speed Detector...
start cmd /k "python speed_detector.py"

echo Starting Telegram Alert...
start cmd /k "python telegram_alert.py"

echo Starting Streamlit Dashboard...
start cmd /k "streamlit run dashboard_app.py"
