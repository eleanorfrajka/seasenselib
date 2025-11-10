# Example SeaSenseLib Plugin

This is a working example of a SeaSenseLib plugin that demonstrates how to extend SeaSenseLib with custom readers and writers.

## What This Plugin Provides

- **JsonReader**: Reads oceanographic data from JSON files
- **JsonWriter**: Writes xarray Datasets to JSON format
- **HistogramPlotter**: Creates histogram plots showing parameter distributions

## Installation

From this directory:

```bash
pip install -e .
```

Or if published:

```bash
pip install seasenselib-example-plugin
```

## Usage

Once installed, the plugin formats are automatically available:

### Command Line

```bash
# List all formats (including plugin formats)
seasenselib formats

# Convert using the plugin reader
seasenselib convert data.json output.nc

# Convert using the plugin writer
seasenselib convert input.cnv output.json --output-format example-json
```

### Python API

```python
from seasenselib.api import convert_file
from seasenselib import read
from seasenselib.plotters import HistogramPlotter

# Use plugin reader (detected by .json extension)
convert_file('data.json', 'output.nc')

# Use plugin writer
convert_file('input.cnv', 'output.json', output_format='example-json')

# Use plugin plotter
ds = read('data.json')
plotter = HistogramPlotter(ds)
plotter.plot(parameter='temperature', bins=20, output_file='histogram.png')
```

## Testing the Plugin

**Quick test with the demo script:**

```bash
python demo_all_plugins.py
```

This will demonstrate all three plugin types (reader, writer, plotter) in action.

**Or test manually:**

Create a test JSON file:

```json
{
    "time": ["2024-01-01T00:00:00", "2024-01-01T01:00:00"],
    "temperature": [15.2, 15.4],
    "salinity": [35.1, 35.2],
    "metadata": {
        "instrument": "Example Sensor",
        "location": "Test Site"
    }
}
```

Then convert it:

```bash
seasenselib convert test.json output.nc
```

## Plugin Architecture

This plugin demonstrates:

1. **Entry point registration** in `pyproject.toml`
2. **AbstractReader implementation** in `json_reader.py`
3. **AbstractWriter implementation** in `json_writer.py`
4. **AbstractPlotter implementation** in `histogram_plotter.py`
5. **Format metadata** via `format_key()` and `format_name()` methods
6. **Automatic discovery** - no manual registration needed

## Development

To modify this plugin:

1. Edit the reader/writer classes
2. Reinstall: `pip install -e .`
3. Test: `seasenselib formats` should show your changes

## Files

- `pyproject.toml` - Plugin configuration and entry points
- `example_plugin/` - Plugin package
  - `__init__.py` - Package initialization
  - `json_reader.py` - JSON reader implementation
  - `json_writer.py` - JSON writer implementation
  - `histogram_plotter.py` - Histogram plotter implementation
- `README.md` - This file

## License

Same as SeaSenseLib (AGPL-3.0)
