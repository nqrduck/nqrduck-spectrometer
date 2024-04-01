"""Settings for the different spectrometers."""

import logging
import ipaddress
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QLineEdit, QComboBox, QCheckBox
from nqrduck.helpers.duckwidgets import DuckFloatEdit, DuckIntEdit

logger = logging.getLogger(__name__)


class Setting(QObject):
    """A setting for the spectrometer is a value that is the same for all events in a pulse sequence.

    E.g. the Transmit gain or the number of points in a spectrum.

    Args:
        name (str) : The name of the setting
        description (str) : A description of the setting
        default : The default value of the setting

    Attributes:
        name (str) : The name of the setting
        description (str) : A description of the setting
        value : The value of the setting
        widget : The widget that is used to change the setting
    """

    settings_changed = pyqtSignal()

    def __init__(self, name: str, description: str, default=None) -> None:
        """Create a new setting.

        Args:
            name (str): The name of the setting.
            description (str): A description of the setting.
            default: The default value of the setting.
        """
        super().__init__()
        self.name = name
        self.description = description
        if default is not None:
            self.value = default

        # This can be overridden by subclasses
        self.widget = self.get_widget()

    @pyqtSlot(str)
    def on_value_changed(self, value):
        """This method is called when the value of the setting is changed.

        Args:
            value (str): The new value of the setting.
        """
        logger.debug("Setting %s changed to %s", self.name, value)
        self.value = value
        self.settings_changed.emit()

    def get_setting(self):
        """Return the value of the setting.

        Returns:
            The value of the setting.
        """
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
        widget.editingFinished.connect(
            lambda x=widget, s=self: s.on_value_changed(x.text())
        )
        return widget


class FloatSetting(Setting):
    """A setting that is a Float.

    Args:
        name (str) : The name of the setting
        default : The default value of the setting
        description (str) : A description of the setting
        min_value : The minimum value of the setting
        max_value : The maximum value of the setting
    """

    DEFAULT_LENGTH = 100

    def __init__(
        self,
        name: str,
        default: float,
        description: str,
        min_value: float = None,
        max_value: float = None,
    ) -> None:
        """Create a new float setting."""
        super().__init__(name, description, default)

        self.widget = DuckFloatEdit(min_value=min_value, max_value=max_value)
        self.widget.setText(str(default))
        self.widget.state_updated.connect(self.on_state_updated)

    def on_state_updated(self, state, text):
        """Update the value of the setting.

        Args:
            state (bool): The state of the input (valid or not).
            text (str): The new value of the setting.
        """
        if state:
            self.value = text

    @property
    def value(self):
        """The value of the setting. In this case, a float."""
        return self._value

    @value.setter
    def value(self, value):
        self._value = float(value)
        self.settings_changed.emit()


class IntSetting(Setting):
    """A setting that is an Integer.

    Args:
        name (str) : The name of the setting
        default : The default value of the setting
        description (str) : A description of the setting
        min_value : The minimum value of the setting
        max_value : The maximum value of the setting
    """

    def __init__(
        self,
        name: str,
        default: int,
        description: str,
        min_value=None,
        max_value=None,
    ) -> None:
        """Create a new int setting."""
        super().__init__(name, description, default)

        self.widget = DuckIntEdit(min_value=min_value, max_value=max_value)
        self.widget.setText(str(default))

        self.widget.state_updated.connect(self.on_state_updated)

    def on_state_updated(self, state, text):
        """Update the value of the setting.

        Args:
            state (bool): The state of the input (valid or not).
            text (str): The new value of the setting.
        """
        if state:
            self.value = text

    @property
    def value(self):
        """The value of the setting. In this case, an int."""
        return self._value

    @value.setter
    def value(self, value):
        value = int(float(value))
        self._value = value
        self.settings_changed.emit()



class BooleanSetting(Setting):
    """A setting that is a Boolean.

    Args:
        name (str) : The name of the setting
        default : The default value of the setting
        description (str) : A description of the setting
    """

    def __init__(self, name: str, default: bool, description: str) -> None:
        """Create a new boolean setting."""
        super().__init__(name, description, default)

        # Overrides the default widget
        self.widget = self.get_widget()

    @property
    def value(self):
        """The value of the setting. In this case, a bool."""
        return self._value

    @value.setter
    def value(self, value):
        try:
            self._value = bool(value)
            self.settings_changed.emit()
        except ValueError:
            raise ValueError("Value must be a bool")

    def get_widget(self):
        """Return a widget for the setting.

        This returns a QCheckBox widget.

        Returns:
            QCheckBox: A QCheckBox widget that can be used to change the setting.
        """
        widget = QCheckBox()
        widget.setChecked(self.value)
        widget.stateChanged.connect(
            lambda x=widget, s=self: s.on_value_changed(bool(x))
        )
        return widget


class SelectionSetting(Setting):
    """A setting that is a selection from a list of options.

    Args:
        name (str) : The name of the setting
        options (list) : A list of options to choose from
        default : The default value of the setting
        description (str) : A description of the setting
    """

    def __init__(
        self, name: str, options: list, default: str, description: str
    ) -> None:
        """Create a new selection setting."""
        super().__init__(name, description, default)
        # Check if default is in options
        if default not in options:
            raise ValueError("Default value must be one of the options")

        self.options = options

        # Overrides the default widget
        self.widget = self.get_widget()

    @property
    def value(self):
        """The value of the setting. In this case, a string."""
        return self._value

    @value.setter
    def value(self, value):
        try:
            if value in self.options:
                self._value = value
                self.settings_changed.emit()
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
        widget.currentTextChanged.connect(
            lambda x=widget, s=self: s.on_value_changed(x)
        )
        return widget


class IPSetting(Setting):
    """A setting that is an IP address.

    Args:
        name (str) : The name of the setting
        default : The default value of the setting
        description (str) : A description of the setting
    """

    def __init__(self, name: str, default: str, description: str) -> None:
        """Create a new IP setting."""
        super().__init__(name, description)
        self.value = default

    @property
    def value(self):
        """The value of the setting. In this case, an IP address."""
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
    """A setting that is a string.

    Args:
        name (str) : The name of the setting
        default : The default value of the setting
        description (str) : A description of the setting
    """

    def __init__(self, name: str, default: str, description: str) -> None:
        """Create a new string setting."""
        super().__init__(name, description, default)

    @property
    def value(self):
        """The value of the setting. In this case, a string."""
        return self._value

    @value.setter
    def value(self, value):
        try:
            self._value = str(value)
            self.settings_changed.emit()
        except ValueError:
            raise ValueError("Value must be a string")
