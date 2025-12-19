# Contributing to BRO Grondwater Tools

Thank you for your interest in contributing to BRO Grondwater Tools!

## Development Status

This is currently a private repository maintained by CWG Ingenieurs. We may open it for public contributions in the future.

## Reporting Issues

If you encounter bugs or have feature requests:

1. Check if the issue already exists in the Issues section
2. Create a new issue with:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - QGIS version and operating system
   - Error messages or screenshots

## Development Setup

### Prerequisites

- QGIS 3.x installed
- Python 3.7+
- Git

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/CWG-Ingenieurs/bro-groundwater-tools.git
cd bro-groundwater-tools
```

2. Create symbolic link to QGIS plugins directory:
```bash
# Windows (as Administrator)
mklink /D "C:\Users\<YourUsername>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\bro_groundwater_tools" "path\to\cloned\repo"

# macOS/Linux
ln -s /path/to/cloned/repo ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/bro_groundwater_tools
```

3. Install development dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available
```

4. Reload plugin in QGIS:
   - Use Plugin Reloader plugin for development
   - Or restart QGIS after each change

### Code Style

- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions focused and concise

### Testing

Before submitting changes:

1. Test with different QGIS versions (if possible)
2. Test on different operating systems
3. Verify all features work:
   - Well retrieval
   - Filtering
   - Plotting
   - Excel export
4. Check for Python errors in QGIS Message Log

## Pull Request Process

1. Fork the repository (when public)
2. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes
4. Test thoroughly
5. Commit with clear messages:
   ```bash
   git commit -m "Add: description of your changes"
   ```
6. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
7. Create a Pull Request with:
   - Description of changes
   - Why the changes are needed
   - Testing performed

## Code Review

All contributions will be reviewed by CWG Ingenieurs before merging.

## Areas for Contribution

Potential areas where contributions would be valuable:

- **Bug Fixes**: Fix reported issues
- **Performance**: Optimize data retrieval and processing
- **Features**: 
  - Additional filters
  - More export formats
  - Advanced plotting options
  - Batch processing
- **Documentation**: Improve README, add tutorials
- **Internationalization**: Add translations
- **Testing**: Unit tests, integration tests

## Questions?

Contact: info@cwg-ingenieurs.nl

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
