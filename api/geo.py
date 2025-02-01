"""Geometry functions."""
import numpy as np


def arclen(x, y):
    """Compute cumulative arc length of curve (x, y)."""
    dx = np.diff(x)
    dy = np.diff(y)
    ds = np.sqrt(dx ** 2 + dy ** 2)
    s = np.cumsum(ds)
    s = np.concatenate(([0.0], s))
    return s


def curvature(x, y, closed=False):
    """Compute curvature of curve (x, y).

    This uses Menger curvature (see https://hratliff.com/posts/2019/02/curvature-of-three-points).
    """
    # pylint: disable=too-many-locals
    n = len(x)
    c = np.zeros((n,))
    if closed:
        msg = "start and end point must be the same"
        assert np.isclose(x[-1], x[0]), msg
        assert np.isclose(y[-1], y[0]), msg
        x = x[:-1]
        y = y[:-1]
        n = n - 1
    i_start, i_end = (0, n) if closed else (1, n-1)
    for i in range(i_start, i_end):
        x_a = x[(i - 1) % n]
        x_b = x[i]
        x_c = x[(i + 1) % n]
        y_a = y[(i - 1) % n]
        y_b = y[i]
        y_c = y[(i + 1) % n]
        f = np.sqrt((x_a - x_b) ** 2 + (y_a - y_b) ** 2)
        g = np.sqrt((x_b - x_c) ** 2 + (y_b - y_c) ** 2)
        h = np.sqrt((x_c - x_a) ** 2 + (y_c - y_a) ** 2)
        area = 0.5 * (x_a*y_b - x_b*y_a + x_b*y_c - x_c*y_b + x_c*y_a - x_a*y_c)
        c[i] = 4 * area / (f * g * h)
    if closed:
        c[-1] = c[0]
    else:
        c[0] = c[1]
        c[-1] = c[-2]
    return c


def speed(c, a_lat):
    """Maximum curve speed.

    Maximum curve speed in m/s given curvature in 1/m and allowed lateral acceleration in m/s^2."""
    return np.sqrt(a_lat / np.abs(c))
