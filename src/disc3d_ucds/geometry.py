from __future__ import annotations

import math
from typing import Iterable, Tuple

import numpy as np


def deg2rad(value: float) -> float:
    return value * math.pi / 180.0


def opk_to_world_to_camera(omega_deg: float, phi_deg: float, kappa_deg: float) -> np.ndarray:
    """Convert photogrammetric OPK angles to a world-to-camera rotation matrix.

    The convention is documented in docs/CAMERA_CONVENTIONS.md. The original
    OPK values are also preserved in UCDS, so this conversion can be audited
    or replaced for a specific DISC3D calibration.
    """
    om = deg2rad(omega_deg)
    ph = deg2rad(phi_deg)
    ka = deg2rad(kappa_deg)

    com, som = math.cos(om), math.sin(om)
    cph, sph = math.cos(ph), math.sin(ph)
    cka, ska = math.cos(ka), math.sin(ka)

    r_om = np.array([[1, 0, 0], [0, com, -som], [0, som, com]], dtype=float)
    r_ph = np.array([[cph, 0, sph], [0, 1, 0], [-sph, 0, cph]], dtype=float)
    r_ka = np.array([[cka, -ska, 0], [ska, cka, 0], [0, 0, 1]], dtype=float)

    r_body_to_world = r_ka @ r_ph @ r_om
    return r_body_to_world.T


def rotation_to_quaternion_wxyz(r: np.ndarray) -> Tuple[float, float, float, float]:
    """Convert 3x3 rotation matrix to COLMAP-style quaternion (w, x, y, z)."""
    m = np.asarray(r, dtype=float)
    trace = float(np.trace(m))
    if trace > 0:
        s = math.sqrt(trace + 1.0) * 2.0
        qw = 0.25 * s
        qx = (m[2, 1] - m[1, 2]) / s
        qy = (m[0, 2] - m[2, 0]) / s
        qz = (m[1, 0] - m[0, 1]) / s
    elif m[0, 0] > m[1, 1] and m[0, 0] > m[2, 2]:
        s = math.sqrt(1.0 + m[0, 0] - m[1, 1] - m[2, 2]) * 2.0
        qw = (m[2, 1] - m[1, 2]) / s
        qx = 0.25 * s
        qy = (m[0, 1] + m[1, 0]) / s
        qz = (m[0, 2] + m[2, 0]) / s
    elif m[1, 1] > m[2, 2]:
        s = math.sqrt(1.0 + m[1, 1] - m[0, 0] - m[2, 2]) * 2.0
        qw = (m[0, 2] - m[2, 0]) / s
        qx = (m[0, 1] + m[1, 0]) / s
        qy = 0.25 * s
        qz = (m[1, 2] + m[2, 1]) / s
    else:
        s = math.sqrt(1.0 + m[2, 2] - m[0, 0] - m[1, 1]) * 2.0
        qw = (m[1, 0] - m[0, 1]) / s
        qx = (m[0, 2] + m[2, 0]) / s
        qy = (m[1, 2] + m[2, 1]) / s
        qz = 0.25 * s
    return float(qw), float(qx), float(qy), float(qz)


def camera_center_to_tvec(r_world_to_cam: np.ndarray, center: Iterable[float]) -> Tuple[float, float, float]:
    c = np.asarray(list(center), dtype=float).reshape(3)
    t = -np.asarray(r_world_to_cam, dtype=float) @ c
    return float(t[0]), float(t[1]), float(t[2])


def world_to_camera_to_camera_to_world(r_world_to_cam: np.ndarray, tvec: Iterable[float]) -> np.ndarray:
    """Return a 4x4 camera-to-world matrix from COLMAP-style R,t."""
    r_wc = np.asarray(r_world_to_cam, dtype=float)
    t = np.asarray(list(tvec), dtype=float).reshape(3)
    r_cw = r_wc.T
    c = -r_cw @ t
    mat = np.eye(4, dtype=float)
    mat[:3, :3] = r_cw
    mat[:3, 3] = c
    return mat
