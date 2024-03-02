import logging
import ipaddress
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

logger = logging.getLogger(__name__)

class Setting(QObject):
        """A setting for the spectrometer is a value that is the same for all events in a pulse sequence.
        E.g. the number of averages or the number of points in a spectrum."""
        settings_changed = pyqtSignal()

        def __init__(self, name, description) -> None:
            super().__init__()
            self.name = name
            self.description = description

        @pyqtSlot(str)
        def on_value_changed(self, value):
            logger.debug("Setting %s changed to %s", self.name, value)
            self.value = value
            self.settings_changed.emit()

        def get_setting(self):
            return float(self.value)
        
class FloatSetting(Setting):
    """ A setting that is a Float. """
    def __init__(self, name : str, default : float, description : str) -> None:
        super().__init__(name, description)
        self.value = default

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        try:
            self._value = float(value)
        except ValueError:
            raise ValueError("Value must be a float")
        self.settings_changed.emit()
         

class IntSetting(Setting):
    """ A setting that is an Integer."""
    def __init__(self, name : str, default : int, description : str) -> None:
        super().__init__(name, description)
        self.value = default

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        try:
            self._value = int(value)
        except ValueError:
            raise ValueError("Value must be an int")
        self.settings_changed.emit()

class BooleanSetting(Setting):
    """ A setting that is a Boolean."""
    
    def __init__(self, name : str, default : bool, description : str) -> None:
        super().__init__(name, description)
        self.value = default

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        try:
            self._value = bool(value)
        except ValueError:
            raise ValueError("Value must be a bool")
        self.settings_changed.emit()

class SelectionSetting(Setting):
    """ A setting that is a selection from a list of options."""
    def __init__(self, name : str, options : list, default : str, description : str) -> None:
        super().__init__(name, description)
        # Check if default is in options
        if default not in options:
            raise ValueError("Default value must be one of the options")
        
        self.options = options
        self.value = default

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        if value in self.options:
            self._value = value
        else:
            raise ValueError("Value must be one of the options")
        self.settings_changed.emit()

class IPSetting(Setting):
    """ A setting that is an IP address."""
    def __init__(self, name : str, default : str, description : str) -> None:
        super().__init__(name, description)
        self.value = default

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        try:
            ipaddress.ip_address(value)
            self._value = value
        except ValueError:
            raise ValueError("Value must be a valid IP address")
        self.settings_changed.emit()

class StringSetting(Setting):
    """ A setting that is a string."""
    def __init__(self, name : str, default : str, description : str) -> None:
        super().__init__(name, description)
        self.value = default

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        try:
            self._value = str(value)
        except ValueError:
            raise ValueError("Value must be a string")
        
        self.settings_changed.emit()