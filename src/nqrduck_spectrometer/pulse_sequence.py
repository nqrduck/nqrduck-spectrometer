import logging
from collections import OrderedDict

logger = logging.getLogger(__name__)

class PulseSequence:
    """A pulse sequence is a collection of events that are executed in a certain order."""
    def __init__(self, name) -> None:
        self.name = name
        self.events = list()

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

        def on_duration_changed(self, duration: float) -> None:
            logger.debug("Duration of event %s changed to %s", self.name, duration)
            self.duration = duration

    def dump_sequence_data(self):
        """Returns a dict with all the data in the pulse sequence"""
        data = {
            "name": self.name,
            "events": []
        }
        for event in self.events:
            event_data = {
                "name": event.name,
                "duration": event.duration,
                "parameters": []
            }
            for parameter in event.parameters.keys():
                event_data["parameters"].append({
                    "name": parameter,
                    "value": event.parameters[parameter].get_options()
                })
            data["events"].append(event_data)
        return data