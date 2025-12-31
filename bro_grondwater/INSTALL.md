# Installation Guide

## System Requirements

- **QGIS**: Version 3.0 or higher
- **Python**: 3.7+ (included with QGIS)
- **Operating System**: Windows, macOS, or Linux
- **Internet Connection**: Required for data retrieval from BRO

## Step-by-Step Installation

### 1. Install QGIS

If you don't have QGIS installed:
- Download from: https://qgis.org/en/site/forusers/download.html
- Follow the installation instructions for your operating system

### 2. Install Python Dependencies

#### Option A: Using OSGeo4W Shell (Windows)

1. Open **OSGeo4W Shell** as Administrator
   - Search for "OSGeo4W Shell" in Windows Start Menu
   - Right-click and select "Run as administrator"

2. Install dependencies:
```bash
python3 -m pip install hydropandas pandas xlsxwriter matplotlib
```

#### Option B: Using QGIS Python Console (All Platforms)

1. Open QGIS
2. Go to `Plugins` → `Python Console`
3. Run these commands one by one:

```python
import subprocess
import sys

# Install all dependencies
subprocess.check_call([sys.executable, '-m', 'pip', 'install',
                      'hydropandas', 'pandas', 'xlsxwriter', 'matplotlib'])
```

#### Option C: Using Terminal/Command Prompt (macOS/Linux)

1. Find your QGIS Python path:
   - **macOS**: `/Applications/QGIS.app/Contents/MacOS/bin/python3`
   - **Linux**: `/usr/bin/python3` (or QGIS-specific Python)

2. Install dependencies:
```bash
# macOS example
/Applications/QGIS.app/Contents/MacOS/bin/python3 -m pip install hydropandas pandas xlsxwriter matplotlib

# Linux example
python3 -m pip install hydropandas pandas xlsxwriter matplotlib
```

### 3. Install the Plugin

#### Option A: Manual Installation

1. **Download the plugin**:
   - Download from GitHub: https://github.com/CWGI/bro-grondwater-plugin
   - Click "Code" → "Download ZIP"
   - Extract the ZIP file

2. **Locate QGIS plugins directory**:
   - **Windows**: `C:\Users\<YourUsername>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins`
   - **macOS**: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins`
   - **Linux**: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins`

   If the directory doesn't exist, create it.

3. **Copy plugin folder**:
   - Copy the entire `bro_grondwater` folder to the plugins directory

4. **Verify structure**:
   Your plugins directory should look like this:
   ```
   plugins/
   └── bro_grondwater/
       ├── __init__.py
       ├── bro_grondwater.py
       ├── metadata.txt
       └── ... (other files)
   ```

#### Option B: From GitHub (For Developers)

```bash
cd /path/to/QGIS/plugins/
git clone https://github.com/CWGI/bro-grondwater-plugin.git bro_grondwater
```

### 4. Enable the Plugin

1. **Restart QGIS**
2. Go to `Plugins` → `Manage and Install Plugins`
3. Click on `Installed` tab
4. Find **BRO Grondwater Plugin** in the list
5. Check the checkbox to enable it

### 5. Verify Installation

1. You should see a new menu item: `Plugins` → `BRO Grondwater Plugin`
2. A toolbar icon should appear (if toolbar is visible)
3. Click the menu item or icon to open the plugin dialog

## Troubleshooting Installation

### "Module not found" errors

If you get errors like `ModuleNotFoundError: No module named 'hydropandas'`:

1. Verify you're installing to the correct Python environment
2. Check which Python QGIS is using:
   ```python
   import sys
   print(sys.executable)
   ```
3. Install packages to that specific Python

### Permission errors (Windows)

- Run OSGeo4W Shell as Administrator
- Or use `--user` flag:
  ```bash
  python3 -m pip install --user <package>
  ```

### SSL/Certificate errors

If you get SSL errors during installation:
```bash
python3 -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org <package>
```

### Plugin doesn't appear in menu

1. Check if plugin folder name is exactly `bro_grondwater`
2. Verify `metadata.txt` and `__init__.py` exist
3. Check QGIS Plugin Manager for error messages
4. Look in QGIS logs: `Settings` → `Options` → `Message Log`

### Hydropandas issues

Reinstall hydropandas:
```bash
python3 -m pip uninstall hydropandas
python3 -m pip install hydropandas
```

### Testing Installation

Run this test in QGIS Python Console:
```python
try:
    import hydropandas as hpd
    import pandas as pd
    import matplotlib.pyplot as plt
    import xlsxwriter
    print("✓ All dependencies installed successfully!")
except ImportError as e:
    print(f"✗ Missing dependency: {e}")
```

## Updating the Plugin

### Manual Update
1. Download the latest version
2. Delete old `bro_grondwater` folder from plugins directory
3. Copy new folder
4. Restart QGIS

### Git Update (For Developers)
```bash
cd /path/to/QGIS/plugins/bro_grondwater
git pull origin main
```

## Uninstalling

1. Close QGIS
2. Delete `bro_grondwater` folder from plugins directory
3. Optional: Uninstall Python packages:
   ```bash
   python3 -m pip uninstall hydropandas pandas xlsxwriter matplotlib
   ```

## Getting Help

If you encounter issues:

1. Check the [README.md](README.md) for usage instructions
2. Review error messages in QGIS Message Log
3. Verify all dependencies are installed correctly
4. Contact CWG Ingenieurs b.v.: info@cwgi.nl

## Next Steps

Once installed, see [README.md](README.md) for usage instructions.
