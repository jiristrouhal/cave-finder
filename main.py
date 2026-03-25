from __future__ import annotations
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
        self._position = position
        self._neighbours: set[Cell] = set()

    @property
    def value(self) -> float:
        return self._value

    @property
    def neighbours(self) -> set[Cell]:
        return self._neighbours

    def add_neighbours(self, *cells: Cell) -> None:
        for cell in cells:
            assert isinstance(cell, Cell), (
                f"Expected {Cell.__name__}, received {type(cell).__name__}"
            )
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


class Connection:
    @dataclasses.dataclass(slots=True)
    class Values:
        raw_prob: float = dataclasses.field(init=False, default=0.0)

    def __init__(self, source: Cell, target: Cell) -> None:
        self._source = source
        self._target = target
        self._values = self.Values()

    @property
    def source(self) -> Cell:
        return self._source

    @property
    def target(self) -> Cell:
        return self._target

    @property
    def values(self) -> Values:
        return self._values


def build_connections(cells: set[Cell]) -> set[Connection]:
    connections: set[Connection] = set()
    for cell in cells:
        for ncell in cell.neighbours:
            connection = Connection(source=cell, target=ncell)
            connections.add(connection)
    return connections


class ConnectionCollection:
    def __init__(self, cells: set[Cell]):
        self._connections: dict[Cell, Connection] = set()
        for cell in cells:
            for ncell in cell.neighbours:
                connection = Connection(source=cell, target=ncell)
                self._connections.add(connection)


# class Grid:
#     def __init__(self, cells: set[Cell], environment: Environment) -> None:
#         self._cells = cells
#         self._env = environment
#         self._connections

#     @property
#     def connections(self) -> set[Connection]:
#         return self._connections
