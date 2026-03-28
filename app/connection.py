from __future__ import annotations
import dataclasses

from .geometry import (
    Position as _Position,
    Vector as _Vector,
    vector_plane_cosine as _vector_plane_cosine,
)
from .environment import Environment as _Environment
from .cell import Cell as Cell


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


def evaluate_connections(connections: set[Connection], environment: _Environment) -> None:
    """Assign probabilities to connections."""
    for conn in connections:
        planes = environment.get_values(conn.midpoint).planes
        conn.values.prob = sum(_vector_plane_cosine(conn.vector, plane) for plane in planes)
