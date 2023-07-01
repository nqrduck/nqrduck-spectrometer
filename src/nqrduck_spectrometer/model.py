from PyQt5.QtCore import pyqtSignal, QObject
from nqrduck.module.module_model import ModuleModel


class SpectrometerModel(ModuleModel):
    spectrometer_changed = pyqtSignal()

    @property
    def spectrometer(self):
        return self._spectrometer

