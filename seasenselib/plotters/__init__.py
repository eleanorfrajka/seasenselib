"""
SeaSenseLib Plotters Module with Autodiscovery

This module provides various plotter classes for visualizing CTD sensor data
from xarray Datasets using matplotlib. It uses an autodiscovery mechanism
to automatically find and register all available plotter classes.

Available Plotters:
------------------
All plotter classes are automatically discovered from the plotters directory.
Common plotters include:
- TsDiagramPlotter: Create T-S (Temperature-Salinity) diagrams with density isolines
- DepthProfilePlotter: Create CTD depth profiles for temperature and salinity
- TimeSeriesPlotter: Create time series plots for single or multiple parameters

Example Usage:
--------------
from seasenselib.plotters import TsDiagramPlotter, DepthProfilePlotter, TimeSeriesPlotter

# Create a T-S diagram
ts_plotter = TsDiagramPlotter(data)
ts_plotter.plot(title="Station 001 T-S Diagram", output_file="ts_diagram.png")

# Create a vertical profile  
profile_plotter = DepthProfilePlotter(data)
profile_plotter.plot(title="CTD Profile", output_file="profile.png")

# Create a time series plot (single or multiple parameters)
time_plotter = TimeSeriesPlotter(data)
time_plotter.plot(parameter_names=['temperature'], output_file="temp_series.png")
time_plotter.plot(parameter_names=['temperature', 'salinity'], dual_axis=True, output_file="multi_series.png")
"""

# Import the base class
from .base import AbstractPlotter

# Import autodiscovery functionality (lazy to avoid circular imports)
def _get_plotter_discovery():
    """Get plotter discovery instance lazily."""
    from ..core.autodiscovery import PlotterDiscovery
    return PlotterDiscovery()

# Discover all available plotter classes
_all_plotters = {}
_discovery_done = False

def _ensure_plotters_discovered():
    """Ensure plotters are discovered and loaded into module namespace."""
    global _all_plotters, _discovery_done
    if not _discovery_done:
        discovery = _get_plotter_discovery()
        _all_plotters = discovery.discover_classes()
        
        # Import all discovered plotter classes into this module's namespace
        for class_name, class_obj in _all_plotters.items():
            globals()[class_name] = class_obj
        
        _discovery_done = True

# Trigger discovery on import
_ensure_plotters_discovered()

# Build __all__ list
__all__ = ['AbstractPlotter'] + list(_all_plotters.keys())

# Utility functions
def get_all_plotter_classes():
    """Get list of all plotter class names."""
    discovery = _get_plotter_discovery()
    return discovery.get_all_class_names()