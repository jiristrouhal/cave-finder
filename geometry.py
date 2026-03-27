from __future__ import annotations
import dataclasses
import math


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
    z = abs(math.sin(math.radians(plane.tilt_deg)))
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
