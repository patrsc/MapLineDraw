"""B-Splines."""
from dataclasses import dataclass
import numpy as np
from numpy import ndarray
from scipy.interpolate import splev
from .geo import arclen


@dataclass
class BSpline:
    """Represents a B-spline curve."""

    control: ndarray  # shape (n, 2)
    knots: ndarray  # shape (m,)
    degree: int
    domain: tuple[float, float]  # (u_start, u_end)

    @staticmethod
    def create(
        control_points: list[tuple[float, float]], desired_degree: int, closed=False
    ) -> 'BSpline':
        """Create curve based on control points and degree."""
        max_degree = len(control_points) - 1
        degree = min(desired_degree, max_degree)
        cp = np.array(control_points)

        if closed:
            # wrap p points:
            # https://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/B-spline/bspline-curve-closed.html
            first = cp[0:degree, :]
            cp = np.concatenate((cp, first), axis=0)

        n = int(cp.shape[0])
        if closed:
            t = np.linspace(0, 1, n + degree + 1, endpoint=True)
            u_start = t[degree]
            u_end = t[len(t)-degree-1]
            domain = (u_start, u_end)
        else:
            t = np.linspace(0, 1, n - degree + 1, endpoint=True)
            t = np.append([0] * degree, t)
            t = np.append(t, [1] * degree)
            domain = (0, 1)

        return BSpline(control=cp, knots=t, degree=degree, domain=domain)

    def evaluate(self, u: ndarray) -> tuple[ndarray, ndarray]:
        """Evaluate spline."""
        x = self.control[:, 0]
        y = self.control[:, 1]
        spline = (self.knots, [x, y], self.degree)
        data = splev(u, spline)
        x_s = data[0]
        y_s = data[1]
        return x_s, y_s

    def uniform_u(self, start: float | None = None, end: float | None = None, points: int = 10):
        """Generate uniform u space."""
        if start is None:
            start = self.domain[0]
        if end is None:
            end = self.domain[1]
        u = np.linspace(start, end, points, endpoint=True)
        return u

    def evaluate_uniform(self, points: int = 10):
        """Evaluate spline on whole domain uniformly."""
        return self.evaluate(self.uniform_u(points=points))

    def evaluate_auto(self, max_distance=0.1):
        """Evaluate spline using automatically tuned number of evaluation points.

        Number of evaluation points chosen such that distance between two points in the (x, y) space
        is smaller or equal to max_distance.
        """

        ds_max = np.inf
        n_eval = 2 * self.control.shape[0]  # initial guess

        while ds_max > max_distance:
            x_s, y_s = self.evaluate_uniform(points=n_eval)
            s = arclen(x_s, y_s)
            ds_max = max(np.diff(s))
            factor = ds_max / max_distance
            n_eval = max(round(n_eval * factor), n_eval + 1)

        return x_s, y_s
