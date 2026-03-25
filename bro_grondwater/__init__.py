"""
BRO Grondwater Plugin
A QGIS plugin for retrieving and analyzing BRO groundwater monitoring data
"""


def _install_dependencies():
    """Auto-install required packages via pip if not already present."""
    import subprocess
    import sys
    packages = ['hydropandas', 'brodata', 'xlsxwriter']
    for package in packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            try:
                subprocess.check_call(
                    [sys.executable, '-m', 'pip', 'install', '--quiet', package],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except Exception:
                pass


_install_dependencies()


def classFactory(iface):
    """Load BROGrondwaterPlugin class from file bro_grondwater.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    try:
        from .bro_grondwater import BROGrondwaterPlugin
        return BROGrondwaterPlugin(iface)
    except ImportError as e:
        from qgis.PyQt.QtWidgets import QMessageBox
        QMessageBox.critical(
            None,
            "BRO Grondwater Plugin",
            f"Missing dependency: {e}\n\n"
            "Please restart QGIS. If the problem persists, install manually via OSGeo4W Shell:\n"
            "  pip install hydropandas brodata pandas xlsxwriter matplotlib"
        )
        raise
