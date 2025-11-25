"""
Example Histogram Plotter Plugin for SeaSenseLib.

This plotter demonstrates how to create a custom plotter plugin that extends
SeaSenseLib with a histogram visualization for oceanographic data.
"""

import xarray as xr
import numpy as np
from seasenselib.plotters.base import AbstractPlotter


class HistogramPlotter(AbstractPlotter):
    """
    Plotter for creating histograms of oceanographic parameters.
    
    This is an example plugin that creates histogram plots showing
    the distribution of any parameter in the dataset.
    """

    def __init__(self, data: xr.Dataset | None = None):
        """
        Initialize the histogram plotter.
        
        Parameters:
        -----------
        data : xr.Dataset, optional
            The xarray Dataset containing the oceanographic data
        """
        super().__init__(data)

    @staticmethod
    def key() -> str:
        """Return the unique format identifier."""
        return "histogram"

    @staticmethod
    def name() -> str:
        """Return the human-readable format name."""
        return "Histogram Plot"

    def plot(
        self,
        parameter: str = "temperature",
        bins: int = 30,
        title: str | None = None,
        output_file: str | None = None,
        **kwargs
    ):
        """
        Create a histogram plot for a parameter.
        
        Parameters:
        -----------
        parameter : str
            Name of the parameter to plot (default: 'temperature')
        bins : int
            Number of histogram bins (default: 30)
        title : str, optional
            Plot title. If None, auto-generated from parameter name
        output_file : str, optional
            Path to save the plot. If None, plot is displayed
        **kwargs
            Additional arguments passed to matplotlib hist()
        """
        if self.data is None:
            raise ValueError("No data available. Set data before plotting.")

        # Validate that the parameter exists
        self._validate_required_variables([parameter])

        # Get data without NaN values
        ds_clean = self._get_dataset_without_nan()

        # Extract parameter values
        values = ds_clean[parameter].values

        # Get parameter metadata
        param_long_name = ds_clean[parameter].attrs.get('long_name', parameter)
        param_units = ds_clean[parameter].attrs.get('units', '')

        # Create figure
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(10, 6))

        # Create histogram
        n, bins_edges, patches = ax.hist(
            values,
            bins=bins,
            edgecolor='black',
            alpha=0.7,
            **kwargs
        )

        # Customize plot
        xlabel = f"{param_long_name}"
        if param_units:
            xlabel += f" ({param_units})"
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)

        # Set title
        if title is None:
            title = f"Distribution of {param_long_name}"
        ax.set_title(title, fontsize=14, fontweight='bold')

        # Add statistics text box
        mean_val = np.nanmean(values)
        std_val = np.nanstd(values)
        median_val = np.nanmedian(values)
        min_val = np.nanmin(values)
        max_val = np.nanmax(values)

        stats_text = (
            f"n = {len(values)}\n"
            f"Mean = {mean_val:.2f}\n"
            f"Median = {median_val:.2f}\n"
            f"Std = {std_val:.2f}\n"
            f"Min = {min_val:.2f}\n"
            f"Max = {max_val:.2f}"
        )

        ax.text(
            0.98, 0.97,
            stats_text,
            transform=ax.transAxes,
            verticalalignment='top',
            horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
            fontsize=10
        )

        # Add grid
        ax.grid(True, alpha=0.3, linestyle='--')

        # Tight layout
        plt.tight_layout()

        # Save or show
        self._save_or_show_plot(output_file)
