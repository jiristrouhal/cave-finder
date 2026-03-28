import pytest

from app.geometry import Position, Plane
from app.cell import Cell
from app.connection import Connection, build_connections, evaluate_connections
from app.environment import Environment


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
