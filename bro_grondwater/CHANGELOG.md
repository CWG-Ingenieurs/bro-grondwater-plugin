# Changelog

All notable changes to the BRO Grondwater Plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Additional filter options (multiple depth ranges, quality flags)
- Custom map styling options
- CSV export format
- Batch export functionality
- Advanced plotting options (multiple y-axes, custom date ranges)
- Integration with other BRO datasets

## [0.1] - 2024-12-18

### Added
- Initial release
- Extent-based well retrieval using Hydropandas (with brodata engine if available)
- Automatic layer creation with RD coordinates (EPSG:28992)
- Depth filtering by top_filter attribute
- Interactive plot visualization using matplotlib
- Excel export with multiple sheets (metadata and measurements)
- QMD styling support for graduated symbols
- Progress bar and status updates
- Credits to Artesia/Hydropandas
- Built-in disclaimer
- CWG Ingenieurs branding

### Features
- Retrieve BRO groundwater monitoring wells for current map extent
- Apply depth filters (min/max)
- Select wells using QGIS selection tools
- Plot measurements for selected wells
- Export data to Excel format
- Automatic coordinate transformation from WGS84 to RD

### Technical
- Compatible with QGIS 3.0+
- Uses Hydropandas with brodata engine fallback (tries faster engine first)
- Memory-based vector layer
- Support for multiple well selection
- Error handling and user feedback

## Version History

### Version Naming Convention
- **Major** (X.0.0): Significant changes, breaking changes
- **Minor** (1.X.0): New features, backwards compatible
- **Patch** (1.0.X): Bug fixes, minor improvements

---

## Future Versions (Tentative)

### [1.1.0] - Planned
- Additional export formats (CSV, GeoJSON)
- Custom date range selection for measurements
- Filter by quality flags
- Multi-extent retrieval
- Save/load filter presets

### [1.2.0] - Planned
- Integration with other BRO data types
- Advanced plotting (comparison plots, statistics)
- Batch processing capabilities
- Report generation

### [2.0.0] - Planned
- Complete UI redesign
- Database connection support
- Custom analysis tools
- API for external integrations

---

For detailed information about each version, see the commit history and release notes on GitHub.
