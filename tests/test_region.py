import pytest

from app.geometry import Region, XYPoint, HeightFunc


@pytest.fixture
def top() -> HeightFunc:
    def top_(point: XYPoint) -> float:
        return 1

    return top_


@pytest.fixture
def bottom() -> HeightFunc:
    def bottom_(point: XYPoint) -> float:
        return 0

    return bottom_


class TestDefiningRegion:
    def test_y_group_index(self, top: HeightFunc, bottom: HeightFunc) -> None:
        p: list[XYPoint] = [(0, 0), (1, 0), (1, 1.8), (0, 1)]
        region = Region(boundary=p, top=top, bottom=bottom, cell_size=1)
        assert region.get_y_group_index(-1.5) == 0
        assert region.get_y_group_index(0) == 0
        assert region.get_y_group_index(0.5) == 0
        assert region.get_y_group_index(1) == 1
        assert region.get_y_group_index(1.5) == 1
        assert region.get_y_group_index(1.8) == 1
        assert region.get_y_group_index(5) == 2

    def test_grouping_boundary_parts_by_y_coord(self, top: HeightFunc, bottom: HeightFunc) -> None:
        # trapezoid
        p: list[XYPoint] = [(0, 0), (1, 0), (1, 2), (0, 1)]
        region = Region(boundary=p, top=top, bottom=bottom, cell_size=1)
        assert len(region.boundary_y_groups) == 2

        expected_0_group = [(p[-1], p[0]), (p[0], p[1]), (p[1], p[2])]
        expected_1_group = [(p[-1], p[0]), (p[2], p[3]), (p[1], p[2])]
        assert region.get_boundary_segments(0) == expected_0_group
        assert region.get_boundary_segments(1) == expected_1_group
