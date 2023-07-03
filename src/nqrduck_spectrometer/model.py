import logging
from PyQt5.QtCore import pyqtSignal
from nqrduck.module.module_model import ModuleModel

logger = logging.getLogger(__name__)

class SpectrometerModel(ModuleModel):
    spectrometer_changed = pyqtSignal()

    def __init__(self, module) -> None:
        super().__init__(module)
        self._active_spectrometer = None
        self._available_spectrometers = []
        self._load_available_spectrometers()

    @property
    def active_spectrometer(self):
        return self._active_spectrometer
    
    @active_spectrometer.setter
    def active_spectrometer(self, value):
        self._active_spectrometer = value
        self.spectrometer_changed.emit()
    
    @property
    def available_spectrometers(self):
        return self._available_spectrometers
    
    def _load_available_spectrometers(self):
        pass

    
    def _load_spectrometer(self, spectrometer_module_name):
        pass


