"""
SeaSenseLib Writers Module with Autodiscovery

This module provides various writer classes for exporting CTD sensor data
from xarray Datasets to different file formats. It uses an autodiscovery
mechanism to automatically find and register all available writer classes.

Available Writers:
-----------------
All writer classes are automatically discovered from the writers directory.
Common writers include:
- NetCdfWriter: Export to NetCDF format
- CsvWriter: Export to CSV format  
- ExcelWriter: Export to Excel format

Example Usage:
--------------
from seasenselib.writers import NetCdfWriter, CsvWriter, ExcelWriter

# Write to NetCDF
writer = NetCdfWriter(data)
writer.write("output.nc")

# Write to CSV
csv_writer = CsvWriter(data)
csv_writer.write("output.csv")

# Write to Excel
excel_writer = ExcelWriter(data) 
excel_writer.write("output.xlsx")
"""

# Import the base class
from .base import AbstractWriter

# Import autodiscovery functionality (lazy to avoid circular imports)
def _get_writer_discovery():
    """Get writer discovery instance lazily."""
    from ..core.autodiscovery import WriterDiscovery
    return WriterDiscovery()

# Discover all available writer classes
_all_writers = {}
_discovery_done = False

def _ensure_writers_discovered():
    """Ensure writers are discovered and loaded into module namespace."""
    global _all_writers, _discovery_done
    if not _discovery_done:
        discovery = _get_writer_discovery()
        _all_writers = discovery.discover_classes()

        # Import all discovered writer classes into this module's namespace
        for class_name, class_obj in _all_writers.items():
            globals()[class_name] = class_obj

        _discovery_done = True

# Trigger discovery on import
_ensure_writers_discovered()

# Build __all__ list
__all__ = ['AbstractWriter'] + list(_all_writers.keys())

# Utility functions for compatibility
def get_writer_by_extension(extension: str):
    """Get writer class by file extension."""
    discovery = _get_writer_discovery()
    return discovery.get_writer_by_extension(extension)

def get_supported_extensions():
    """Get all supported file extensions."""
    discovery = _get_writer_discovery()
    return discovery.get_supported_extensions()

def get_all_writer_classes():
    """Get list of all writer class names."""
    discovery = _get_writer_discovery()
    return discovery.get_all_class_names()
