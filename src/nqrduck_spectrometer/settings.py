import logging
import ipaddress
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QLineEdit, QComboBox, QCheckBox

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
        
        def get_widget(self):
            """Return a widget for the setting.
            The default widget is simply a QLineEdit.
            This method can be overwritten by subclasses to return a different widget.
            
            Returns:
                QLineEdit: A QLineEdit widget that can be used to change the setting.
                
            """
            widget = QLineEdit(str(self.value))
            widget.setMinimumWidth(100)
            widget.editingFinished.connect(lambda x=widget, s=self: s.on_value_changed(x.text()))
            return widget
        
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


    def get_widget(self):
        """Return a widget for the setting.
        This returns a QCheckBox widget.
        
        Returns:
            QCheckBox: A QCheckBox widget that can be used to change the setting.
        """
        widget = QCheckBox()
        widget.setChecked(self.value)
        widget.stateChanged.connect(lambda x=widget, s=self: s.on_value_changed(bool(x)))
        return widget

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

    def get_widget(self):
        """Return a widget for the setting.
        This returns a QComboBox widget.
        
        Returns:
            QComboBox: A QComboBox widget that can be used to change the setting.
        """
        widget = QComboBox()
        widget.addItems(self.options)
        widget.setCurrentText(self.value)
        widget.currentTextChanged.connect(lambda x=widget, s=self: s.on_value_changed(x))
        return widget

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

    def get_widget(self):
        """Return a widget for the setting.
        The default widget is simply a QLineEdit.
        This method can be overwritten by subclasses to return a different widget.
        
        Returns:
            QLineEdit: A QLineEdit widget that can be used to change the setting.
        """
        widget = QLineEdit(str(self.value))
        widget.setMinimumWidth(100)
        widget.editingFinished.connect(lambda x=widget, s=self: s.on_value_changed(x.text()))
        return widget