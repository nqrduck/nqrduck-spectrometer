from nqrduck.module.module_controller import ModuleController

class BaseSpectrometerController(ModuleController):
    """The base class for all spectrometer controllers."""

    def __init__(self, module):
        super().__init__(module)

    def start_measurement(self):
        """Starts the measurement.
        This method should be called when the measurement is started.
        """
        raise NotImplementedError
    
    def set_frequency(self, value):
        """Sets the frequency of the spectrometer."""
        raise NotImplementedError
    
    def set_averages(self, value):
        raise NotImplementedError