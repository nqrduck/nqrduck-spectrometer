from ...spectrometer import Spectrometer

class LimeNQR(Spectrometer):
    def __init__(self, model, controller):
        super(LimeNQR, self).__init__(model, controller)
        self._model = model
        self._controller = controller
        