import pytest

from app.geometry import Region, XYPoint, HeightFunc, Boundary


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
    def test_n_of_groups_for_valid_range(self) -> None:
        assert Region.calc_n_groups(1, 1) == 1
        assert Region.calc_n_groups(1, 0.8) == 2
        assert Region.calc_n_groups(0.8, 1) == 1
        assert Region.calc_n_groups(1, 1) == 1

    def test_y_group_index(self, top: HeightFunc, bottom: HeightFunc) -> None:
        p: list[XYPoint] = [(0, 0), (1, 0), (1, 1.8), (0, 1)]
        region = Region(boundary_points=p, top=top, bottom=bottom, cell_size=1)
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
        region = Region(boundary_points=p, top=top, bottom=bottom, cell_size=1)
        assert len(region.boundary_y_groups) == 2

        expected_0_group = [(p[-1], p[0]), (p[0], p[1]), (p[1], p[2])]
        expected_1_group = [(p[-1], p[0]), (p[2], p[3]), (p[1], p[2])]
        assert region.get_boundary_segments(0) == expected_0_group
        assert region.get_boundary_segments(1) == expected_1_group

    def test_grouping_boundary_parts_by_y_coord_for_negative_coords(
        self, top: HeightFunc, bottom: HeightFunc
    ) -> None:
        p: list[XYPoint] = [(-1, -1), (0, -1), (-1, 0)]
        region = Region(boundary_points=p, top=top, bottom=bottom, cell_size=1)
        assert region._n_groups == 1
        assert region.get_boundary_segments(0) == [(p[-1], p[0]), (p[0], p[1]), (p[1], p[-1])]


class TestBoundary:
    def test_calculating_dimensions(self) -> None:
        b = Boundary(points=[(0, 0), (1, 0), (0, 1)])
        assert b.x_dim == 1
        assert b.y_range == 1

    def test_calculating_bounds(self) -> None:
        b = Boundary(points=[(-1, 0), (5, 0), (-3, 7)])
        assert b.x_bounds == (-3, 5)
        assert b.y_bounds == (0, 7)


class TestGridPoints:
    def test_triangular_boundary_produces_four_grid_points(self):
        b = Boundary(points=[(0, 0), (1, 0), (0, 1)])


class TestLowerTriangularGrid:
    def test_cell_size_set_to_domain_size_produces_single_cells(
        self, top: HeightFunc, bottom: HeightFunc
    ) -> None:
        boundary: list[XYPoint] = [(0, 0), (1, 0), (0, 1)]
        region = Region(boundary, top, bottom, cell_size=1)
        grid = region.generate_2d_grid()
        assert len(grid) == 1
        assert len(grid[0]) == 1

    @pytest.mark.xfail(reason="The logic is not imlemented yet")
    def test_cell_half_domain_size_produces_3_cells(
        self, top: HeightFunc, bottom: HeightFunc
    ) -> None:
        boundary: list[XYPoint] = [(0, 0), (1, 0), (0, 1)]
        region = Region(boundary, top, bottom, cell_size=0.5)
        grid = region.generate_2d_grid()
        assert len(grid) == 2
        assert len(grid[0]) == 1, "Top row contains only single cell"
        assert len(grid[1]) == 2, "Bottom row contains 2 cells"
