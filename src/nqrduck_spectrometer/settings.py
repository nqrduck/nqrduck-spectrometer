import logging
import ipaddress
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QRegularExpression
from PyQt6.QtWidgets import QLineEdit, QComboBox, QCheckBox
from PyQt6.QtGui import QValidator, QRegularExpressionValidator

logger = logging.getLogger(__name__)

class Setting(QObject):
        """A setting for the spectrometer is a value that is the same for all events in a pulse sequence.
        E.g. the number of averages or the number of points in a spectrum."""
        settings_changed = pyqtSignal()

        def __init__(self, name : str, description : str, default = None) -> None:
            """ Create a new setting.
            
            Args:
                name (str): The name of the setting.
                description (str): A description of the setting.
            """
            super().__init__()
            self.name = name
            self.description = description
            if default is not None:
                self.value = default

            # This can be overriden by subclasses
            self.widget = self.get_widget()

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
        
        def update_widget_style(self):
            """ Update the style of the QLineEdit widget to indicate if the value is valid."""
            logger.debug("Updating widget style")
            if self.validator.validate(self.widget.text(), 0)[0] == QValidator.State.Acceptable:
                self.widget.setStyleSheet("QLineEdit { background-color: white; }")
            elif self.validator.validate(self.widget.text(), 0)[0] == QValidator.State.Intermediate:
                self.widget.setStyleSheet("QLineEdit { background-color: yellow; }")
            else:
                self.widget.setStyleSheet("QLineEdit { background-color: red; }")

class FloatSetting(Setting):
    """ A setting that is a Float. """
    DEFAULT_LENGTH = 100
    def __init__(self, name : str, default : float, description : str, validator : QValidator = None) -> None:
        super().__init__(name, description, default)

        # If a validator is given, set it for the QLineEdit widget
        if validator:
            self.validator = validator
        else:
            # Create a regex validator that only allows floats
            regex = "[-+]?[0-9]*\.?[0-9]+"
            self.validator = QRegularExpressionValidator(QRegularExpression(regex))

            self.widget = self.get_widget()
            # self.widget.setValidator(self.validator)
            # Connect the update_widget_style method to the textChanged signal
            self.widget.textChanged.connect(self.update_widget_style)

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        try:
            if self.validator.validate(value, 0)[0] == QValidator.State.Acceptable:
                self._value = float(value)
                self.settings_changed.emit()
        # This should never be reached because the validator should prevent this
        except ValueError:
            raise ValueError("Value must be a float")
        # This happens when the validator has not yet been set
        except AttributeError:
            self._value = float(value)
            self.settings_changed.emit()

class IntSetting(Setting):
    """ A setting that is an Integer."""
    def __init__(self, name : str, default : int, description : str, validator : QValidator = None) -> None:
        super().__init__(name, description, default)

        # If a validator is given, set it for the QLineEdit widget
        if validator:
            self.validator = validator
        else:
            # Create a regex validator that only allows integers
            regex = "[-+]?[0-9]+"
            self.validator = QRegularExpressionValidator(QRegularExpression(regex))

            self.widget = self.get_widget()
            # Connect the update_widget_style method to the textChanged signal
            self.widget.textChanged.connect(self.update_widget_style)

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
        super().__init__(name, description, default)

        # Overrides the default widget
        self.widget = self.get_widget()

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
        super().__init__(name, description, default)
        # Check if default is in options
        if default not in options:
            raise ValueError("Default value must be one of the options")
        
        self.options = options

        # Overrides the default widget
        self.widget = self.get_widget()

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        try:
            if value in self.options:
                self._value = value
            else:
                raise ValueError("Value must be one of the options")
        # This fixes a bug when creating the widget when the options are not yet set
        except AttributeError:
            self._value = value
            self.options = [value]

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
        super().__init__(name, description, default)

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