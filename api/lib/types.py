"""Type definitions."""
from typing import Annotated
from annotated_types import Len
from pydantic import BaseModel, Field, model_validator, ConfigDict, StringConstraints
from pydantic_string_url import HttpUrl


InputList = Annotated[list[float], Len(2)]
HexColor = Annotated[str, StringConstraints(pattern=r'^#[0-9a-fA-F]{6}$')]


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
    color: HexColor
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
