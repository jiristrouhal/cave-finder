from __future__ import annotations
import dataclasses
import uuid

from geometry import (
    Plane as Plane,
    Position as _Position,
    Vector as _Vector,
    vector_plane_cosine as _vector_plane_cosine,
)


@dataclasses.dataclass(slots=True, frozen=True)
class EnvironmentValues:
    planes: set[Plane]


class Cell:
    def __init__(self, position: _Position) -> None:
        self._id = uuid.uuid1()
        self._value = 0.0
        self._position = position
        self._neighbours: set[Cell] = set()

    @property
    def value(self) -> float:
        return self._value

    @property
    def neighbours(self) -> set[Cell]:
        return self._neighbours

    @property
    def position(self) -> _Position:
        return self._position

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

    def __hash__(self) -> int:
        return self._id.int


class Environment:
    def __init__(self) -> None:
        self._planes: set[Plane] = set()

    def get_values(self, position: _Position) -> EnvironmentValues:
        return EnvironmentValues(self._planes)

    def add_plane(self, plane: Plane, *args) -> None:
        self._planes.add(plane)


class Connection:
    @dataclasses.dataclass(slots=True)
    class Values:
        prob: float = dataclasses.field(init=False, default=0.0)

    def __init__(self, source: Cell, target: Cell) -> None:
        self._source = source
        self._target = target
        self._values = self.Values()
        self._midpoint = self._source.position.midpoint(self._target.position)
        self._vector = self._target.position - self._source.position

    @property
    def source(self) -> Cell:
        return self._source

    @property
    def midpoint(self) -> _Position:
        return self._midpoint

    @property
    def vector(self) -> _Vector:
        """Get vector oriented from source to target."""
        return self._vector

    @property
    def target(self) -> Cell:
        return self._target

    @property
    def values(self) -> Values:
        return self._values


def build_connections(cells: set[Cell]) -> set[Connection]:
    """Instantiate connections for neighbouring cells."""
    assert all(isinstance(c, Cell) for c in cells), f"Expected {Cell.__name__}"
    connections: set[Connection] = set()
    for cell in cells:
        for ncell in cell.neighbours:
            connection = Connection(source=cell, target=ncell)
            connections.add(connection)
    return connections


def evaluate_connections(connections: set[Connection], environment: Environment) -> None:
    """Assign probabilities to connections."""
    for conn in connections:
        planes = environment.get_values(conn.midpoint).planes
        conn.values.prob = sum(_vector_plane_cosine(conn.vector, plane) for plane in planes)
