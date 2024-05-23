"""Class for handling measurement data."""

import logging
import numpy as np
from scipy.optimize import curve_fit
from sympy.utilities.lambdify import lambdify
from nqrduck.helpers.signalprocessing import SignalProcessing as sp
from nqrduck.helpers.functions import Function

logger = logging.getLogger(__name__)


class Measurement:
    """This class defines how measurement data should look.

    It includes pulse parameters necessary for further signal processing.
    Every spectrometer should adhere to this data structure in order to be compatible with the rest of the nqrduck.

    Args:
        name (str): Name of the measurement.
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
        name: str,
        tdx: np.array,
        tdy: np.array,
        target_frequency: float,
        frequency_shift: float = 0,
        IF_frequency: float = 0,
    ) -> None:
        """Initializes the measurement."""
        self.name = name
        self.tdx = tdx
        self.tdy = tdy
        self.target_frequency = target_frequency
        self.fdx, self.fdy = sp.fft(tdx, tdy, frequency_shift)
        self.IF_frequency = IF_frequency

        self.fits = []

    def apodization(self, function: Function):
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
            self.name,
            self.tdx,
            tdy_measurement,
            target_frequency=self.target_frequency,
            IF_frequency=self.IF_frequency,
        )

        return apodized_measurement

    def add_fit(self, fit):
        """Adds a fit to the measurement.

        Args:
            fit (Fit): The fit to add.
        """
        self.fits.append(fit)

    def delete_fit(self, fit):
        """Deletes a fit from the measurement.
        
        Args:
            fit (Fit): The fit to delete.
        """

        self.fits.remove(fit)

    def edit_fit_name(self, fit, name : str):
        """Edits the name of a fit.

        Args:
            fit (Fit): The fit to edit.
            name (str): The new name.
        """
        logger.debug(f"Editing fit name to {name}.")
        fit.name = name

    # Data saving and loading

    def to_json(self):
        """Converts the measurement to a json-compatible format.

        Returns:
            dict : The measurement in json-compatible format.
        """
        return {
            "name": self.name,
            "tdx": self.tdx.tolist(),
            "tdy": [
                [x.real, x.imag] for x in self.tdy
            ],  # Convert complex numbers to list
            "target_frequency": self.target_frequency,
            "IF_frequency": self.IF_frequency,
            "fits": [fit.to_json() for fit in self.fits],
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
            json["name"],
            np.array(json["tdx"]),
            tdy,
            target_frequency=json["target_frequency"],
            IF_frequency=json["IF_frequency"],
            fits=[Fit.from_json(fit) for fit in json["fits"]],
        )

    # Measurement data
    @property
    def name(self):
        """Name of the measurement."""
        return self._name
    
    @name.setter
    def name(self, value):
        self._name = value

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

    @property
    def fits(self):
        """Fits of the measurement."""
        return self._fits
    
    @fits.setter
    def fits(self, value):
        self._fits = value

class Fit():
    """The fit class for measurement data. A fit can be performed on either the frequency or time domain data.
    
    A measurement can have multiple fits.

    Examples for fits in time domain would be the T2* relaxation time, while in frequency domain it could be the line width.

    A fit has a name, a nqrduck function and a strategy for the algorithm to use.
    """

    def __init__(self, name: str, domain: str, measurement : Measurement) -> None:
        """Initializes the fit."""
        self.name = name
        self.domain = domain
        self.measurement = measurement

    def fit(self):
        """Fits the measurement data, sets the x and y data and returns the fit parameters and covariance. """
        if self.domain == "time":
            x = self.measurement.tdx
            y = self.measurement.tdy
        elif self.domain == "frequency":
            x = self.measurement.fdx
            y = self.measurement.fdy
        else:
            raise ValueError("Domain not recognized.")

        initial_guess = self.initial_guess()
        parameters, covariance = curve_fit(self.fit_function, x, abs(y), p0=initial_guess)

        self.x = x
        self.y = self.fit_function(x, *parameters)

        
        return parameters, covariance
    
    def get_fit_parameters_string(self):
        """Get the fit parameters as a string.

        Returns:
            str : The fit parameters as a string.
        """
        return " ".join([f"{param:.2f}" for param in self.parameters])
    
    def fit_function(self, x, *parameters):
        """The fit function.

        Args:
            x (np.array): The x data.
            *parameters : The fit parameters.

        Returns:
            np.array : The y data.
        """
        raise NotImplementedError
    
    def initial_guess(self):
        """Initial guess for the fit.

        Returns:
            list : The initial guess.
        """
        raise NotImplementedError
        

    def to_json(self):
        """Converts the fit to a json-compatible format.

        Returns:
            dict : The fit in json-compatible format.
        """
        return {
            "name": self.name,
            "function": self.function.to_json(),
            "strategy": self.strategy,
        }
    
    @classmethod
    def from_json(cls, json: dict):
        """Converts the json format to a fit.

        Args:
            json (dict) : The fit in json-compatible format.

        Returns:
            Fit : The fit.
        """
        function = Function.from_json(json["function"])
        return cls(json["name"], function, json["strategy"])
    
    @property
    def x(self):
        """The x data of the fit."""
        return self._x
    
    @x.setter
    def x(self, value):
        self._x = value

    @property
    def y(self):
        """The y data of the fit."""
        return self._y
    
    @y.setter
    def y(self, value):
        self._y = value
    
class T2StarFit(Fit):

    def __init__(self, measurement: Measurement) -> None:
        self.name = "T2*"
        self.domain = "time"
        self.measurement = measurement
    
    def fit(self):
        parameters, covariance = super().fit()
        # Create dict with fit parameters and covariance
        self.parameters = {
            "S0": parameters[0],
            "T2Star": parameters[1],
            "covariance": covariance
        }

    def fit_function (self, t, S0, T2Star):
        return S0 * np.exp(-t / T2Star)
    
    def initial_guess(self):
        return [1, 1]