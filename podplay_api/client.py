"""PodPlay API."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from http import HTTPStatus
import json
import math
import socket
from typing import Literal, Self

from aiohttp.client import ClientError, ClientSession
from aiohttp.hdrs import METH_GET
import async_timeout
from asyncstdlib.functools import cached_property
from yarl import URL

from podplay_api.const import (
    LOGGER as _LOGGER,
    PODPLAY_API_URL,
    PODPLAY_USER_AGENT,
    TIMEOUT,
)
from podplay_api.exceptions import (
    PodPlayApiConnectionError,
    PodPlayApiConnectionTimeoutError,
    PodPlayApiError,
    PodPlayApiRateLimitError,
)
from podplay_api.models import (
    PodPlayCategory,
    PodPlayEpisode,
    PodPlayLanguage,
    PodPlayPodcast,
)
from podplay_api.utils import nested_categories

PagingOrderType = Literal["asc", "desc"]


@dataclass
class PodPlayClient:
    """PodPlay API client."""

    language: PodPlayLanguage = PodPlayLanguage.EN

    request_timeout: int = TIMEOUT
    session: ClientSession | None = None

    _close_session: bool = False

    def _build_request_url(self, uri: str) -> URL:
        return URL(f"{PODPLAY_API_URL}/{self.language}/{uri}")

    async def _request(
        self,
        uri: str,
        method: str = METH_GET,
        **kwargs,
    ) -> str | dict[any, any] | list | None:
        """Make a request."""
        url = self._build_request_url(uri)
        _LOGGER.debug("Executing %s API request to %s.", method, url)
        headers = kwargs.get("headers")
        headers = self.request_header if headers is None else dict(headers)

        _LOGGER.debug("With headers: %s", headers)
        if self.session is None:
            self.session = ClientSession()
            _LOGGER.debug("New session created.")
            self._close_session = True

        try:
            with async_timeout.timeout(self.request_timeout):
                response = await self.session.request(
                    method,
                    url,
                    **kwargs,
                    headers=headers,
                )
        except asyncio.TimeoutError as exception:
            raise PodPlayApiConnectionTimeoutError(
                "Timeout occurred while connecting to the PodPlay API"
            ) from exception
        except (ClientError, socket.gaierror) as exception:
            raise PodPlayApiConnectionError(
                "Error occurred while communicating with the PodPlay API"
            ) from exception

        content_type = response.headers.get("Content-Type", "")
        # Error handling
        if (response.status // 100) in [4, 5]:
            contents = await response.read()
            response.close()

            if response.status == HTTPStatus.TOO_MANY_REQUESTS:
                raise PodPlayApiRateLimitError(
                    "Rate limit error has occurred with the PodPlay API"
                )

            if content_type == "application/json":
                raise PodPlayApiError(response.status, json.loads(contents.decode("utf8")))
            raise PodPlayApiError(response.status, {"message": contents.decode("utf8")})

        # Handle empty response
        if response.status == HTTPStatus.NO_CONTENT:
            _LOGGER.warning("Request to <%s> resulted in status 204. Your dataset could be out of date.", url)
            return None

        if "application/json" in content_type:
            result = await response.json()
            _LOGGER.debug("Response: %s", str(result))
            return result
        result = await response.text()
        _LOGGER.debug("Response: %s", str(result))
        return result

    @property
    def request_header(self):
        """Generate default headers."""

        return {
            "User-Agent": PODPLAY_USER_AGENT,
            "Accept": "application/json",
        }


    async def _get_pages(
        self,
        uri,
        get_pages: int = math.inf,
        page_size: int = 50,
        params: dict | None = None,
        order: PagingOrderType = "desc",
        items_key: str | None = None,
    ):
        offset = 0
        params = params or {}
        data = []

        try:
            for _page in range(get_pages):
                new_results = await self._request(
                    uri,
                    params={
                        "limit": page_size,
                        "offset": offset,
                        "order": order,
                        **params,
                    },
                )
                if not isinstance(new_results, list) and items_key is not None:
                    new_results = new_results.get(items_key, [])
                if not new_results:
                    break
                data.extend(new_results)
                offset += len(new_results)
        except PodPlayApiError as err:
            _LOGGER.warning("Error occurred while fetching pages from %s: %s", uri, err)

        return data

    @cached_property
    async def categories(self) -> list[PodPlayCategory]:
        data = await self._request("category")
        categories = [PodPlayCategory.from_dict(d) for d in data["results"]]
        return nested_categories(categories)

    async def resolve_category_ids(self, ids: list[int]) -> list[PodPlayCategory]:
        categories = await self.categories
        return [c for c in categories if c.id in ids]

    async def get_podcasts_by_category(
        self,
        category: PodPlayCategory | int,
        originals: bool = False,
    ) -> list[PodPlayPodcast]:
        category_id = category.id if isinstance(category, PodPlayCategory) else category
        data = await self._request(
            "toplist",
            params={
                "category_id": category_id,
                "original": str(originals).lower(),
            })
        return [PodPlayPodcast.from_dict(d) for d in data["results"]]

    async def get_popular_podcasts(
        self,
        category: list[PodPlayCategory] | None = None,
        pages: int | None = None,
        page_size: int | None = None,
    ) -> list[PodPlayPodcast]:
        pass

    async def get_podcast(self, podcast_id: int) -> PodPlayPodcast:
        data = await self._request(
            f"podcast/{podcast_id}",
        )
        return PodPlayPodcast.from_dict(data)

    async def get_podcast_episodes(self, podcast_id: int) -> list[PodPlayEpisode]:
        data = await self._get_pages(
            f"podcast/{podcast_id}/episode",
        )

        return [PodPlayEpisode.from_dict(d) for d in data]

    async def search_podcast(
        self,
        search: str,
        pages: int | None = None,
        page_size: int | None = None,
    ) -> list[PodPlayPodcast]:
        podcasts = await self._get_pages(
            "search",
            params={
                "q": search,
            },
            get_pages=pages,
            page_size=page_size,
            items_key="results",
        )
        return [PodPlayPodcast.from_dict(data) for data in podcasts]

    async def get_episode_ids(self, podcast_id: int) -> list[int]:
        episodes = await self.get_podcast_episodes(podcast_id)
        return [e.id for e in episodes]

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> Self:
        """Async enter."""
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        """Async exit."""
        await self.close()
