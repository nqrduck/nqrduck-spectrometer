import logging
from PyQt5.QtWidgets import QWidget, QToolButton, QToolBar, QAction, QMenu
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from nqrduck.module.module_view import ModuleView
from .widget import Ui_Form

logger = logging.getLogger(__name__)

class SpectrometerView(ModuleView):
    def __init__(self, module):
        super().__init__(module)

        widget = QWidget()
        self._ui_form = Ui_Form()
        self.widget = widget
        self._ui_form.setupUi(self)
        self._actions = dict()

    def on_active_spectrometer_changed(self, module):
        self._ui_form.stackedWidget.setCurrentWidget(module._inner_view)

    def on_spectrometer_widget_changed(self, widget):
        logger.debug("Adding module widget to stacked widget: %s", widget)
        self._ui_form.stackedWidget.addWidget(widget)
        self._ui_form.stackedWidget.setCurrentWidget(widget)


    def on_spectrometer_added(self, module):
        """This method changes the active spectrometer to the one that was just added."""
        module.change_spectrometer.connect(self.on_menu_button_clicked)
        self.on_spectrometer_widget_changed(module._inner_view)

    def create_menu_entry(self):
        logger.debug("Creating menu entry for spectrometer module")
        menu_item = QMenu("Hardware")
        logger.debug("Available spectrometer models: %s", self._module.model._available_spectrometers)

        
        for spectrometer_name, spectrometer_module in self._module.model._available_spectrometers.items():
            logger.debug("Adding module to menu: %s", spectrometer_name)
            self._actions[spectrometer_name] = QAction(spectrometer_module.model.toolbar_name, menu_item)
            self._actions[spectrometer_name].triggered.connect(spectrometer_module.set_active)
            # Make it checkable
            self._actions[spectrometer_name].setCheckable(True)
        
        # Get last added action and check it
        last_added_action = self._actions[list(self._actions.keys())[-1]]
        last_added_action.setChecked(True)

        self.add_menubar_item.emit("Hardware", list(self._actions.values()))

    @pyqtSlot(str)
    def on_menu_button_clicked(self, spectrometer_name):
        """This method is called when a menu button is clicked. It changes the active spectrometer to the one that was clicked.
        It also unchecks all other menu buttons.

        :param spectrometer_name: The name of the spectrometer that was clicked."""
        logger.debug("Active module changed to: %s", spectrometer_name)
        for action in self._actions.values():
            action.setChecked(False)
        self._actions[spectrometer_name].setChecked(True)
        self._module.model.active_spectrometer = self._module.model.available_spectrometers[spectrometer_name]

