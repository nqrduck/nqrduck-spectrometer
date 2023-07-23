import logging
from collections import OrderedDict
from PyQt6.QtCore import pyqtSlot, pyqtSignal, QObject
from nqrduck.module.module_model import ModuleModel

logger = logging.getLogger(__name__)

class BaseSpectrometerModel(ModuleModel):
    settings : OrderedDict
    pulse_parameter_options : OrderedDict

    class Setting(QObject):
        """A setting for the spectrometer is a value that is the same for all events in a pulse sequence.
        E.g. the number of averages or the number of points in a spectrum."""
        settings_changed = pyqtSignal()

        def __init__(self, name, default, description) -> None:
            super().__init__()
            self.name = name
            self.value = default
            self.description = description

        @pyqtSlot(str)
        def on_value_changed(self, value):
            logger.debug("Setting %s changed to %s", self.name, value)
            self.value = value
            self.settings_changed.emit()

        def get_setting(self):
            return float(self.value)
        

    class PulseParameter:
        """A pulse parameter is a value that can be different for each event in a pulse sequence.
        E.g. the transmit pulse power or the phase of the transmit pulse.
        
        Arguments:
            name (str) -- The name of the pulse parameter
            
        Attributes:
            name (str) -- The name of the pulse parameter
            options (OrderedDict) -- The options of the pulse parameter
        """
        def __init__(self, name):
            self.name = name
            self.options = list()
        
        def get_pixmap(self):
            raise NotImplementedError
        
        def add_option(self, option):
            self.options.append(option)

        def get_options(self):
            return self.options
        
        def get_option_by_name(self, name : str) -> "Option":
            for option in self.options:
                if option.name == name:
                    return option
            raise ValueError("Option with name %s not found" % name)
        

    def __init__(self, module):
        super().__init__(module)
        self.settings = OrderedDict()
        self.pulse_parameter_options = OrderedDict()

    def add_setting(self, name, value, description, category) -> None:
        if category not in self.settings.keys():
            self.settings[category] = []
        self.settings[category].append(self.Setting(name, value, description))

    def get_setting_by_name(self, name : str) -> Setting:
        for category in self.settings.keys():
            for setting in self.settings[category]:
                if setting.name == name:
                    return setting
        raise ValueError("Setting with name %s not found" % name)

    def add_pulse_parameter_option(self, name, pulse_parameter_class) -> None:
        self.pulse_parameter_options[name] = pulse_parameter_class

    @property
    def target_frequency(self):
        raise NotImplementedError
    
    @target_frequency.setter
    def target_frequency(self, value):
        raise NotImplementedError
    
    @property
    def averages(self):
        raise NotImplementedError
    
    @averages.setter
    def averages(self, value):
        raise NotImplementedError
