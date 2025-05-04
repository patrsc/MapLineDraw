"""REST API for computing B-spline curves."""
import os
from typing import Annotated
from annotated_types import Len
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, model_validator, ConfigDict, StringConstraints
from pydantic_string_url import HttpUrl
import numpy as np
from fastapi_simple_errors import (
    NotFoundError,
    BadRequestError,
    error_responses_from_status_codes as err,
)

from globe import GlobePoint, Point
from spline import BSpline
from geo import arclen, curvature, speed
from util import generate_id

API_ROOT_PATH = os.environ.get("API_ROOT_PATH", "/")
API_ALLOWED_ORIGIN = os.environ.get("API_ALLOWED_ORIGIN", "http://localhost:3000")

MAX_FILE_SIZE = 1 * 1024 * 1024
MAX_URL_LENGTH = 250

app = FastAPI(title="MapLineDraw API", root_path=API_ROOT_PATH)

origins = [
    API_ALLOWED_ORIGIN,
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


class PublishInput(BaseModel):
    """Publish inputs."""
    url: HttpUrl


class PublishOutput(BaseModel):
    """Publish outputs."""
    id: str


class ProjectInfo(BaseModel):
    """Project info."""
    name: str
    description: str
    author: str

    model_config = ConfigDict(extra='forbid')


class LatLonPoint(BaseModel):
    """Control point."""
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)

    model_config = ConfigDict(extra='forbid')


class ProjectCurve(BaseModel):
    """Curve."""
    name: str
    controlPoints: list[LatLonPoint]
    closed: bool

    model_config = ConfigDict(extra='forbid')


class ProjectColorMapItem(BaseModel):
    """Color map item."""
    limit: None | float
    color: Annotated[str, StringConstraints(pattern=r'^#[0-9a-fA-F]{6}$')]
    label: str

    model_config = ConfigDict(extra='forbid')


class ProjectColorMap(BaseModel):
    """Color map."""
    name: str
    items: list[ProjectColorMapItem]

    model_config = ConfigDict(extra='forbid')


class ProjectMapSettings(BaseModel):
    """Project settings."""
    center: LatLonPoint
    zoom: int = Field(ge=0)
    background: str

    model_config = ConfigDict(extra='forbid')


class ProjectSettings(BaseModel):
    """Project settings."""
    selectedColorMapIndex: int = Field(ge=0)
    map: ProjectMapSettings

    model_config = ConfigDict(extra='forbid')


class Project(BaseModel):
    """Project."""
    info: ProjectInfo
    curves: list[ProjectCurve]
    colorMaps: list[ProjectColorMap]
    settings: ProjectSettings

    model_config = ConfigDict(extra='forbid')


@app.post("/curve")
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


@app.post("/publish", responses=err(404, 400))
def publish_project(data: PublishInput) -> PublishOutput:
    """Publish a project."""
    # pylint: disable=redefined-builtin
    # Verify URL length limit or fail with 400
    if len(data.url) > MAX_URL_LENGTH:
        msg = f"The provided URL is too long. At most {MAX_URL_LENGTH} characters are supported."
        raise BadRequestError(msg)

    download_and_parse(data.url)

    # Generate id
    id = generate_id()

    # Store item including current date

    print(data)
    res = PublishOutput(id=id)
    raise NotImplementedError()


@app.get("/public/:id", responses=err(404, 400))
def get_public_project(id: str) -> Project:
    """Get a published project as JSON."""
    # pylint: disable=redefined-builtin
    # Get stored URL or fail with 404
    not_found_message = "Project not found."
    url = ""
    if not url:
        raise NotFoundError(not_found_message)

    try:
        project = download_and_parse(url)
    except NotFoundError:
        raise NotFoundError(not_found_message)  # overwrite message

    return project


def download_and_parse(url: HttpUrl) -> Project:
    """Download from URL and parse JSON."""
    # Download file from URL or fail with 404 if source file cannot be accessed
    msg = "File cannot be accessed. Make sure it is publicly accessible and a direct download link."
    raise NotFoundError(msg)

    # Verify file size limit or fail with 422
    msg = (
        f"Files larger than {MAX_FILE_SIZE/1024**2} MB are not supported. "
        "Use a smaller project file."
    )
    raise BadRequestError(msg)

    # Parse JSON or fail with 422
    raise BadRequestError("The file content is not valid JSON.")

    # Validate JSON schema or fail with 422
    raise BadRequestError("The file does not respect the JSON schema of MapLineDraw.")

    print(url)
    return project
