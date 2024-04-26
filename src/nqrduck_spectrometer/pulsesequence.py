"""Contains the PulseSequence class that is used to store a pulse sequence and its events."""

import logging
import importlib.metadata
from collections import OrderedDict
from nqrduck.helpers.unitconverter import UnitConverter
from nqrduck_spectrometer.pulseparameters import Option

logger = logging.getLogger(__name__)


class PulseSequence:
    """A pulse sequence is a collection of events that are executed in a certain order.

    Args:
        name (str): The name of the pulse sequence

    Attributes:
        name (str): The name of the pulse sequence
        events (list): The events of the pulse sequence
    """

    def __init__(self, name, version = None) -> None:
        """Initializes the pulse sequence."""
        self.name = name
        # Saving version to check for compatability of saved sequence
        if version is not None:
            self.version = version
        else:
            self.version = importlib.metadata.version("nqrduck_spectrometer")
        self.events = list()

    def get_event_names(self) -> list:
        """Returns a list of the names of the events in the pulse sequence.

        Returns:
            list: The names of the events
        """
        return [event.name for event in self.events]

    class Event:
        """An event is a part of a pulse sequence. It has a name and a duration and different parameters that have to be set.

        Args:
            name (str): The name of the event
            duration (str): The duration of the event

        Attributes:
            name (str): The name of the event
            duration (str): The duration of the event
            parameters (OrderedDict): The parameters of the event
        """

        def __init__(self, name: str, duration: str) -> None:
            """Initializes the event."""
            self.parameters = OrderedDict()
            self.name = name
            self.duration = duration

        def add_parameter(self, parameter) -> None:
            """Adds a parameter to the event.

            Args:
                parameter: The parameter to add
            """
            self.parameters.append(parameter)

        def on_duration_changed(self, duration: str) -> None:
            """This method is called when the duration of the event is changed.

            Args:
                duration (str): The new duration of the event
            """
            logger.debug("Duration of event %s changed to %s", self.name, duration)
            self.duration = duration

        @classmethod
        def load_event(cls, event, pulse_parameter_options):
            """Loads an event from a dict.

            The pulse paramter options are needed to load the parameters
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
                        pulse_parameter_class = pulse_parameter_options[
                            pulse_parameter_option
                        ]
                        obj.parameters[pulse_parameter_option] = pulse_parameter_class(
                            parameter["name"]
                        )
                        # Delete the default instances of the pulse parameter options
                        obj.parameters[pulse_parameter_option].options = []
                        for option in parameter["value"]:
                            obj.parameters[pulse_parameter_option].options.append(
                                Option.from_json(option)
                            )

            return obj

        @property
        def duration(self):
            """The duration of the event."""
            return self._duration

        @duration.setter
        def duration(self, duration: str):
            # Duration needs to be a positive number
            try:
                duration = UnitConverter.to_float(duration)
            except ValueError:
                raise ValueError("Duration needs to be a number")
            if duration < 0:
                raise ValueError("Duration needs to be a positive number")

            self._duration = duration

    def to_json(self):
        """Returns a dict with all the data in the pulse sequence.

        Returns:
            dict: The dict with the sequence data
        """
        # Get the versions of this package
        data = {"name": self.name, "version" : self.version, "events": []}
        for event in self.events:
            event_data = {
                "name": event.name,
                "duration": event.duration,
                "parameters": [],
            }
            for parameter in event.parameters.keys():
                event_data["parameters"].append({"name": parameter, "value": []})
                for option in event.parameters[parameter].options:
                    event_data["parameters"][-1]["value"].append(option.to_json())
            data["events"].append(event_data)
        return data

    @classmethod
    def load_sequence(cls, sequence, pulse_parameter_options):
        """Loads a pulse sequence from a dict.

        The pulse paramter options are needed to load the parameters
        and make sure the correct spectrometer is active.

        Args:
            sequence (dict): The dict with the sequence data
            pulse_parameter_options (dict): The dict with the pulse parameter options

        Returns:
            PulseSequence: The loaded pulse sequence

        Raises:
            KeyError: If the pulse parameter options are not the same as the ones in the pulse sequence
        """
        obj = cls(sequence["name"], version = sequence["version"])
        for event_data in sequence["events"]:
            obj.events.append(cls.Event.load_event(event_data, pulse_parameter_options))

        return obj

    class Variable:
        """A variable is a parameter that can be used within a pulsesequence as a placeholder.

        For example the event duration a Variable with name a can be set. This variable can then be set to a list of different values.
        On execution of the pulse sequence the event duration will be set to the first value in the list.
        Then the pulse sequence will be executed with the second value of the list. This is repeated until the pulse sequence has
        been executed with all values in the list.
        """

        @property
        def name(self):
            """The name of the variable."""
            return self._name

        @name.setter
        def name(self, name: str):
            if not isinstance(name, str):
                raise TypeError("Name needs to be a string")
            self._name = name

        @property
        def values(self):
            """The values of the variable. This is a list of values that the variable can take."""
            return self._values

        @values.setter
        def values(self, values: list):
            if not isinstance(values, list):
                raise TypeError("Values needs to be a list")
            self._values = values

    class VariableGroup:
        """Variables can be grouped together.

        If we have groups a and b the pulse sequence will be executed for all combinations of variables in a and b.
        """

        @property
        def name(self):
            """The name of the variable group."""
            return self._name

        @name.setter
        def name(self, name: str):
            if not isinstance(name, str):
                raise TypeError("Name needs to be a string")
            self._name = name

        @property
        def variables(self):
            """The variables in the group. This is a list of variables."""
            return self._variables

        @variables.setter
        def variables(self, variables: list):
            if not isinstance(variables, list):
                raise TypeError("Variables needs to be a list")
            self._variables = variables
