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

        @classmethod
        def load_event(cls, event, pulse_parameter_options):
            """
            Loads an event from a dict. The pulse paramter options are needed to load the parameters
            and determine if the correct spectrometer is active.

            Args:
                event (dict): The dict with the event data
                pulse_parameter_options (dict): The dict with the pulse parameter options

            Returns:
                Event: The loaded event
            """
            obj = cls(event["name"], event["duration"])
            for parameter in event["parameters"]:
                for pulse_parameter_option in pulse_parameter_options.keys():
                    # This checks if the pulse paramter options are the same as the ones in the pulse sequence
                    if pulse_parameter_option == parameter["name"]:
                        pulse_paramter_class = pulse_parameter_options[
                            pulse_parameter_option
                        ]
                        obj.parameters[pulse_parameter_option] = pulse_paramter_class(
                            parameter["name"]
                        )
                        for option in parameter["value"]:
                            obj.parameters[pulse_parameter_option].options[
                                option["name"]
                            ].value = option["value"]

            return obj

    def dump_sequence_data(self):
        """Returns a dict with all the data in the pulse sequence

        Returns:
            dict: The dict with the sequence data"""
        data = {"name": self.name, "events": []}
        for event in self.events:
            event_data = {
                "name": event.name,
                "duration": event.duration,
                "parameters": [],
            }
            for parameter in event.parameters.keys():
                event_data["parameters"].append({"name": parameter, "value": []})
                for option in event.parameters[parameter].options.keys():
                    event_data["parameters"][-1]["value"].append(
                        {
                            "name": option,
                            "value": event.parameters[parameter].options[option].value,
                        }
                    )
            data["events"].append(event_data)
        return data

    @classmethod
    def load_sequence(cls, sequence, pulse_parameter_options):
        """Loads a pulse sequence from a dict. The pulse paramter options are needed to load the parameters
        and make sure the correct spectrometer is active.

        Args:
            sequence (dict): The dict with the sequence data
            pulse_parameter_options (dict): The dict with the pulse parameter options

        Returns:
            PulseSequence: The loaded pulse sequence

        Raises:
            KeyError: If the pulse parameter options are not the same as the ones in the pulse sequence
        """
        obj = cls(sequence["name"])
        for event_data in sequence["events"]:
            obj.events.append(cls.Event.load_event(event_data, pulse_parameter_options))

        return obj
