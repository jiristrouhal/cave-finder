from app.geometry import Region, XYPoint


class TestDefiningRegion:
    def test_grouping_boundary_parts_by_y_coord(self) -> None:
        def top(point: XYPoint) -> float:
            return 1

        def bottom(point: XYPoint) -> float:
            return 0

        # trapezoid
        region = Region(
            boundary=[(0, 0), (1, 0), (1, 2), (0, 1)], top=top, bottom=bottom, cell_size=1
        )
        assert len(region.boundary_y_groups) == 2
