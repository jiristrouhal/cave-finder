import pytest

from app.geometry import vector_plane_cosine, Vector, Plane


class TestPlaneCosine:
    @pytest.mark.parametrize("tilt", (0, 90, -90, 12, -45))
    def test_any_x_parallel_plane_and_x_vector_gives_1_cosine(sefl, tilt: float) -> None:
        plane = Plane(90, tilt)
        vector = Vector(1, 0, 0)
        assert vector_plane_cosine(vector, plane) == 1

    def test_yz_plane_and_x_vector_gives_0_cosine(self) -> None:
        plane = Plane(0, 0)
        vector = Vector(1, 0, 0)
        assert vector_plane_cosine(vector, plane) == 0

    def test_yx_plane_and_x_vector_gives_1_cosine(self) -> None:
        plane = Plane(0, 90)
        vector = Vector(1, 0, 0)
        assert vector_plane_cosine(vector, plane) == 1

    @pytest.mark.parametrize("tilt", (0, 90, -90, 12, -45))
    def test_any_y_parallel_plane_and_y_vector_gives_1_cosine(self, tilt: float) -> None:
        plane = Plane(0, tilt)
        vector = Vector(0, 1, 0)
        assert vector_plane_cosine(vector, plane) == 1

    def test_yz_plane_and_y_vector_gives_0_cosine(self) -> None:
        plane = Plane(0, 0)
        vector = Vector(1, 0, 0)
        assert vector_plane_cosine(vector, plane) == 0

    @pytest.mark.parametrize("azimuth", (0, 90, 180, 125, -125, -90, 12, -45))
    def test_any_z_parallel_plane_and_z_vector_gives_1_cosine(self, azimuth: float) -> None:
        plane = Plane(azimuth, 0)
        vector = Vector(0, 0, 1)
        assert vector_plane_cosine(vector, plane)
