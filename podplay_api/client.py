"""PodPlay API."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import socket
from typing import Literal, Self

from aiohttp.client import ClientError, ClientResponseError, ClientSession
from aiohttp.hdrs import METH_GET
import async_timeout
from asyncstdlib.functools import cached_property
import orjson
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

    user_agent: str | None = None

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
        headers = kwargs.get("headers")
        headers = self.request_header if headers is None else dict(headers)

        params = kwargs.get("params")
        if params is not None:
            kwargs.update(params={k: v for k, v in params.items() if v is not None})

        _LOGGER.debug(
            "Executing %s API request to %s.",
            method,
            url.with_query(kwargs.get("params")),
        )
        _LOGGER.debug("With headers: %s", headers)
        if self.session is None:
            self.session = ClientSession()
            _LOGGER.debug("New session created.")
            self._close_session = True

        try:
            async with async_timeout.timeout(self.request_timeout):
                response = await self.session.request(
                    method,
                    url,
                    **kwargs,
                    headers=headers,
                )
                response.raise_for_status()
        except asyncio.TimeoutError as exception:
            raise PodPlayApiConnectionTimeoutError(
                "Timeout occurred while connecting to the PodPlay API"
            ) from exception
        except (ClientError, ClientResponseError, socket.gaierror) as exception:
            raise PodPlayApiConnectionError(
                "Error occurred while communicating with the PodPlay API"
            ) from exception
        content_type = response.headers.get("Content-Type", "")
        text = await response.text()
        if "application/json" not in content_type:
            msg = "Unexpected response from the PodPlay API"
            raise PodPlayApiError(
                msg,
                {"Content-Type": content_type, "response": text},
            )
        return orjson.loads(text)

    @property
    def request_header(self):
        """Generate default headers."""
        return {
            "Accept": "application/json",
            "User-Agent": self.user_agent or PODPLAY_USER_AGENT,
        }

    async def _get_pages(
        self,
        uri,
        get_pages: int | None = None,
        page_size: int | None = None,
        params: dict | None = None,
        order: PagingOrderType = "desc",
        items_key: str | None = None,
    ):
        offset = 0
        params = params or {}
        get_pages = get_pages or 99
        page_size = page_size or 50
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
                total = new_results.get("total")
                if not isinstance(new_results, list) and items_key is not None:
                    new_results = new_results.get(items_key, [])
                if not new_results:
                    break
                data.extend(new_results)
                offset += len(new_results)

                if offset >= total:
                    break
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
            },
        )
        return [PodPlayPodcast.from_dict(d) for d in data["results"]]

    async def _process_podcast(self, podcast: PodPlayPodcast) -> PodPlayPodcast:
        podcast.category = await self.resolve_category_ids(podcast.category_id)
        return podcast

    async def get_podcast(self, podcast_id: int) -> PodPlayPodcast:
        data = await self._request(
            f"podcast/{podcast_id}",
        )
        return await self._process_podcast(PodPlayPodcast.from_dict(data["podcast"]))

    async def get_podcasts(self, podcast_id: list[int]) -> list[PodPlayPodcast]:
        data = await self._request(
            "podcast-by-id",
            params={
                "id": [str(p) for p in podcast_id],
            },
        )
        return [
            await self._process_podcast(PodPlayPodcast.from_dict(d))
            for d in data["results"]
        ]

    async def get_episode(self, episode_id: int) -> PodPlayEpisode:
        data = await self._request(
            f"episode/{episode_id}",
        )
        return PodPlayEpisode.from_dict(data["episode"])

    async def get_episodes(self, episode_id: list[int]) -> list[PodPlayEpisode]:
        data = await self._request(
            "episode-by-id",
            params={
                "id": [str(e) for e in episode_id],
            },
        )
        return [PodPlayEpisode.from_dict(d) for d in data["results"]]

    async def get_podcast_episodes(
        self,
        podcast_id: int,
        pages: int | None = None,
        page_size: int | None = None,
    ) -> list[PodPlayEpisode]:
        data = await self._get_pages(
            f"podcast/{podcast_id}/episode",
            get_pages=pages,
            page_size=page_size,
            items_key="results",
        )

        return [PodPlayEpisode.from_dict(d) for d in data]

    async def search_podcast(
        self,
        search: str,
    ) -> list[PodPlayPodcast]:
        results = await self._request(
            "search",
            params={
                "q": search,
            },
        )
        return [
            await self._process_podcast(PodPlayPodcast.from_dict(data))
            for data in results["results"]
        ]

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
