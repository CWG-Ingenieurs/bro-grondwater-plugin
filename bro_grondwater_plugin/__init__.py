"""
BRO Grondwater Plugin
A QGIS plugin for retrieving and analyzing BRO groundwater monitoring data
"""

import subprocess
import sys
import os


def check_and_install_dependencies():
    """Check for required dependencies and install if missing."""
    dependencies = {
        'pandas': 'pandas>=1.3.0',
        'openpyxl': 'openpyxl>=3.0.0',
        'matplotlib': 'matplotlib>=3.3.0',
        'hydropandas': 'git+https://github.com/ArtesiaWater/hydropandas.git@dev',
    }

    missing = []
    for module, package in dependencies.items():
        try:
            __import__(module)
        except ImportError:
            missing.append((module, package))

    if missing:
        from qgis.PyQt.QtWidgets import QMessageBox

        msg = "The following dependencies are missing:\n\n"
        msg += "\n".join([f"  - {m[0]}" for m in missing])
        msg += "\n\nWould you like to install them automatically?"

        reply = QMessageBox.question(
            None,
            "BRO Grondwater Plugin - Missing Dependencies",
            msg,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )

        if reply == QMessageBox.Yes:
            for module, package in missing:
                try:
                    subprocess.check_call([
                        sys.executable, '-m', 'pip', 'install', package
                    ])
                except subprocess.CalledProcessError as e:
                    QMessageBox.warning(
                        None,
                        "Installation Error",
                        f"Failed to install {module}:\n{str(e)}\n\n"
                        "Please install manually using pip."
                    )
                    return False

            QMessageBox.information(
                None,
                "Installation Complete",
                "Dependencies installed successfully!\n\n"
                "Please restart QGIS for changes to take effect."
            )
            return False

        return False

    return True


def classFactory(iface):
    """Load BROGrondwaterPlugin class from file bro_grondwater_plugin.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    # Check dependencies before loading the plugin
    if not check_and_install_dependencies():
        # Return a dummy plugin that does nothing if dependencies are missing
        class DummyPlugin:
            def __init__(self, iface):
                pass
            def initGui(self):
                pass
            def unload(self):
                pass
        return DummyPlugin(iface)

    from .bro_grondwater_plugin import BROGrondwaterPlugin
    return BROGrondwaterPlugin(iface)
