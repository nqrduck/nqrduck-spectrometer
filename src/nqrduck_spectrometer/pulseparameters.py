"""Contains the classes for the pulse parameters of the spectrometer. It includes the functions and the options for the pulse parameters.

Todo:
    * This shouldn't be in the spectrometer module. It should be in it"s own pulse sequence module.
"""

from __future__ import annotations
import logging
import numpy as np
import sympy
from decimal import Decimal
from PyQt6.QtGui import QPixmap
from nqrduck.contrib.mplwidget import MplWidget
from nqrduck.helpers.signalprocessing import SignalProcessing as sp
from nqrduck.assets.icons import PulseParamters
from .base_spectrometer_model import BaseSpectrometerModel

logger = logging.getLogger(__name__)


class Function:
    """A function that can be used as a pulse parameter.

    This class is the base class for all functions that can be used as pulse parameters. Functions can be used for pulse shapes, for example.

    Args:
        expr (str | sympy.Expr): The expression of the function.

    Attributes:
        name (str): The name of the function.
        parameters (list): The parameters of the function.
        expr (sympy.Expr): The sympy expression of the function.
        resolution (Decimal): The resolution of the function in seconds.
        start_x (float): The x value where the evalution of the function starts.
        end_x (float): The x value where the evalution of the function ends.
    """

    name: str
    parameters: list
    expression: str | sympy.Expr
    resolution: Decimal
    start_x: float
    end_x: float

    def __init__(self, expr) -> None:
        """Initializes the function."""
        self.parameters = []
        self.expr = expr
        self.resolution = Decimal(1 / 30.72e6)
        self.start_x = -1
        self.end_x = 1

    def get_time_points(self, pulse_length: Decimal) -> np.ndarray:
        """Returns the time domain points for the function with the given pulse length.

        Args:
            pulse_length (Decimal): The pulse length in seconds.

        Returns:
            np.ndarray: The time domain points.
        """
        # Get the time domain points
        n = int(pulse_length / self.resolution)
        t = np.linspace(0, float(pulse_length), n)
        return t

    def evaluate(self, pulse_length: Decimal, resolution: Decimal = None) -> np.ndarray:
        """Evaluates the function for the given pulse length.

        Args:
            pulse_length (Decimal): The pulse length in seconds.
            resolution (Decimal, optional): The resolution of the function in seconds. Defaults to None.

        Returns:
            np.ndarray: The evaluated function.
        """
        if resolution is None:
            resolution = self.resolution
        n = int(pulse_length / resolution)
        t = np.linspace(self.start_x, self.end_x, n)
        x = sympy.symbols("x")

        found_variables = dict()
        # Create a dictionary of the parameters and their values
        for parameter in self.parameters:
            found_variables[parameter.symbol] = parameter.value

        final_expr = self.expr.subs(found_variables)
        # If the expression is a number (does not depend on x), return an array of that number
        if final_expr.is_number:
            return np.full(t.shape, float(final_expr))

        f = sympy.lambdify([x], final_expr, "numpy")

        return f(t)

    def get_tdx(self, pulse_length: float) -> np.ndarray:
        """Returns the time domain points and the evaluated function for the given pulse length.

        Args:
            pulse_length (float): The pulse length in seconds.

        Returns:
            np.ndarray: The time domain points.
        """
        n = int(pulse_length / self.resolution)
        t = np.linspace(self.start_x, self.end_x, n)
        return t

    def frequency_domain_plot(self, pulse_length: Decimal) -> MplWidget:
        """Plots the frequency domain of the function for the given pulse length.

        Args:
            pulse_length (Decimal): The pulse length in seconds.

        Returns:
            MplWidget: The matplotlib widget containing the plot.
        """
        mpl_widget = MplWidget()
        td = self.get_time_points(pulse_length)
        yd = self.evaluate(pulse_length)
        xdf, ydf = sp.fft(td, yd)
        mpl_widget.canvas.ax.plot(xdf, abs(ydf))
        mpl_widget.canvas.ax.set_xlabel("Frequency in Hz")
        mpl_widget.canvas.ax.set_ylabel("Magnitude")
        mpl_widget.canvas.ax.grid(True)
        return mpl_widget

    def time_domain_plot(self, pulse_length: Decimal) -> MplWidget:
        """Plots the time domain of the function for the given pulse length.

        Args:
            pulse_length (Decimal): The pulse length in seconds.

        Returns:
            MplWidget: The matplotlib widget containing the plot.
        """
        mpl_widget = MplWidget()
        td = self.get_time_points(pulse_length)
        mpl_widget.canvas.ax.plot(td, abs(self.evaluate(pulse_length)))
        mpl_widget.canvas.ax.set_xlabel("Time in s")
        mpl_widget.canvas.ax.set_ylabel("Magnitude")
        mpl_widget.canvas.ax.grid(True)
        return mpl_widget

    def get_pulse_amplitude(
        self, pulse_length: Decimal, resolution: Decimal = None
    ) -> np.array:
        """Returns the pulse amplitude in the time domain.

        Args:
            pulse_length (Decimal): The pulse length in seconds.
            resolution (Decimal, optional): The resolution of the function in seconds. Defaults to None.

        Returns:
            np.array: The pulse amplitude.
        """
        return self.evaluate(pulse_length, resolution=resolution)

    def add_parameter(self, parameter: Function.Parameter) -> None:
        """Adds a parameter to the function.

        Args:
        parameter (Function.Parameter): The parameter to add.
        """
        self.parameters.append(parameter)

    def to_json(self) -> dict:
        """Returns a json representation of the function.

        Returns:
            dict: The json representation of the function.
        """
        return {
            "name": self.name,
            "parameters": [parameter.to_json() for parameter in self.parameters],
            "expression": str(self.expr),
            "resolution": self.resolution,
            "start_x": self.start_x,
            "end_x": self.end_x,
        }

    @classmethod
    def from_json(cls, data: dict) -> Function:
        """Creates a function from a json representation.

        Args:
            data (dict): The json representation of the function.

        Returns:
            Function: The function.
        """
        for subclass in cls.__subclasses__():
            if subclass.name == data["name"]:
                cls = subclass
                break

        obj = cls()
        obj.expr = data["expression"]
        obj.name = data["name"]
        obj.resolution = data["resolution"]
        obj.start_x = data["start_x"]
        obj.end_x = data["end_x"]

        obj.parameters = []
        for parameter in data["parameters"]:
            obj.add_parameter(Function.Parameter.from_json(parameter))

        return obj

    @property
    def expr(self):
        """The sympy expression of the function."""
        return self._expr

    @expr.setter
    def expr(self, expr):
        if isinstance(expr, str):
            try:
                self._expr = sympy.sympify(expr)
            except ValueError:
                logger.error("Could not convert %s to a sympy expression", expr)
                raise SyntaxError("Could not convert %s to a sympy expression" % expr)
        elif isinstance(expr, sympy.Expr):
            self._expr = expr

    @property
    def resolution(self):
        """The resolution of the function in seconds."""
        return self._resolution

    @resolution.setter
    def resolution(self, resolution):
        try:
            self._resolution = Decimal(resolution)
        except ValueError:
            logger.error("Could not convert %s to a decimal", resolution)
            raise SyntaxError("Could not convert %s to a decimal" % resolution)

    @property
    def start_x(self):
        """The x value where the evalution of the function starts."""
        return self._start_x

    @start_x.setter
    def start_x(self, start_x):
        try:
            self._start_x = float(start_x)
        except ValueError:
            logger.error("Could not convert %s to a float", start_x)
            raise SyntaxError("Could not convert %s to a float" % start_x)

    @property
    def end_x(self):
        """The x value where the evalution of the function ends."""
        return self._end_x

    @end_x.setter
    def end_x(self, end_x):
        try:
            self._end_x = float(end_x)
        except ValueError:
            logger.error("Could not convert %s to a float", end_x)
            raise SyntaxError("Could not convert %s to a float" % end_x)

    def get_pixmap(self):
        """This is the default pixmap for every function. If one wants to have a custom pixmap, this method has to be overwritten.

        Returns:
        QPixmap : The default pixmap for every function
        """
        pixmap = PulseParamters.TXCustom()
        return pixmap

    class Parameter:
        """A parameter of a function.

        This can be for example the standard deviation of a Gaussian function.

        Args:
            name (str): The name of the parameter.
            symbol (str): The symbol of the parameter.
            value (float): The value of the parameter.

        Attributes:
            name (str): The name of the parameter.
            symbol (str): The symbol of the parameter.
            value (float): The value of the parameter.
            default (float): The default value of the parameter.
        """

        def __init__(self, name: str, symbol: str, value: float) -> None:
            """Initializes the parameter."""
            self.name = name
            self.symbol = symbol
            self.value = value
            self.default = value

        def set_value(self, value: float) -> None:
            """Sets the value of the parameter.

            Args:
                value (float): The new value of the parameter.
            """
            self.value = value
            logger.debug("Parameter %s set to %s", self.name, self.value)

        def to_json(self) -> dict:
            """Returns a json representation of the parameter.

            Returns:
                dict: The json representation of the parameter.
            """
            return {
                "name": self.name,
                "symbol": self.symbol,
                "value": self.value,
                "default": self.default,
            }

        @classmethod
        def from_json(cls, data):
            """Creates a parameter from a json representation.

            Args:
                data (dict): The json representation of the parameter.

            Returns:
                Function.Parameter: The parameter.
            """
            obj = cls(data["name"], data["symbol"], data["value"])
            obj.default = data["default"]
            return obj


class RectFunction(Function):
    """The rectangular function."""

    name = "Rectangular"

    def __init__(self) -> None:
        """Initializes the RecFunction."""
        expr = sympy.sympify("1")
        super().__init__(expr)

    def get_pixmap(self) -> QPixmap:
        """Returns the pixmap of the rectangular function.

        Returns:
            QPixmap: The pixmap of the rectangular function.
        """
        pixmap = PulseParamters.TXRect()
        return pixmap


class SincFunction(Function):
    """The sinc function.

    The sinc function is defined as sin(x * l) / (x * l).
    The parameter is the scale factor l.
    """

    name = "Sinc"

    def __init__(self) -> None:
        """Initializes the SincFunction."""
        expr = sympy.sympify("sin(x * l)/ (x * l)")
        super().__init__(expr)
        self.add_parameter(Function.Parameter("Scale Factor", "l", 2))
        self.start_x = -np.pi
        self.end_x = np.pi

    def get_pixmap(self):
        """Returns the pixmap of the sinc function.

        Returns:
            QPixmap: The pixmap of the sinc function.
        """
        pixmap = PulseParamters.TXSinc()
        return pixmap


class GaussianFunction(Function):
    """The Gaussian function.

    The Gaussian function is defined as exp(-0.5 * ((x - mu) / sigma)**2).
    The parameters are the mean and the standard deviation.
    """

    name = "Gaussian"

    def __init__(self) -> None:
        """Initializes the GaussianFunction."""
        expr = sympy.sympify("exp(-0.5 * ((x - mu) / sigma)**2)")
        super().__init__(expr)
        self.add_parameter(Function.Parameter("Mean", "mu", 0))
        self.add_parameter(Function.Parameter("Standard Deviation", "sigma", 1))
        self.start_x = -np.pi
        self.end_x = np.pi

    def get_pixmap(self):
        """Returns the QPixmap of the Gaussian function.

        Returns:
            QPixmap: The QPixmap of the Gaussian function.
        """
        pixmap = PulseParamters.TXGauss()
        return pixmap


# class TriangleFunction(Function):
#    def __init__(self) -> None:
#        expr = sympy.sympify("triang(x)")
#        super().__init__(lambda x: triang(x))


class CustomFunction(Function):
    """A custom function."""

    name = "Custom"

    def __init__(self) -> None:
        """Initializes the Custom Function."""
        expr = sympy.sympify(" 2 * x**2 + 3 * x + 1")
        super().__init__(expr)


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
        return {"name": self.name, "value": self.value, "type": self.TYPE}

    @classmethod
    def from_json(cls, data) -> Option:
        """Creates an option from a json representation.

        Args:
            data (dict): The json representation of the option.

        Returns:
            Option: The option.
        """
        for subclass in cls.__subclasses__():
            if subclass.TYPE == data["type"]:
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

    TYPE = "Boolean"

    def set_value(self, value):
        """Sets the value of the option."""
        self.value = value


class NumericOption(Option):
    """Defines a numeric option for a pulse parameter option."""

    TYPE = "Numeric"

    def set_value(self, value):
        """Sets the value of the option."""
        self.value = float(value)


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

    TYPE = "Function"

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
        raise ValueError("Function with name %s not found" % name)

    def to_json(self):
        """Returns a json representation of the option.

        Returns:
            dict: The json representation of the option.
        """
        return {"name": self.name, "value": self.value.to_json(), "type": self.TYPE}

    @classmethod
    def from_json(cls, data):
        """Creates a FunctionOption from a json representation.

        Args:
            data (dict): The json representation of the FunctionOption.

        Returns:
            FunctionOption: The FunctionOption.
        """
        functions = [function() for function in Function.__subclasses__()]
        obj = cls(data["name"], functions)
        obj.value = Function.from_json(data["value"])
        return obj

    def get_pixmap(self):
        """Returns the pixmap of the function."""
        return self.value.get_pixmap()


class TXPulse(BaseSpectrometerModel.PulseParameter):
    """Basic TX Pulse Parameter. It includes options for the relative amplitude, the phase and the pulse shape.

    Args:
        name (str): The name of the pulse parameter.

    Attributes:
        RELATIVE_AMPLITUDE (str): The relative amplitude of the pulse.
        TX_PHASE (str): The phase of the pulse.
        TX_PULSE_SHAPE (str): The pulse shape.
    """

    RELATIVE_AMPLITUDE = "Relative TX Amplitude"
    TX_PHASE = "TX Phase"
    TX_PULSE_SHAPE = "TX Pulse Shape"

    def __init__(self, name) -> None:
        """Initializes the TX Pulse Parameter.

        It adds the options for the relative amplitude, the phase and the pulse shape.
        """
        super().__init__(name)
        self.add_option(NumericOption(self.RELATIVE_AMPLITUDE, 0))
        self.add_option(NumericOption(self.TX_PHASE, 0))
        self.add_option(
            FunctionOption(
                self.TX_PULSE_SHAPE,
                [RectFunction(), SincFunction(), GaussianFunction(), CustomFunction()],
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
