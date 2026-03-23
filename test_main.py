from math import inf, nan
import pytest

from main import Cell, Position


@pytest.fixture
def position() -> Position:
    return Position(1, 2, 3)


@pytest.fixture
def cell(position: Position) -> Cell:
    return Cell(position)


def test_cell_is_initially_with_zero_value_without_neighbours(cell: Cell) -> None:
    assert cell.value == 0
    assert not cell.neighbours


def test_setting_neigbours(position: Position, cell: Cell) -> None:
    cell.add_neighbour(Cell(position))
    assert len(cell.neighbours) == 1
    cell.add_neighbour(Cell(position))
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


if __name__ == "__main__":
    pytest.main()
