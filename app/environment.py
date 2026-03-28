import dataclasses

from .geometry import Plane as _Plane, Position as _Position


@dataclasses.dataclass(slots=True, frozen=True)
class EnvironmentValues:
    planes: set[_Plane]


class Environment:
    def __init__(self) -> None:
        self._planes: set[_Plane] = set()

    def get_values(self, position: _Position) -> EnvironmentValues:
        return EnvironmentValues(self._planes)

    def add_plane(self, plane: _Plane, *args) -> None:
        self._planes.add(plane)
