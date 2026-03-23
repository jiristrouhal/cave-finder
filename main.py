MAX_VALS = 1000


class CellVals:
    def __init__(self) -> None:
        self._values = [0.0] * MAX_VALS

    @property
    def values(self) -> list[float]:
        return self._values
