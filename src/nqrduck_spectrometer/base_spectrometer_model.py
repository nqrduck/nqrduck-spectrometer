from collections import OrderedDict
from nqrduck.module.module_model import ModuleModel

class BaseSpectrometerModel(ModuleModel):

    def __init__(self, module):
        super().__init__(module)
        self.settings = OrderedDict()
        self.pulse_parameter_options = OrderedDict()
        
    def add_setting(self, name, value, description) -> None:
        self.settings[name] = self.Setting(name, value, description)

    def add_pulse_parameter_option(self, name, options) -> None:
        self.pulse_parameter_options[name] = options

    class Setting():
        def __init__(self, name, default, description) -> None:
            self.name = name
            self.value = default
            self.description = description

    class PulseParameter():
        def __init__(self, name):
            self.name = name

    class PulseSequence():
        def __init__(self) -> None:
            self.events = list()

        def get_event_names(self) -> list:
            return [event.name for event in self.events]

    class Event():
        parameters = list()

        def __init__(self, name : str, duration : float) -> None:
            self.name = name
            self.duration = duration

        def add_parameter(self, parameter) -> None:
            self.parameters.append(parameter)