"""
Example JSON Writer Plugin for SeaSenseLib.

This writer demonstrates how to create a custom writer plugin that extends
SeaSenseLib with support for writing xarray Datasets to JSON format.
"""

import json
from pathlib import Path
import xarray as xr
import numpy as np
import pandas as pd
from seasenselib.writers.base import AbstractWriter


class JsonWriter(AbstractWriter):
    """
    Writer for oceanographic data to JSON format.
    
    This is an example plugin that writes xarray Datasets to a simple
    JSON structure that can be read back by the JsonReader plugin.
    """

    def __init__(self, data: xr.Dataset):
        """
        Initialize the JSON writer.
        
        Parameters:
        -----------
        data : xr.Dataset
            The xarray Dataset to write
        """
        self.data = data

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

    def write(self, output_file: str) -> None:
        """
        Write Dataset to JSON file.
        
        Parameters:
        -----------
        output_file : str
            Path to the output JSON file
        """
        output_path = Path(output_file)

        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert Dataset to JSON-serializable structure
        json_data = self._dataset_to_dict()

        # Write to file with pretty printing
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, default=str)

    def _dataset_to_dict(self) -> dict:
        """
        Convert xarray Dataset to JSON-serializable dictionary.
        
        Returns:
        --------
        dict
            Dictionary representation of the Dataset
        """
        result = {}

        # Extract time coordinate if present
        if 'time' in self.data.coords:
            time_values = self.data['time'].values
            # Convert numpy datetime64 to ISO strings
            result['time'] = [
                pd.Timestamp(t).isoformat() 
                for t in time_values
            ]

        # Extract data variables
        for var_name in self.data.data_vars:
            var = self.data[var_name]

            # Convert to list (handling NaN)
            values = var.values.tolist()
            result[var_name] = [
                None if (isinstance(v, float) and np.isnan(v)) else v
                for v in values
            ]

        # Extract global attributes as metadata
        if self.data.attrs:
            metadata = {}
            for key, value in self.data.attrs.items():
                # Skip certain attributes
                if key in ['source_file', 'reader', 'date_created']:
                    continue

                # Convert numpy types to Python types
                if isinstance(value, (np.integer, np.floating)):
                    value = value.item()

                metadata[key] = value

            if metadata:
                result['metadata'] = metadata

        return result
