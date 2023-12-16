import logging
import numpy as np
from nqrduck.helpers.signalprocessing import SignalProcessing as sp

logger = logging.getLogger(__name__)

class Measurement():
    """This class defines how measurement data should look. 
    It includes pulse parameters necessary for further signal processing.
    Every spectrometer should adhere to this data structure in order to be compatible with the rest of the nqrduck.

    Attributes:
        tdx (np.array): Time axis for the x axis of the measurement data.
        tdy (np.array): Time axis for the y axis of the measurement data.
        target_frequency (float): Target frequency of the measurement.
        frequency_shift (float): Frequency shift of the measurement.
        IF_frequency (float): Intermediate frequency of the measurement.
        xf (np.array): Frequency axis for the x axis of the measurement data.
        yf (np.array): Frequency axis for the y axis of the measurement data.
    """

    def __init__(self, tdx, tdy, target_frequency, frequency_shift : float = 0, IF_frequency : float = 0) -> None:
        self.tdx = tdx
        self.tdy = tdy
        self.target_frequency = target_frequency
        self.fdx, self.fdy = sp.fft(tdx, tdy, frequency_shift)
        self.IF_frequency = IF_frequency

    # Data saving and loading

    def to_json(self):
        """Converts the measurement to a json-compatible format."""
        return {
            "tdx": [[x.real, x.imag] for x in self.tdx], # Convert complex numbers to list
            "tdy": [[x.real, x.imag] for x in self.tdy], # Convert complex numbers to list
            "target_frequency": self.target_frequency,
            "IF_frequency": self.IF_frequency
        }
    
    @classmethod
    def from_json(cls, json):
        """Converts the json format to a measurement."""
        tdx = np.array([complex(x[0], x[1]) for x in json["tdx"]])
        tdy = np.array([complex(y[0], y[1]) for y in json["tdy"]])
        return cls(
            tdx,
            tdy,
            json["target_frequency"],
            json["IF_frequency"]
        )

    # Measurement data
    @property
    def tdx(self):
        """Time axis for the x axis of the measurement data."""
        return self._tdx
    
    @tdx.setter
    def tdx(self, value):
        self._tdx = value

    @property
    def tdy(self):
        """Time axis for the y axis of the measurement data."""
        return self._tdy
    
    @tdy.setter
    def tdy(self, value):
        self._tdy = value

    @property
    def fdx(self):
        """Frequency axis for the x axis of the measurement data."""
        return self._fdx
    
    @fdx.setter
    def fdx(self, value):
        self._fdx = value

    @property
    def fdy(self):
        """Frequency axis for the y axis of the measurement data."""
        return self._fdy
    
    @fdy.setter
    def fdy(self, value):
        self._fdy = value

    # Pulse parameters
    @property
    def target_frequency(self):
        """Target frequency of the measurement."""
        return self._target_frequency
    
    @target_frequency.setter
    def target_frequency(self, value):
        self._target_frequency = value
