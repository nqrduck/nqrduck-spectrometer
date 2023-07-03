from nqrduck.module.module import Module
from nqrduck_spectrometer.model import SpectrometerModel
from nqrduck_spectrometer.view import SpectrometerView
from nqrduck_spectrometer.controller import SpectrometerController

Spectrometer = Module(SpectrometerModel, SpectrometerView, SpectrometerController)