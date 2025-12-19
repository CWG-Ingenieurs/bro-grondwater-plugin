"""
BRO Grondwater Plugin - Main Plugin
"""

import os
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog, QMessageBox
from qgis.core import (QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry, 
                       QgsPointXY, QgsField, QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform, QgsRectangle)
from qgis.PyQt.QtCore import QVariant
from .bro_grondwater_plugin_dialog import BROGrondwaterPluginDialog
import sys


class BROGrondwaterPlugin:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'BROGrondwaterPlugin_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&BRO Grondwater Plugin')
        self.toolbar = self.iface.addToolBar(u'BROGrondwaterPlugin')
        self.toolbar.setObjectName(u'BROGrondwaterPlugin')
        
        self.dlg = None
        self.wells_layer = None

    def tr(self, message):
        """Get the translation for a string using Qt translation API."""
        return QCoreApplication.translate('BROGrondwaterPlugin', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar."""

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = os.path.join(self.plugin_dir, 'icon.png')
        self.add_action(
            icon_path,
            text=self.tr(u'BRO Grondwater Plugin'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&BRO Grondwater Plugin'),
                action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar

    def run(self):
        """Run method that performs all the real work"""
        
        # Create the dialog with elements (after translation) and keep reference
        if self.dlg is None:
            self.dlg = BROGrondwaterPluginDialog()
            
            # Connect signals
            self.dlg.btnRetrieveWells.clicked.connect(self.retrieve_wells)
            self.dlg.btnApplyFilter.clicked.connect(self.apply_filter)
            self.dlg.btnPlotData.clicked.connect(self.plot_measurements)
            self.dlg.btnExportExcel.clicked.connect(self.export_to_excel)
            
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()

    def retrieve_wells(self):
        """Retrieve BRO groundwater monitoring wells for the current extent."""
        try:
            # Import hydropandas here to avoid import errors if not installed
            try:
                import hydropandas as hpd
            except ImportError:
                QMessageBox.critical(
                    self.dlg,
                    "Import Error",
                    "Hydropandas is not installed. Please install it using:\n"
                    "pip install hydropandas[brodata]"
                )
                return
            
            # Get current map extent
            canvas = self.iface.mapCanvas()
            extent = canvas.extent()
            crs = canvas.mapSettings().destinationCrs()
            
            self.dlg.progressBar.setValue(10)
            self.dlg.statusLabel.setText("Retrieving well locations from BRO...")
            
            # Transform extent to WGS84 if needed (BRO uses WGS84)
            if crs.authid() != 'EPSG:4326':
                transform = QgsCoordinateTransform(
                    crs,
                    QgsCoordinateReferenceSystem('EPSG:4326'),
                    QgsProject.instance()
                )
                extent_wgs84 = transform.transformBoundingBox(extent)
            else:
                extent_wgs84 = extent
            
            # Create extent tuple for hydropandas
            extent_tuple = (
                extent_wgs84.xMinimum(),
                extent_wgs84.yMinimum(),
                extent_wgs84.xMaximum(),
                extent_wgs84.yMaximum()
            )
            
            self.dlg.progressBar.setValue(30)
            
            # Retrieve observations using hydropandas with brodata engine
            try:
                obs_collection = hpd.GroundwaterObs.from_bro(
                    extent=extent_tuple,
                    tmin=None,
                    tmax=None,
                    engine='brodata'  # Use the faster brodata engine
                )
            except Exception as e:
                QMessageBox.warning(
                    self.dlg,
                    "Retrieval Error",
                    f"Error retrieving data from BRO:\n{str(e)}\n\n"
                    "Make sure you have the DEV version of hydropandas installed:\n"
                    "pip install git+https://github.com/ArtesiaWater/hydropandas.git"
                )
                self.dlg.progressBar.setValue(0)
                self.dlg.statusLabel.setText("Ready")
                return
            
            self.dlg.progressBar.setValue(60)
            
            if len(obs_collection) == 0:
                QMessageBox.information(
                    self.dlg,
                    "No Data",
                    "No monitoring wells found in the current extent."
                )
                self.dlg.progressBar.setValue(0)
                self.dlg.statusLabel.setText("Ready")
                return
            
            # Create vector layer
            layer = QgsVectorLayer('Point?crs=EPSG:28992', 'BRO Monitoring Wells', 'memory')
            provider = layer.dataProvider()
            
            # Add fields
            provider.addAttributes([
                QgsField('name', QVariant.String),
                QgsField('bro_id', QVariant.String),
                QgsField('x', QVariant.Double),
                QgsField('y', QVariant.Double),
                QgsField('ground_level', QVariant.Double),
                QgsField('top_filter', QVariant.Double),
                QgsField('bottom_filter', QVariant.Double),
                QgsField('tube_nr', QVariant.Int),
            ])
            layer.updateFields()
            
            # Add features
            features = []
            for obs in obs_collection:
                feature = QgsFeature()
                
                # Get coordinates (assuming RD coordinates in metadata)
                if hasattr(obs, 'x') and hasattr(obs, 'y'):
                    x, y = obs.x, obs.y
                elif 'x' in obs.metadata and 'y' in obs.metadata:
                    x = obs.metadata['x']
                    y = obs.metadata['y']
                else:
                    continue
                
                feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x, y)))
                
                # Set attributes
                attributes = [
                    obs.name if hasattr(obs, 'name') else '',
                    obs.metadata.get('bro_id', ''),
                    x,
                    y,
                    obs.metadata.get('ground_level', None),
                    obs.metadata.get('screen_top', None),
                    obs.metadata.get('screen_bottom', None),
                    obs.metadata.get('tube_nr', None),
                ]
                feature.setAttributes(attributes)
                features.append(feature)
            
            provider.addFeatures(features)
            layer.updateExtents()
            
            self.dlg.progressBar.setValue(80)
            
            # Add layer to map
            QgsProject.instance().addMapLayer(layer)
            self.wells_layer = layer
            
            # Apply QMD styling if available
            qmd_path = os.path.join(self.plugin_dir, 'styles', 'wells_style.qmd')
            if os.path.exists(qmd_path):
                layer.loadNamedStyle(qmd_path)
                layer.triggerRepaint()
            
            self.dlg.progressBar.setValue(100)
            self.dlg.statusLabel.setText(f"Retrieved {len(features)} monitoring wells")
            
            # Store observation collection for later use
            self.obs_collection = obs_collection
            
            QMessageBox.information(
                self.dlg,
                "Success",
                f"Successfully retrieved {len(features)} monitoring wells."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self.dlg,
                "Error",
                f"An error occurred:\n{str(e)}"
            )
            self.dlg.progressBar.setValue(0)
            self.dlg.statusLabel.setText("Error occurred")

    def apply_filter(self):
        """Apply depth filter to the wells layer."""
        if self.wells_layer is None:
            QMessageBox.warning(
                self.dlg,
                "No Layer",
                "Please retrieve wells first."
            )
            return
        
        try:
            min_depth = self.dlg.spinMinDepth.value()
            max_depth = self.dlg.spinMaxDepth.value()
            
            # Build filter expression
            if max_depth > min_depth:
                filter_expr = f'"top_filter" >= {min_depth} AND "top_filter" <= {max_depth}'
            else:
                filter_expr = f'"top_filter" >= {min_depth}'
            
            self.wells_layer.setSubsetString(filter_expr)
            
            filtered_count = self.wells_layer.featureCount()
            self.dlg.statusLabel.setText(f"Filter applied: {filtered_count} wells visible")
            
        except Exception as e:
            QMessageBox.critical(
                self.dlg,
                "Filter Error",
                f"Error applying filter:\n{str(e)}"
            )

    def plot_measurements(self):
        """Plot measurements for selected wells."""
        if self.wells_layer is None:
            QMessageBox.warning(
                self.dlg,
                "No Layer",
                "Please retrieve wells first."
            )
            return
        
        selected_features = self.wells_layer.selectedFeatures()
        if len(selected_features) == 0:
            QMessageBox.warning(
                self.dlg,
                "No Selection",
                "Please select one or more wells using QGIS selection tools."
            )
            return
        
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
            from PyQt5.QtWidgets import QDialog, QVBoxLayout
            
            # Get measurements for selected wells
            self.dlg.statusLabel.setText("Retrieving measurements...")
            
            # Create plot dialog
            plot_dialog = QDialog(self.dlg)
            plot_dialog.setWindowTitle("Groundwater Measurements")
            plot_dialog.resize(800, 600)
            layout = QVBoxLayout()
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            for feature in selected_features:
                bro_id = feature['bro_id']
                name = feature['name']
                
                # Find corresponding observation in collection
                obs = None
                for o in self.obs_collection:
                    if o.metadata.get('bro_id', '') == bro_id or o.name == name:
                        obs = o
                        break
                
                if obs is not None and len(obs) > 0:
                    # Plot the measurements
                    obs.plot(ax=ax, label=name or bro_id)
            
            ax.set_xlabel('Date')
            ax.set_ylabel('Groundwater Level (m NAP)')
            ax.set_title('Groundwater Measurements')
            ax.legend()
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            
            canvas = FigureCanvasQTAgg(fig)
            layout.addWidget(canvas)
            plot_dialog.setLayout(layout)
            
            self.dlg.statusLabel.setText("Plot created")
            plot_dialog.exec_()
            
        except ImportError:
            QMessageBox.critical(
                self.dlg,
                "Import Error",
                "Matplotlib is required for plotting. Please install it using:\n"
                "pip install matplotlib"
            )
        except Exception as e:
            QMessageBox.critical(
                self.dlg,
                "Plot Error",
                f"Error creating plot:\n{str(e)}"
            )

    def export_to_excel(self):
        """Export measurements for selected wells to Excel."""
        if self.wells_layer is None:
            QMessageBox.warning(
                self.dlg,
                "No Layer",
                "Please retrieve wells first."
            )
            return
        
        selected_features = self.wells_layer.selectedFeatures()
        if len(selected_features) == 0:
            QMessageBox.warning(
                self.dlg,
                "No Selection",
                "Please select one or more wells using QGIS selection tools."
            )
            return
        
        # Get file path from user
        file_path, _ = QFileDialog.getSaveFileName(
            self.dlg,
            "Save Excel File",
            "",
            "Excel Files (*.xlsx)"
        )
        
        if not file_path:
            return
        
        try:
            import pandas as pd
            
            self.dlg.statusLabel.setText("Exporting to Excel...")
            
            # Create Excel writer
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Write metadata sheet
                metadata_list = []
                for feature in selected_features:
                    metadata_list.append({
                        'Name': feature['name'],
                        'BRO ID': feature['bro_id'],
                        'X': feature['x'],
                        'Y': feature['y'],
                        'Ground Level': feature['ground_level'],
                        'Top Filter': feature['top_filter'],
                        'Bottom Filter': feature['bottom_filter'],
                        'Tube Nr': feature['tube_nr']
                    })
                
                metadata_df = pd.DataFrame(metadata_list)
                metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
                
                # Write measurements for each well
                for feature in selected_features:
                    bro_id = feature['bro_id']
                    name = feature['name']
                    
                    # Find corresponding observation
                    obs = None
                    for o in self.obs_collection:
                        if o.metadata.get('bro_id', '') == bro_id or o.name == name:
                            obs = o
                            break
                    
                    if obs is not None and len(obs) > 0:
                        sheet_name = (name or bro_id)[:31]  # Excel sheet name limit
                        obs.to_excel(writer, sheet_name=sheet_name)
                
                # Add credits and disclaimer sheet
                credits_data = {
                    'Information': [
                        'BRO Grondwater Plugin',
                        'Version 0.1',
                        'Developed by: CWGI',
                        '',
                        'Powered by Hydropandas (Artesia)',
                        'Data source: BRO (Basisregistratie Ondergrond)',
                        '',
                        'DISCLAIMER',
                        'This software is provided "as is", without warranty of any kind, express or implied,',
                        'including but not limited to the warranties of merchantability, fitness for a particular',
                        'purpose and noninfringement. In no event shall the authors or copyright holders be liable',
                        'for any claim, damages or other liability, whether in an action of contract, tort or otherwise,',
                        'arising from, out of or in connection with the software or the use or other dealings in the software.',
                    ]
                }
                credits_df = pd.DataFrame(credits_data)
                credits_df.to_excel(writer, sheet_name='Credits & Disclaimer', index=False, header=False)
            
            self.dlg.statusLabel.setText(f"Exported to {file_path}")
            QMessageBox.information(
                self.dlg,
                "Success",
                f"Data successfully exported to:\n{file_path}"
            )
            
        except ImportError:
            QMessageBox.critical(
                self.dlg,
                "Import Error",
                "Pandas and openpyxl are required for Excel export. Please install them using:\n"
                "pip install pandas openpyxl"
            )
        except Exception as e:
            QMessageBox.critical(
                self.dlg,
                "Export Error",
                f"Error exporting to Excel:\n{str(e)}"
            )
