"""podplay_api cli tool."""

from __future__ import annotations

import argparse
import asyncio
import logging
from typing import TYPE_CHECKING

from rich.box import SIMPLE_HEAD
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel

from podplay_api.client import PodPlayClient
from podplay_api.utils import pretty_dataclass, pretty_dataclass_list, seconds_to_time

if TYPE_CHECKING:
    from aiohttp.client import ClientSession

    from podplay_api.models import PodPlayCategory

http_client: ClientSession

console = Console(width=200)


def main_parser() -> argparse.ArgumentParser:
    """Create the ArgumentParser with all relevant subparsers."""
    parser = argparse.ArgumentParser(
        description="A simple executable to use and test the library."
    )
    _add_default_arguments(parser)

    subparsers = parser.add_subparsers(dest="cmd")
    subparsers.required = True

    categories_parser = subparsers.add_parser(
        "categories", description="Get a list of categories."
    )
    categories_parser.set_defaults(func=get_categories)

    category_parser = subparsers.add_parser(
        "category", description="Get podcasts in a category."
    )
    category_parser.add_argument("category_id", type=int, help="Category id")
    category_parser.add_argument(
        "--originals", action="store_true", help='Only get "original" podcasts'
    )
    category_parser.set_defaults(func=get_category)

    get_podcast_parser = subparsers.add_parser("podcast", description="Get podcast(s).")
    get_podcast_parser.add_argument(
        "podcast_id", type=int, nargs="+", help="The podcast id"
    )
    get_podcast_parser.set_defaults(func=get_podcast)

    get_episodes_parser = subparsers.add_parser(
        "episodes", description="Get podcast episodes."
    )
    get_episodes_parser.add_argument("podcast_id", type=int, help="The podcast id")
    _add_paging_arguments(get_episodes_parser)
    get_episodes_parser.set_defaults(func=get_podcast_episodes)

    get_episode_parser = subparsers.add_parser("episode", description="Get episode(s).")
    get_episode_parser.add_argument(
        "episode_id", type=int, nargs="+", help="The episode id"
    )
    get_episode_parser.set_defaults(func=get_episode)

    search_podcasts_parser = subparsers.add_parser(
        "search", description="Search podcasts."
    )
    search_podcasts_parser.add_argument("search", help="Search term")
    search_podcasts_parser.set_defaults(func=search_podcasts)

    return parser


def _add_default_arguments(parser: argparse.ArgumentParser) -> None:
    """Add default arguments."""
    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="Logging verbosity level"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument(
        "-l", "--language", help="(optional) Language to use", default="en"
    )


def _add_paging_arguments(parser: argparse.ArgumentParser) -> None:
    """Add paging arguments."""
    parser.add_argument("--pages", type=int, help="Number of pages to return")
    parser.add_argument("--per_page", type=int, help="Number of results per page")


async def get_categories(args) -> None:
    """Retrieve categories."""
    async with PodPlayClient(language=args.language) as client:
        categories = await client.categories
        console.print(categories_tree(categories))


async def get_category(args) -> None:
    """Retrieve category."""
    async with PodPlayClient(language=args.language) as client:
        podcasts = await client.get_podcasts_by_category(
            category=args.category_id, originals=args.originals
        )
        tables = [
            Panel(
                pretty_dataclass_list(
                    podcasts,
                    title="Podcasts",
                    visible_fields=[
                        "id",
                        "title",
                        "popularity",
                    ],
                ),
                box=SIMPLE_HEAD,
            ),
            Panel(
                f"podplay episodes {podcasts[0].id}",
                title="Get episodes",
                box=SIMPLE_HEAD,
            ),
            Panel(
                f"podplay podcast {podcasts[0].id}",
                title="Get podcast",
                box=SIMPLE_HEAD,
            ),
        ]
        console.print(*tables)


async def get_podcast(args) -> None:
    """Retrieve podcast(s)."""
    async with PodPlayClient(language=args.language) as client:
        podcasts = await client.get_podcasts(args.podcast_id)
        for podcast in podcasts:
            console.print(
                Panel(
                    pretty_dataclass(
                        podcast,
                        title="Podcast",
                    ),
                    box=SIMPLE_HEAD,
                )
            )


async def get_podcast_episodes(args) -> None:
    """Retrieve podcast episodes."""
    async with PodPlayClient(language=args.language) as client:
        episodes = await client.get_podcast_episodes(
            args.podcast_id, pages=args.pages, page_size=args.per_page
        )
        if len(episodes) == 0:
            console.print("No episodes found")
            return
        tables = [
            Panel(
                pretty_dataclass_list(
                    episodes,
                    title="Episodes",
                    visible_fields=[
                        "id",
                        "title",
                        "published",
                        "duration",
                        "type",
                    ],
                    field_formatters={
                        "published": lambda x: x.strftime("%Y-%m-%d"),
                        "duration": lambda x: seconds_to_time(x),
                    },
                ),
                box=SIMPLE_HEAD,
            ),
            Panel(
                f"podplay episode {episodes[0].id}",
                title="Get episode",
                box=SIMPLE_HEAD,
            ),
        ]
        console.print(*tables)


async def get_episode(args) -> None:
    """Retrieve episode(s)."""
    async with PodPlayClient(language=args.language) as client:
        episodes = await client.get_episodes(args.episode_id)
        for episode in episodes:
            console.print(
                Panel(
                    pretty_dataclass(
                        episode,
                        title="Episode",
                    ),
                    box=SIMPLE_HEAD,
                )
            )


async def search_podcasts(args) -> None:
    """Search podcasts."""
    async with PodPlayClient(language=args.language) as client:
        podcasts = await client.search_podcast(args.search)
        for podcast in podcasts:
            console.print(
                Panel(
                    pretty_dataclass(
                        podcast,
                        title="Podcast",
                    ),
                    box=SIMPLE_HEAD,
                )
            )


def category_tree(
    category: PodPlayCategory, prefix="", is_last=True, is_root=True
) -> str:
    if is_root:
        ret = f"# {category.name} ({category.id})\n"
    else:
        ret = "{prefix}{leaf}{name}\n".format(
            prefix=prefix,
            leaf=("└── " if is_last else "├── "),
            name=f"{category.name} ({category.id})",
        )
    prefix += "" if is_last else "│   "
    for i, child in enumerate(category.children):
        ret += category_tree(child, prefix, i == len(category.children) - 1, False)
    return ret


def categories_tree(categories: list[PodPlayCategory]) -> str:
    return "".join([category_tree(c) for c in categories])


def main():
    """Run."""
    parser = main_parser()
    args = parser.parse_args()

    if args.debug:
        logging_level = logging.DEBUG
    elif args.verbose:
        logging_level = 50 - (args.verbose * 10)
        if logging_level <= 0:
            logging_level = logging.NOTSET
    else:
        logging_level = logging.ERROR

    logging.basicConfig(
        level=logging_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console)],
    )

    asyncio.run(args.func(args))


if __name__ == "__main__":
    main()
