from __future__ import annotations
import dataclasses
import math
from typing import Callable


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


class Boundary:
    def __init__(
        self,
        points: list[XYPoint],
    ) -> None:
        self._points: list[XYPoint] = points
        self._x_min: float = min(p[0] for p in points)
        self._x_max: float = max(p[0] for p in points)
        self._y_min: float = min(p[1] for p in points)
        self._y_max: float = max(p[1] for p in points)
        self._n_groups: int = 0

    @property
    def x_dim(self) -> float:
        return self._x_max - self._x_min

    @property
    def y_range(self) -> float:
        return self._y_max - self._y_min

    @property
    def x_bounds(self) -> tuple[float, float]:
        return self._x_min, self._x_max

    @property
    def y_bounds(self) -> tuple[float, float]:
        return self._y_min, self._y_max


class Region:
    @dataclasses.dataclass
    class GridCell:
        is_boundary: bool

    def __init__(
        self, boundary_points: list[XYPoint], top: HeightFunc, bottom: HeightFunc, cell_size: float
    ) -> None:
        self._cell_size = cell_size
        self._boundary = Boundary(points=boundary_points)
        self._n_groups = self.calc_n_groups(self._boundary.y_range, cell_size)
        assert self._n_groups > 0
        self._boundary_y_groups: list[list[XYSegment]] = self._fill_y_groups(boundary_points)
        self._top = top
        self._bottom = bottom

    @property
    def boundary_y_groups(self) -> list[list[XYSegment]]:
        """Return boundaries grouped by y-coord range they fall into. Single boundary can belong to mutliple groups."""
        return self._boundary_y_groups

    def get_boundary_segments(self, y: float) -> list[XYSegment]:
        group_index = self.get_y_group_index(y)
        if 0 <= group_index < self._n_groups:
            return self._boundary_y_groups[group_index]
        if group_index == self._n_groups:
            return self._boundary_y_groups[-1]
        return []

    def generate_2d_grid(self) -> list[list[GridCell]]:
        result: list[list[Region.GridCell]] = []
        grid_points: list[list[XYPoint]] = []
        n_rows = int(math.ceil(self._boundary.y_range / self._cell_size))

        # begin new row
        for i in range(n_rows):
            new_row: list[Region.GridCell] = []
            result.append(new_row)

            new_row.append(self.GridCell(is_boundary=True))
        return result

    def _fill_y_groups(self, boundary: list[XYPoint]) -> list[list[XYSegment]]:
        assert boundary[0] != boundary[-1], "The first and last point must not be identical."
        empty_list: list[XYSegment] = []
        groups = [empty_list.copy() for _ in range(self._n_groups)]
        a = boundary[-1]
        for b in boundary:
            segment = (a, b)
            segment_y_min, segment_y_max = min(a[1], b[1]), max(a[1], b[1])
            first_group_id = self.get_y_group_index(segment_y_min)
            last_group_id = self.get_y_group_index(segment_y_max)
            assert first_group_id >= 0
            assert last_group_id <= self._n_groups
            for i in range(first_group_id, min(self._n_groups, last_group_id + 1)):
                groups[i].append(segment)
            a = b

        for i, g in enumerate(groups):
            groups[i] = sorted(g, key=lambda x: min(x[0][0], x[1][0]))
        return groups

    def get_y_group_index(self, y: float) -> int:
        """Returns the y group index for given coord y.

        If y is below min y, return 0, if y is above max y, return n of groups.
        """
        y_min, y_max = self._boundary.y_bounds
        if y_min <= y < y_max:
            index = int((y - y_min) / self._cell_size)
            assert index >= 0
            return index
        if y == y_max:
            return self._n_groups - 1
        if y > y_max:
            return self._n_groups
        return 0

    def get_1d_grid_points(self, y: float) -> list[XYPoint]:
        result: list[XYPoint] = []
        max_points = int(math.ceil(self._boundary.x_dim / self._cell_size)) + 1
        segments = self.get_boundary_segments(y)
        crossable_segments = set(s for s in segments if s[0][1] != s[1][1])
        assert len(crossable_segments) >= 2

        in_ = False

        # The following loop ensures that grid covers the first hit boundary segment
        # If if were not here, the grid might start from inside region
        i0 = 0
        for j in range(max_points):
            x = self._boundary.x_bounds[0] + j * self._cell_size
            for segment in crossable_segments:
                if self.crossed_line(x, y, segment):
                    if j > 0:
                        prev_x = self._boundary.x_bounds[0] + (j - 1) * self._cell_size
                        result.append((prev_x, y))
                    i0 = j
                    break
            if result:
                assert len(result) == 1
                # The initial point has been added
                break

        for i in range(i0, max_points):
            x = self._boundary.x_bounds[0] + i * self._cell_size
            just_crossed: set[XYSegment] = set()

            # check for crossed segments
            for segment in crossable_segments:
                if self.crossed_line(x, y, segment):
                    in_ = not in_
                    just_crossed.add(segment)
            crossable_segments -= just_crossed

            if in_:
                result.append((x, y))

            if not crossable_segments:
                # If there are no more crossable segments, we can stop checking for more points, because the ray will not cross any more segments.
                # One more point must be added to ensure the grid covers the whole region
                result.append((x, y))
                break
        return result

    @staticmethod
    def crossed_line(x: float, y: float, segment: XYSegment) -> bool:
        """Returns whether the ray from (-inf, y) to (x, y) crosses the line segment.

        If the segment is horizontal, it is not considered crossing. If the ray touches the segment at its end, it is considered crossing only if the other end of the segment is above the ray.

        If the ray is exactly on the segment, it is considered crossing the segment.
        """
        (x1, y1), (x2, y2) = segment
        if x1 > x2:
            x1, y1, x2, y2 = x2, y2, x1, y1
        if y1 == y2:
            # horizontal segment is not crossing
            return False
        if x < x1:
            return False
        if x > x2:
            return True
        if x1 == x2:
            # in this case, the x is between x1 and x2, so the ray is on the line of the segment.
            # The ray is crossing the segment
            return True
        x_frac = (x - x1) / (x2 - x1)
        y_frac = (y - y1) / (y2 - y1)
        return x_frac >= y_frac

    @staticmethod
    def calc_n_groups(y_range: float, cell_size: float) -> int:
        assert cell_size > 0, "Cell size must be positive"
        assert y_range >= 0, "Y range must be non-negative"
        return int(math.ceil((y_range) / cell_size))
