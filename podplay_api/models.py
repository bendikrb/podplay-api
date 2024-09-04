"""podplay_api models."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING

from mashumaro.config import BaseConfig
from mashumaro.mixins.orjson import DataClassORJSONMixin

if TYPE_CHECKING:
    from datetime import datetime


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

    def __repr__(self):
        return self.value.lower()

    def uri_segment(self):
        return f"/{self.value}"


class PodPlayRegion(StrEnum):
    NO = "no"
    SE = "se"
    FI = "fi"
    GLOBAL = "en"

    def __repr__(self):
        return self.value.lower()


@dataclass
class PodPlayCategory(BaseDataClassORJSONMixin):
    id: int
    name: str
    parent_id: int | None = None
    children: list[PodPlayCategory] = field(default_factory=list)


@dataclass
class PodPlayPodcast(BaseDataClassORJSONMixin):
    id: int
    title: str
    author: str
    image: str
    original: bool
    description: str
    language_iso: str
    popularity: float
    category_id: list[int] | None = field(default=None)
    link: str | None = field(default=None)
    rss: str | None = field(default=None)
    seasonal: bool | None = field(default=None)
    slug: str | None = field(default=None)
    type: str | None = field(default=None)


@dataclass
class PodPlayEpisode(BaseDataClassORJSONMixin):
    id: int
    title: str
    description: str
    duration: int
    encoded: bool
    exclusive: bool
    mime_type: str
    podcast_id: int
    published: datetime
    slug: str
    type: str
    url: str
    episode: int | None = None
    season: int | None = None
