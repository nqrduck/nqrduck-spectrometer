from PyQt6.QtCore import pyqtSignal
from nqrduck.module.module import Module

class BaseSpectrometer(Module):
    """Base class for all spectrometers. All spectrometers should inherit from this class."""
    change_spectrometer = pyqtSignal(str)

    def __init__(self, model, view, controller):
        super().__init__(model, None, controller)
        # This stops the view from being added to the main window.
        self._view = None
        self.settings_view = view(self)
    
    def set_active(self):
        """Sets the spectrometer as the active spectrometer.
        """
        self.change_spectrometer.emit(self._model.name)

    @property
    def settings_view(self):
        """The settings view of the spectrometer.
        """
        return self._settings_view
    
    @settings_view.setter
    def settings_view(self, value):
        self._settings_view = value
