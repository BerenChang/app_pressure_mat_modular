@echo off
setlocal EnableDelayedExpansion

:: Check if Python script name is provided as an argument
if "%1"=="" (
    echo Error: Please provide the Python script name as an argument (e.g., %0 script.py)
    exit /b 1
)

:: Store the Python script name
set "SCRIPT_NAME=%1"
set "SCRIPT_NAME=%SCRIPT_NAME:.py=%"

:: Check if the Python script exists
if not exist "%SCRIPT_NAME%.py" (
    echo Error: The file %SCRIPT_NAME%.py does not exist in the current directory
    exit /b 1
)

:: Install PyInstaller if not already installed
echo Installing PyInstaller...
pip install pyinstaller
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to install PyInstaller
    exit /b 1
)

:: Run PyInstaller to create a single executable
echo Converting %SCRIPT_NAME%.py to executable...
pyinstaller --onefile "%SCRIPT_NAME%.py"
if %ERRORLEVEL% neq 0 (
    echo Error: PyInstaller failed to create the executable
    exit /b 1
)

:: Check if the executable was created
if exist "dist\%SCRIPT_NAME%.exe" (
    echo Success: Executable created at dist\%SCRIPT_NAME%.exe
) else (
    echo Error: Executable was not created
    exit /b 1
)

endlocal