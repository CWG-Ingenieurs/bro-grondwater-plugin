"""
BRO Grondwater Plugin Panel
"""

import os
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QWidget

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'bro_grondwater_dialog_base.ui'))


class BROGrondwaterPluginPanel(QWidget, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(BROGrondwaterPluginPanel, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        self.setupUi(self)


# Keep old name for compatibility
BROGrondwaterPluginDialog = BROGrondwaterPluginPanel
