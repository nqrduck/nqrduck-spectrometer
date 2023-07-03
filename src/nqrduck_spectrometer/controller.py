from nqrduck.module.module_controller import ModuleController


class SpectrometerController(ModuleController):
    def __init__(self, module):
        super().__init__(module)

    def _load_spectrometer_modules(self):
        pass