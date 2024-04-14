"""View for the Spectrometer Module. Careful - this is not the base class for the spectrometer submodules, but the view for the spectrometer module itself."""

import logging
from PyQt6.QtWidgets import QWidget, QMenu
from PyQt6.QtGui import QAction
from PyQt6.QtCore import pyqtSlot
from nqrduck.module.module_view import ModuleView
from .widget import Ui_Form

logger = logging.getLogger(__name__)


class SpectrometerView(ModuleView):
    """The view for the spectrometer module. This class is responsible for displaying the spectrometer module in the main window.

    It contains the menu buttons for the different spectrometers and the stacked widget that shows the different spectrometer views.

    Args:
        module (Module) : The spectrometer module that this view belongs to
    """

    def __init__(self, module):
        """Initializes the spectrometer view. It sets up the UI and the stacked widget for the spectrometers."""
        super().__init__(module)

        widget = QWidget()
        self._ui_form = Ui_Form()
        self.widget = widget
        self._ui_form.setupUi(self)
        self._actions = dict()

        self.blank = QWidget()

        self._ui_form.stackedWidgetSettings.setStyleSheet(
            "QStackedWidget { border: 2px solid #000; }"
        )

        self._ui_form.stackedWidgetPulseProgrammer.setStyleSheet(
            "QStackedWidget { border: 2px solid #000; }"
        )

    def on_active_spectrometer_changed(self, module):
        """This method is called when the active spectrometer is changed.

        It changes the active view in the stacked widget to the one that was just activated.

        Args:
            module (BaseSpectrometer) : The spectrometer module that was just activated
        """
        self._ui_form.stackedWidgetSettings.setCurrentWidget(module.settings_view)

        try:
            self._ui_form.stackedWidgetPulseProgrammer.setCurrentWidget(
                module.model.pulse_programmer.pulse_programmer_view
            )
        except AttributeError:
            logger.debug(
                "No pulse programmer widget to change to for spectrometer %s",
                module.model.name,
            )
            self._ui_form.stackedWidgetPulseProgrammer.setCurrentWidget(self.blank)

    def on_spectrometer_widget_changed(self, module):
        """This method is called when a new spectrometer widget is added to the module.

        It adds the widget to the stacked widget and sets it as the current widget.

        Args:
            module (BaseSpectrometer) : The spectrometer module that was just added
        """
        logger.debug(
            "Adding settings widget to stacked widget: %s", module.settings_view
        )
        self._ui_form.stackedWidgetSettings.addWidget(module.settings_view)
        self._ui_form.stackedWidgetSettings.setCurrentWidget(module.settings_view)

        try:
            logger.debug(
                "Adding pulse programmer widget to stacked widget: %s",
                module.model.pulse_programmer.pulse_programmer_view,
            )
            self._ui_form.stackedWidgetPulseProgrammer.addWidget(
                module.model.pulse_programmer.pulse_programmer_view
            )
            self._ui_form.stackedWidgetPulseProgrammer.setCurrentWidget(
                module.model.pulse_programmer.pulse_programmer_view
            )
        except AttributeError:
            logger.debug(
                "No pulse programmer widget to add for spectrometer %s",
                module.model.name,
            )
            # Sets the pulse programmer widget to a blank widget if there is no pulse programmer widget.
            self._ui_form.stackedWidgetPulseProgrammer.addWidget(self.blank)
            self._ui_form.stackedWidgetPulseProgrammer.setCurrentWidget(self.blank)

    def on_spectrometer_added(self, module):
        """This method changes the active spectrometer to the one that was just added.

        Args:
            module (BaseSpectrometer) : The spectrometer module that was just added
        """
        module.change_spectrometer.connect(self.on_menu_button_clicked)
        self.on_spectrometer_widget_changed(module)

    def create_menu_entry(self):
        """This method creates the menu entry for the spectrometer module. It creates a menu item for each spectrometer that is available."""
        logger.debug("Creating menu entry for spectrometer module")
        menu_item = QMenu("Hardware")
        logger.debug(
            "Available spectrometer models: %s",
            self._module.model._available_spectrometers,
        )

        # Create an header action called 'Spectrometer"
        self._actions["Spectrometer"] = QAction("Spectrometer:", menu_item)
        font = self._actions["Spectrometer"].font()
        font.setBold(True)
        self._actions["Spectrometer"].setFont(font)
        self._actions["Spectrometer"].setEnabled(False)
        menu_item.addSeparator()

        for (
            spectrometer_name,
            spectrometer_module,
        ) in self._module.model._available_spectrometers.items():
            logger.debug("Adding module to menu: %s", spectrometer_name)
            self._actions[spectrometer_name] = QAction(
                spectrometer_module.model.toolbar_name, menu_item
            )
            self._actions[spectrometer_name].triggered.connect(
                spectrometer_module.set_active
            )
            # Make it checkable
            self._actions[spectrometer_name].setCheckable(True)

        # Get last added action and check it
        last_added_action = self._actions[list(self._actions.keys())[-1]]
        last_added_action.setChecked(True)

        self.add_menubar_item.emit("Hardware", list(self._actions.values()), True)

    @pyqtSlot(str)
    def on_menu_button_clicked(self, spectrometer_name):
        """This method is called when a menu button is clicked.

        It changes the active spectrometer to the one that was clicked.
        It also unchecks all other menu buttons.

        Args:
            spectrometer_name (str) : The name of the spectrometer that was clicked
        """
        logger.debug("Active module changed to: %s", spectrometer_name)
        for action in self._actions.values():
            action.setChecked(False)
        self._actions[spectrometer_name].setChecked(True)
        self._module.model.active_spectrometer = (
            self._module.model.available_spectrometers[spectrometer_name]
        )
