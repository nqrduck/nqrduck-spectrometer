from nqrduck.module.module import Module

class BaseSpectrometer(Module):
    """Base class for all spectrometers. All spectrometers should inherit from this class."""

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
