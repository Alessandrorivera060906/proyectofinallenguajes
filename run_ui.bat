@echo off
cd /d "%~dp0"
call ".venv\Scripts\activate"
python -m streamlit run chomsky_classifier_ai\ui_streamlit.py --server.port 8502
pause
