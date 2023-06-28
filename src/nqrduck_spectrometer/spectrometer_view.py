from PyQt5.QtWidgets import QWidget
from nqrduck.module.module_view import ModuleView
from .spectrometer_widget import Ui_Form


class SpectrometerView(ModuleView):
    def __init__(self, model, controller):
        super().__init__(model, controller)

        widget = QWidget()
        self._ui_form = Ui_Form()
        self._ui_form.setupUi(widget)
        self._model.widget = widget
