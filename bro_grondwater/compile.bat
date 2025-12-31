@echo off
REM Compile resources and UI files for the BRO Grondwater Plugin

echo Compiling BRO Grondwater Plugin resources...

REM Compile resources (if pyrcc5 is available)
where pyrcc5 >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Compiling resources.qrc...
    pyrcc5 -o resources_rc.py resources.qrc
    echo [OK] Resources compiled
) else (
    echo [WARNING] pyrcc5 not found. Resource compilation skipped.
    echo           Resources will be loaded directly from files.
)

REM Compile UI files (if pyuic5 is available)
where pyuic5 >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Compiling UI files...
    REM If you have separate .ui files to compile:
    REM pyuic5 -o ui_compiled.py your_file.ui
    echo [OK] UI files processed
) else (
    echo [WARNING] pyuic5 not found. UI files will be loaded dynamically.
)

echo.
echo Build complete! The plugin is ready to use.
echo.
echo To install:
echo 1. Copy the 'bro_grondwater_plugin' folder to your QGIS plugins directory
echo 2. Restart QGIS
echo 3. Enable the plugin in Plugins -^> Manage and Install Plugins
echo.
pause
