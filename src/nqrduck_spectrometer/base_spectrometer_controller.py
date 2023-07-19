from nqrduck.module.module_controller import ModuleController

class BaseSpectrometerController(ModuleController):

    def __init__(self, module):
        super().__init__(module)

    def start_measurement(self):
        """Starts the measurement.
        """
        raise NotImplementedError
    
    def set_frequency(self, value):
        raise NotImplementedError
    
    def set_averages(self, value):
        raise NotImplementedError