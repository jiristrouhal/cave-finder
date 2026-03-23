from __future__ import annotations
import abc
import dataclasses


@dataclasses.dataclass(slots=True, frozen=True)
class Position:
    x: float
    y: float
    z: float = 0.0


@dataclasses.dataclass(slots=True, frozen=True)
class Plane:
    azimuth: float
    tilt_deg: float


@dataclasses.dataclass(slots=True, frozen=True)
class EnvironmentValues:
    planes: set[Plane]


class Cell:
    def __init__(self, position: Position) -> None:
        self._value = 0.0
        self.position = position
        self._neighbours: set[Cell] = set()

    @property
    def value(self) -> float:
        return self._value

    @property
    def neighbours(self) -> set[Cell]:
        return self._neighbours

    def add_neighbour(self, cell: Cell) -> None:
        assert isinstance(cell, Cell), f"Expected {Cell.__name__}, received {type(cell).__name__}"
        self._neighbours.add(cell)

    def set_to(self, value: float) -> None:
        assert isinstance(value, float | int), (
            f"Expected int or float, received {type(value).__name__}."
        )
        if not 0 <= value <= 1:
            raise ValueError(f"Cell value must be 0 <= and <= 1, received {value}.")
        self._value = value


class Environment:
    def __init__(self) -> None:
        self._planes: set[Plane] = set()

    def get_values(self, position: Position) -> EnvironmentValues:
        return EnvironmentValues(self._planes)

    def add_plane(self, plane: Plane, *args) -> None:
        self._planes.add(plane)
