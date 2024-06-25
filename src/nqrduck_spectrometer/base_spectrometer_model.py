"""The base class for all spectrometer models."""

import logging
from PyQt6.QtCore import QSettings
from nqrduck.module.module_model import ModuleModel
from quackseq.spectrometer.spectrometer_settings import FloatSetting, BooleanSetting, IntSetting, StringSetting, SelectionSetting
from .visual_settings import VisualFloatSetting, VisualIntSetting, VisualBooleanSetting, VisualStringSetting, VisualSelectionSetting

logger = logging.getLogger(__name__)


class BaseSpectrometerModel(ModuleModel):
    """The base class for all spectrometer models.

    It contains the settings and pulse parameters of the spectrometer.

    Args:
        module (Module) : The module that the spectrometer is connected to

    Attributes:
        SETTING_FILE_EXTENSION (str) : The file extension for the settings file
        default_settings (QSettings) : The default settings of the spectrometer
        quackseq_model (QuackseqModel) : The quackseq model of the spectrometer
        quackseq_visuals (dict) : The visual settings of the spectrometer
    """

    SETTING_FILE_EXTENSION = "setduck"

    def __init__(self, module):
        """Initializes the spectrometer model.

        Args:
            module (Module) : The module that the spectrometer is connected to
        """
        super().__init__(module)
        self.default_settings = QSettings("nqrduck-spectrometer", "nqrduck")

        self.quackseq_model = None
        self.quackseq_visuals = dict()

    def visualize_settings(self) -> None:
        """Visualizes the settings of the spectrometer.
        
        This method creates a dictionary of visual settings from the settings of the spectrometer.
        """
        settings  = self.quackseq_model.settings

        for name, setting in settings.items():
            logger.debug(f"Setting: {name}, Value: {setting.value}")

            # Now we need to translate for example a FloatSetting to a VisualFloat setting
            if isinstance(setting, FloatSetting):
                self.quackseq_visuals[name] = VisualFloatSetting(setting)

            elif isinstance(setting, IntSetting):
                self.quackseq_visuals[name] = VisualIntSetting(setting)

            elif isinstance(setting, BooleanSetting):
                self.quackseq_visuals[name] = VisualBooleanSetting(setting)

            elif isinstance(setting, StringSetting):
                self.quackseq_visuals[name] = VisualStringSetting(setting)

            elif isinstance(setting, SelectionSetting):
                self.quackseq_visuals[name] = VisualSelectionSetting(setting)
                
            else:
                logger.error(f"Setting type {type(setting)} not supported")


    def set_default_settings(self) -> None:
        """Sets the default settings of the spectrometer."""
        self.default_settings.clear()
        settings = self.quackseq_model.settings

        for setting in settings.values():
            setting_string = f"{self.module.model.name},{setting.name}"
            self.default_settings.setValue(setting_string, setting.value)
            logger.debug(f"Setting default value for {setting_string} to {setting.value}")

    def load_default_settings(self) -> None:
        """Load the default settings of the spectrometer."""
        visual_settings = self.quackseq_visuals

        for visual_setting in visual_settings.values():
            setting_string = f"{self.module.model.name},{visual_setting.setting.name}"
            value = self.default_settings.value(setting_string)
            if value is None:
                logger.debug(f"Setting {setting_string} not found in default settings")
                continue
            visual_setting.value = value

    def clear_default_settings(self) -> None:
        """Clear the default settings of the spectrometer."""
        self.default_settings.clear()

    @property
    def target_frequency(self):
        """The target frequency of the spectrometer in Hz. This is the frequency where the magnetic resonance experiment is performed."""
        raise NotImplementedError

    @target_frequency.setter
    def target_frequency(self, value):
        raise NotImplementedError

    @property
    def averages(self):
        """The number of averages for the spectrometer."""
        raise NotImplementedError

    @averages.setter
    def averages(self, value):
        raise NotImplementedError
