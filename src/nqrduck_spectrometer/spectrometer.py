from PyQt5.QtCore import pyqtSignal, QObject
from nqrduck.module.module_model import ModuleModel


class Spectrometer(ModuleModel):
    widget_changed = pyqtSignal(QObject)
    spectrometer_changed = pyqtSignal()

    @property
    def spectrometer(self):
        return self._spectrometer

    @property
    def widget(self):
        return self._widget

    @widget.setter
    def widget(self, value):
        self._widget = value
        self.widget_changed.emit(value)

