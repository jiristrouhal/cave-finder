import pytest

from app.geometry import Plane, Position
from app.environment import Environment, EnvironmentValues


class TestDefiningPlanes:
    @pytest.mark.parametrize("position", [Position(1, 2, 0), Position(-5, 1.1, -2)])
    def test_initially_environment_vars_are_always_empty(self, env: Environment, position) -> None:
        assert env.get_values(position) == EnvironmentValues(set())

    @pytest.mark.parametrize("position", [Position(1, 2, 0), Position(-5, 1.1, -2)])
    @pytest.mark.parametrize("plane", [Plane(120, 20), Plane(140, -15)])
    def test_first_plane_added_to_environment_is_accessible_anywhere(
        self, env: Environment, position: Position, plane: Plane
    ) -> None:
        env.add_plane(plane)
        assert env.get_values(position).planes == {plane}

    def test_adding_multiple_planes(self, env: Environment) -> None:
        plane_1 = Plane(120, 15)
        plane_2 = Plane(170, 2)
        env.add_plane(plane_1)
        env.add_plane(plane_2)
        assert env.get_values(Position(0, 0, 0)).planes == {plane_1, plane_2}
