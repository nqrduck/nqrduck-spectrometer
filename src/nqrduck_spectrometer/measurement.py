"""Class for handling measurement data."""

import logging
import numpy as np
from nqrduck.helpers.signalprocessing import SignalProcessing as sp
from nqrduck.helpers.functions import Function

logger = logging.getLogger(__name__)


class Measurement:
    """This class defines how measurement data should look.

    It includes pulse parameters necessary for further signal processing.
    Every spectrometer should adhere to this data structure in order to be compatible with the rest of the nqrduck.

    Args:
        tdx (np.array): Time axis for the x axis of the measurement data.
        tdy (np.array): Time axis for the y axis of the measurement data.
        target_frequency (float): Target frequency of the measurement.
        frequency_shift (float, optional): Frequency shift of the measurement. Defaults to 0.
        IF_frequency (float, optional): Intermediate frequency of the measurement. Defaults to 0.

    Attributes:
        tdx (np.array): Time axis for the x axis of the measurement data.
        tdy (np.array): Time axis for the y axis of the measurement data.
        target_frequency (float): Target frequency of the measurement.
        frequency_shift (float): Frequency shift of the measurement.
        IF_frequency (float): Intermediate frequency of the measurement.
        xf (np.array): Frequency axis for the x axis of the measurement data.
        yf (np.array): Frequency axis for the y axis of the measurement data.
    """

    def __init__(
        self,
        tdx,
        tdy,
        target_frequency,
        frequency_shift: float = 0,
        IF_frequency: float = 0,
    ) -> None:
        """Initializes the measurement."""
        # Convert to decimal 
        self.tdx = tdx
        self.tdy = tdy
        self.target_frequency = target_frequency
        self.fdx, self.fdy = sp.fft(tdx, tdy, frequency_shift)
        self.IF_frequency = IF_frequency

    def apodization(self, function : Function):
        """Applies apodization to the measurement data.

        Args:
            function (Function): Apodization function.

        returns:
            Measurement : The apodized measurement.
        """
        # Get the y data weights from the function
        duration = (self.tdx[-1] - self.tdx[0]) * 1e-6

        resolution = duration / len(self.tdx)

        logger.debug("Resolution: %s", resolution)

        y_weight = function.get_pulse_amplitude(duration, resolution)

        tdy_measurement = self.tdy * y_weight

        apodized_measurement = Measurement(
            self.tdx,
            tdy_measurement,
            target_frequency=self.target_frequency,
            IF_frequency=self.IF_frequency,
        )

        return apodized_measurement


    # Data saving and loading

    def to_json(self):
        """Converts the measurement to a json-compatible format.

        Returns:
            dict : The measurement in json-compatible format.
        """
        return {
            "tdx": self.tdx.tolist(),
            "tdy": [
                [x.real, x.imag] for x in self.tdy
            ],  # Convert complex numbers to list
            "target_frequency": self.target_frequency,
            "IF_frequency": self.IF_frequency,
        }

    @classmethod
    def from_json(cls, json: dict):
        """Converts the json format to a measurement.

        Args:
            json (dict) : The measurement in json-compatible format.

        Returns:
            Measurement : The measurement.
        """
        tdy = np.array([complex(y[0], y[1]) for y in json["tdy"]])
        return cls(
            np.array(json["tdx"]),
            tdy,
            target_frequency=json["target_frequency"],
            IF_frequency=json["IF_frequency"],
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
