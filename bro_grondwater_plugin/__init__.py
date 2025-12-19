"""
BRO Grondwater Plugin
A QGIS plugin for retrieving and analyzing BRO groundwater monitoring data
"""


def classFactory(iface):
    """Load BROGrondwaterPlugin class from file bro_grondwater_plugin.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    from .bro_grondwater_plugin import BROGrondwaterPlugin
    return BROGrondwaterPlugin(iface)
