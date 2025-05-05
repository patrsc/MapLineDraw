"""Global coordinates utilities using WGS-84 ellipsoid.

References:
* https://en.wikipedia.org/w/index.php?title=Earth_radius&oldid=999938637
* https://en.wikipedia.org/w/index.php?title=Longitude&oldid=1001163010
* https://en.wikipedia.org/w/index.php?title=Latitude&oldid=997841104
* http://wiki.gis.com/wiki/index.php?title=Latitude&oldid=719292
"""
import numpy as np
from numpy import sin, cos, sqrt, radians, degrees


class Earth:
    """Earth geometric constants (using WGS-84 ellipsoid)."""
    # pylint: disable=too-few-public-methods

    a = 6378137.0  # semi-major axis [m]
    b = 6356752.3142  # semi-minor axis [m]
    e = 8.1819190842622e-2  # first eccentricity

    @property
    def radius(self):
        """Mean radius [m]."""
        r = (2 * self.a + self.b) / 3
        return r


class Point:
    """A point or sequence of points in 3D Euclidean space (x, y, z)."""

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __eq__(self, other):
        return isinstance(other, Point) and (
            np.array_equal(self.x, other.x, equal_nan=True) and
            np.array_equal(self.y, other.y, equal_nan=True) and
            np.array_equal(self.z, other.z, equal_nan=True)
        )

    @classmethod
    def vectorize(cls, p_list: list['Point']) -> 'Point':
        """Convert a list of Point instances to a Point with vector coordinates."""
        x = np.array([p.x for p in p_list])
        y = np.array([p.y for p in p_list])
        z = np.array([p.z for p in p_list])
        return cls(x, y, z)

    def __getitem__(self, index):
        """Extract single Point from Point sequence."""
        x = self.x[index]
        y = self.y[index]
        z = self.y[index]
        return Point(x, y, z)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y, self.z - other.z)

    def distance(self, p_ref: 'Point'):
        """Cartesian distance between two points.

        If the points have been converted from points on Earth, they should lie close to each
        other, otherwise this distance is not accurate.
        """
        d = (self - p_ref).length()
        return d

    def length(self):
        """Vector length (distance from origin)."""
        return norm(self.x, self.y, self.z)

    def shift(self) -> 'Point':
        """Shift point sequence by one index, prepend with first value."""
        return Point(shift(self.x), shift(self.y), shift(self.z))

    def path_segment_distance(self, two_dim=False):
        """Vector of segment distances of a path (sequence of points)."""
        current = Point(self.x, self.y, self.z)
        prev = current.shift()
        if two_dim:
            # this will correctly ignore NaN values in the z coordinate
            current.z = np.zeros_like(current.z)
            prev.z = current.z
        return current.distance(prev)

    def path_distance(self, two_dim=False):
        """Vector of cumulative segment distances of a path (sequence of points)."""
        return np.cumsum(self.path_segment_distance(two_dim=two_dim))

    def path_length(self, two_dim=False):
        """Total length of a path (sequence of points)."""
        return self.path_distance(two_dim=two_dim)[-1]

    def slope(self):
        """Path slope."""
        s = self.path_distance(two_dim=True)
        h = self.z
        return slope(s, h)

    def angle(self):
        """Path slope angle."""
        return angle(self.slope())

    def curvature(self, periodic=False):
        """Path curvature."""
        return curvature(self.x, self.y, periodic=periodic)

    def to_global(self, lat_ref=None, lon_ref=None):
        """Convert Point to GlobePoint.

        This is the inverse of `GlobePoint.to_cartesian()`.
        """
        if lat_ref is None or lon_ref is None:
            raise ValueError('reference point (lat_ref, lon_ref) must be specified')

        d_phi = self.y / north_south_curvature(lat_ref)
        phi = d_phi + radians(lat_ref)
        d_lambda = self.x / (west_east_curvature(lat_ref) * cos(phi))

        lat = degrees(phi)
        lon = degrees(d_lambda) + lon_ref
        alt = self.z
        return GlobePoint(lat, lon, alt)


class GlobePoint:
    """A point or sequence of points on the globe (WGS-84)."""

    def __init__(self, lat, lon, alt):
        self.lat = lat
        self.lon = lon
        self.alt = alt

    def __eq__(self, other):
        return isinstance(other, GlobePoint) and (
            np.array_equal(self.lat, other.lat, equal_nan=True) and
            np.array_equal(self.lon, other.lon, equal_nan=True) and
            np.array_equal(self.alt, other.alt, equal_nan=True)
        )

    def __getitem__(self, index):
        """Extract single GlobePoint from GlobePoint sequence."""
        lat = self.lat[index]
        lon = self.lon[index]
        alt = self.alt[index]
        return GlobePoint(lat, lon, alt)

    @classmethod
    def vectorize(cls, g_list: list['GlobePoint']) -> 'GlobePoint':
        """Convert a list of Point instances to a Point with vector coordinates."""
        lat = np.array([g.lat for g in g_list])
        lon = np.array([g.lon for g in g_list])
        alt = np.array([g.alt for g in g_list])
        return cls(lat, lon, alt)

    def shift(self):
        """Shift globe point sequence by one index, prepend with first value."""
        return GlobePoint(shift(self.lat), shift(self.lon), shift(self.alt))

    def to_cartesian(self, lat_ref=None, lon_ref=None):
        """Cartesian coordinates along Earth surface with respect to reference point at sea level

        This is the inverse of `Point.to_global()`.
        """
        if lat_ref is None:
            lat_ref = self.lat[0]
        if lon_ref is None:
            lon_ref = self.lon[0]
        phi = radians(self.lat)
        d_lambda = radians(self.lon - lon_ref)
        d_phi = radians(self.lat - lat_ref)

        x = west_east_curvature(lat_ref) * cos(phi) * d_lambda
        y = north_south_curvature(lat_ref) * d_phi
        z = self.alt
        return Point(x, y, z)

    def distance(self, g_ref):
        """Distance between two globe points.

        The points should lie close to each other, otherwise this distance is not accurate.
        """
        p = self.to_cartesian(lat_ref=g_ref.lat, lon_ref=g_ref.lon)
        p_ref = Point(0.0, 0.0, g_ref.alt)
        return p.distance(p_ref)

    def path_segment_distance(self, two_dim=False):
        """
        Compute relative distances between (lat, lon, alt) coordinate points.

        @param two_dim: True/False, whether altitude difference between the points should be
        considered
        @returns: array of distances between neighboring points
        """
        # vector of segment distances of a path (sequence of points)
        return self.to_cartesian().path_segment_distance(two_dim=two_dim)

    def path_distance(self, two_dim=False):
        """Vector of cumulative segment distances of a path (sequence of points)."""
        return self.to_cartesian().path_distance(two_dim=two_dim)

    def path_length(self, two_dim=False):
        """Total length of a path (sequence of points)."""
        return self.to_cartesian().path_length(two_dim=two_dim)

    def slope(self):
        """Path slope."""
        s = self.path_distance(two_dim=True)
        h = self.alt
        return slope(s, h)

    def angle(self):
        """Path slope angle."""
        return angle(self.slope())

    def curvature(self, periodic=False):
        """Path curvature."""
        return self.to_cartesian().curvature(periodic=periodic)


def angle(slope_rate):
    """Angle in radians."""
    return np.arctan(slope_rate)


def shift(x):
    """Shift vector by one index, prepend with first value (returns a shifted copy)."""
    y = np.roll(x, 1)
    y[0] = x[0]
    return y


def north_south_curvature(lat):
    """Radius of curvature in the (north-south) meridian."""
    e = Earth.e
    a = Earth.a
    return (1 - e**2) / a**2 * west_east_curvature(lat)**3


def west_east_curvature(lat):
    """Radius of curvature in the prime vertical."""
    phi = radians(lat)
    e = Earth.e
    a = Earth.a
    return a / sqrt(1 - e**2 * sin(phi)**2)


def norm(x, y, z):
    """Euclidian norm of a vector."""
    return sqrt(x ** 2 + y ** 2 + z ** 2)


def curvature(x, y, periodic=False):
    """Menger curvature: curvature of a circle that passes 3 points.

    Compute approximate curvature of a path by considering 2 neighboring points and current point
    * x: vector of n x coordinates of the path
    * y: vector of n y coordinates of the path

    see: https://en.wikipedia.org/wiki/Menger_curvature
    """
    # pylint: disable=too-many-locals
    n = len(x)
    c = np.zeros((n,))
    rng = range(0, n) if periodic else range(1, n - 1)
    if periodic:
        msg = "start and end point must be the same"
        assert np.isclose(x[0], x[-1]) and np.isclose(y[0], y[-1]), msg
        # remove redundant point if periodic
        x = x[0:n-1]
        y = y[0:n-1]
        n = len(x)
    for i in rng:
        # a ... point before, b ... current point, c ... point after
        x_a = x[i - 1]
        y_a = y[i - 1]
        x_b = x[i % n]
        y_b = y[i % n]
        x_c = x[(i + 1) % n]
        y_c = y[(i + 1) % n]
        d = np.sqrt((x_c - x_a) ** 2 + (y_c - y_a) ** 2)
        alpha = 2 * np.pi - (np.arctan2(y_c - y_b, x_c - x_b) - np.arctan2(y_b - y_a, x_b - x_a))
        c[i] = -2 * np.sin(alpha) / d
    return c


def slope(s, h):
    """Slope rate."""
    ds = np.diff(s)
    dh = np.diff(h)
    slope_rate = dh / ds
    slope_rate = np.concatenate([slope_rate, np.array([slope_rate[-1]])], axis=0)
    return slope_rate
