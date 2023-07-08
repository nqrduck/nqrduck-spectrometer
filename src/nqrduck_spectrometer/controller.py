import logging
from PyQt6.QtCore import pyqtSlot
from nqrduck.module.module_controller import ModuleController
from nqrduck.core.main_controller import MainController
from nqrduck_spectrometer.base_spectrometer import BaseSpectrometer

logger = logging.getLogger(__name__)


class SpectrometerController(ModuleController):
    """This class is the controller for the spectrometer module."""

    def __init__(self, module):
        """This method initializes the controller.
        :param module: The module that this controller belongs to.
        """
        super().__init__(module)

    def _load_spectrometer_modules(self):
        """This method loads the spectrometer modules and adds them to the spectrometer model."""
        # Get the modules with entry points in the nqrduck group
        modules = MainController._get_modules()
        logger.debug("Found modules: %s", modules)

        for module_name, module in modules.items():
            # Check if the module instance is a spectrometer by checking if it inherits from BaseSpectrometer
            if not issubclass(type(module), BaseSpectrometer):
                logger.debug(
                    "Module is not a spectrometer: %s ... skipping", module_name
                )
                continue

            # Import the module
            logger.debug("Loading spectromter module: %s", module_name)
            module.model.widget_changed.connect(
                self._module.view.on_spectrometer_widget_changed
            )
            logger.debug("Adding spectrometer to spectrometer model: %s", module_name)
            self._module.model.add_spectrometers(module_name, module)

        self._module.view.create_menu_entry()

    def process_signals(self, key: str, value: str):
        if key == "start_measurement":
            self.on_measurement_start()

    def on_loading(self):
        """This method is called when the module is loaded.
        It connects the signals from the spectrometer model to the view.
        """
        self._module.model.spectrometer_added.connect(
            self.module.view.on_spectrometer_added
        )
        self._module.model.active_spectrometer_changed.connect(
            self.module.view.on_active_spectrometer_changed
        )
        self._load_spectrometer_modules()

    def on_measurement_start(self):
        """This method is called when a measurement is started.
        It calls the on_measurement_start method of the active spectrometer.
        """
        logger.debug(
            "Measurement started with spectrometer: %s",
            self.module.model.active_spectrometer,
        )
        self.module.model.active_spectrometer.controller.start_measurement()
