"""The model for the nqrduck-spectrometer module. This module is responsible for managing the spectrometers."""

import logging
from PyQt6.QtCore import pyqtSignal
from nqrduck.module.module_model import ModuleModel
from .base_spectrometer import BaseSpectrometer

logger = logging.getLogger(__name__)


class SpectrometerModel(ModuleModel):
    """The model for the spectrometer module.

    This class is responsible for managing the spectrometers.

    Args:
        module (Module) : The module that the spectrometer is connected to

    Attributes:
        active_spectrometer (BaseSpectrometer) : The currently active spectrometer
        available_spectrometers (dict) : A dictionary of all available spectrometers

    Signals:
        spectrometer_added (BaseSpectrometer) : Signal emitted when a spectrometer is added
        active_spectrometer_changed (BaseSpectrometer) : Signal emitted when the active spectrometer is changed
    """

    spectrometer_added = pyqtSignal(BaseSpectrometer)
    active_spectrometer_changed = pyqtSignal(BaseSpectrometer)

    def __init__(self, module) -> None:
        """Initializes the spectrometer model."""
        super().__init__(module)
        self._active_spectrometer = None
        self._available_spectrometers = dict()

    @property
    def active_spectrometer(self):
        """The currently active spectrometer. This is the one that is currently being used."""
        return self._active_spectrometer

    @active_spectrometer.setter
    def active_spectrometer(self, value):
        self._active_spectrometer = value
        self.active_spectrometer_changed.emit(value)
        spectrometer_module_name = value.model.toolbar_name
        logger.debug("Active spectrometer changed to %s", spectrometer_module_name)
        self.module.nqrduck_signal.emit(
            "active_spectrometer_changed", spectrometer_module_name
        )

    @property
    def available_spectrometers(self):
        """A dictionary of all available spectrometers. The key is the name of the spectrometer and the value is the module."""
        return self._available_spectrometers

    def add_spectrometers(self, spectrometer_module_name, module):
        """Adds a spectrometer to the available spectrometers.

        Args:
            spectrometer_module_name (str) : The name of the spectrometer
            module (BaseSpectrometer) : The module of the spectrometer
        """
        self._available_spectrometers[spectrometer_module_name] = module
        logger.debug("Added module: %s", spectrometer_module_name)
        self.spectrometer_added.emit(module)
        self.active_spectrometer = module
        self.add_submodule(spectrometer_module_name)
