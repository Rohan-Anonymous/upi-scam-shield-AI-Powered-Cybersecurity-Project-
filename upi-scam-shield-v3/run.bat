@echo off
cd backend
pip install -r ..\requirements.txt
start http://127.0.0.1:8000
uvicorn main:app --reload
