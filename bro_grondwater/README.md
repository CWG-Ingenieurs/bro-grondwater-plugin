# BRO Grondwater Plugin

A QGIS plugin for retrieving and analyzing BRO (Basisregistratie Ondergrond) groundwater monitoring well data using Hydropandas.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![QGIS](https://img.shields.io/badge/QGIS-%3E%3D3.0-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## Features

- **Retrieve Wells**: Automatically retrieve BRO groundwater monitoring well locations for the current map extent
- **Fast Data Access**: Uses Hydropandas library for efficient BRO data retrieval
- **Depth Filtering**: Filter wells based on filter depth (top_filter)
- **Data Visualization**: Plot groundwater measurements for selected wells
- **Excel Export**: Export well metadata and measurements to Excel format
- **QMD Styling**: Automatic styling of well locations on the map

## Installation

### Prerequisites

- QGIS 3.0 or higher
- Python 3.7 or higher (usually comes with QGIS)

### Install Plugin

1. Download the plugin repository
2. Copy the `bro_grondwater` folder to your QGIS plugins directory:
   - **Windows**: `C:\Users\<YourUsername>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins`
   - **macOS**: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins`
   - **Linux**: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins`

3. Install Python dependencies in QGIS Python environment:

```bash
# Open OSGeo4W Shell (Windows) or QGIS Python Console

# Install all dependencies
pip install hydropandas pandas xlsxwriter matplotlib
```

4. Restart QGIS
5. Enable the plugin: `Plugins` → `Manage and Install Plugins` → `Installed` → Check `BRO Grondwater Plugin`

## Usage

### 1. Retrieve Wells

1. Open the plugin from `Plugins` → `BRO Grondwater Plugin` or click the toolbar icon
2. Zoom to your area of interest in QGIS
3. Click **"Retrieve Wells from Current Extent"**
4. The plugin will retrieve all BRO groundwater monitoring wells within the visible extent
5. Wells will be added as a new layer to your map

### 2. Filter by Depth

1. After retrieving wells, set your desired depth range:
   - **Min Depth**: Minimum filter depth in meters
   - **Max Depth**: Maximum filter depth in meters
2. Click **"Apply Filter"**
3. The layer will show only wells matching your depth criteria

### 3. Analyze Selected Wells

#### Plot Measurements
1. Use QGIS selection tools to select one or more wells
2. Click **"Plot Measurements"**
3. A plot window will open showing groundwater level time series for selected wells

#### Export to Excel
1. Select wells using QGIS selection tools
2. Click **"Export to Excel"**
3. Choose save location
4. Excel file will contain:
   - **Metadata sheet**: Well information (coordinates, depths, etc.)
   - **Individual sheets**: Time series data for each well
   - **Credits & Disclaimer sheet**: Attribution and legal information

## QMD Styling

To customize the appearance of wells on the map:

1. Create a QGIS style file (`.qmd`)
2. Save it as `styles/wells_style.qmd` in the plugin directory
3. The style will be automatically applied when retrieving wells

Example style features:
- Graduated symbols based on depth
- Color coding by tube number
- Label wells with BRO ID

## Technical Details

### Data Source
- **BRO (Basisregistratie Ondergrond)**: Dutch national subsurface registry
- **API Access**: Via Hydropandas library

### Coordinate Systems
- Input: Current QGIS map CRS (automatically transformed)
- BRO Data: WGS84 (EPSG:4326)
- Output Layer: RD New (EPSG:28992)

### Performance
- Typical retrieval time: 10-30 seconds depending on extent and number of wells
- Progress bar shows retrieval status

## Troubleshooting

### "Hydropandas is not installed"
Install hydropandas:
```bash
pip install hydropandas
```

### "No monitoring wells found"
- Check if your extent covers the Netherlands
- Ensure you have internet connectivity
- Try a larger extent

### "Error retrieving data from BRO"
- Check BRO service status
- Ensure internet connection is working

### Import Errors
Install missing packages in QGIS Python environment:
```bash
pip install hydropandas pandas xlsxwriter matplotlib
```

## Credits

- **Developed by**: CWG Ingenieurs b.v.
- **Powered by**: [Hydropandas](https://github.com/ArtesiaWater/hydropandas) (Artesia)
- **Data Source**: [BRO](https://www.broloket.nl/) (Basisregistratie Ondergrond)

## Disclaimer

This software is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the software.

## License

MIT License - See LICENSE file for details

## Contributing

This is a private repository. For bug reports or feature requests, please contact CWG Ingenieurs b.v.

## Version History

### 0.1 (2024)
- Initial release
- Extent-based well retrieval
- Depth filtering
- Measurement plotting
- Excel export
- QMD styling support

## Contact

**CWG Ingenieurs b.v.**
- Website: [www.cwgi.nl](https://www.cwgi.nl)
- Email: info@cwgi.nl

## Links

- [QGIS](https://qgis.org/)
- [Hydropandas](https://github.com/ArtesiaWater/hydropandas)
- [BRO Loket](https://www.broloket.nl/)
- [BRO Documentation](https://basisregistratieondergrond.nl/)
