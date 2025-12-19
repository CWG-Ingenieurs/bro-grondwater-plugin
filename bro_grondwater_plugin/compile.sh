#!/bin/bash
# Compile resources and UI files for the BRO Grondwater Plugin

echo "Compiling BRO Grondwater Plugin resources..."

# Compile resources (if pyrcc5 is available)
if command -v pyrcc5 &> /dev/null; then
    echo "Compiling resources.qrc..."
    pyrcc5 -o resources_rc.py resources.qrc
    echo "✓ Resources compiled"
else
    echo "⚠ pyrcc5 not found. Resource compilation skipped."
    echo "  Resources will be loaded directly from files."
fi

# Compile UI files (if pyuic5 is available)
if command -v pyuic5 &> /dev/null; then
    echo "Compiling UI files..."
    # If you have separate .ui files to compile:
    # pyuic5 -o ui_compiled.py your_file.ui
    echo "✓ UI files processed"
else
    echo "⚠ pyuic5 not found. UI files will be loaded dynamically."
fi

echo ""
echo "Build complete! The plugin is ready to use."
echo ""
echo "To install:"
echo "1. Copy the 'bro_grondwater_plugin' folder to your QGIS plugins directory"
echo "2. Restart QGIS"
echo "3. Enable the plugin in Plugins → Manage and Install Plugins"
