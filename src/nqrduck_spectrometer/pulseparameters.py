import logging
import numpy as np
import sympy
from pathlib import Path
from PyQt6.QtGui import QPixmap
from nqrduck.contrib.mplwidget import MplWidget
from nqrduck.helpers.signalprocessing import SignalProcessing as sp
from .base_spectrometer_model import BaseSpectrometerModel

logger = logging.getLogger(__name__)


class Function:
    name: str
    parameters: list
    expression: str | sympy.Expr
    resolution: float
    start_x: float
    end_x: float

    def __init__(self, expr) -> None:
        self.parameters = []
        self.expr = expr
        self.resolution = 16/30.72e6
        self.start_x = -1
        self.end_x = 1

    def get_time_points(self, pulse_length: float) -> np.ndarray:
        """Returns the time domain points for the function with the given pulse length."""
        # Get the time domain points
        n = int(pulse_length / self.resolution)
        t = np.linspace(0, pulse_length, n)
        return t

    def evaluate(self, pulse_length: float) -> np.ndarray:
        """Evaluates the function for the given pulse length."""
        n = int(pulse_length / self.resolution)
        t = np.linspace(self.start_x, self.end_x, n)
        x = sympy.symbols("x")

        # If the expression is a string, convert it to a sympy expression
        if isinstance(self.expr, str):
            self.expr = sympy.sympify(self.expr)

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

    def frequency_domain_plot(self, pulse_length: float) -> MplWidget:
        mpl_widget = MplWidget()
        td = self.get_time_points(pulse_length)
        yd = self.evaluate(pulse_length)
        xdf, ydf = sp.fft(td, yd)
        mpl_widget.canvas.ax.plot(xdf, ydf)
        mpl_widget.canvas.ax.set_xlabel("Frequency in Hz")
        mpl_widget.canvas.ax.set_ylabel("Magnitude")
        return mpl_widget

    def time_domain_plot(self, pulse_length: float) -> MplWidget:
        mpl_widget = MplWidget()
        td = self.get_time_points(pulse_length)
        mpl_widget.canvas.ax.plot(td, self.evaluate(pulse_length))
        mpl_widget.canvas.ax.set_xlabel("Time in s")
        mpl_widget.canvas.ax.set_ylabel("Magnitude")
        return mpl_widget
    
    def get_pulse_amplitude(self, pulse_length: float) -> np.array:
        """Returns the pulse amplitude in the time domain."""
        return self.evaluate(pulse_length)

    def add_parameter(self, parameter: "Function.Parameter"):
        self.parameters.append(parameter)

    def to_json(self):
        return {
            "name": self.name,
            "parameters": [parameter.to_json() for parameter in self.parameters],
            "expression": str(self.expr),
            "resolution": self.resolution,
            "start_x": self.start_x,
            "end_x": self.end_x,
        }

    @classmethod
    def from_json(cls, data):
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

    class Parameter:
        def __init__(self, name: str, symbol: str, value: float) -> None:
            self.name = name
            self.symbol = symbol
            self.value = value
            self.default = value

        def set_value(self, value: float):
            self.value = value
            logger.debug("Parameter %s set to %s", self.name, self.value)

        def to_json(self):
            return {
                "name": self.name,
                "symbol": self.symbol,
                "value": self.value,
                "default": self.default,
            }

        @classmethod
        def from_json(cls, data):
            obj = cls(data["name"], data["symbol"], data["value"])
            obj.default = data["default"]
            return obj

class RectFunction(Function):
    name = "Rectangular"

    def __init__(self) -> None:
        expr = sympy.sympify("1")
        super().__init__(expr)


class SincFunction(Function):
    name = "Sinc"

    def __init__(self) -> None:
        expr = sympy.sympify("sin(x * l)/ (x * l)")
        super().__init__(expr)
        self.add_parameter(Function.Parameter("Scale Factor", "l", 2))
        self.start_x = -np.pi
        self.end_x = np.pi


class GaussianFunction(Function):
    name = "Gaussian"

    def __init__(self) -> None:
        expr = sympy.sympify("exp(-0.5 * ((x - mu) / sigma)**2)")
        super().__init__(expr)
        self.add_parameter(Function.Parameter("Mean", "mu", 0))
        self.add_parameter(Function.Parameter("Standard Deviation", "sigma", 1))
        self.start_x = -np.pi
        self.end_x = np.pi


# class TriangleFunction(Function):
#    def __init__(self) -> None:
#        expr = sympy.sympify("triang(x)")
#        super().__init__(lambda x: triang(x))


class CustomFunction(Function):
    name = "Custom"

    def __init__(self) -> None:
        expr = sympy.sympify(" 2 * x**2 + 3 * x + 1")
        super().__init__(expr)


class Option:
    """Defines options for the pulse parameters which can then be set accordingly."""

    def __init__(self, name: str, value) -> None:
        self.name = name
        self.value = value

    def set_value(self):
        raise NotImplementedError

    def to_json(self):
        return {"name": self.name, "value": self.value, "type": self.TYPE}
    
    @classmethod
    def from_json(cls, data) -> "Option":
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
        self.value = value


class NumericOption(Option):
    """Defines a numeric option for a pulse parameter option."""
    TYPE = "Numeric"

    def set_value(self, value):
        self.value = float(value)


class FunctionOption(Option):
    """Defines a selection option for a pulse parameter option.
    It takes different function objects."""
    TYPE = "Function"

    def __init__(self, name, functions) -> None:
        super().__init__(name, functions[0])
        self.functions = functions

    def set_value(self, value):
        self.value = value

    def get_function_by_name(self, name):
        for function in self.functions:
            if function.name == name:
                return function
        raise ValueError("Function with name %s not found" % name)

    def to_json(self):
        return {"name": self.name, "value": self.value.to_json(), "type": self.TYPE}
    
    @classmethod
    def from_json(cls, data):
        functions = [function() for function in Function.__subclasses__()]
        obj = cls(data["name"], functions)
        obj.value = Function.from_json(data["value"])
        return obj


class TXPulse(BaseSpectrometerModel.PulseParameter):
    RELATIVE_AMPLITUDE = "Relative TX Amplitude"
    TX_PHASE = "TX Phase"
    TX_PULSE_SHAPE = "TX Pulse Shape"

    def __init__(self, name) -> None:
        super().__init__(name)
        self.add_option(NumericOption(self.RELATIVE_AMPLITUDE, 0))
        self.add_option(NumericOption(self.TX_PHASE, 0))
        self.add_option(
            FunctionOption(self.TX_PULSE_SHAPE, [RectFunction(), SincFunction(), GaussianFunction()]),
        )

    def get_pixmap(self):
        self_path = Path(__file__).parent
        if self.get_option_by_name(self.RELATIVE_AMPLITUDE).value > 0:
            image_path = self_path / "resources/pulseparameter/TXOn.png"
        else:
            image_path = self_path / "resources/pulseparameter/TXOff.png"
        pixmap = QPixmap(str(image_path))
        return pixmap


class RXReadout(BaseSpectrometerModel.PulseParameter):
    RX = "RX"
    def __init__(self, name) -> None:
        super().__init__(name)
        self.add_option(BooleanOption(self.RX, False))

    def get_pixmap(self):
        self_path = Path(__file__).parent
        if self.get_option_by_name(self.RX).value == False:
            image_path = self_path / "resources/pulseparameter/RXOff.png"
        else:
            image_path = self_path / "resources/pulseparameter/RXOn.png"
        pixmap = QPixmap(str(image_path))
        return pixmap


class Gate(BaseSpectrometerModel.PulseParameter):
    GATE_STATE = "Gate State"
    def __init__(self, name) -> None:
        super().__init__(name)
        self.add_option(BooleanOption(self.GATE_STATE, False))

    def get_pixmap(self):
        self_path = Path(__file__).parent
        if self.get_option_by_name(self.GATE_STATE).value == False:
            image_path = self_path / "resources/pulseparameter/GateOff.png"
        else:
            image_path = self_path / "resources/pulseparameter/GateOn.png"
        pixmap = QPixmap(str(image_path))
        return pixmap
