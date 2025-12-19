# Plugin Architecture

Technical documentation for developers working on BRO Grondwater Tools.

## Directory Structure

```
bro_groundwater_tools/
├── __init__.py                          # Plugin entry point
├── bro_groundwater_tools.py             # Main plugin class
├── bro_groundwater_tools_dialog.py      # Dialog wrapper
├── bro_groundwater_tools_dialog_base.ui # Qt Designer UI file
├── metadata.txt                         # Plugin metadata
├── icon.png                             # Plugin icon
├── resources.qrc                        # Qt resources file
├── requirements.txt                     # Python dependencies
├── README.md                            # User documentation
├── INSTALL.md                           # Installation guide
├── QUICKSTART.md                        # Quick start guide
├── CHANGELOG.md                         # Version history
├── CONTRIBUTING.md                      # Contribution guidelines
├── LICENSE                              # MIT license
├── .gitignore                           # Git ignore patterns
├── compile.sh / compile.bat             # Build scripts
├── styles/
│   └── wells_style.qmd                  # Default map styling
└── .github/
    └── ISSUE_TEMPLATE/
        ├── bug_report.md                # Bug report template
        └── feature_request.md           # Feature request template
```

## Component Overview

### 1. Entry Point (`__init__.py`)

```python
def classFactory(iface):
    from .bro_groundwater_tools import BROGroundwaterTools
    return BROGroundwaterTools(iface)
```

- Called by QGIS when plugin is loaded
- Returns plugin instance
- Receives QGIS interface object

### 2. Main Plugin Class (`bro_groundwater_tools.py`)

**Purpose**: Core plugin logic and QGIS integration

**Key Methods**:
- `__init__(iface)`: Initialize plugin
- `initGui()`: Create menu items and toolbar
- `unload()`: Cleanup when plugin disabled
- `run()`: Main entry point when plugin activated
- `retrieve_wells()`: BRO data retrieval
- `apply_filter()`: Depth filtering
- `plot_measurements()`: Data visualization
- `export_to_excel()`: Data export

**Dependencies**:
- `qgis.core`: Vector layers, features, geometry
- `qgis.PyQt`: Qt widgets and UI
- `hydropandas`: BRO data access
- `matplotlib`: Plotting
- `pandas`, `openpyxl`: Excel export

### 3. Dialog Class (`bro_groundwater_tools_dialog.py`)

**Purpose**: Manage plugin dialog window

**Responsibilities**:
- Load UI file
- Initialize dialog components
- Handle window events

**Pattern**: Loads UI dynamically using `uic.loadUiType()`

### 4. UI File (`bro_groundwater_tools_dialog_base.ui`)

**Purpose**: Define user interface layout

**Components**:
- Logo/branding section
- Well retrieval controls
- Depth filter inputs
- Analysis buttons
- Progress bar
- Status label
- Credits footer

**Created With**: Qt Designer (XML format)

## Data Flow

### 1. Well Retrieval Flow

```
User clicks "Retrieve Wells"
    ↓
Get current map extent
    ↓
Transform extent to WGS84
    ↓
Call hydropandas.GroundwaterObs.from_bro()
    ↓
Process observation collection
    ↓
Create QgsVectorLayer with features
    ↓
Apply QMD styling (if available)
    ↓
Add layer to QGIS project
    ↓
Store obs_collection for later use
```

### 2. Filtering Flow

```
User sets depth range
    ↓
User clicks "Apply Filter"
    ↓
Build filter expression
    ↓
Apply layer.setSubsetString()
    ↓
Layer updates display
    ↓
Show filtered count
```

### 3. Export Flow

```
User selects wells
    ↓
User clicks "Export to Excel"
    ↓
Get file path from dialog
    ↓
Create ExcelWriter
    ↓
Write metadata sheet
    ↓
For each selected well:
    - Find in obs_collection
    - Write measurements sheet
    ↓
Add credits sheet
    ↓
Save and close file
```

## Key Design Patterns

### Singleton Dialog
Dialog is created once and reused:
```python
if self.dlg is None:
    self.dlg = BROGroundwaterToolsDialog()
```

### Signal-Slot Pattern
Qt signals connect UI to logic:
```python
self.dlg.btnRetrieveWells.clicked.connect(self.retrieve_wells)
```

### Memory Layer Pattern
Vector layer stored in memory:
```python
layer = QgsVectorLayer('Point?crs=EPSG:28992', 'BRO Monitoring Wells', 'memory')
```

### Error Handling Pattern
Try-catch with user feedback:
```python
try:
    # Operation
except Exception as e:
    QMessageBox.critical(self.dlg, "Error", str(e))
```

## API Integration

### Hydropandas Integration

```python
# Use brodata engine for performance
obs_collection = hpd.GroundwaterObs.from_bro(
    extent=extent_tuple,  # (xmin, ymin, xmax, ymax) in WGS84
    tmin=None,            # All dates
    tmax=None,
    engine='brodata'      # Fast engine
)
```

**Key Classes**:
- `GroundwaterObs`: Individual observation/well
- `ObsCollection`: Collection of observations

**Attributes**:
- `obs.name`: Well name
- `obs.x`, `obs.y`: Coordinates
- `obs.metadata`: Dictionary with well info
- `obs` (data): Pandas DataFrame with measurements

### QGIS API Integration

**Layer Management**:
```python
# Create layer
layer = QgsVectorLayer('Point?crs=EPSG:28992', name, 'memory')

# Add fields
provider = layer.dataProvider()
provider.addAttributes([QgsField('name', QVariant.String)])
layer.updateFields()

# Add features
features = [...]
provider.addFeatures(features)

# Add to project
QgsProject.instance().addMapLayer(layer)
```

**Coordinate Transformation**:
```python
transform = QgsCoordinateTransform(
    source_crs,
    dest_crs,
    QgsProject.instance()
)
transformed_extent = transform.transformBoundingBox(extent)
```

## Threading & Performance

### Current Implementation
- Synchronous operations
- UI blocks during retrieval
- Progress bar for user feedback

### Future Improvements
- QThread for long operations
- Async data retrieval
- Caching of retrieved data
- Background extent monitoring

## Testing Strategy

### Manual Testing Checklist
- [ ] Well retrieval in different extents
- [ ] Coordinate transformation accuracy
- [ ] Filter with various depth ranges
- [ ] Multiple well selection
- [ ] Plot with 1, 5, 10+ wells
- [ ] Excel export with various selections
- [ ] Error handling (no connection, no data, etc.)

### Unit Testing (Future)
```python
def test_extent_transformation():
    # Test coordinate transformation
    pass

def test_filter_expression():
    # Test filter string generation
    pass

def test_feature_creation():
    # Test QGIS feature creation
    pass
```

## Configuration & Settings

### Plugin Settings
Currently hardcoded. Future: QSettings storage
```python
# Future implementation
settings = QSettings()
settings.setValue('BROTools/default_min_depth', 0)
settings.setValue('BROTools/default_max_depth', 100)
```

### Styling
QMD file location: `styles/wells_style.qmd`

Edit with QGIS:
1. Style layer manually
2. Save style to file
3. Copy to plugin `styles/` directory

## Error Handling

### Import Errors
```python
try:
    import hydropandas as hpd
except ImportError:
    QMessageBox.critical("Hydropandas not installed...")
    return
```

### Data Errors
```python
if len(obs_collection) == 0:
    QMessageBox.information("No data found...")
    return
```

### Network Errors
Handled by hydropandas library, propagated to user via try-except

## Logging & Debugging

### QGIS Message Log
```python
from qgis.core import QgsMessageLog, Qgis

QgsMessageLog.logMessage(
    'Debug info',
    'BRO Tools',
    Qgis.Info
)
```

### Python Console
Access via: `Plugins` → `Python Console`

Test code:
```python
from bro_groundwater_tools import BROGroundwaterTools
plugin = iface.plugins['bro_groundwater_tools']
# Test methods
```

## Dependencies

### Required
- **QGIS**: 3.0+
- **Python**: 3.7+
- **hydropandas**: DEV version with brodata
- **pandas**: Data structures
- **matplotlib**: Plotting
- **openpyxl**: Excel writing

### Optional
- **pyrcc5**: Resource compilation
- **pyuic5**: UI compilation

## Internationalization (i18n)

### Current Status
English only

### Future Implementation
1. Extract translatable strings
2. Create .ts files
3. Translate
4. Compile to .qm files
5. Load based on locale

## Performance Optimization

### Current Bottlenecks
1. BRO data retrieval (network)
2. Large number of wells (rendering)
3. Multiple well plotting

### Optimization Strategies
1. **Caching**: Store retrieved data
2. **Pagination**: Limit results
3. **Lazy loading**: Load measurements on-demand
4. **Spatial indexing**: For large datasets
5. **Async operations**: Non-blocking UI

## Security Considerations

### Data Privacy
- No user data collected
- No analytics or tracking
- Data retrieved from public BRO

### API Security
- Uses HTTPS for BRO access
- No API keys required (public data)

## Deployment

### Manual Deployment
1. Copy folder to plugins directory
2. Restart QGIS

### Plugin Repository (Future)
1. Create plugin ZIP
2. Upload to QGIS Plugin Repository
3. Users install via Plugin Manager

## Maintenance

### Version Updates
1. Update `metadata.txt` version
2. Update `CHANGELOG.md`
3. Tag release in Git
4. Create GitHub release

### Dependency Updates
Monitor and update:
- Hydropandas releases
- QGIS API changes
- Python package updates

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - See [LICENSE](LICENSE) file.

---

**For questions or technical support:**
Contact: info@cwg-ingenieurs.nl
