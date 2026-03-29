from __future__ import annotations
import dataclasses
import math
from typing import Callable, NewType


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


XYPoint = tuple[float | int, float | int]
XYSegment = tuple[XYPoint, XYPoint]
HeightFunc = Callable[[XYPoint], float]


class Region:
    def __init__(
        self, boundary: list[XYPoint], top: HeightFunc, bottom: HeightFunc, cell_size: float
    ) -> None:
        self._boundary_y_groups: list[list[XYSegment]] = self._fill_y_groups(boundary, cell_size)
        self._top = top
        self._bottom = bottom

    @property
    def boundary_y_groups(self) -> list[list[XYSegment]]:
        return self._boundary_y_groups

    def _fill_y_groups(self, boundary: list[XYPoint], cell_size: float) -> list[list[XYSegment]]:
        assert boundary[0] != boundary[-1], "The first and last point must not be identical."
        y_min, y_max = min((b[1] for b in boundary)), max((b[1] for b in boundary))
        n_groups = int(math.ceil((y_max - y_min) / cell_size))
        empty_list: list[XYSegment] = []
        groups = [empty_list.copy() for _ in range(n_groups)]
        b_prev = boundary[-1]
        for b in boundary:
            y_b_min, y_b_max = min(b[1], b_prev[1]), max(b[1], b_prev[1])
            first_group_id = int(y_b_min // cell_size)
            last_group_id = int(y_b_max // cell_size)
            for i in range(first_group_id, last_group_id):
                groups[i].append((b_prev, b))
        return groups
