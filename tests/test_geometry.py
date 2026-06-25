import numpy as np

from disc3d_ucds.geometry import opk_to_world_to_camera, rotation_to_quaternion_wxyz


def test_rotation_is_orthonormal():
    r = opk_to_world_to_camera(10, 20, 30)
    assert np.allclose(r @ r.T, np.eye(3), atol=1e-8)


def test_quaternion_has_unit_norm():
    r = opk_to_world_to_camera(10, 20, 30)
    q = rotation_to_quaternion_wxyz(r)
    assert abs(sum(v * v for v in q) - 1.0) < 1e-8
