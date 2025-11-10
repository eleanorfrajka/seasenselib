"""
SeaSenseLib Core Module

Core functionality including I/O operations, autodiscovery, factories, and utilities.
"""

from .io_manager import DataIOManager
from .autodiscovery import FormatDetector, ReaderDiscovery, WriterDiscovery, PlotterDiscovery
from .factories import ReaderFactory, WriterFactory
from .exceptions import SeaSenseLibError, FormatDetectionError, DependencyError, ValidationError

__all__ = [
    'DataIOManager', 
    'FormatDetector',
    'ReaderDiscovery',
    'WriterDiscovery',
    'PlotterDiscovery',
    'ReaderFactory',
    'WriterFactory',
    'SeaSenseLibError',
    'FormatDetectionError',
    'DependencyError',
    'ValidationError'
]
