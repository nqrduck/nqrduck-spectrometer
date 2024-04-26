"""Contains the classes for the pulse parameters of the spectrometer. It includes the functions and the options for the pulse parameters.

Todo:
    * This shouldn't be in the spectrometer module. It should be in it"s own pulse sequence module.
"""

from __future__ import annotations
import logging

from numpy.core.multiarray import array as array

from nqrduck.assets.icons import PulseParamters
from nqrduck.helpers.functions import (
    Function,
    RectFunction,
    SincFunction,
    GaussianFunction,
    CustomFunction,
)
from .base_spectrometer_model import BaseSpectrometerModel

logger = logging.getLogger(__name__)


class Option:
    """Defines options for the pulse parameters which can then be set accordingly.

    Options can be of different types, for example boolean, numeric or function.

    Args:
        name (str): The name of the option.
        value: The value of the option.

    Attributes:
        name (str): The name of the option.
        value: The value of the option.
    """

    subclasses = []

    def __init_subclass__(cls, **kwargs):
        """Adds the subclass to the list of subclasses."""
        super().__init_subclass__(**kwargs)
        cls.subclasses.append(cls)

    def __init__(self, name: str, value) -> None:
        """Initializes the option."""
        self.name = name
        self.value = value

    def set_value(self):
        """Sets the value of the option.

        This method has to be implemented in the derived classes.
        """
        raise NotImplementedError

    def to_json(self):
        """Returns a json representation of the option.

        Returns:
            dict: The json representation of the option.
        """
        return {
            "name": self.name,
            "value": self.value,
            "class": self.__class__.__name__,
        }

    @classmethod
    def from_json(cls, data) -> Option:
        """Creates an option from a json representation.

        Args:
            data (dict): The json representation of the option.

        Returns:
            Option: The option.
        """
        for subclass in cls.subclasses:
            logger.debug(f"Keys data: {data.keys()}")
            if subclass.__name__ == data["class"]:
                cls = subclass
                break

        # Check if from_json is implemented for the subclass
        if cls.from_json.__func__ == Option.from_json.__func__:
            obj = cls(data["name"], data["value"])
        else:
            obj = cls.from_json(data)

        return obj


class BooleanOption(Option):
    """Defines a boolean option for a pulse parameter option."""

    def set_value(self, value):
        """Sets the value of the option."""
        self.value = value


class NumericOption(Option):
    """Defines a numeric option for a pulse parameter option."""

    def __init__(
        self, name: str, value, is_float=True, min_value=None, max_value=None
    ) -> None:
        """Initializes the NumericOption.
        
        Args:
            name (str): The name of the option.
            value: The value of the option.
            is_float (bool): If the value is a float.
            min_value: The minimum value of the option.
            max_value: The maximum value of the option.
        """
        super().__init__(name, value)
        self.is_float = is_float
        self.min_value = min_value
        self.max_value = max_value

    def set_value(self, value):
        """Sets the value of the option."""
        if value < self.min_value:
            self.value = self.min_value
        elif value >= self.max_value:
            self.value = self.max_value
        else:
            raise ValueError(
                f"Value {value} is not in the range of {self.min_value} to {self.max_value}. This should have been cought earlier."
            )

    def to_json(self):
        """Returns a json representation of the option.

        Returns:
            dict: The json representation of the option.
        """
        return {
            "name": self.name,
            "value": self.value,
            "class": self.__class__.__name__,
            "is_float": self.is_float,
            "min_value": self.min_value,
            "max_value": self.max_value,
        }
    
    @classmethod
    def from_json(cls, data):
        """Creates a NumericOption from a json representation.

        Args:
            data (dict): The json representation of the NumericOption.

        Returns:
            NumericOption: The NumericOption.
        """
        obj = cls(
            data["name"],
            data["value"],
            is_float=data["is_float"],
            min_value=data["min_value"],
            max_value=data["max_value"],
        )
        return obj


class FunctionOption(Option):
    """Defines a selection option for a pulse parameter option.

    It takes different function objects.

    Args:
        name (str): The name of the option.
        functions (list): The functions that can be selected.

    Attributes:
        name (str): The name of the option.
        functions (list): The functions that can be selected.
    """

    def __init__(self, name, functions) -> None:
        """Initializes the FunctionOption."""
        super().__init__(name, functions[0])
        self.functions = functions

    def set_value(self, value):
        """Sets the value of the option.

        Args:
            value: The value of the option.
        """
        self.value = value

    def get_function_by_name(self, name):
        """Returns the function with the given name.

        Args:
            name (str): The name of the function.

        Returns:
            Function: The function with the given name.
        """
        for function in self.functions:
            if function.name == name:
                return function
        raise ValueError(f"Function with name {name} not found")

    def to_json(self):
        """Returns a json representation of the option.

        Returns:
            dict: The json representation of the option.
        """
        return {
            "name": self.name,
            "value": self.value.to_json(),
            "class": self.__class__.__name__,
            "functions": [function.to_json() for function in self.functions],
        }

    @classmethod
    def from_json(cls, data):
        """Creates a FunctionOption from a json representation.

        Args:
            data (dict): The json representation of the FunctionOption.

        Returns:
            FunctionOption: The FunctionOption.
        """
        logger.debug(f"Data: {data}")
        # These are all available functions
        functions = [Function.from_json(function) for function in data["functions"]]
        obj = cls(data["name"], functions)
        obj.value = Function.from_json(data["value"])
        return obj

    def get_pixmap(self):
        """Returns the pixmap of the function."""
        return self.value.get_pixmap()


class TXRectFunction(RectFunction):
    """TX Rectangular function.

    Adds the pixmap of the function to the class.
    """

    def __init__(self) -> None:
        """Initializes the TX Rectangular function."""
        super().__init__()
        self.name = "Rectangular"

    def get_pixmap(self):
        """Returns the pixmaps of the function."""
        return PulseParamters.TXRect()


class TXSincFunction(SincFunction):
    """TX Sinc function.

    Adds the pixmap of the function to the class.
    """

    def __init__(self) -> None:
        """Initializes the TX Sinc function."""
        super().__init__()
        self.name = "Sinc"

    def get_pixmap(self):
        """Returns the pixmaps of the function."""
        return PulseParamters.TXSinc()


class TXGaussianFunction(GaussianFunction):
    """TX Gaussian function.

    Adds the pixmap of the function to the class.
    """

    def __init__(self) -> None:
        """Initializes the TX Gaussian function."""
        super().__init__()
        self.name = "Gaussian"

    def get_pixmap(self):
        """Returns the pixmaps of the function."""
        return PulseParamters.TXGauss()


class TXCustomFunction(CustomFunction):
    """TX Custom function.

    Adds the pixmap of the function to the class.
    """

    def __init__(self) -> None:
        """Initializes the TX Custom function."""
        super().__init__()
        self.name = "Custom"

    def get_pixmap(self):
        """Returns the pixmaps of the function."""
        return PulseParamters.TXCustom()


class TXPulse(BaseSpectrometerModel.PulseParameter):
    """Basic TX Pulse Parameter. It includes options for the relative amplitude, the phase and the pulse shape.

    Args:
        name (str): The name of the pulse parameter.
    """

    RELATIVE_AMPLITUDE = "Relative TX Amplitude (%)"
    TX_PHASE = "TX Phase"
    TX_PULSE_SHAPE = "TX Pulse Shape"

    def __init__(self, name: str) -> None:
        """Initializes the TX Pulse Parameter.

        It adds the options for the relative amplitude, the phase and the pulse shape.
        """
        super().__init__(name)
        self.add_option(
            NumericOption(
                self.RELATIVE_AMPLITUDE, 0, is_float=False, min_value=0, max_value=100
            )
        )
        self.add_option(NumericOption(self.TX_PHASE, 0))
        self.add_option(
            FunctionOption(
                self.TX_PULSE_SHAPE,
                [
                    TXRectFunction(),
                    TXSincFunction(),
                    TXGaussianFunction(),
                    TXCustomFunction(),
                ],
            ),
        )

    def get_pixmap(self):
        """Returns the pixmap of the TX Pulse Parameter.

        Returns:
            QPixmap: The pixmap of the TX Pulse Parameter depending on the relative amplitude.
        """
        if self.get_option_by_name(self.RELATIVE_AMPLITUDE).value > 0:
            return self.get_option_by_name(self.TX_PULSE_SHAPE).get_pixmap()
        else:
            pixmap = PulseParamters.TXOff()
            return pixmap


class RXReadout(BaseSpectrometerModel.PulseParameter):
    """Basic PulseParameter for the RX Readout. It includes an option for the RX Readout state.

    Args:
        name (str): The name of the pulse parameter.

    Attributes:
        RX (str): The RX Readout state.
    """

    RX = "RX"

    def __init__(self, name) -> None:
        """Initializes the RX Readout PulseParameter.

        It adds an option for the RX Readout state.
        """
        super().__init__(name)
        self.add_option(BooleanOption(self.RX, False))

    def get_pixmap(self):
        """Returns the pixmap of the RX Readout PulseParameter.

        Returns:
            QPixmap: The pixmap of the RX Readout PulseParameter depending on the RX Readout state.
        """
        if self.get_option_by_name(self.RX).value is False:
            pixmap = PulseParamters.RXOff()
        else:
            pixmap = PulseParamters.RXOn()
        return pixmap


class Gate(BaseSpectrometerModel.PulseParameter):
    """Basic PulseParameter for the Gate. It includes an option for the Gate state.

    Args:
        name (str): The name of the pulse parameter.

    Attributes:
        GATE_STATE (str): The Gate state.
    """

    GATE_STATE = "Gate State"

    def __init__(self, name) -> None:
        """Initializes the Gate PulseParameter.

        It adds an option for the Gate state.
        """
        super().__init__(name)
        self.add_option(BooleanOption(self.GATE_STATE, False))

    def get_pixmap(self):
        """Returns the pixmap of the Gate PulseParameter.

        Returns:
            QPixmap: The pixmap of the Gate PulseParameter depending on the Gate state.
        """
        if self.get_option_by_name(self.GATE_STATE).value is False:
            pixmap = PulseParamters.GateOff()
        else:
            pixmap = PulseParamters.GateOn()
        return pixmap
