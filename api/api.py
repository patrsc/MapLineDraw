"""REST API for computing B-spline curves."""
import os
import re
import json
from datetime import datetime, timezone
import aiohttp
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
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
from lib.types import CurveInput, CurveOutput, PublishInput, PublishOutput, Project, ProjectStore

API_ROOT_PATH = os.environ.get("API_ROOT_PATH", "/")
API_ALLOWED_ORIGIN = os.environ.get("API_ALLOWED_ORIGIN", "http://localhost:3000")

MAX_FILE_SIZE = 1 * 1024 * 1024
MAX_URL_LENGTH = 250
PROJECT_STORE = os.path.join(os.path.dirname(__file__), "projects")

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

if not os.path.isdir(PROJECT_STORE):
    os.makedirs(PROJECT_STORE)


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
async def publish_project(data: PublishInput) -> PublishOutput:
    """Publish a project."""
    # pylint: disable=redefined-builtin
    url = convert_known_cloud_provider_url(data.url)

    # Verify URL length limit
    if len(url) > MAX_URL_LENGTH:
        msg = f"The provided URL is too long. At most {MAX_URL_LENGTH} characters are supported."
        raise BadRequestError(msg)

    # Download project
    project = await download_project(url)
    print(f'Project name: {project.info.name}')

    # Generate id
    id = generate_id()

    # Store item including current date
    value = ProjectStore(url=url, time=datetime.now(timezone.utc))
    json_str = value.model_dump_json()
    with open(os.path.join(PROJECT_STORE, f"{id}.json"), 'w', encoding='utf8') as f:
        f.write(json_str)
    return PublishOutput(id=id)


@app.get("/public/:id", responses=err(404, 400))
async def get_public_project(id: str) -> Project:
    """Get a published project as JSON."""
    # pylint: disable=redefined-builtin

    # Get stored URL
    not_found_message = "Project not found."
    try:
        with open(os.path.join(PROJECT_STORE, f"{id}.json"), 'r', encoding='utf8') as f:
            value = ProjectStore.model_validate_json(f.read())
    except FileNotFoundError as e:
        raise NotFoundError(not_found_message) from e
    url = value.url

    try:
        project = await download_project(url)
    except NotFoundError as e:
        raise NotFoundError(not_found_message) from e # overwrite message

    return project


async def download_project(url: HttpUrl) -> Project:
    """Download from URL and parse project JSON."""
    # Download file from URL or fail if source file cannot be downloaded or is too large
    data = await download_file(url, MAX_FILE_SIZE)

    # Parse JSON
    try:
        text = data.decode('utf-8')
        json_data = json.loads(text)
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise BadRequestError("The file content is not valid JSON.") from e

    # Validate JSON schema
    try:
        project = Project.model_validate(json_data)
    except ValidationError as e:
        msg = "The file does not respect the MapLineDraw project JSON schema."
        raise BadRequestError(msg) from e

    return project


async def download_file(url: str, max_size: int) -> bytes:
    """
    Downloads a file from the given URL into memory as a bytes object.
    Aborts early if the file size exceeds max_size.

    :param url: URL of the file to download.
    :param max_size: Maximum size in bytes. Download fails if exceeded.
    :return: The downloaded file as bytes.
    :raises ValueError: If file size exceeds max_size.
    :raises aiohttp.ClientError: For network-related errors.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if not response.ok:
                msg = (
                    "File cannot be accessed. "
                    "Make sure it is publicly accessible and a direct download link."
                )
                raise NotFoundError(msg)
            data = bytearray()
            async for chunk in response.content.iter_chunked(1024):
                data.extend(chunk)
                if len(data) > max_size:
                    msg = (
                        f"Files larger than {max_size/(1024**2)} MB are not supported. "
                        "Use a smaller project file."
                    )
                    raise BadRequestError(msg)
            return bytes(data)


def convert_known_cloud_provider_url(url: HttpUrl) -> HttpUrl:
    """Convert URLs from known cloud providers to direct download URLs."""
    if 'dropbox.com' in (url.url.host or ''):
        if 'dl=0' in url:
            return HttpUrl(url.replace('dl=0', 'dl=1'))
    if 'google.com' in (url.url.host or ''):
        match = re.match(r'https?://drive\.google\.com/file/d/([^/]+)/view', url)
        if match:
            file_id = match.group(1)
            return HttpUrl(f'https://drive.google.com/uc?export=download&id={file_id}')
    return url
