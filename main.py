from __future__ import annotations
import math
import dataclasses
import uuid


@dataclasses.dataclass(slots=True, frozen=True)
class Position:
    x: float
    y: float
    z: float = 0.0

    def __add__(self, other: Position) -> Position:
        assert isinstance(other, Position), f"Expected {Position.__name__}"
        return Position(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: Position) -> Vector:
        assert isinstance(other, Position), f"Expected {Vector.__name__}"
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def midpoint(self, other: Position) -> Position:
        assert isinstance(other, Position), f"Expected {Position.__name__}"
        return Position((self.x + other.x) / 2, (self.y + other.y) / 2, (self.z + other.z) / 2)


@dataclasses.dataclass(slots=True, frozen=True)
class Vector(Position):
    pass

    def __mul__(self, other: Vector) -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    @property
    def size(self) -> float:
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)


@dataclasses.dataclass(slots=True, frozen=True)
class Plane:
    azimuth: float
    tilt_deg: float


def vector_plane_cosine(vector: Vector, plane: Plane) -> float:
    # x/y is given by the plane azimuth
    # z is given by the plane angle
    z = abs(math.sin(plane.tilt_deg))
    xy = math.sqrt(1 - z**2)

    # calculate plane unit normal - the xy projection of plane normal
    # has azimuth 90 degs rotated from the plane azimuth - 90 degs must be
    # added
    angle_rad = math.radians(plane.azimuth + 90)
    # angle 0 corresponds to y direction, pi/2 to x direction
    y = xy * math.cos(angle_rad)
    x = xy * math.sin(angle_rad)
    assert 1 - 1e-05 <= x**2 + y**2 + z**2 <= 1 + 1e-05, (
        "The unit vector magnitude must be approx 1"
    )
    unit_normal = Vector(x, y, z)

    # calculate size of projection of vector into the plane
    cos = math.sqrt(1 - ((vector * unit_normal) / vector.size) ** 2)
    return cos


@dataclasses.dataclass(slots=True, frozen=True)
class EnvironmentValues:
    planes: set[Plane]


class Cell:
    def __init__(self, position: Position) -> None:
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
    def position(self) -> Position:
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

    def get_values(self, position: Position) -> EnvironmentValues:
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
    def midpoint(self) -> Position:
        return self._midpoint

    @property
    def vector(self) -> Vector:
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
        conn.values.prob = sum(vector_plane_cosine(conn.vector, plane) for plane in planes)
