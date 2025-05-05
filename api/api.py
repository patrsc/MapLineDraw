"""REST API for computing B-spline curves."""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic_string_url import HttpUrl
import numpy as np
from fastapi_simple_errors import (
    NotFoundError,
    BadRequestError,
    error_responses_from_status_codes as err,
)

from lib.globe import GlobePoint, Point
from lib.spline import BSpline
from lib.geo import arclen, curvature, speed
from lib.util import generate_id
from lib.types import CurveInput, CurveOutput, PublishInput, PublishOutput, Project

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

    # Verify URL length limit
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
