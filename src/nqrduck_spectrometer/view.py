import logging
from PyQt5.QtWidgets import QWidget, QToolButton, QToolBar, QAction, QMenu
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

    def on_active_spectrometer_changed(self, module):
        self._ui_form.stackedWidget.setCurrentWidget(module._inner_view)

    def on_spectrometer_widget_changed(self, widget):
        logger.debug("Adding module widget to stacked widget: %s", widget)
        self._ui_form.stackedWidget.addWidget(widget)
        self._ui_form.stackedWidget.setCurrentWidget(widget)


    def on_spectrometer_added(self, module):
        """This method changes the active spectrometer to the one that was just added."""
        self.on_spectrometer_widget_changed(module._inner_view)

    def create_menu_entry(self):
        logger.debug("Creating menu entry for spectrometer module")
        menu_item = QMenu("Hardware")
        logger.debug("Available spectrometer models: %s", self._module.model._available_spectrometers)

        actions = []
        for spectrometer_name, spectrometer_module in self._module.model._available_spectrometers.items():
            logger.debug("Adding module to menu: %s", spectrometer_name)
            select_action = QAction(spectrometer_module.model.toolbar_name, menu_item)
            select_action.triggered.connect(lambda: self.on_menu_button_clicked(spectrometer_name))
            actions.append(select_action)
        
        self.add_menubar_item.emit("Hardware", actions)

    def on_menu_button_clicked(self, spectrometer_name):
        logger.debug("Active module changed to: %s", spectrometer_name)
        self._module.model.active_spectrometer = self._module.model.available_spectrometers[spectrometer_name]
