from PyQt6.QtGui import QPixmap
from pathlib import Path
from .base_spectrometer_model import BaseSpectrometerModel

class Option():
    """Defines options for the pulse parameters which can then be set accordingly.
    """
    def set_value(self):
        raise NotImplementedError

class BooleanOption(Option):
    """Defines a boolean option for a pulse parameter.
    """
    def __init__(self, state) -> None:
        super().__init__()
        self.state = state

    def set_value(self, state):
        self.state = state
        
class NumericOption(Option):
    """Defines a numeric option for a pulse parameter.
    """
    def __init__(self, value) -> None:
        super().__init__()
        self.value = value

    def set_value(self, value):
        self.value = float(value)

class WidgetSelectionOption(Option):
    """Defines a widget selection option for a pulse parameter.
    """
    def __init__(self, widgets) -> None:
        super().__init__()


class TXPulse(BaseSpectrometerModel.PulseParameter):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.add_option("TX Amplitude", NumericOption(0))
        self.add_option("TX Phase", NumericOption(0))

    def get_pixmap(self):
        self_path = Path(__file__).parent
        if self.options["TX Amplitude"].value > 0:
            image_path = self_path / "resources/pulseparameter/wip_txpulse.png"
        else:
            image_path = self_path / "resources/pulseparameter/wip_no_txpulse.png"
        pixmap = QPixmap(str(image_path))
        return pixmap

    class RectPulse():
        def __init__(self, name) -> None:
            super().__init__(name)
  
    class SincPulse():
        def __init__(self, name) -> None:
            super().__init__(name)

    class GaussianPulse():
        def __init__(self, name) -> None:
            super().__init__(name)

class RXReadout(BaseSpectrometerModel.PulseParameter):
    def __init__(self, name) -> None:
        super().__init__(name)

class Gate(BaseSpectrometerModel.PulseParameter):
    
    def __init__(self, name) -> None:
        super().__init__(name)
        self.add_option("Gate State", BooleanOption(False))

    def get_pixmap(self):
        self_path = Path(__file__).parent
        if self.options["Gate State"].state == False:
            image_path = self_path / "resources/pulseparameter/wip_no_txpulse.png"
        else:
            image_path = self_path / "resources/pulseparameter/wip_txpulse.png"
        pixmap = QPixmap(str(image_path))
        return pixmap

    def set_options(self, options):
        self.state = options

    