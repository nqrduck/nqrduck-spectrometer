from PyQt5.QtCore import pyqtSignal, QObject
from nqrduck.module.module import Module
from nqrduck_spectrometer.model import SpectrometerModel
from nqrduck_spectrometer.view import SpectrometerView
from nqrduck_spectrometer.controller import SpectrometerController
from nqrduck_spectrometer.widget import Ui_Form

Spectrometer = Module(SpectrometerModel, SpectrometerController, SpectrometerView)