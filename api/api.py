"""REST API for computing B-spline curves."""
from typing import Annotated
from annotated_types import Len
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, model_validator
import numpy as np

from globe import GlobePoint, Point
from spline import BSpline
from geo import arclen, curvature, speed

app = FastAPI(title="Curve API")

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_CURVATURE = 100.0
MAX_SPEED = 1e4  # km/h

InputList = Annotated[list[float], Len(2)]


class ControlPoints(BaseModel):
    """Control points."""
    lat: InputList
    lon: InputList

    @model_validator(mode='after')
    def check_lengths(self):
        """Check length consistency."""
        if len(self.lat) != len(self.lon):
            raise ValueError("lat and lon must have the same length")
        return self


class CurveInput(BaseModel):
    """Inputs."""
    control: ControlPoints
    desired_degree: Annotated[int, Field(strict=True, ge=1)]
    closed: bool
    max_distance: Annotated[float, Field(strict=True, gt=0)]


class CurveOutput(BaseModel):
    """Outputs."""
    degree: int
    lat: list[float]
    lon: list[float]
    distance: list[float]
    curvature: list[float]
    speed: list[float]


@app.post("/curve", response_model=CurveOutput)
def compute_curve(data: CurveInput) -> CurveOutput:
    """Compute B-spline curve."""
    # pylint: disable=too-many-locals
    lat = np.array(data.control.lat)
    lon = np.array(data.control.lon)
    alt = np.zeros_like(lat)
    g = GlobePoint(lat, lon, alt)
    lat_ref = g.lat[0]
    lon_ref = g.lon[0]
    p = g.to_cartesian(lat_ref=lat_ref, lon_ref=lon_ref)
    control_points = [(p.x[i], p.y[i]) for i in range(len(p.x))]
    max_distance = data.max_distance
    spline = BSpline.create(control_points, data.desired_degree, closed=data.closed)
    x_s, y_s = spline.evaluate_auto(max_distance=max_distance)
    c = curvature(x_s, y_s, closed=data.closed)
    c[np.isnan(c)] = MAX_CURVATURE
    c[c == np.inf] = MAX_CURVATURE
    c[c == -np.inf] = -MAX_CURVATURE
    v = speed(c, 1.73) * 3.6
    v[v == np.inf] = MAX_SPEED
    z_s = np.zeros_like(x_s)
    ps = Point(x_s, y_s, z_s)
    gs = ps.to_global(lat_ref=lat_ref, lon_ref=lon_ref)
    return CurveOutput(
        degree=spline.degree,
        lat=gs.lat,
        lon=gs.lon,
        distance=arclen(x_s, y_s),
        curvature=c,
        speed=v,
    )
