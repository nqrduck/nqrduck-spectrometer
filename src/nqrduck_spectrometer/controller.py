import logging
from nqrduck.module.module_controller import ModuleController
from nqrduck.core.main_controller import MainController
from nqrduck_spectrometer.base_spectrometer import BaseSpectrometer

logger = logging.getLogger(__name__)

class SpectrometerController(ModuleController):
    def __init__(self, module):
        super().__init__(module)

    def _load_spectrometer_modules(self):
        # Get the modules with entry points in the nqrduck group
        modules = MainController._get_modules()
        logger.debug("Found modules: %s", modules)

        for module_name, module in modules.items():
            # Check if the module instance is a spectrometer by checking if it inherits from BaseSpectrometer
            if not issubclass(type(module), BaseSpectrometer):
                logger.debug("Module is not a spectrometer: %s ... skipping", module_name)
                continue

            # Import the module
            logger.debug("Loading spectromter module: %s", module_name)
            module.model.widget_changed.connect(self._module.view.on_spectrometer_widget_changed)
            logger.debug("Adding spectrometer to spectrometer model: %s", module_name)
            self._module.model.add_spectrometers(module_name, module)
        
        self._module.view.create_menu_entry()

    def on_loading(self):
        self._module.model.spectrometer_added.connect(self._module.view.on_spectrometer_added)
        self._module.model.active_spectrometer_changed.connect(self._module.view.on_active_spectrometer_changed)
        self._load_spectrometer_modules()