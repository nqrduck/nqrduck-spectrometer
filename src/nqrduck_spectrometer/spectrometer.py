"""Module creation for the spectrometer module."""
from nqrduck.module.module import Module
from .model import SpectrometerModel
from .view import SpectrometerView
from .controller import SpectrometerController

Spectrometer = Module(SpectrometerModel, SpectrometerView, SpectrometerController)