@echo off
REM Run backend development server
cd %~dp0\..\src\backend\autofactoryscope_api

REM Activate virtual environment if it exists
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

REM Run the API
uvicorn main:app --reload --host 0.0.0.0 --port 8000
