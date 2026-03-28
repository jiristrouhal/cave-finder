from __future__ import annotations
import uuid

from geometry import Position as _Position


class Cell:
    def __init__(self, position: _Position) -> None:
        self._id = uuid.uuid1()
        self._value = 0.0
        self._position = position
        self._neighbours: set[Cell] = set()

    @property
    def value(self) -> float:
        return self._value

    @property
    def neighbours(self) -> set[Cell]:
        return self._neighbours

    @property
    def position(self) -> _Position:
        return self._position

    def add_neighbours(self, *cells: Cell) -> None:
        for cell in cells:
            assert isinstance(cell, Cell), (
                f"Expected {Cell.__name__}, received {type(cell).__name__}"
            )
            self._neighbours.add(cell)

    def set_to(self, value: float) -> None:
        assert isinstance(value, float | int), (
            f"Expected int or float, received {type(value).__name__}."
        )
        if not 0 <= value <= 1:
            raise ValueError(f"Cell value must be 0 <= and <= 1, received {value}.")
        self._value = value

    def __hash__(self) -> int:
        return self._id.int
