"""podplay_api utils."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from podplay_api.models import PodPlayCategory


def nested_categories(categories: list[PodPlayCategory]) -> list[PodPlayCategory]:
    categories_by_id = {item.id: item for item in categories}
    categories_nested = []

    for item in categories:
        parent_id = item.parent_id
        if parent_id is None:
            categories_nested.append(item)
        else:
            parent = categories_by_id.get(parent_id)
            parent.children = parent.children or []
            parent.children.append(item)

    return categories_nested
