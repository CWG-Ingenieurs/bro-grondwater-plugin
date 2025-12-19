# Quick Start Guide

Get started with BRO Grondwater Plugin in 5 minutes!

## Prerequisites Checklist

Before you begin, make sure you have:
- [ ] QGIS 3.0 or higher installed
- [ ] Internet connection (for BRO data retrieval)
- [ ] Python dependencies installed (see below)

## 1. Install Dependencies (5 minutes)

### Quick Install Script

Open QGIS Python Console (`Plugins` → `Python Console`) and paste:

```python
import subprocess, sys

# Install all dependencies at once
packages = ['hydropandas', 'pandas', 'openpyxl', 'matplotlib']

for package in packages:
    print(f"Installing {package}...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

print("✓ All dependencies installed!")
```

## 2. Install Plugin (2 minutes)

1. Download the plugin ZIP from GitHub
2. Copy `bro_grondwater_plugin` folder to QGIS plugins directory
3. Restart QGIS
4. Enable in `Plugins` → `Manage and Install Plugins`

## 3. Your First Analysis (3 minutes)

### Step 1: Retrieve Wells
1. Open the plugin: `Plugins` → `BRO Grondwater Plugin`
2. Zoom to a location in the Netherlands (e.g., Utrecht)
3. Click **"Retrieve Wells from Current Extent"**
4. Wait 10-30 seconds for data retrieval

### Step 2: Filter Wells
1. In the "Filter by Depth" section:
   - Set **Min Depth**: 0 m
   - Set **Max Depth**: 20 m
2. Click **"Apply Filter"**
3. Only shallow wells will be visible

### Step 3: Analyze Data
1. Use QGIS selection tool (click wells on map)
2. Select 2-3 wells
3. Click **"Plot Measurements"**
4. View the time series plot

### Step 4: Export Data
1. With wells still selected, click **"Export to Excel"**
2. Choose save location
3. Open Excel file to see:
   - Metadata sheet with well information
   - Individual sheets with measurements
   - Credits & Disclaimer sheet

## Common Workflows

### Finding Deep Groundwater Wells

```
1. Zoom to province or region
2. Retrieve Wells
3. Set Min Depth: 50 m, Max Depth: 999 m
4. Apply Filter
5. Review results
```

### Comparing Multiple Wells

```
1. Retrieve Wells
2. Select 5-10 wells (use rectangle select)
3. Plot Measurements
4. Compare time series visually
5. Export to Excel for detailed analysis
```

### Creating a Report

```
1. Retrieve and filter wells
2. Take screenshot of map
3. Select key wells
4. Export to Excel
5. Add Excel data and screenshot to report
```

## Tips & Tricks

### Better Selection
- Use **Select Features by Polygon** for irregular areas
- Hold Shift to add to selection
- Hold Ctrl to remove from selection

### Performance
- Smaller extents = faster retrieval
- Filter before selecting for better overview
- Close plot windows when done

### Styling
- Customize `styles/wells_style.qmd` for your preferences
- Create multiple style files for different use cases
- Right-click layer → Properties → Symbology to modify on-the-fly

## Keyboard Shortcuts

While in QGIS:
- **Ctrl+E**: Open plugin (if set in QGIS keyboard shortcuts)
- **Spacebar**: Pan tool
- **Ctrl+Wheel**: Zoom in/out
- **Shift+Click**: Add to selection

## Next Steps

Now that you're familiar with the basics:

1. Read the full [README.md](README.md) for detailed features
2. Review [INSTALL.md](INSTALL.md) if you have installation issues
3. Customize the QMD style file for your workflow
4. Explore different regions and depth ranges

## Getting Help

- **Error messages**: Check QGIS Message Log (`View` → `Panels` → `Log Messages`)
- **Installation issues**: See [INSTALL.md](INSTALL.md)
- **Bug reports**: Create an issue on GitHub
- **Questions**: Contact info@cwgi.nl

## Example Use Cases

### Hydrogeologist
*"Find all monitoring wells in my project area with filters between 5-15m depth"*
1. Import project shapefile as background
2. Zoom to project boundary
3. Retrieve wells
4. Filter: Min=5, Max=15
5. Export for analysis

### Environmental Consultant
*"Get recent groundwater levels for impact assessment"*
1. Zoom to site location + buffer
2. Retrieve wells
3. Select wells near site
4. Plot to check data quality
5. Export to include in report

### Student
*"Understand groundwater level trends in Utrecht"*
1. Zoom to Utrecht province
2. Retrieve wells
3. Select diverse wells across region
4. Plot to observe patterns
5. Export for thesis data

## Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| "No wells found" | Check you're zoomed to Netherlands |
| Import errors | Re-run dependency installation |
| Slow retrieval | Zoom to smaller extent |
| Can't select wells | Check layer is active in Layers panel |
| Plot window blank | Check wells have data in selected period |
| Excel export fails | Verify openpyxl is installed |

---

**Ready to start?** Open QGIS and give it a try! 🚀
