import pytest

from main import CellVals


@pytest.fixture
def cell_values() -> CellVals:
    return CellVals()


def test_all_cell_values_are_initially_zero(cell_values: CellVals) -> None:
    assert all(v == 0 for v in cell_values.values)


if __name__ == "__main__":
    pytest.main()
