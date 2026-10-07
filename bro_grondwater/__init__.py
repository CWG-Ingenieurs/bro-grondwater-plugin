"""
BRO Grondwater Plugin
A QGIS plugin for retrieving and analyzing BRO groundwater monitoring data
"""

import io
import sys

# Fix stdout/stderr for QGIS before any imports that may emit warnings
if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()


# Packages installed into the QGIS Python environment, with minimum versions.
# The minimums of the pure-Python HTTP stack (requests, urllib3, idna, certifi)
# and tqdm avoid versions with known vulnerabilities (CVEs, issue #25). Compiled
# packages that ship with QGIS (numpy, pillow, lxml, ...) are deliberately not
# upgraded from here: replacing them with pip can break QGIS itself. Keep in sync
# with requirements.txt and pip_dependencies in metadata.txt.
DEPENDENCIES = {
    "hydropandas": None,
    "brodata": None,
    "pandas": "1.3.0",
    "xlsxwriter": "3.0.0",
    "pyqtgraph": None,
    "requests": "2.33.0",
    "urllib3": "2.8.0",
    "idna": "3.15",
    "certifi": "2024.7.4",
    "tqdm": "4.66.3",
}


def _needs_install(package, minimum):
    """Return True if package is missing or older than its minimum version."""
    from importlib.metadata import PackageNotFoundError, version

    try:
        installed = version(package)
    except PackageNotFoundError:
        return True
    if minimum is None:
        return False
    try:
        from packaging.version import Version
    except ImportError:
        from pip._vendor.packaging.version import Version
    try:
        return Version(installed) < Version(minimum)
    except Exception:
        return False


def _install_dependencies():
    """Install missing packages and upgrade ones below their minimum version."""
    for package, minimum in DEPENDENCIES.items():
        requirement = f"{package}>={minimum}" if minimum else package
        try:
            if not _needs_install(package, minimum):
                continue
            from pip._internal.cli.main import main as pip_main

            pip_main(["install", "--quiet", requirement])
        except Exception as e:
            # Don't block loading the plugin; a missing package is reported
            # when classFactory imports the plugin.
            from qgis.core import Qgis, QgsMessageLog

            QgsMessageLog.logMessage(
                f"Could not install {requirement}: {e}", "BRO Grondwater", Qgis.Warning
            )


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
            "Please restart QGIS. If the problem persists, install manually via "
            "OSGeo4W Shell:\n"
            "  pip install hydropandas brodata pandas xlsxwriter pyqtgraph",
        )
        raise
