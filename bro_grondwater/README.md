# BRO Grondwater Plugin

A QGIS plugin for retrieving and analyzing BRO (Basisregistratie Ondergrond) groundwater monitoring well data using Hydropandas.

![Version](https://img.shields.io/badge/version-0.2.5-blue)
![QGIS](https://img.shields.io/badge/QGIS-4.x-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## Features

- **Retrieve Wells**: Automatically retrieve BRO groundwater monitoring well locations for the current map extent
- **Fast Data Access**: Uses Hydropandas library for efficient BRO data retrieval
- **Depth Filtering**: Filter wells on the top of the filter screen (bovenkant filter, `screen_top`), in m NAP
- **Data Visualization**: Plot groundwater measurements for selected wells
- **Excel Export**: Export well metadata and measurements to Excel format
- **QMD Styling**: Automatic styling of well locations on the map

## Installation

### Prerequisites

- QGIS 4.x (the plugin requires QGIS 4.0 or higher; QGIS 3 is not supported)
- The Python environment that comes with QGIS
- An internet connection: data is retrieved from the BRO and PDOK

### Python dependencies

The plugin installs these packages into the QGIS Python environment automatically
when it loads. Packages that are already installed but older than the minimum
version are upgraded:

| Package | Minimum version | Used for |
|---|---|---|
| hydropandas | | Retrieving BRO wells and measurements |
| brodata | | Fast BRO retrieval (hydropandas `brodata` engine) |
| pandas | 1.3.0 | Data handling |
| xlsxwriter | 3.0.0 | Excel export |
| pyqtgraph | | Plots and the screen-top histogram |
| requests | 2.33.0 | HTTP requests to the BRO and PDOK |
| urllib3 | 2.8.0 | Used by requests |
| idna | 3.15 | Used by requests |
| certifi | 2024.7.4 | Used by requests |
| tqdm | 4.66.3 | Progress reporting in hydropandas |

The minimum versions of requests, urllib3, idna, certifi and tqdm avoid versions
with known vulnerabilities. Compiled packages that come with QGIS (such as numpy,
pillow and lxml) are not upgraded by the plugin; update those by updating QGIS.
The same list is in [requirements.txt](requirements.txt).

### Install Plugin

1. Download the plugin repository
2. Copy the `bro_grondwater` folder to your QGIS plugins directory:
   - **Windows**: `C:\Users\<YourUsername>\AppData\Roaming\QGIS\QGIS4\profiles\default\python\plugins`
   - **macOS**: `~/Library/Application Support/QGIS/QGIS4/profiles/default/python/plugins`
   - **Linux**: `~/.local/share/QGIS/QGIS4/profiles/default/python/plugins`
3. Restart QGIS
4. Enable the plugin: `Plugins` → `Manage and Install Plugins` → `Installed` → Check `BRO Grondwater`.
   The Python dependencies are installed automatically the first time the plugin
   loads; restart QGIS once more afterwards.

If the automatic installation fails (for example behind a proxy), install the
dependencies manually in the QGIS Python environment (OSGeo4W Shell on Windows),
from the plugin folder:

```bash
pip install -r requirements.txt
```

## Usage

### 1. Retrieve Wells

1. Open the plugin from `Plugins` → `BRO Grondwater Plugin` or click the toolbar icon
2. Zoom to your area of interest in QGIS
3. Click **"Retrieve Wells from Current Extent"**
4. The plugin will retrieve all BRO groundwater monitoring wells within the visible extent
5. Wells will be added as a new layer to your map

### 2. Filter by Top of Screen

1. After retrieving wells, set the range for the top of the filter screen
   (bovenkant filter, `screen_top`). The values are levels in m NAP, not depths
   below ground level; the bottom of the screen is not used:
   - **Min top**: lowest screen top to show (m NAP)
   - **Max top**: highest screen top to show (m NAP)
2. Click **"Apply"**
3. The layer will show only tubes whose screen top lies in this range

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
Restart QGIS so the plugin can install its dependencies. If that doesn't help,
install them manually (see [Python dependencies](#python-dependencies)):
```bash
pip install -r requirements.txt
```

### "No monitoring wells found"
- Check if your extent covers the Netherlands
- Ensure you have internet connectivity
- Try a larger extent

### "Error retrieving data from BRO"
- Check BRO service status
- Ensure internet connection is working

### Import Errors
Install missing packages in the QGIS Python environment (OSGeo4W Shell on Windows),
from the plugin folder:
```bash
pip install -r requirements.txt
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
