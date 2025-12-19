"""
BRO Grondwater Plugin
A QGIS plugin for retrieving and analyzing BRO groundwater monitoring data
"""


def classFactory(iface):
    """Load BROGrondwaterPlugin class from file bro_grondwater_plugin.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    try:
        from .bro_grondwater_plugin import BROGrondwaterPlugin
        return BROGrondwaterPlugin(iface)
    except ImportError as e:
        from qgis.PyQt.QtWidgets import QMessageBox
        QMessageBox.critical(
            None,
            "BRO Grondwater Plugin",
            f"Missing dependency: {e}\n\n"
            "Install via OSGeo4W Shell:\n"
            "  pip install hydropandas pandas openpyxl matplotlib"
        )
        raise
