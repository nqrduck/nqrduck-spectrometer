import logging
import numpy as np
import sympy
from pathlib import Path
from PyQt6.QtGui import QPixmap
from nqrduck.contrib.mplwidget import MplWidget
from nqrduck.helpers.signalprocessing import SignalProcessing as sp
from .base_spectrometer_model import BaseSpectrometerModel

logger = logging.getLogger(__name__)

class Function():
    name: str
    parameters : list
    expression: str | sympy.Expr
    resolution: float
    start_x: float
    end_x: float

    def __init__(self, expr) -> None:
        self.parameters = []
        self.expr = expr
        self.resolution = 22e-9 * 16# 1e-6
        self.start_x = -1
        self.end_x = 1

    def get_time_points(self, pulse_length : float) -> np.ndarray:
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
    
    def frequency_domain_plot(self, pulse_length : float) -> MplWidget:
        mpl_widget = MplWidget()
        td = self.get_time_points(pulse_length)
        yd = self.evaluate(pulse_length)
        xdf, ydf = sp.fft(td, yd)
        mpl_widget.canvas.ax.plot(xdf, ydf)
        mpl_widget.canvas.ax.set_xlabel("Frequency in Hz")
        mpl_widget.canvas.ax.set_ylabel("Magnitude")
        return mpl_widget

    def time_domain_plot(self, pulse_length : float) -> MplWidget:
        mpl_widget = MplWidget()
        td = self.get_time_points(pulse_length)
        mpl_widget.canvas.ax.plot(td, self.evaluate(pulse_length))
        mpl_widget.canvas.ax.set_xlabel("Time in s")
        mpl_widget.canvas.ax.set_ylabel("Magnitude")
        return mpl_widget
        
    def add_parameter(self, parameter : "Function.Parameter"):
        self.parameters.append(parameter)


    class Parameter:
        def __init__(self, name : str, symbol : str, value : float) -> None:
            self.name = name
            self.symbol = symbol
            self.value = value
            self.default = value

        def set_value(self, value : float):
            self.value = value
            logger.debug("Parameter %s set to %s", self.name, self.value)

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

#class TriangleFunction(Function):
#    def __init__(self) -> None:
#        expr = sympy.sympify("triang(x)")
#        super().__init__(lambda x: triang(x))

class CustomFunction(Function):
    def __init__(self) -> None:
        super().__init__()

class Option:
    """Defines options for the pulse parameters which can then be set accordingly."""

    def set_value(self):
        raise NotImplementedError


class BooleanOption(Option):
    """Defines a boolean option for a pulse parameter option."""

    def __init__(self, value) -> None:
        super().__init__()
        self.value = value

    def set_value(self, value):
        self.value = value


class NumericOption(Option):
    """Defines a numeric option for a pulse parameter option."""

    def __init__(self, value) -> None:
        super().__init__()
        self.value = value

    def set_value(self, value):
        self.value = float(value)


class FunctionOption(Option):
    """Defines a selection option for a pulse parameter option.
    It takes different function objects."""
    
    def __init__(self, functions) -> None:
        super().__init__()
        self.functions = functions
        self.value = functions[0]

    def set_value(self, value):
        self.value = value
       

class TXPulse(BaseSpectrometerModel.PulseParameter):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.add_option("TX Amplitude", NumericOption(0))
        self.add_option("TX Phase", NumericOption(0))
        self.add_option("TX Pulse Shape", FunctionOption([RectFunction(), SincFunction(), GaussianFunction()]))

    def get_pixmap(self):
        self_path = Path(__file__).parent
        if self.options["TX Amplitude"].value > 0:
            image_path = self_path / "resources/pulseparameter/TXOn.png"
        else:
            image_path = self_path / "resources/pulseparameter/TXOff.png"
        pixmap = QPixmap(str(image_path))
        return pixmap

class RXReadout(BaseSpectrometerModel.PulseParameter):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.add_option("RX", BooleanOption(False))

    def get_pixmap(self):
        self_path = Path(__file__).parent
        if self.options["RX"].value == False:
            image_path = self_path / "resources/pulseparameter/RXOff.png"
        else:
            image_path = self_path / "resources/pulseparameter/RXOn.png"
        pixmap = QPixmap(str(image_path))
        return pixmap

    def set_options(self, options):
        self.state = options


class Gate(BaseSpectrometerModel.PulseParameter):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.add_option("Gate State", BooleanOption(False))

    def get_pixmap(self):
        self_path = Path(__file__).parent
        if self.options["Gate State"].state == False:
            image_path = self_path / "resources/pulseparameter/GateOff.png"
        else:
            image_path = self_path / "resources/pulseparameter/GateOn.png"
        pixmap = QPixmap(str(image_path))
        return pixmap

    def set_options(self, options):
        self.state = options
