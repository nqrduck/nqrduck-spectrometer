from PyQt5.QtCore import pyqtSignal
from nqrduck.module.module import Module

class BaseSpectrometer(Module):
    """Base class for all spectrometers. All spectrometers should inherit from this class."""
    change_spectrometer = pyqtSignal(str)

    def __init__(self, model, view, controller):
        super().__init__(model, None, controller)
        # This stops the view from being added to the main window.
        self._view = None
        self._inner_view = view(self)

    @property
    def pulse_program(self):
        """Pulse program of the spectrometer."""
        raise NotImplementedError

    def start_measurement(self):
        """Starts the measurement."""
        raise NotImplementedError
    
    def set_active(self):
        """Sets the spectrometer as the active spectrometer."""
        self.change_spectrometer.emit(self._model.name)
