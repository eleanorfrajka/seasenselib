"""
Command factory for creating command instances.
"""

from ...core import DataIOManager
from ...core.exceptions import SeaSenseLibError
from .base import BaseCommand
from .data_commands import ConvertCommand, ShowCommand, SubsetCommand, CalcCommand
from .plot_commands import PlotCommand
from .info_commands import FormatsCommand, ListCommand


class CommandFactory:
    """Factory for creating command instances."""

    def create_command(self, command_name: str, io_manager: DataIOManager) -> BaseCommand:
        """
        Create a command instance based on command name.
        
        Parameters:
        -----------
        command_name : str
            Name of the command to create
        io_manager : DataIOManager
            I/O manager instance
            
        Returns:
        --------
        BaseCommand
            Command instance
            
        Raises:
        -------
        SeaSenseLibError
            If command is unknown
        """
        # Data processing commands
        if command_name == 'convert':
            return ConvertCommand(io_manager)
        elif command_name == 'show':
            return ShowCommand(io_manager)
        elif command_name == 'subset':
            return SubsetCommand(io_manager)
        elif command_name == 'calc':
            return CalcCommand(io_manager)

        # Plotting commands
        elif command_name == 'plot':
            return PlotCommand(io_manager)

        # Info commands
        elif command_name == 'list':
            return ListCommand(io_manager)
        elif command_name == 'formats':
            return FormatsCommand(io_manager)

        else:
            raise SeaSenseLibError(f"Unknown command: {command_name}")
