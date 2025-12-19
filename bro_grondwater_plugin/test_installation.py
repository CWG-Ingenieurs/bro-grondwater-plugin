"""
Test script for BRO Grondwater Plugin
Run this in QGIS Python Console to verify installation
"""

def test_plugin():
    """Test plugin installation and dependencies"""

    print("=" * 50)
    print("BRO Grondwater Plugin - Installation Test")
    print("=" * 50)
    print()
    
    # Test 1: Check if plugin is loaded
    print("Test 1: Plugin Loading")
    try:
        plugin = iface.plugins.get('bro_grondwater_plugin')
        if plugin:
            print("✓ Plugin loaded successfully")
        else:
            print("✗ Plugin not found in loaded plugins")
            print("  → Enable plugin in Plugin Manager")
    except Exception as e:
        print(f"✗ Error checking plugin: {e}")
    print()
    
    # Test 2: Check dependencies
    print("Test 2: Dependencies")
    dependencies = {
        'hydropandas': 'Hydropandas (BRO data access)',
        'pandas': 'Pandas (data manipulation)',
        'matplotlib': 'Matplotlib (plotting)',
        'openpyxl': 'OpenPyXL (Excel export)'
    }
    
    all_ok = True
    for module, description in dependencies.items():
        try:
            __import__(module)
            print(f"✓ {description}")
        except ImportError:
            print(f"✗ {description} - NOT INSTALLED")
            all_ok = False
    print()
    
    # Test 3: Check Hydropandas version and brodata support
    print("Test 3: Hydropandas Configuration")
    try:
        import hydropandas as hpd
        print(f"✓ Hydropandas version: {hpd.__version__ if hasattr(hpd, '__version__') else 'Unknown'}")
        
        # Check if brodata engine is available
        try:
            # Try to check for brodata availability
            print("  Checking brodata engine support...")
            print("  ℹ To verify brodata works, try retrieving data")
        except Exception as e:
            print(f"  ⚠ Could not verify brodata engine: {e}")
    except ImportError:
        print("✗ Hydropandas not available")
        all_ok = False
    print()
    
    # Test 4: Check QGIS API access
    print("Test 4: QGIS API")
    try:
        from qgis.core import QgsVectorLayer, QgsProject
        from qgis.PyQt.QtWidgets import QMessageBox
        print("✓ QGIS core modules accessible")
        print("✓ Qt widgets accessible")
    except ImportError as e:
        print(f"✗ QGIS API error: {e}")
        all_ok = False
    print()
    
    # Test 5: Check plugin files
    print("Test 5: Plugin Files")
    import os
    plugin_dir = os.path.dirname(os.path.abspath(__file__))
    required_files = [
        '__init__.py',
        'bro_grondwater_plugin.py',
        'bro_grondwater_plugin_dialog.py',
        'bro_grondwater_plugin_dialog_base.ui',
        'metadata.txt',
        'icon.png'
    ]
    
    for filename in required_files:
        filepath = os.path.join(plugin_dir, filename)
        if os.path.exists(filepath):
            print(f"✓ {filename}")
        else:
            print(f"✗ {filename} - MISSING")
            all_ok = False
    print()
    
    # Test 6: Check optional files
    print("Test 6: Optional Files")
    optional_files = ['styles/wells_style.qmd']
    for filename in optional_files:
        filepath = os.path.join(plugin_dir, filename)
        if os.path.exists(filepath):
            print(f"✓ {filename}")
        else:
            print(f"⚠ {filename} - Optional (styling will be basic)")
    print()
    
    # Summary
    print("=" * 50)
    if all_ok:
        print("✓ ALL TESTS PASSED")
        print()
        print("Plugin is ready to use!")
        print("Open it from: Plugins → BRO Grondwater Plugin")
    else:
        print("✗ SOME TESTS FAILED")
        print()
        print("Please install missing dependencies:")
        print("pip install git+https://github.com/ArtesiaWater/hydropandas.git")
        print("pip install pandas openpyxl matplotlib")
    print("=" * 50)

# Run the test
if __name__ == '__main__':
    test_plugin()
