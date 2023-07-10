class PulseSequence:
    def __init__(self) -> None:
        self.events = list()

    def get_event_names(self) -> list:
        return [event.name for event in self.events]

    class Event:
        """An event is a part of a pulse sequence. It has a name and a duration and different parameters that have to be set."""

        parameters = list()

        def __init__(self, name: str, duration: float) -> None:
            self.name = name
            self.duration = duration

        def add_parameter(self, parameter) -> None:
            self.parameters.append(parameter)