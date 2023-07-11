from collections import OrderedDict
class PulseSequence:
    def __init__(self, name) -> None:
        self.name = name
        self.events = OrderedDict()

    def get_event_names(self) -> list:
        return [event.name for event in self.events]

    class Event:
        """An event is a part of a pulse sequence. It has a name and a duration and different parameters that have to be set."""

        def __init__(self, name: str, duration: float) -> None:
            self.parameters = OrderedDict()
            self.name = name
            self.duration = duration

        def add_parameter(self, parameter) -> None:
            self.parameters.append(parameter)

    def dump_sequence_data(self):
        """Returns a dict with all the data in the pulse sequence"""
        data = {
            "name": self.name,
            "events": []
        }
        for event in self.events.keys():
            event_data = {
                "name": self.events[event].name,
                "duration": self.events[event].duration,
                "parameters": []
            }
            for parameter in self.events[event].parameters.keys():
                event_data["parameters"].append({
                    "name": parameter,
                    "value": self.events[event].parameters[parameter].state
                })
            data["events"].append(event_data)
        return data