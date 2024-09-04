"""podplay_api cli tool."""
from __future__ import annotations

import argparse
import asyncio
import logging
from typing import TYPE_CHECKING

from rich import print as rprint

from podplay_api.client import PodPlayClient

if TYPE_CHECKING:
    from aiohttp.client import ClientSession

    from podplay_api.models import PodPlayCategory

http_client: ClientSession

def main_parser() -> argparse.ArgumentParser:
    """Create the ArgumentParser with all relevant subparsers."""
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='A simple executable to use and test the library.')
    _add_default_arguments(parser)

    subparsers = parser.add_subparsers(dest='cmd')
    subparsers.required = True

    categories_parser = subparsers.add_parser('categories', description='Get a list of categories.')
    categories_parser.set_defaults(func=get_categories)

    category_parser = subparsers.add_parser('category', description='Get podcasts in a category.')
    # category_parser.add_argument('--id', type=int, help='Category ID')
    category_parser.set_defaults(func=get_category)

    get_podcast_parser = subparsers.add_parser('podcast', description='Get a single podcast.')
    get_podcast_parser.set_defaults(func=get_podcast)

    return parser


def _add_default_arguments(parser: argparse.ArgumentParser) -> None:
    """Add default arguments."""
    parser.add_argument('-l', '--language', help='(optional) Language to use', default='en')


async def get_popular(args) -> None:
    """Retrieve favourite podcasts."""
    async with PodPlayClient(language=args.language) as client:
        podcasts = await client.get_popular_podcasts(
            page_size=args.per_page,
            pages=args.pages,
            category=args.category,
        )
        for p in podcasts:
            rprint(p)


async def get_categories(args) -> None:
    """Retrieve categories."""
    async with PodPlayClient(language=args.language) as client:
        categories = await client.get_categories()
        rprint(categories_tree(categories))


async def get_category(args) -> None:
    """Retrieve category."""
    async with PodPlayClient(language=args.language) as client:
        podcasts = await client.get_podcasts_by_category(category=1310)
        rprint(podcasts)


async def get_podcast(args) -> None:
    """Retrieve podcast."""
    async with PodPlayClient(language=args.language) as client:
        podcast = await client.get_podcast(args.podcast_id)
        rprint(podcast)


def category_tree(category: PodPlayCategory, prefix="", is_last=True, is_root=True) -> str:
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
    asyncio.run(args.func(args))


if __name__ == '__main__':
    main()
