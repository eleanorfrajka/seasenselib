"""
Autodiscovery module for readers, writers, and plotters.

This module provides functionality to automatically discover and register
reader, writer, and plotter classes without requiring manual registry maintenance.
It also includes format detection utilities.
"""

import importlib
import inspect
import os
import pkgutil
from pathlib import Path
from typing import Dict, List, Type, Set, Optional
from abc import ABC
from .exceptions import FormatDetectionError


def _convert_class_name_to_module_name(class_name: str) -> str:
    """Convert PascalCase class name to snake_case module name."""
    # Handle special cases first
    special_cases = {
        'NetCdfWriter': 'netcdf_writer',
        'NetCdfReader': 'netcdf_reader',
    }

    if class_name in special_cases:
        return special_cases[class_name]

    # Convert PascalCase to snake_case
    import re
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', class_name)
    name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
    return name


def _get_expected_module_name(class_name: str, base_class_name: str) -> str:
    """Get expected module name based on class name and type."""
    if base_class_name.lower() in class_name.lower():
        # If class name contains base class name, use conversion
        return _convert_class_name_to_module_name(class_name)
    else:
        # Fallback for unusual naming patterns
        return _convert_class_name_to_module_name(class_name)


class BaseDiscovery:
    """Base class for autodiscovery functionality."""

    def __init__(self, package_name: str, base_class: Type[ABC]):
        """
        Initialize the discovery system.
        
        Parameters:
        -----------
        package_name : str
            The full package name (e.g., 'seasenselib.readers')
        base_class : Type[ABC]
            The abstract base class that all discovered classes must inherit from
        """
        self.package_name = package_name
        self.base_class = base_class
        self._discovered_classes: Dict[str, Type] = {}
        self._class_modules: Dict[str, str] = {}

    def discover_classes(self) -> Dict[str, Type]:
        """
        Discover all classes that inherit from the base class.
        
        Returns:
        --------
        Dict[str, Type]
            Dictionary mapping class names to class objects
        """
        if self._discovered_classes:
            return self._discovered_classes

        try:
            # Import the package
            package = importlib.import_module(self.package_name)
            package_path = package.__path__

            # Walk through all modules in the package
            for _, modname, ispkg in pkgutil.iter_modules(package_path):
                if ispkg:
                    continue

                # Skip certain modules
                if modname in ['__init__', 'base', 'registry', 'api']:
                    continue

                full_module_name = f"{self.package_name}.{modname}"
                try:
                    # Import the module
                    module = importlib.import_module(full_module_name)

                    # Find all classes in the module that inherit from base class
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if (obj != self.base_class and 
                            issubclass(obj, self.base_class) and 
                            obj.__module__ == full_module_name):

                            self._discovered_classes[name] = obj
                            self._class_modules[name] = modname

                except ImportError as e:
                    # Log warning but continue discovery
                    print(f"Warning: Could not import {full_module_name}: {e}")
                    continue

        except ImportError as e:
            print(f"Error: Could not import package {self.package_name}: {e}")

        return self._discovered_classes

    def get_class_by_name(self, class_name: str) -> Optional[Type]:
        """Get a specific class by name."""
        classes = self.discover_classes()
        return classes.get(class_name)

    def get_all_class_names(self) -> List[str]:
        """Get list of all discovered class names."""
        classes = self.discover_classes()
        return list(classes.keys())

    def get_class_modules(self) -> Dict[str, str]:
        """Get mapping of class names to module names."""
        self.discover_classes()  # Ensure discovery is complete
        return self._class_modules.copy()


class ReaderDiscovery(BaseDiscovery):
    """Autodiscovery for reader classes."""

    def __init__(self):
        from ..readers.base import AbstractReader
        super().__init__('seasenselib.readers', AbstractReader)

    def get_reader_by_format_key(self, format_key: str) -> Optional[Type]:
        """
        Get reader class by format key.
        
        Parameters:
        -----------
        format_key : str
            The format key to search for
            
        Returns:
        --------
        Optional[Type]
            The reader class if found, None otherwise
        """
        classes = self.discover_classes()

        for _, class_obj in classes.items():
            try:
                # Check if class has format_key method and it matches
                if hasattr(class_obj, 'format_key'):
                    if class_obj.format_key() == format_key:
                        return class_obj
            except (AttributeError, TypeError):
                # Skip classes that don't implement format_key properly
                continue

        return None

    def get_readers_by_extension(self, extension: str) -> List[Type]:
        """
        Get reader classes that can handle a specific file extension.
        
        Parameters:
        -----------
        extension : str
            The file extension to search for
            
        Returns:
        --------
        List[Type]
            List of reader classes that can handle the extension
        """
        classes = self.discover_classes()
        matching_readers = []

        for _, class_obj in classes.items():
            try:
                # Check if class has file_extension method and it matches
                if hasattr(class_obj, 'file_extension'):
                    if class_obj.file_extension() == extension:
                        matching_readers.append(class_obj)
            except (AttributeError, TypeError):
                # Skip classes that don't implement file_extension properly
                continue

        return matching_readers

    def get_format_info(self) -> List[Dict[str, str]]:
        """
        Get format information for all discovered readers using their static methods.
        
        Returns:
        --------
        List[Dict[str, str]]
            List of format information dictionaries
        """
        classes = self.discover_classes()
        formats = []

        for class_name, class_obj in classes.items():
            try:
                # Use static methods to get format information
                if (hasattr(class_obj, 'format_key') and 
                    hasattr(class_obj, 'format_name')):

                    format_info = {
                        'class_name': class_name,
                        'format': class_obj.format_name(),
                        'key': class_obj.format_key(),
                    }

                    # Get file extension if available
                    if hasattr(class_obj, 'file_extension'):
                        ext = class_obj.file_extension()
                        if ext:
                            format_info['extension'] = ext

                    formats.append(format_info)
            except (AttributeError, TypeError, NotImplementedError):
                # Skip classes that don't implement required methods properly
                continue

        return formats


class WriterDiscovery(BaseDiscovery):
    """Autodiscovery for writer classes."""

    def __init__(self):
        from ..writers.base import AbstractWriter
        super().__init__('seasenselib.writers', AbstractWriter)

    def get_writer_by_extension(self, extension: str) -> Optional[Type]:
        """
        Get writer class by file extension.
        
        Parameters:
        -----------
        extension : str
            The file extension to search for
            
        Returns:
        --------
        Optional[Type]
            The writer class if found, None otherwise
        """
        classes = self.discover_classes()

        for _, class_obj in classes.items():
            try:
                # Check if class has file_extension method and it matches
                if hasattr(class_obj, 'file_extension'):
                    if class_obj.file_extension() == extension:
                        return class_obj
            except (AttributeError, TypeError):
                # Skip classes that don't implement file_extension properly
                continue

        return None

    def get_writer_by_format_key(self, format_key: str) -> Optional[Type]:
        """
        Get writer class by format key.
        
        Parameters:
        -----------
        format_key : str
            The format key to search for (e.g., 'netcdf', 'csv', 'excel')
            
        Returns:
        --------
        Optional[Type]
            The writer class if found, None otherwise
        """
        classes = self.discover_classes()

        for _, class_obj in classes.items():
            try:
                # Check if class has format_key method and it matches
                if hasattr(class_obj, 'format_key'):
                    if class_obj.format_key() == format_key:
                        return class_obj
            except (AttributeError, TypeError):
                # Skip classes that don't implement format_key properly
                continue

        return None

    def get_format_info(self) -> List[Dict[str, str]]:
        """
        Get format information for all discovered writers using their static methods.
        
        Returns:
        --------
        List[Dict[str, str]]
            List of format information dictionaries with keys:
            'class_name', 'format', 'key', 'extension'
        """
        classes = self.discover_classes()
        formats = []

        for class_name, class_obj in classes.items():
            try:
                # Use static methods to get format information
                if (hasattr(class_obj, 'format_key') and 
                    hasattr(class_obj, 'format_name')):

                    format_info = {
                        'class_name': class_name,
                        'format': class_obj.format_name(),
                        'key': class_obj.format_key(),
                    }

                    # Get file extension if available
                    if hasattr(class_obj, 'file_extension'):
                        ext = class_obj.file_extension()
                        if ext:
                            format_info['extension'] = ext

                    formats.append(format_info)
            except (AttributeError, TypeError, NotImplementedError):
                # Skip classes that don't implement required methods properly
                continue

        return formats

    def get_supported_extensions(self) -> Set[str]:
        """
        Get all supported file extensions.
        
        Returns:
        --------
        Set[str]
            Set of supported file extensions
        """
        classes = self.discover_classes()
        extensions = set()

        for _, class_obj in classes.items():
            try:
                if hasattr(class_obj, 'file_extension'):
                    ext = class_obj.file_extension()
                    if ext:
                        extensions.add(ext)
            except (AttributeError, TypeError):
                # Skip classes that don't implement file_extension properly
                continue
 
        return extensions


class PlotterDiscovery(BaseDiscovery):
    """Autodiscovery for plotter classes."""

    def __init__(self):
        from ..plotters.base import AbstractPlotter
        super().__init__('seasenselib.plotters', AbstractPlotter)


# Public format constants for CLI and other modules
def get_input_formats():
    """Get list of all supported input format keys."""
    discovery = ReaderDiscovery()
    format_info = discovery.get_format_info()
    return [info['key'] for info in format_info]


def get_output_formats():
    """Get list of all supported output format keys."""
    discovery = WriterDiscovery()
    format_info = discovery.get_format_info()
    return [info['key'] for info in format_info]


# Deprecated: kept for backward compatibility
OUTPUT_FORMATS = None  # Will be populated dynamically when accessed


class FormatDetector:
    """File format detection using autodiscovery."""

    @staticmethod
    def detect_format(input_file: str, format_hint: Optional[str] = None) -> str:
        """
        Detect file format without importing readers.
        
        Parameters:
        -----------
        input_file : str
            Path to the input file
        format_hint : str, optional
            Explicit format hint to override detection
            
        Returns:
        --------
        str
            The detected format key
            
        Raises:
        -------
        FormatDetectionError
            If format cannot be determined
        """
        if format_hint:
            input_formats = get_input_formats()
            if format_hint in input_formats:
                return format_hint
            else:
                raise FormatDetectionError(f"Unknown format hint: {format_hint}")

        # Check if file exists
        if not os.path.exists(input_file):
            raise FormatDetectionError(f"Input file does not exist: {input_file}")

        # Get file extension
        file_path = Path(input_file)
        extension = file_path.suffix.lower()

        # Map extension to format using autodiscovery
        discovery = ReaderDiscovery()
        format_info = discovery.get_format_info()

        for info in format_info:
            if info.get('extension') == extension:
                return info['key']

        # If no extension match, raise an error
        raise FormatDetectionError(
            f"Cannot determine format for file: {input_file}. "
            f"Extension '{extension}' not recognized and content detection failed."
        )

    @staticmethod
    def validate_output_format(output_file: str, format_hint: Optional[str] = None) -> str:
        """
        Validate and determine output format.
        
        Parameters:
        -----------
        output_file : str
            Path to the output file
        format_hint : str, optional
            Explicit format hint
            
        Returns:
        --------
        str
            The validated output format key
        """
        if format_hint:
            # Validate format hint against available writers
            available_formats = get_output_formats()
            if format_hint in available_formats:
                return format_hint
            else:
                raise FormatDetectionError(
                    f"Unknown output format: {format_hint}. "
                    f"Available formats: {', '.join(available_formats)}"
                )

        # Detect from file extension using WriterDiscovery
        file_path = Path(output_file)
        extension = file_path.suffix.lower()

        # Find writer by extension
        discovery = WriterDiscovery()
        writer_class = discovery.get_writer_by_extension(extension)

        if writer_class and hasattr(writer_class, 'format_key'):
            return writer_class.format_key()
        else:
            # List available extensions for better error message
            available_extensions = discovery.get_supported_extensions()
            raise FormatDetectionError(
                f"No writer found for extension: {extension}. "
                f"Supported extensions: {', '.join(sorted(available_extensions))}"
            )
