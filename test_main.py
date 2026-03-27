from math import inf, nan
import pytest

from geometry import Position, Plane
from main import (
    Cell,
    Environment,
    EnvironmentValues,
    Connection,
    build_connections,
    evaluate_connections,
)


@pytest.fixture
def position() -> Position:
    return Position(1, 2, 3)


@pytest.fixture
def cell(position: Position) -> Cell:
    return Cell(position)


@pytest.fixture
def env() -> Environment:
    return Environment()


def test_cell_is_initially_with_zero_value_without_neighbours(cell: Cell) -> None:
    assert cell.value == 0
    assert not cell.neighbours


def test_setting_neigbours(position: Position, cell: Cell) -> None:
    cell.add_neighbours(Cell(position))
    assert len(cell.neighbours) == 1
    cell.add_neighbours(Cell(position))
    assert len(cell.neighbours) == 2


@pytest.mark.parametrize("new_value", [1, 0, 0.1, 0.5])
def test_cell_value_can_be_set_to_any_probability_value(cell: Cell, new_value: float) -> None:
    cell.set_to(new_value)
    assert cell.value == new_value


@pytest.mark.parametrize("new_value", [-1, -0.1, 5, nan, inf, -inf])
def test_setting_cell_value_outside_probability_range_raises_error(
    cell: Cell, new_value: float
) -> None:
    with pytest.raises(ValueError):
        cell.set_to(new_value)


class TestEnvironment:
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


class TestBuildingConnections:
    def test_each_of_two_neighbours_yields_one_connection(self) -> None:
        cell_1 = Cell(Position(1, 1, 1))
        cell_2 = Cell(Position(3, 3, 4))
        cell_1.add_neighbours(cell_2)
        cell_2.add_neighbours(cell_1)
        connections = build_connections({cell_1, cell_2})
        assert len(connections) == 2

    def test_three_defined_neigbours_yield_single_connection(self) -> None:
        cell_1 = Cell(Position(1, 1, 1))
        cell_2 = Cell(Position(1, 2.2, 3))
        cell_3 = Cell(Position(4, 5, 2))
        cell_1.add_neighbours(cell_3, cell_2)
        cell_2.add_neighbours(cell_3, cell_1)
        cell_3.add_neighbours(cell_2)  # not cell_1 - this means 5 neighbours, in total
        connections = build_connections({cell_1, cell_2, cell_3})
        assert len(connections) == 5


class TestEvaluatingConnections:
    def test_evaluating_empty_set_does_nothing(self, env: Environment):
        connections: set[Connection] = set()
        evaluate_connections(connections, env)
        assert connections == set()

    def test_evaluating_connection_with_single_plane(self, env: Environment) -> None:
        source = Cell(Position(0, 0, 0))
        target = Cell(Position(1, 0, 0))
        env.add_plane(Plane(90, 0))  # go east - with the x
        conn_1 = Connection(source=source, target=target)
        connections = {conn_1}
        evaluate_connections(connections, env)
        assert conn_1.values.prob == 1.0


if __name__ == "__main__":
    pytest.main()
