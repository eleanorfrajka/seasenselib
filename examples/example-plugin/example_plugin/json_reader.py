"""
Example JSON Reader Plugin for SeaSenseLib.

This reader demonstrates how to create a custom reader plugin that extends
SeaSenseLib with support for reading oceanographic data from JSON files.
"""

import json
from pathlib import Path
from datetime import datetime
import xarray as xr
import numpy as np
import pandas as pd
from seasenselib.readers.base import AbstractReader


class JsonReader(AbstractReader):
    """
    Reader for oceanographic data in JSON format.
    
    This is an example plugin that reads a simple JSON structure:
    
    {
        "time": ["2024-01-01T00:00:00", ...],
        "temperature": [15.2, 15.4, ...],
        "salinity": [35.1, 35.2, ...],
        "metadata": {
            "instrument": "...",
            "location": "..."
        }
    }
    """

    def __init__(self, input_file: str):
        """
        Initialize the JSON reader.
        
        Parameters:
        -----------
        input_file : str
            Path to the JSON data file
        """
        self.input_file = Path(input_file)
        self._data = None
        self._validate_file()

    def _validate_file(self):
        """Validate that the input file exists and is readable."""
        if not self.input_file.exists():
            raise FileNotFoundError(f"File not found: {self.input_file}")

        if not self.input_file.is_file():
            raise ValueError(f"Not a file: {self.input_file}")

        if self.input_file.suffix.lower() != '.json':
            raise ValueError(f"Expected .json file, got: {self.input_file.suffix}")

    @staticmethod
    def format_key() -> str:
        """Return the unique format identifier."""
        return "example-json"

    @staticmethod
    def format_name() -> str:
        """Return the human-readable format name."""
        return "Example JSON Format"

    @staticmethod
    def file_extension() -> str:
        """Return the file extension for this format."""
        return ".json"

    def get_data(self) -> xr.Dataset:
        """
        Read JSON data and return as xarray Dataset.
        
        Returns:
        --------
        xr.Dataset
            Dataset containing the oceanographic data
            
        Raises:
        -------
        ValueError
            If the JSON structure is invalid
        """
        if self._data is None:
            self._data = self._read_json_file()
        return self._data

    def _read_json_file(self) -> xr.Dataset:
        """
        Internal method to read and parse JSON file.
        
        Returns:
        --------
        xr.Dataset
            Parsed dataset with oceanographic data
        """
        # Read JSON file
        with open(self.input_file, 'r') as f:
            data = json.load(f)

        # Validate structure
        if not isinstance(data, dict):
            raise ValueError("JSON root must be an object")

        # Extract time coordinate
        if 'time' not in data:
            raise ValueError("JSON must contain 'time' field")

        times = pd.to_datetime(data['time'])

        # Extract data variables
        data_vars = {}
        metadata = data.pop('metadata', {})

        for key, values in data.items():
            if key == 'time':
                continue

            if not isinstance(values, list):
                continue

            # Convert to numpy array
            arr = np.array(values)

            # Create DataArray
            data_vars[key] = xr.DataArray(
                arr,
                coords={'time': times},
                dims=['time'],
                attrs=self._get_variable_attrs(key)
            )

        # Create Dataset
        ds = xr.Dataset(data_vars)

        # Add global attributes
        ds.attrs['source_file'] = str(self.input_file)
        ds.attrs['reader'] = self.format_name()
        ds.attrs['reader_version'] = '0.1.0'
        ds.attrs['date_created'] = datetime.now().isoformat()

        # Add metadata from JSON
        for key, value in metadata.items():
            ds.attrs[key] = value

        # Add time coordinate attributes
        ds['time'].attrs['standard_name'] = 'time'
        ds['time'].attrs['long_name'] = 'Time'
        ds['time'].attrs['axis'] = 'T'

        return ds

    def _get_variable_attrs(self, var_name: str) -> dict:
        """
        Get standard attributes for a variable.
        
        Parameters:
        -----------
        var_name : str
            Variable name
            
        Returns:
        --------
        dict
            Attributes dictionary
        """
        # Standard oceanographic variable attributes
        attrs_map = {
            'temperature': {
                'long_name': 'Sea Water Temperature',
                'standard_name': 'sea_water_temperature',
                'units': 'degree_Celsius',
            },
            'salinity': {
                'long_name': 'Sea Water Practical Salinity',
                'standard_name': 'sea_water_practical_salinity',
                'units': 'PSU',
            },
            'pressure': {
                'long_name': 'Sea Water Pressure',
                'standard_name': 'sea_water_pressure',
                'units': 'dbar',
            },
            'depth': {
                'long_name': 'Depth',
                'standard_name': 'depth',
                'units': 'm',
                'positive': 'down',
            },
        }

        return attrs_map.get(var_name, {
            'long_name': var_name.replace('_', ' ').title(),
        })
