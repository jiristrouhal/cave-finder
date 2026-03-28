import pytest

from app.geometry import Position
from app.cell import Cell
from app.environment import Environment


@pytest.fixture
def position() -> Position:
    return Position(1, 2, 3)


@pytest.fixture
def cell(position: Position) -> Cell:
    return Cell(position)


@pytest.fixture
def env() -> Environment:
    return Environment()
