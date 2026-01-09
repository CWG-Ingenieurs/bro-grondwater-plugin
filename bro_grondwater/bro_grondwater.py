"""
BRO Grondwater Plugin - Main Plugin
"""

import sys
import io

# Fix stdout/stderr for QGIS at module load time (before numpy/pandas imports)
if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()

import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt, QTimer
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog, QMessageBox, QDockWidget
from qgis.core import (QgsProject, QgsVectorLayer, QgsRasterLayer, QgsFeature, QgsGeometry,
                       QgsPointXY, QgsField, QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform, QgsRectangle, QgsMessageLog, Qgis)
from qgis.PyQt.QtCore import QVariant
from .bro_grondwater_dialog import BROGrondwaterPluginPanel


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
        self.dock_widget = None
        self.wells_layer = None
        self.wms_layer = None
        self.basemap_layer = None
        self.histogram_canvas = None
        self.obs_collection = None
        self.engine_used = None
        self._cancelled = False
        self._downloaded_measurements = {}  # Cache for downloaded measurements {cache_key: data}

        # ThreadPoolExecutor for background downloads
        self._executor = None
        self._futures = []
        self._poll_timer = None
        self._expected_results = 0
        self._downloaded_count = 0
        self._failed_count = 0

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

        # Remove dock widget
        if self.dock_widget is not None:
            self.iface.removeDockWidget(self.dock_widget)
            self.dock_widget = None
            self.dlg = None

    def run(self):
        """Run method that performs all the real work"""

        # Create the dock widget if not already created
        if self.dock_widget is None:
            # Create the panel
            self.dlg = BROGrondwaterPluginPanel()

            # Connect signals
            self.dlg.btnAddBasemap.clicked.connect(self.add_basemap)
            self.dlg.btnAddWmsLayer.clicked.connect(self.add_wms_layer)
            self.dlg.btnRetrieveWells.clicked.connect(self.retrieve_wells)
            self.dlg.btnApplyFilter.clicked.connect(self.apply_filter)
            self.dlg.btnDownloadMeasurements.clicked.connect(self.download_measurements)
            self.dlg.btnPlotData.clicked.connect(self.plot_measurements)
            self.dlg.btnExportExcel.clicked.connect(self.export_to_excel)
            self.dlg.btnCancel.clicked.connect(self._cancel_operation)

            # Create dock widget and add panel
            self.dock_widget = QDockWidget("BRO Grondwater", self.iface.mainWindow())
            self.dock_widget.setWidget(self.dlg)
            self.dock_widget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

            # Add to QGIS interface on the right side
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dock_widget)

        # Show/toggle the dock widget
        if self.dock_widget.isVisible():
            self.dock_widget.hide()
        else:
            self.dock_widget.show()

    def add_wms_layer(self):
        """Add WMS layer with GMW locations from PDOK."""
        # Fix stdout/stderr for QGIS
        import io
        if sys.stdout is None:
            sys.stdout = io.StringIO()
        if sys.stderr is None:
            sys.stderr = io.StringIO()

        try:
            # Check if layer already exists
            if self.wms_layer is not None:
                try:
                    layer_id = self.wms_layer.id()
                    if QgsProject.instance().mapLayer(layer_id) is not None:
                        self.dlg.statusLabel.setText("WMS layer already added")
                        return
                except RuntimeError:
                    # Layer was deleted, reset reference
                    self.wms_layer = None

            # WMS URL for GMW locations
            wms_url = (
                "crs=EPSG:28992&"
                "layers=gm_gmw&"
                "styles=default&"
                "format=image/png&"
                "url=https://service.pdok.nl/bzk/bro-gminsamenhang-karakteristieken/wms/v1_0?"
                "request=GetCapabilities&service=WMS"
            )

            self.wms_layer = QgsRasterLayer(wms_url, "BRO GMW Locations (WMS)", "wms")

            if self.wms_layer.isValid():
                QgsProject.instance().addMapLayer(self.wms_layer)
                self.dlg.statusLabel.setText("WMS layer added successfully")
            else:
                QMessageBox.warning(
                    self.dlg,
                    "WMS Error",
                    "Could not load WMS layer. Check your internet connection."
                )
                self.wms_layer = None

        except Exception as e:
            QMessageBox.critical(
                self.dlg,
                "Error",
                f"Error adding WMS layer:\n{str(e)}"
            )

    def add_basemap(self):
        """Add the BRT background basemap layer."""
        # Fix stdout/stderr for QGIS
        import io
        if sys.stdout is None:
            sys.stdout = io.StringIO()
        if sys.stderr is None:
            sys.stderr = io.StringIO()

        try:
            # Check if layer already exists
            if self.basemap_layer is not None:
                try:
                    layer_id = self.basemap_layer.id()
                    if QgsProject.instance().mapLayer(layer_id) is not None:
                        self.dlg.statusLabel.setText("Basemap already added")
                        return
                except RuntimeError:
                    # Layer was deleted, reset reference
                    self.basemap_layer = None

            # WMTS URL for BRT background map
            # Using contextualWMSLegend=0 and dpiMode=7 for better compatibility
            wmts_url = (
                "contextualWMSLegend=0&"
                "crs=EPSG:28992&"
                "dpiMode=7&"
                "format=image/png&"
                "layers=grijs&"
                "styles=default&"
                "tileMatrixSet=EPSG:28992&"
                "url=https://service.pdok.nl/brt/achtergrondkaart/wmts/v2_0?request%3DGetCapabilities%26service%3DWMTS"
            )

            # Create layer using QgsRasterLayer with wms provider
            self.basemap_layer = QgsRasterLayer(wmts_url, "BRT Achtergrondkaart (grijs)", "wms")

            if self.basemap_layer.isValid():
                # First add to project with addToLegend=True (default)
                QgsProject.instance().addMapLayer(self.basemap_layer, True)

                # Move layer to bottom of layer tree
                root = QgsProject.instance().layerTreeRoot()
                layer_node = root.findLayer(self.basemap_layer.id())
                if layer_node:
                    # Clone and re-add at bottom
                    cloned_node = layer_node.clone()
                    root.insertChildNode(-1, cloned_node)
                    # Remove original node (which was at top)
                    parent = layer_node.parent()
                    if parent:
                        parent.removeChildNode(layer_node)

                # Force refresh
                self.basemap_layer.triggerRepaint()
                self.iface.mapCanvas().refresh()

                self.dlg.statusLabel.setText("Basemap added successfully")
            else:
                QMessageBox.warning(
                    self.dlg,
                    "Basemap Error",
                    "Could not load basemap. Check your internet connection.\n\n"
                    "You can manually add the BRT basemap via:\n"
                    "Layer > Add Layer > Add WMS/WMTS Layer"
                )
                self.basemap_layer = None

        except Exception as e:
            QMessageBox.critical(
                self.dlg,
                "Error",
                f"Error adding basemap:\n{str(e)}"
            )

    def _start_operation(self):
        """Prepare UI for a long-running operation."""
        self._cancelled = False
        self.dlg.btnCancel.setEnabled(True)
        self.dlg.btnRetrieveWells.setEnabled(False)
        self.dlg.btnDownloadMeasurements.setEnabled(False)
        self.dlg.btnPlotData.setEnabled(False)
        self.dlg.btnExportExcel.setEnabled(False)

    def _end_operation(self):
        """Reset UI after operation completes."""
        self._cancelled = False
        self.dlg.btnCancel.setEnabled(False)
        self.dlg.btnRetrieveWells.setEnabled(True)
        self.dlg.btnDownloadMeasurements.setEnabled(True)
        self.dlg.btnPlotData.setEnabled(True)
        self.dlg.btnExportExcel.setEnabled(True)
        self.dlg.progressBar.setValue(0)

    def _cancel_operation(self):
        """Cancel the current operation."""
        self._cancelled = True
        self.dlg.statusLabel.setText("Cancelling...")

    def retrieve_wells(self):
        """Retrieve BRO groundwater monitoring wells for the current extent."""
        self._start_operation()
        try:
            # Import hydropandas here to avoid import errors if not installed
            try:
                # Fix for tqdm writing to None stdout in QGIS
                import io
                if sys.stdout is None:
                    sys.stdout = io.StringIO()
                if sys.stderr is None:
                    sys.stderr = io.StringIO()

                import hydropandas as hpd
            except ImportError:
                QMessageBox.critical(
                    self.dlg,
                    "Missing Dependency",
                    "Hydropandas is not installed.\n\n"
                    "Install via OSGeo4W Shell:\n"
                    "  pip install hydropandas pandas xlsxwriter matplotlib brodata"
                )
                return

            # Get current map extent
            canvas = self.iface.mapCanvas()
            extent = canvas.extent()
            crs = canvas.mapSettings().destinationCrs()
            
            self.dlg.progressBar.setValue(10)
            self.dlg.statusLabel.setText("Retrieving well locations from BRO...")
            
            # Transform extent to RD (EPSG:28992) if needed (hydropandas default)
            if crs.authid() != 'EPSG:28992':
                transform = QgsCoordinateTransform(
                    crs,
                    QgsCoordinateReferenceSystem('EPSG:28992'),
                    QgsProject.instance()
                )
                extent_rd = transform.transformBoundingBox(extent)
            else:
                extent_rd = extent

            # Create extent tuple for hydropandas (xmin, xmax, ymin, ymax)
            extent_tuple = (
                extent_rd.xMinimum(),
                extent_rd.xMaximum(),
                extent_rd.yMinimum(),
                extent_rd.yMaximum()
            )
            
            self.dlg.progressBar.setValue(30)

            # Retrieve observations using hydropandas
            # Use read_bro for extent-based queries (returns ObsCollection)
            # Use only_metadata=True for fast initial retrieval (measurements loaded on-demand)
            # Try brodata engine first (faster), fall back to default if not available
            engine_used = None
            try:
                try:
                    obs_collection = hpd.read_bro(
                        extent=extent_tuple,
                        tmin=None,
                        tmax=None,
                        only_metadata=True,
                        engine='brodata'
                    )
                    engine_used = 'brodata'
                except TypeError:
                    # brodata engine not available, use default
                    obs_collection = hpd.read_bro(
                        extent=extent_tuple,
                        tmin=None,
                        tmax=None,
                        only_metadata=True
                    )
                    engine_used = 'default'
            except Exception as e:
                QMessageBox.warning(
                    self.dlg,
                    "Retrieval Error",
                    f"Error retrieving data from BRO:\n{str(e)}\n\n"
                    "Please check your internet connection and try again."
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
            for idx, row in obs_collection.iterrows():
                obs = row['obs']
                feature = QgsFeature()

                # Get coordinates (assuming RD coordinates in metadata)
                if hasattr(obs, 'x') and hasattr(obs, 'y'):
                    x, y = obs.x, obs.y
                elif hasattr(obs, 'metadata') and 'x' in obs.metadata and 'y' in obs.metadata:
                    x = obs.metadata['x']
                    y = obs.metadata['y']
                elif 'x' in row and 'y' in row:
                    x, y = row['x'], row['y']
                else:
                    continue

                feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x, y)))

                # Get metadata from obs object or row
                metadata = obs.metadata if hasattr(obs, 'metadata') else {}

                # Set attributes
                attributes = [
                    obs.name if hasattr(obs, 'name') else row.get('name', ''),
                    metadata.get('bro_id', row.get('bro_id', '')),
                    x,
                    y,
                    metadata.get('ground_level', row.get('ground_level', None)),
                    metadata.get('screen_top', row.get('screen_top', None)),
                    metadata.get('screen_bottom', row.get('screen_bottom', None)),
                    metadata.get('tube_nr', row.get('tube_nr', None)),
                ]
                feature.setAttributes(attributes)
                features.append(feature)
            
            provider.addFeatures(features)
            layer.updateExtents()
            
            self.dlg.progressBar.setValue(80)
            
            # Add layer to map
            QgsProject.instance().addMapLayer(layer)
            self.wells_layer = layer
            
            # Apply QML styling if available
            qml_path = os.path.join(self.plugin_dir, 'styles', 'gmw.qml')
            if os.path.exists(qml_path):
                success, msg = layer.loadNamedStyle(qml_path)
                if success:
                    layer.triggerRepaint()
                else:
                    print(f"Failed to load style: {msg}")
            else:
                print(f"Style file not found: {qml_path}")
            
            self.dlg.progressBar.setValue(100)
            self.dlg.statusLabel.setText(f"Retrieved {len(features)} wells (engine: {engine_used})")

            # Store observation collection for later use
            self.obs_collection = obs_collection
            self.engine_used = engine_used

            # Update filter histogram with top_filter values
            self._update_filter_histogram()
            
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
            self.dlg.statusLabel.setText("Error occurred")
        finally:
            self._end_operation()

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

            # Refresh the layer and canvas
            self.wells_layer.triggerRepaint()
            self.iface.mapCanvas().refresh()

            filtered_count = self.wells_layer.featureCount()
            self.dlg.statusLabel.setText(f"Filter applied: {filtered_count} wells visible")

            # Zoom to filtered features if any
            if filtered_count > 0:
                self.wells_layer.updateExtents()
                self.iface.mapCanvas().setExtent(self.wells_layer.extent())
                self.iface.mapCanvas().refresh()

            # Update histogram to show filter range
            self._update_filter_histogram(min_depth, max_depth)

        except Exception as e:
            QMessageBox.critical(
                self.dlg,
                "Filter Error",
                f"Error applying filter:\n{str(e)}"
            )

    def download_measurements(self):
        """Download measurements for selected wells (or all if none selected).

        Uses multiprocessing to run downloads in separate Python processes,
        avoiding pyproj/PROJ conflicts with QGIS.
        """
        if self.wells_layer is None:
            QMessageBox.warning(
                self.dlg,
                "No Layer",
                "Please retrieve wells first."
            )
            return

        selected_features = self.wells_layer.selectedFeatures()

        # If no selection, use all visible features
        if len(selected_features) == 0:
            selected_features = list(self.wells_layer.getFeatures())
            if len(selected_features) == 0:
                QMessageBox.warning(
                    self.dlg,
                    "No Wells",
                    "No wells available to download."
                )
                return

        # Filter out already downloaded wells
        features_to_download = []
        for feature in selected_features:
            cache_key = f"{feature['bro_id']}_{feature['tube_nr']}_{feature['name']}"
            if cache_key not in self._downloaded_measurements:
                features_to_download.append({
                    'bro_id': feature['bro_id'],
                    'name': feature['name'],
                    'tube_nr': feature['tube_nr'],
                })

        if len(features_to_download) == 0:
            self.dlg.statusLabel.setText(f"All {len(selected_features)} wells already downloaded")
            return

        # Warn user if downloading many wells
        if len(features_to_download) > 20:
            reply = QMessageBox.warning(
                self.dlg,
                "Large Download",
                f"You are about to download measurements for {len(features_to_download)} wells.\n\n"
                "This may take a long time. Consider selecting fewer wells or "
                "applying a filter first.\n\n"
                f"Do you want to download the timeseries for all {len(features_to_download)} wells anyway?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                self.dlg.statusLabel.setText("Download cancelled")
                return

        self._start_operation()
        self.dlg.statusLabel.setText(f"Starting download of {len(features_to_download)} wells...")

        # Setup for threaded downloads
        self._expected_results = len(features_to_download)
        self._downloaded_count = 0
        self._failed_count = 0
        self._futures = []

        # Start ThreadPoolExecutor
        try:
            self._executor = ThreadPoolExecutor(max_workers=8)

            # Submit all downloads
            for feature_data in features_to_download:
                future = self._executor.submit(self._download_single_well, feature_data)
                self._futures.append(future)

            # Start timer to poll for results
            self._poll_timer = QTimer()
            self._poll_timer.timeout.connect(self._poll_download_results)
            self._poll_timer.start(200)  # Poll every 200ms

        except Exception as e:
            QMessageBox.critical(
                self.dlg,
                "Download Error",
                f"Error starting download:\n{str(e)}"
            )
            self._end_operation()

    def _download_single_well(self, feature_data):
        """Download measurements for a single well (runs in thread)."""
        import hydropandas as hpd

        bro_id = feature_data['bro_id']
        name = feature_data['name']
        tube_nr = feature_data['tube_nr']
        cache_key = f"{bro_id}_{tube_nr}_{name}"

        # Try to find GMW id
        gmw_id = None
        for candidate in [bro_id, name]:
            if candidate and 'GMW' in str(candidate):
                match = re.search(r'GMW\d+', str(candidate))
                if match:
                    gmw_id = match.group(0)
                    break

        if not gmw_id:
            return {
                'success': False,
                'cache_key': cache_key,
                'error': 'No GMW ID found',
                'name': name,
                'bro_id': bro_id,
                'tube_nr': tube_nr
            }

        try:
            obs = hpd.GroundwaterObs.from_bro(gmw_id, tube_nr or 1)

            if obs is not None and len(obs) > 0:
                # Serialize the observation data
                dates = [d.isoformat() for d in obs.index.tolist()]
                values = obs.iloc[:, 0].tolist()

                # Extract metadata from obs object
                metadata = {
                    'tube_nr': getattr(obs, 'tube_nr', tube_nr),
                    'x': getattr(obs, 'x', None),
                    'y': getattr(obs, 'y', None),
                    'ground_level': getattr(obs, 'ground_level', None),
                    'screen_top': getattr(obs, 'screen_top', None),
                    'screen_bottom': getattr(obs, 'screen_bottom', None),
                    'tube_top': getattr(obs, 'tube_top', None),
                    'source': getattr(obs, 'source', 'BRO'),
                    'unit': getattr(obs, 'unit', 'm NAP'),
                }

                return {
                    'success': True,
                    'cache_key': cache_key,
                    'data': {
                        'dates': dates,
                        'values': values,
                        'metadata': metadata,
                    },
                    'name': name,
                    'bro_id': bro_id,
                    'tube_nr': tube_nr
                }
            else:
                return {
                    'success': False,
                    'cache_key': cache_key,
                    'error': 'No data returned',
                    'name': name,
                    'bro_id': bro_id,
                    'tube_nr': tube_nr
                }
        except Exception as e:
            return {
                'success': False,
                'cache_key': cache_key,
                'error': str(e),
                'name': name,
                'bro_id': bro_id,
                'tube_nr': tube_nr
            }

    def _poll_download_results(self):
        """Poll for results from worker threads."""
        # Check for cancellation
        if self._cancelled:
            self._cancel_download()
            return

        # Check completed futures
        completed_futures = [f for f in self._futures if f.done()]

        for future in completed_futures:
            self._futures.remove(future)

            try:
                result = future.result()
                if result.get('success'):
                    self._downloaded_measurements[result['cache_key']] = {
                        'data': result['data'],
                        'name': result['name'],
                        'bro_id': result['bro_id'],
                        'tube_nr': result['tube_nr']
                    }
                    self._downloaded_count += 1
                else:
                    QgsMessageLog.logMessage(
                        f"Download failed for {result.get('name', 'unknown')}: {result.get('error', 'Unknown')}",
                        "BRO Grondwater", Qgis.Warning
                    )
                    self._failed_count += 1
            except Exception as e:
                QgsMessageLog.logMessage(f"Error processing result: {e}", "BRO Grondwater", Qgis.Warning)
                self._failed_count += 1

        # Update progress
        completed = self._downloaded_count + self._failed_count
        if self._expected_results > 0:
            progress = int((completed / self._expected_results) * 100)
            self.dlg.progressBar.setValue(progress)
            self.dlg.statusLabel.setText(f"Downloading: {completed}/{self._expected_results} completed")

        # Check if all done
        if completed >= self._expected_results and len(self._futures) == 0:
            self._finish_download()

    def _finish_download(self):
        """Finish the download process."""
        if self._poll_timer:
            self._poll_timer.stop()
            self._poll_timer = None

        if self._executor:
            self._executor.shutdown(wait=False)
            self._executor = None

        downloaded_count = self._downloaded_count
        failed_count = self._failed_count

        self._futures = []

        self.dlg.progressBar.setValue(100)
        status_msg = f"Downloaded {downloaded_count} wells"
        if failed_count > 0:
            status_msg += f" ({failed_count} failed)"
        self.dlg.labelDownloadStatus.setText(status_msg)
        self.dlg.labelDownloadStatus.setStyleSheet("color: #006600; font-style: normal;")
        self.dlg.statusLabel.setText(status_msg)

        self._end_operation()

    def _cancel_download(self):
        """Cancel the download process."""
        if self._poll_timer:
            self._poll_timer.stop()
            self._poll_timer = None

        if self._executor:
            self._executor.shutdown(wait=False, cancel_futures=True)
            self._executor = None

        self._futures = []

        self.dlg.statusLabel.setText("Download cancelled")
        self._end_operation()

    def _update_filter_histogram(self, filter_min=None, filter_max=None):
        """Update the histogram showing top_filter distribution."""
        if self.wells_layer is None:
            return

        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
            import numpy as np

            # Get top_filter values from the layer (unfiltered)
            self.wells_layer.setSubsetString('')  # Temporarily remove filter
            top_filter_values = []
            for feature in self.wells_layer.getFeatures():
                val = feature['top_filter']
                if val is not None:
                    top_filter_values.append(val)

            # Restore filter if set
            if filter_min is not None and filter_max is not None and filter_max > filter_min:
                self.wells_layer.setSubsetString(
                    f'"top_filter" >= {filter_min} AND "top_filter" <= {filter_max}'
                )

            if not top_filter_values:
                return

            # Clear existing histogram
            if hasattr(self, 'histogram_canvas') and self.histogram_canvas is not None:
                self.histogram_canvas.setParent(None)
                self.histogram_canvas.deleteLater()

            # Create new histogram
            fig, ax = plt.subplots(figsize=(4, 1.5))
            fig.patch.set_facecolor('#f0f0f0')
            ax.set_facecolor('#f0f0f0')

            # Plot histogram
            n, bins, patches = ax.hist(top_filter_values, bins=20, color='#0066cc',
                                        edgecolor='white', alpha=0.7)

            # Highlight filtered range if set
            if filter_min is not None and filter_max is not None:
                for i, (left, right) in enumerate(zip(bins[:-1], bins[1:])):
                    if left >= filter_min and right <= filter_max:
                        patches[i].set_facecolor('#00cc66')

            ax.set_xlabel('Top Filter Depth (m NAP)', fontsize=8)
            ax.set_ylabel('Count', fontsize=8)
            ax.tick_params(axis='both', labelsize=7)

            # Update spin box ranges based on data
            data_min = min(top_filter_values)
            data_max = max(top_filter_values)
            self.dlg.spinMinDepth.setMinimum(data_min - 10)
            self.dlg.spinMinDepth.setMaximum(data_max + 10)
            self.dlg.spinMaxDepth.setMinimum(data_min - 10)
            self.dlg.spinMaxDepth.setMaximum(data_max + 10)

            # Set default values to cover all data
            if filter_min is None:
                self.dlg.spinMinDepth.setValue(data_min)
                self.dlg.spinMaxDepth.setValue(data_max)

            fig.tight_layout()

            # Embed in dialog
            self.histogram_canvas = FigureCanvasQTAgg(fig)
            self.dlg.frameHistogram.layout().addWidget(self.histogram_canvas)

        except Exception as e:
            # Histogram is not critical, just log error
            print(f"Error creating histogram: {e}")

    def _get_measurements_for_well(self, bro_id, tube_nr, name=None):
        """Fetch measurements for a single well on-demand."""
        # Fix for tqdm/numpy writing to None stdout in QGIS
        import io
        if sys.stdout is None:
            sys.stdout = io.StringIO()
        if sys.stderr is None:
            sys.stderr = io.StringIO()

        import hydropandas as hpd

        # Try to find GMW id from bro_id or name
        gmw_id = None
        for candidate in [bro_id, name]:
            if candidate and 'GMW' in str(candidate):
                # Extract GMW id (format: GMW000000041261)
                import re
                match = re.search(r'GMW\d+', str(candidate))
                if match:
                    gmw_id = match.group(0)
                    break

        if not gmw_id:
            print(f"No GMW id found in bro_id={bro_id}, name={name}")
            return None

        try:
            obs = hpd.GroundwaterObs.from_bro(gmw_id, tube_nr or 1)
            return obs
        except Exception as e:
            print(f"Error fetching measurements for {gmw_id}: {e}")
            return None

    def _get_numeric_values(self, obs):
        """Extract numeric measurement values from GroundwaterObs object.

        The obs object may be a Series or DataFrame. If DataFrame, find the
        column with numeric measurement data (usually 'values' or 'stand').
        """
        # Fix stdout/stderr for QGIS
        import io
        if sys.stdout is None:
            sys.stdout = io.StringIO()
        if sys.stderr is None:
            sys.stderr = io.StringIO()

        import pandas as pd
        import numpy as np

        # If it's a Series, try to convert to numeric
        if isinstance(obs, pd.Series):
            numeric_vals = pd.to_numeric(obs, errors='coerce')
            mask = ~np.isnan(numeric_vals)
            return obs.index[mask], numeric_vals[mask]

        # If it's a DataFrame, find the right column
        if hasattr(obs, 'columns'):
            # Try common column names for groundwater measurements
            for col_name in ['values', 'stand', 'head', 'value']:
                if col_name in obs.columns:
                    vals = pd.to_numeric(obs[col_name], errors='coerce')
                    mask = ~np.isnan(vals)
                    return obs.index[mask], vals[mask]

            # Fall back to first numeric column
            for col in obs.columns:
                try:
                    vals = pd.to_numeric(obs[col], errors='coerce')
                    if vals.notna().any():
                        mask = ~np.isnan(vals)
                        return obs.index[mask], vals[mask]
                except:
                    continue

        # Last resort: try obs.values directly but filter non-numeric
        try:
            vals = pd.to_numeric(pd.Series(obs.values), errors='coerce')
            mask = ~np.isnan(vals)
            return obs.index[mask], vals.values[mask]
        except:
            return None, None

    def _save_plot(self, fig):
        """Save the current plot to a file."""
        from datetime import datetime
        default_filename = f"BRO_GMW_plot_{datetime.now().strftime('%y%m%d')}.png"
        downloads_folder = os.path.join(os.path.expanduser('~'), 'Downloads')
        if not os.path.exists(downloads_folder):
            downloads_folder = os.path.expanduser('~')
        default_path = os.path.join(downloads_folder, default_filename)

        file_path, _ = QFileDialog.getSaveFileName(
            self.dlg,
            "Save Plot",
            default_path,
            "PNG Files (*.png);;PDF Files (*.pdf);;SVG Files (*.svg)"
        )
        if file_path:
            fig.savefig(file_path, dpi=150, bbox_inches='tight')
            self.dlg.statusLabel.setText(f"Plot saved to {os.path.basename(file_path)}")

    def plot_measurements(self):
        """Plot measurements for downloaded wells."""
        if len(self._downloaded_measurements) == 0:
            QMessageBox.warning(
                self.dlg,
                "No Data",
                "Please download measurements first (step 4)."
            )
            return

        self._start_operation()
        try:
            # Fix stdout/stderr for QGIS
            import io
            if sys.stdout is None:
                sys.stdout = io.StringIO()
            if sys.stderr is None:
                sys.stderr = io.StringIO()

            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton

            # Create plot dialog
            plot_dialog = QDialog(self.dlg)
            plot_dialog.setWindowTitle("Grondwaterstand")
            plot_dialog.resize(800, 600)
            layout = QVBoxLayout()

            fig, ax = plt.subplots(figsize=(10, 6))

            self.dlg.statusLabel.setText("Creating plot...")

            # Plot all downloaded measurements
            plotted_count = 0
            from datetime import datetime as dt
            for cache_key, measurement in self._downloaded_measurements.items():
                series_data = measurement.get('data')
                name = measurement['name']
                bro_id = measurement['bro_id']

                if series_data and series_data.get('dates') and series_data.get('values'):
                    # Extract GMW id for label
                    import re
                    gmw_match = re.search(r'GMW\d+', str(name) + str(bro_id))
                    label = gmw_match.group(0) if gmw_match else (name or bro_id)

                    # Parse dates and get values
                    dates = [dt.fromisoformat(d) for d in series_data['dates']]
                    values = series_data['values']

                    if dates and values:
                        ax.plot(dates, values, label=label)
                        plotted_count += 1

            if self._cancelled:
                self.dlg.statusLabel.setText("Cancelled")
                plt.close(fig)
                return

            if plotted_count == 0:
                QMessageBox.warning(
                    self.dlg,
                    "No Data",
                    "No numeric measurement data found for the selected wells."
                )
                self.dlg.statusLabel.setText("Ready")
                return

            ax.set_xlabel('Datum')
            ax.set_ylabel('Stijghoogte (m NAP)')
            ax.set_title('Grondwaterstand')
            ax.legend()
            ax.grid(True, alpha=0.3)
            plt.tight_layout()

            canvas = FigureCanvasQTAgg(fig)

            # Add navigation toolbar with save button
            toolbar = NavigationToolbar2QT(canvas, plot_dialog)
            layout.addWidget(toolbar)
            layout.addWidget(canvas)

            # Add custom save button
            btn_layout = QHBoxLayout()
            btn_save = QPushButton("Save as PNG")
            btn_save.clicked.connect(lambda: self._save_plot(fig))
            btn_layout.addStretch()
            btn_layout.addWidget(btn_save)
            layout.addLayout(btn_layout)

            plot_dialog.setLayout(layout)

            self.dlg.progressBar.setValue(100)
            self.dlg.statusLabel.setText(f"Plot created ({plotted_count} wells)")
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
        finally:
            self._end_operation()

    def export_to_excel(self):
        """Export downloaded measurements to Excel using xlsxwriter for proper chart support."""
        if len(self._downloaded_measurements) == 0:
            QMessageBox.warning(
                self.dlg,
                "No Data",
                "Please download measurements first (step 4)."
            )
            return

        # Generate default filename with date and time to avoid overwriting
        from datetime import datetime
        default_filename = f"BRO_GMW_{datetime.now().strftime('%y%m%d_%H%M%S')}.xlsx"

        # Get Downloads folder
        downloads_folder = os.path.join(os.path.expanduser('~'), 'Downloads')
        if not os.path.exists(downloads_folder):
            downloads_folder = os.path.expanduser('~')

        default_path = os.path.join(downloads_folder, default_filename)

        # Get file path from user
        file_path, _ = QFileDialog.getSaveFileName(
            self.dlg,
            "Save Excel File",
            default_path,
            "Excel Files (*.xlsx)"
        )

        if not file_path:
            return

        self._start_operation()
        try:
            # Fix stdout/stderr for QGIS
            import io
            if sys.stdout is None:
                sys.stdout = io.StringIO()
            if sys.stderr is None:
                sys.stderr = io.StringIO()

            import re
            import xlsxwriter
            from datetime import datetime as dt

            self.dlg.statusLabel.setText("Exporting to Excel...")

            # Create workbook with xlsxwriter
            # nan_inf_to_errors converts NaN to empty cells and Inf to #NUM! errors
            workbook = xlsxwriter.Workbook(file_path, {'nan_inf_to_errors': True})

            # Add formats
            header_format = workbook.add_format({'bold': True, 'bg_color': '#D9E1F2'})
            date_format = workbook.add_format({'num_format': 'yyyy-mm-dd hh:mm:ss'})

            # Collect all series data first
            all_series_data = {}  # For chart: {gmw_id: (dates, values)}
            metadata_list = []

            for cache_key, measurement in self._downloaded_measurements.items():
                series_data = measurement.get('data', {})
                metadata = series_data.get('metadata', {})
                name = measurement['name']
                bro_id = measurement['bro_id']

                # Extract GMW id
                gmw_match = re.search(r'GMW\d+', str(name) + str(bro_id))
                gmw_id = gmw_match.group(0) if gmw_match else bro_id

                # Get metadata
                measurements_count = len(series_data.get('dates', [])) if series_data else 0
                metadata_list.append({
                    'GMW ID': gmw_id,
                    'Name': name,
                    'BRO ID': bro_id,
                    'Tube Nr': metadata.get('tube_nr', measurement['tube_nr']),
                    'X (RD)': metadata.get('x'),
                    'Y (RD)': metadata.get('y'),
                    'Surface Level (m NAP)': metadata.get('ground_level'),
                    'Filter Top (m NAP)': metadata.get('screen_top'),
                    'Filter Bottom (m NAP)': metadata.get('screen_bottom'),
                    'Tube Top (m NAP)': metadata.get('tube_top'),
                    'Source': metadata.get('source', 'BRO'),
                    'Unit': metadata.get('unit', 'm NAP'),
                    'Measurements Count': measurements_count,
                })

                # Collect series data for chart (use 'name' as series identifier)
                if series_data and series_data.get('dates') and series_data.get('values'):
                    # Use name as identifier, fall back to GMW ID
                    series_name = name if name else gmw_id
                    series_name = series_name[:31]  # Excel sheet name limit
                    dates = [dt.fromisoformat(d) for d in series_data['dates']]
                    values = series_data['values']
                    if dates and values:
                        all_series_data[series_name] = (dates, values)

            exported_count = len(all_series_data)

            # Write Metadata sheet
            meta_ws = workbook.add_worksheet('Metadata')
            meta_headers = ['GMW ID', 'Name', 'BRO ID', 'Tube Nr', 'X (RD)', 'Y (RD)',
                          'Surface Level (m NAP)', 'Filter Top (m NAP)', 'Filter Bottom (m NAP)',
                          'Tube Top (m NAP)', 'Source', 'Unit', 'Measurements Count']

            # Track max width for each column (start with header lengths)
            col_widths = [len(header) for header in meta_headers]

            # Write headers
            for col, header in enumerate(meta_headers):
                meta_ws.write(0, col, header, header_format)

            # Write data and track max widths
            for row, meta in enumerate(metadata_list, 1):
                for col, header in enumerate(meta_headers):
                    value = meta.get(header)
                    meta_ws.write(row, col, value)
                    # Update max width if this value is longer
                    if value is not None:
                        col_widths[col] = max(col_widths[col], len(str(value)))

            # Apply column widths (add small padding, cap at 50)
            for col, width in enumerate(col_widths):
                meta_ws.set_column(col, col, min(width + 2, 50))

            # Write Chart Data sheet and create chart
            if all_series_data:
                # Build combined data with common datetime column
                all_dates = set()
                for dates, values in all_series_data.values():
                    all_dates.update(dates)
                all_dates = sorted(all_dates)

                # Pre-compute lookup dictionaries for fast access
                gmw_ids = list(all_series_data.keys())
                series_dicts = {}
                for gmw_id in gmw_ids:
                    dates_list, values_list = all_series_data[gmw_id]
                    series_dicts[gmw_id] = dict(zip(dates_list, values_list))

                # Create chart data worksheet
                data_ws = workbook.add_worksheet('Chart Data')

                # Write headers as a row
                headers = ['datetime'] + gmw_ids
                data_ws.write_row(0, 0, headers, header_format)

                # Build and write data rows efficiently
                for row, date in enumerate(all_dates, 1):
                    # Write date with explicit format (write_row doesn't apply formats)
                    data_ws.write_datetime(row, 0, date, date_format)
                    # Write values for each series
                    for col, gmw_id in enumerate(gmw_ids, 1):
                        value = series_dicts[gmw_id].get(date)
                        if value is not None:
                            data_ws.write_number(row, col, value)

                # Set column width for date column
                data_ws.set_column(0, 0, 20)
                # Set data column widths based on header length (names can be long)
                for col, series_id in enumerate(gmw_ids, 1):
                    data_ws.set_column(col, col, max(len(series_id) + 2, 18))

                # Create chart with show_blanks_as='span' to connect across gaps
                chart = workbook.add_chart({'type': 'line'})
                chart.show_blanks_as('span')  # This properly connects lines across empty cells

                # Add data series
                num_rows = len(all_dates)
                for col, gmw_id in enumerate(gmw_ids, 1):
                    chart.add_series({
                        'name': ['Chart Data', 0, col],
                        'categories': ['Chart Data', 1, 0, num_rows, 0],
                        'values': ['Chart Data', 1, col, num_rows, col],
                    })

                # Style the chart (Dutch labels)
                chart.set_title({'name': 'Grondwaterstand'})
                chart.set_x_axis({
                    'name': 'Datum',
                    'date_axis': True,
                    'label_position': 'low',  # Labels at bottom of plot area
                    'num_format': 'dd-mm-yyyy',
                })
                chart.set_y_axis({
                    'name': 'Stijghoogte (m NAP)',
                    'crossing': 'min',  # X-axis crosses at y-minimum, not at y=0
                })
                chart.set_legend({'position': 'bottom'})  # Legend below chart
                chart.set_size({'width': 800, 'height': 480})

                # Create a dedicated chart sheet
                chart_ws = workbook.add_chartsheet('Chart')
                chart_ws.set_chart(chart)

            # Write Credits & Disclaimer sheet
            credits_ws = workbook.add_worksheet('Credits & Disclaimer')
            retrieval_date = datetime.now().strftime('%Y-%m-%d %H:%M')
            credits_text = [
                'Data retrieved with the QGIS plugin "BRO Grondwater"',
                f'Date of retrieval: {retrieval_date}',
                '',
                'Developed by: CWG Ingenieurs b.v. (https://www.cwgi.nl)',
                'Powered by the Python packages Hydropandas and Brodata',
                'Data source: BRO (Basisregistratie Ondergrond)',
                '',
                'DISCLAIMER',
                'This software is provided "as is", without warranty of any kind, express or implied,',
                'including but not limited to the warranties of merchantability, fitness for a particular',
                'purpose and noninfringement. In no event shall the authors or copyright holders be liable',
                'for any claim, damages or other liability, whether in an action of contract, tort or otherwise,',
                'arising from, out of or in connection with the software or the use or other dealings in the software.',
            ]
            for row, text in enumerate(credits_text):
                credits_ws.write(row, 0, text)
            credits_ws.set_column(0, 0, 80)

            # Close the workbook
            workbook.close()

            self.dlg.progressBar.setValue(100)
            self.dlg.statusLabel.setText(f"Exported {exported_count} wells to {os.path.basename(file_path)}")
            QMessageBox.information(
                self.dlg,
                "Success",
                f"Data successfully exported to:\n{file_path}\n\n"
                f"Exported measurements for {exported_count} wells."
            )

            # Open the Excel file
            try:
                import subprocess
                if sys.platform == 'win32':
                    os.startfile(file_path)
                elif sys.platform == 'darwin':  # macOS
                    subprocess.run(['open', file_path])
                else:  # Linux
                    subprocess.run(['xdg-open', file_path])
            except Exception as open_error:
                # Don't fail if we can't open the file
                print(f"Could not open file: {open_error}")

        except ImportError:
            QMessageBox.critical(
                self.dlg,
                "Import Error",
                "xlsxwriter is required for Excel export. Please install it using:\n"
                "pip install xlsxwriter"
            )
        except Exception as e:
            QMessageBox.critical(
                self.dlg,
                "Export Error",
                f"Error exporting to Excel:\n{str(e)}"
            )
        finally:
            self._end_operation()
