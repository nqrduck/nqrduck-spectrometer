from PyQt6.QtGui import QPixmap
from pathlib import Path
from .base_spectrometer_model import BaseSpectrometerModel

class TXPulse(BaseSpectrometerModel.PulseParameter):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.tx_state = False
        self.tx_phase = 0

        # Create a button
        self.button = QPushButton(self)
        self.button.setGeometry(0, 0, 200, 200)

        # Set a custom image for the button
        image_path = "resources/wip_no_pulse.png"
        pixmap = QPixmap(image_path)
        self.button.setIcon(pixmap)
        self.button.setIconSize(pixmap.size())

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
            self.rx_freq = 0
            self.rx_phase = 0

class TXPhase(BaseSpectrometerModel.PulseParameter):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.phase = 0

class RXPhase(BaseSpectrometerModel.PulseParameter):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.phase = 0

class Gate(BaseSpectrometerModel.PulseParameter):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.state = False

    def get_pixmap(self):
        self_path = Path(__file__).parent
        if self.state is False:
            image_path = self_path / "resources/pulseparameter/wip_no_txpulse.png"
        elif self.state is True:
            image_path = self_path / "resources/pulseparameter/wip_txpulse.png"
        pixmap = QPixmap(str(image_path))
        return pixmap

    def get_options(self):
        return (bool, self.state)
    
    def set_options(self, options):
        self.state = options

    