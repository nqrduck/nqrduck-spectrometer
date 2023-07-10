import logging
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QHBoxLayout, QSizePolicy
from nqrduck.module.module_view import ModuleView

logger = logging.getLogger(__name__)


class BaseSpectrometerView(ModuleView):
    
    def __init__(self, module):
        super().__init__(module)

    def load_settings_ui(self):
        """This method automaticall generates a view for the settings of the module.
        If there is a widget file that has been generated by Qt Designer, it will be used. Otherwise, a default view will be generated."""
        
        from .base_spectrometer_widget import Ui_Form
        widget = QWidget()
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._ui_form = Ui_Form()
        self.widget = widget
        self._ui_form.setupUi(self)

        # Add name of the spectrometer to the view
        label = QLabel("%s Settings:" % self.module.model.toolbar_name)
        label.setStyleSheet("font-weight: bold;")
        self._ui_form.verticalLayout.setSpacing(5)
        self._ui_form.verticalLayout.addWidget(label)

        for setting in self.module.model.settings.values():
            logger.debug("Adding setting to settings view: %s", setting.name)
            # Create a label for the setting
            label = QLabel(setting.name)
            label.setMinimumWidth(70)
            # Add an QLineEdit for the setting
            line_edit = QLineEdit(str(setting.value))
            line_edit.setMinimumWidth(100)
            # Add a horizontal layout for the setting
            layout = QHBoxLayout()
            # Connect the editingFinished signal to the on_value_changed slot of the setting
            line_edit.editingFinished.connect(lambda: setting.on_value_changed(line_edit.text()))
            # Add the label and the line edit to the layout
            layout.addWidget(label)
            layout.addWidget(line_edit)
            layout.addStretch(1)
            # Add the layout to the vertical layout of the widget
            self._ui_form.verticalLayout.addLayout(layout)
        
        # Push all the settings to the top of the widget
        self._ui_form.verticalLayout.addStretch(1)

        