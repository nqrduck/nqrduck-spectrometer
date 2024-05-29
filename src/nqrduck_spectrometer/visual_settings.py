"""Settings for the different spectrometers."""

import logging
from PyQt6.QtCore import pyqtSignal, pyqtSlot, QObject
from PyQt6.QtWidgets import QLineEdit, QComboBox, QCheckBox
from nqrduck.helpers.duckwidgets import DuckFloatEdit, DuckIntEdit, DuckSpinBox

from quackseq.spectrometer.spectrometer_settings import (
    FloatSetting,
    IntSetting,
    BooleanSetting,
    SelectionSetting,
    StringSetting,
)

logger = logging.getLogger(__name__)


class VisualSetting(QObject):
    """A visual  setting that is  created from a setting.

    Args:
        setting (Setting) : The setting that is used to create the visual setting.
    """

    settings_changed = pyqtSignal()

    def __init__(self, setting, *args, **kwargs) -> None:
        """Create a new setting.

        Args:
            setting (Setting): The setting that is used to create the visual setting.
        """
        self.widget = None
        self.setting = setting
        super().__init__()



class VisualFloatSetting(VisualSetting):
    """A setting that is a Float.

    Args:
        setting (FloatSetting) : The setting that is used to create the visual setting.

    """

    DEFAULT_LENGTH = 100

    def __init__(
        self,
        setting: FloatSetting,
    ) -> None:
        """Create a new float setting."""
        self.spin_box = False
        super().__init__(setting)

        # Create a spin box if  min and max values are set
        if setting.min_value is not None and setting.max_value is not None:
            self.widget = DuckSpinBox(
                min_value=setting.min_value,
                max_value=setting.max_value,
                slider=setting.slider,
                double_box=True,
            )
            self.widget.spin_box.setValue(setting.default)
            self.spin_box = True
        else:
            self.widget = DuckSpinBox(min_value=setting.min_value, max_value=setting.max_value, double_box=True)
            self.widget.set_value(setting.default)

        self.widget.state_updated.connect(self.on_state_updated)

    def on_state_updated(self, state, text):
        """Update the value of the setting.

        Args:
            state (bool): The state of the input (valid or not).
            text (str): The new value of the setting.
        """
        if state:
            self.value = text
            self.settings_changed.emit()

    @property
    def value(self):
        """The value of the setting. In this case, a float."""
        return self.setting.value

    @value.setter
    def value(self, value):
        logger.debug(f"Setting {self.setting.name} to {value}")
        self.setting.value = value
        self.settings_changed.emit()

        if self.widget:
            if self.spin_box:
                self.widget.spin_box.setValue(self.setting.value)
            else:
                value = float(value)
                self.widget.set_value(value)


class VisualIntSetting(VisualSetting):
    """A setting that is an Integer.

    Args:
        setting (IntSetting) : The setting that is used to create the visual setting.
        spin_box : A tuple with two booleans that determine if a spin box is used if the second value is True, a slider will be created as well.
    """

    def __init__(
        self,
        setting: IntSetting,
    ) -> None:
        """Create a new int setting."""
        self.spin_box = False

        super().__init__(setting)

        if setting.min_value is not None and setting.max_value is not None:
            self.widget = DuckSpinBox(
                min_value=setting.min_value,
                max_value=setting.max_value,
                slider=setting.slider,
                double_box=True,
            )
            self.spin_box = True
            self.widget.spin_box.setValue(setting.default)
        
        else:
            self.widget = DuckIntEdit(
                min_value=setting.min_value, max_value=setting.max_value
            )
            self.widget.setText(str(setting.default))

        self.widget.state_updated.connect(self.on_state_updated)

    def on_state_updated(self, state, text):
        """Update the value of the setting.

        Args:
            state (bool): The state of the input (valid or not).
            text (str): The new value of the setting.
        """
        if state:
            self.value = text
            self.settings_changed.emit()

    @property
    def value(self):
        """The value of the setting. In this case, an int."""
        return self.setting.value

    @value.setter
    def value(self, value):
        logger.debug(f"Setting {self.setting.name} to {value}")
        value = int(float(value))
        self.setting.value = value
        self.settings_changed.emit()
        if self.widget:
            if self.spin_box:
                self.widget.spin_box.setValue(value)
            else:
                self.widget.setText(str(value))


class VisualBooleanSetting(VisualSetting):
    """A setting that is a Boolean.

    Args:
        setting (BooleanSetting) : The setting that is used to create the visual setting.
    """

    def __init__(self, setting: BooleanSetting) -> None:
        """Create a new boolean setting."""
        super().__init(
            setting
        )

        # Overrides the default widget
        self.widget = self.get_widget()

    @property
    def value(self):
        """The value of the setting. In this case, a bool."""
        return self.setting.value

    @value.setter
    def value(self, value):
        try:
            self.setting.value = bool(value)
            if self.widget:
                self.widget.setChecked(self._value)
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
        widget.setChecked(self.setting.value)
        widget.stateChanged.connect(
            lambda x=widget, s=self: s.on_value_changed(bool(x))
        )
        return widget


class VisualSelectionSetting(VisualSetting):
    """A setting that is a selection from a list of options.

    Args:
        setting (SelectionSetting) : The setting that is used to create the visual setting.
    """

    def __init__(self, setting: SelectionSetting) -> None:
        """Create a new selection setting."""
        super().__init__(setting)

        # Overrides the default widget
        self.widget = self.get_widget()

    @property
    def value(self):
        """The value of the setting. In this case, a string."""
        return self._value

    @value.setter
    def value(self, value):
        try:
            if value in self.setting.options:
                self.setting.value
                if self.widget:
                    self.widget.setCurrentText(value)
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


class VisualStringSetting(VisualSetting):
    """A setting that is a string.

    Args:
        setting (StringSetting) : The setting that is used to create the visual setting.
    """

    def __init__(self, setting: StringSetting) -> None:
        """Create a new string setting."""
        super().__init__(setting)
        self.widget = self.get_widget()

    @property
    def value(self):
        """The value of the setting. In this case, a string."""
        return self.setting.value

    @value.setter
    def value(self, value):
        try:
            self.setting.value = str(value)
            self.settings_changed.emit()
        except ValueError:
            raise ValueError("Value must be a string")
        
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
