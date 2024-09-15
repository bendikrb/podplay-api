"""podplay_api models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from mashumaro import field_options
from mashumaro.config import BaseConfig
from mashumaro.mixins.orjson import DataClassORJSONMixin

from .const import IMAGE_WIDTHS
from .utils import build_image_url


@dataclass
class BaseDataClassORJSONMixin(DataClassORJSONMixin):
    class Config(BaseConfig):
        omit_none = True
        omit_default = True


class PodPlayLanguage(StrEnum):
    NO = "no"
    SE = "sv"
    FI = "fi"
    EN = "en"


class PodPlayRegion(StrEnum):
    NO = "no"
    SE = "se"
    FI = "fi"
    GLOBAL = "en"


class PodcastType(StrEnum):
    SERIAL = "serial"
    EPISODIC = "episodic"


class EpisodeType(StrEnum):
    FULL = "full"
    TRAILER = "trailer"


@dataclass
class PodPlayCategory(BaseDataClassORJSONMixin):
    id: int
    name: str
    parent_id: int | None = None
    children: list[PodPlayCategory] = field(default_factory=list)

    def __repr__(self):
        return f"({self.id}){self.name}"


@dataclass
class PodPlayImage:
    url: str
    width: int

    def __repr__(self):
        return f"[{self.width}] {self.url}"


@dataclass
class PodPlayPodcast(BaseDataClassORJSONMixin):
    id: int
    title: str
    author: str
    image: str
    images: list[PodPlayImage] = field(init=False)
    original: bool
    description: str
    language_iso: str
    popularity: float
    category_id: list[int] | None = field(default=None)
    category: list[PodPlayCategory] | None = field(init=False, default=None)
    link: str | None = field(default=None)
    rss: str | None = field(default=None)
    seasonal: bool | None = field(default=None)
    slug: str | None = field(default=None)
    type: PodcastType | None = field(default=None)

    def __post_init__(self):
        self.images = [
            PodPlayImage(
                str(build_image_url(self.image, width=w)),
                w,
            )
            for w in IMAGE_WIDTHS
        ]


@dataclass
class PodPlayEpisode(BaseDataClassORJSONMixin):
    id: int
    title: str
    description: str
    encoded: bool
    exclusive: bool
    mime_type: str
    podcast_id: int
    published: datetime = field(
        metadata=field_options(deserialize=datetime.fromtimestamp)
    )
    slug: str
    type: EpisodeType
    url: str
    duration: int | None = None
    episode: int | None = None
    season: int | None = None
