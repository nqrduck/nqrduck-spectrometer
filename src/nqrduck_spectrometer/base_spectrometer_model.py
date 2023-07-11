import logging
from collections import OrderedDict
from PyQt6.QtCore import pyqtSlot
from nqrduck.module.module_model import ModuleModel

logger = logging.getLogger(__name__)

class BaseSpectrometerModel(ModuleModel):
    def __init__(self, module):
        super().__init__(module)
        self.settings = OrderedDict()
        self.pulse_parameter_options = OrderedDict()

    def add_setting(self, name, value, description) -> None:
        self.settings[name] = self.Setting(name, value, description)

    def add_pulse_parameter_option(self, name, pulse_parameter_class) -> None:
        self.pulse_parameter_options[name] = pulse_parameter_class

    class Setting:
        """A setting for the spectrometer is a value that is the same for all events in a pulse sequence.
        E.g. the number of averages or the number of points in a spectrum."""

        def __init__(self, name, default, description) -> None:
            self.name = name
            self.value = default
            self.description = description

        @pyqtSlot(str)
        def on_value_changed(self, value):
            logger.debug("Setting %s changed to %s", self.name, value)
            self.value = value

    class PulseParameter:
        def __init__(self, name):
            self.name = name
        
        def get_pixmap(self):
            raise NotImplementedError
        
        def get_options(self):
            raise NotImplementedError


