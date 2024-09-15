"""Tests for podplay-api."""
from __future__ import annotations

import asyncio
import logging
from unittest.mock import AsyncMock

import aiohttp
from aiohttp.web_response import json_response
from aresponses import ResponsesMockServer
import pytest
from yarl import URL

from podplay_api import PodPlayClient, PodPlayEpisode
from podplay_api.const import PODPLAY_API_URL
from podplay_api.exceptions import (
    PodPlayApiConnectionError,
    PodPlayApiConnectionTimeoutError,
    PodPlayApiError,
)
from podplay_api.models import (
    PodPlayPodcast,
)

from .helpers import build_path_pattern, load_fixture_json

logger = logging.getLogger(__name__)


@pytest.mark.parametrize(
    "podcast_id",
    [
        31428,
    ],
)
async def test_get_podcast(aresponses: ResponsesMockServer, podcast_id: int):
    fixture_name = f"podcast_{podcast_id}"
    uri = f"podcast/{podcast_id}"
    fixture = load_fixture_json(fixture_name)
    aresponses.add(
        URL(PODPLAY_API_URL).host,
        build_path_pattern(uri),
        "GET",
        json_response(data=fixture),
    )
    aresponses.add(
        URL(PODPLAY_API_URL).host,
        build_path_pattern("category"),
        "GET",
        json_response(data=load_fixture_json("category")),
    )

    async with aiohttp.ClientSession() as session:
        api = PodPlayClient(session=session)
        result = await api.get_podcast(podcast_id)
        assert isinstance(result, PodPlayPodcast)


@pytest.mark.parametrize(
    "podcast_ids",
    [
        [31428, 41127],
    ],
)
async def test_get_podcasts(aresponses: ResponsesMockServer, podcast_ids: list[int]):
    fixture_name = f"podcasts_{"_".join([str(e) for e in podcast_ids])}"
    uri = "podcast-by-id"
    fixture = load_fixture_json(fixture_name)
    aresponses.add(
        URL(PODPLAY_API_URL).host,
        build_path_pattern(uri),
        "GET",
        json_response(data=fixture),
    )
    aresponses.add(
        URL(PODPLAY_API_URL).host,
        build_path_pattern("category"),
        "GET",
        json_response(data=load_fixture_json("category")),
    )

    async with aiohttp.ClientSession() as session:
        api = PodPlayClient(session=session)
        result = await api.get_podcasts(podcast_ids)
        assert isinstance(result, list)
        assert all(isinstance(r, PodPlayPodcast) for r in result)


@pytest.mark.parametrize(
    "podcast_id",
    [
        31428,
    ],
)
async def test_get_episode_ids(aresponses: ResponsesMockServer, podcast_id: int):
    fixture_name = f"podcast_episodes_{podcast_id}"
    uri = f"podcast/{podcast_id}/episode"
    fixture = load_fixture_json(fixture_name)
    aresponses.add(
        URL(PODPLAY_API_URL).host,
        build_path_pattern(uri),
        "GET",
        json_response(data=fixture),
    )

    async with aiohttp.ClientSession() as session:
        api = PodPlayClient(session=session)
        result = await api.get_episode_ids(podcast_id)
        fixtures_ids = [e["id"] for e in fixture["results"]]
        assert isinstance(result, list)
        assert result == fixtures_ids


@pytest.mark.parametrize(
    "episode_id",
    [
        2617509,
    ],
)
async def test_get_episode(aresponses: ResponsesMockServer, episode_id: int):
    fixture_name = f"episode_{episode_id}"
    uri = f"episode/{episode_id}"
    fixture = load_fixture_json(fixture_name)
    aresponses.add(
        URL(PODPLAY_API_URL).host,
        build_path_pattern(uri),
        "GET",
        json_response(data=fixture),
    )

    async with aiohttp.ClientSession() as session:
        api = PodPlayClient(session=session)
        result = await api.get_episode(episode_id)
        assert isinstance(result, PodPlayEpisode)


@pytest.mark.parametrize(
    "episode_ids",
    [
        [2617509, 2617516],
    ],
)
async def test_get_episodes(aresponses: ResponsesMockServer, episode_ids: list[int]):
    fixture_name = f"episodes_{"_".join([str(e) for e in episode_ids])}"
    uri = "episode-by-id"
    fixture = load_fixture_json(fixture_name)
    aresponses.add(
        URL(PODPLAY_API_URL).host,
        build_path_pattern(uri),
        "GET",
        json_response(data=fixture),
    )

    async with aiohttp.ClientSession() as session:
        api = PodPlayClient(session=session)
        result = await api.get_episodes(episode_ids)
        assert isinstance(result, list)
        assert all(isinstance(r, PodPlayEpisode) for r in result)


@pytest.mark.parametrize(
    "podcast_id",
    [
        31428,
    ],
)
async def test_get_podcast_episodes(aresponses: ResponsesMockServer, podcast_id: int):
    fixture_name = f"podcast_episodes_{podcast_id}"
    uri = f"podcast/{podcast_id}/episode"
    fixture = load_fixture_json(fixture_name)
    aresponses.add(
        URL(PODPLAY_API_URL).host,
        build_path_pattern(uri),
        "GET",
        json_response(data=fixture),
    )

    async with aiohttp.ClientSession() as session:
        api = PodPlayClient(session=session)
        result = await api.get_podcast_episodes(podcast_id)
        assert isinstance(result, list)
        assert all(isinstance(r, PodPlayEpisode) for r in result)


@pytest.mark.parametrize(
    "query",
    [
        "dude",
    ],
)
async def test_search_podcasts(aresponses: ResponsesMockServer, query: str):
    fixture_name = f"search_{query}"
    uri = "search"
    fixture = load_fixture_json(fixture_name)
    aresponses.add(
        URL(PODPLAY_API_URL).host,
        build_path_pattern(uri),
        "GET",
        json_response(data=fixture),
    )
    aresponses.add(
        URL(PODPLAY_API_URL).host,
        build_path_pattern("category"),
        "GET",
        json_response(data=load_fixture_json("category")),
    )

    async with aiohttp.ClientSession() as session:
        api = PodPlayClient(session=session)
        result = await api.search_podcast(query)
        assert isinstance(result, list)
        assert all(isinstance(r, PodPlayPodcast) for r in result)


@pytest.mark.parametrize(
    "category_id",
    [
        1303,
    ],
)
async def test_get_podcasts_by_category(
    aresponses: ResponsesMockServer, category_id: int
):
    fixture_name = f"podcasts_by_category_{category_id}"
    uri = "toplist"
    fixture = load_fixture_json(fixture_name)
    aresponses.add(
        URL(PODPLAY_API_URL).host,
        build_path_pattern(uri),
        "GET",
        json_response(data=fixture),
    )
    aresponses.add(
        URL(PODPLAY_API_URL).host,
        build_path_pattern("category"),
        "GET",
        json_response(data=load_fixture_json("category")),
    )

    async with aiohttp.ClientSession() as session:
        api = PodPlayClient(session=session)
        result = await api.get_podcasts_by_category(category_id)
        assert isinstance(result, list)
        assert all(isinstance(r, PodPlayPodcast) for r in result)


async def test_internal_session(aresponses: ResponsesMockServer):
    """Test JSON response is handled correctly."""
    aresponses.add(
        URL(PODPLAY_API_URL).host,
        build_path_pattern("language"),
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text='{"status": "ok"}',
        ),
    )
    async with PodPlayClient() as api:
        response = await api._request("language")
        assert response == {"status": "ok"}


async def test_timeout(aresponses: ResponsesMockServer):
    """Test request timeout."""

    # Faking a timeout by sleeping
    async def response_handler(_: aiohttp.ClientResponse):
        """Response handler for this test."""
        await asyncio.sleep(2)
        return aresponses.Response(body="Helluu")

    aresponses.add(
        URL(PODPLAY_API_URL).host,
        build_path_pattern("language"),
        "GET",
        response_handler,
    )

    async with aiohttp.ClientSession() as session:
        api = PodPlayClient(session=session, request_timeout=1)
        with pytest.raises(
            (PodPlayApiConnectionError, PodPlayApiConnectionTimeoutError)
        ):
            assert await api._request("language")


async def test_http_error400(aresponses: ResponsesMockServer):
    """Test HTTP 404 response handling."""
    aresponses.add(
        URL(PODPLAY_API_URL).host,
        build_path_pattern("language"),
        "GET",
        aresponses.Response(text="Not found", status=404),
    )

    async with aiohttp.ClientSession() as session:
        api = PodPlayClient(session=session)
        with pytest.raises(PodPlayApiError):
            assert await api._request("language")


async def test_unexpected_response(aresponses: ResponsesMockServer):
    """Test unexpected response handling."""
    aresponses.add(
        URL(PODPLAY_API_URL).host,
        build_path_pattern("language"),
        "GET",
        aresponses.Response(text="Woopwoop", status=200, content_type="text/plain"),
    )

    async with aiohttp.ClientSession() as session:
        api = PodPlayClient(session=session)
        with pytest.raises(PodPlayApiError):
            assert await api._request("language")


async def test_close():
    api = PodPlayClient()
    api.session = AsyncMock(spec=aiohttp.ClientSession)
    api._close_session = True  # pylint: disable=protected-access
    await api.close()
    api.session.close.assert_called_once()


async def test_context_manager():
    async with PodPlayClient() as api:
        assert isinstance(api, PodPlayClient)
    assert api.session is None or api.session.closed
