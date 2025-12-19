"""
BRO Grondwater Tools
A QGIS plugin for retrieving and analyzing BRO groundwater monitoring data
"""

def classFactory(iface):
    """Load BROGroundwaterTools class from file bro_groundwater_tools.
    
    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    from .bro_groundwater_tools import BROGroundwaterTools
    return BROGroundwaterTools(iface)
