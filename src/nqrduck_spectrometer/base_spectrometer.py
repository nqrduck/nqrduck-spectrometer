class BaseSpectrometer:
    """Base class for all spectrometers. All spectrometers should inherit from this class."""

    def __init__(self):
        pass

    @property
    def name(self):
        """Name of the spectrometer."""
        raise NotImplementedError

    @property
    def pulse_program(self):
        """Pulse program of the spectrometer."""
        raise NotImplementedError

    def start_measurement(self):
        """Starts the measurement."""
        raise NotImplementedError
