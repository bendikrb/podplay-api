"""podplay_api utils."""

from __future__ import annotations

from dataclasses import fields
from typing import TYPE_CHECKING, Callable, Literal

from rich.table import Table
from rich.text import Text
from yarl import URL

from .const import PODPLAY_IMAGE_URL

if TYPE_CHECKING:
    from podplay_api.models import BaseDataClassORJSONMixin, PodPlayCategory


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


def build_image_url(
    image_id: str,
    fit: Literal["crop", "scale"] = "crop",
    width: int | None = None,
    height: int | None = None,
    quality: int | None = None,
) -> URL:
    query = {}
    if width or height:
        query["auto"] = "format,compress"
        query["fit"] = fit
        query["width"] = width
        query["height"] = height
        query["q"] = quality or 75
    return URL(f"{PODPLAY_IMAGE_URL}/{image_id}").with_query(
        {k: v for k, v in query.items() if v is not None}
    )


# noinspection PyTypeChecker
def pretty_dataclass(  # noqa: PLR0912
    dataclass_obj: BaseDataClassORJSONMixin,
    field_formatters: dict[str, Callable[[any], any]] | None = None,
    hidden_fields: list[str] | None = None,
    visible_fields: list[str] | None = None,
    title: str | None = None,
    hide_none: bool = True,
    hide_default: bool = True,
) -> Table:
    """Render a dataclass object in a pretty format using rich."""

    field_formatters = field_formatters or {}
    hidden_fields = hidden_fields or []
    visible_fields = visible_fields or []

    table = Table(title=title)
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")

    if visible_fields:
        # Render fields in the order specified by visible_fields
        for field_name in visible_fields:
            if hidden_fields and field_name in hidden_fields:
                continue

            field = next(
                (f for f in fields(dataclass_obj) if f.name == field_name), None
            )
            if not field:
                continue

            field_value = getattr(dataclass_obj, field_name)

            if hide_none and field_value is None:
                continue

            if hide_none and isinstance(field_value, list) and len(field_value) == 0:
                continue

            if hide_default and field_value == field.default:
                continue

            if field_name in field_formatters:
                field_value = field_formatters[field_name](field_value)
            table.add_row(field_name, str(field_value))
    else:
        # Render all fields (except hidden ones) in the default order
        for field in fields(dataclass_obj):
            if hidden_fields and field.name in hidden_fields:
                continue

            field_value = getattr(dataclass_obj, field.name)

            if hide_none and field_value is None:
                continue

            if hide_none and isinstance(field_value, list) and len(field_value) == 0:
                continue

            if hide_default and field_value == field.default:
                continue

            if field.name in field_formatters:
                field_value = field_formatters[field.name](field_value)
            table.add_row(field.name, str(field_value))

    return table


# noinspection PyTypeChecker
def pretty_dataclass_list(  # noqa: PLR0912
    dataclass_objs: list[BaseDataClassORJSONMixin],
    field_formatters: dict[str, Callable[[any], any]] | None = None,
    hidden_fields: list[str] | None = None,
    visible_fields: list[str] | None = None,
    field_widths: dict[str, int] | None = None,
    field_order: list[str] | None = None,
    title: str | None = None,
    hide_none: bool = True,
    hide_default: bool = True,
) -> Table | Text:
    """Render a list of dataclass objects in a table format using rich."""

    field_formatters = field_formatters or {}
    hidden_fields = hidden_fields or []
    visible_fields = visible_fields or []
    field_widths = field_widths or {}
    field_order = field_order or []

    if not dataclass_objs:
        if title is not None:
            return Text(f"{title}: No results")
        return Text("No results")

    dataclass_fields = list(fields(dataclass_objs[0]))
    ordered_fields = [
        f for f in field_order if f in [field.name for field in dataclass_fields]
    ]
    remaining_fields = [
        f.name for f in dataclass_fields if f.name not in ordered_fields
    ]
    fields_to_render = ordered_fields + remaining_fields

    table = Table(title=title, expand=True)

    for field_name in fields_to_render:
        if hidden_fields and field_name in hidden_fields:
            continue

        if visible_fields and field_name not in visible_fields:
            continue

        table.add_column(
            field_name,
            style="cyan",
            no_wrap=not field_widths.get(field_name, None),
            width=field_widths.get(field_name, None),
        )

    for obj in dataclass_objs:
        row = []
        for field_name in fields_to_render:
            if hidden_fields and field_name in hidden_fields:
                continue

            if visible_fields and field_name not in visible_fields:
                continue

            field = next((f for f in fields(obj) if f.name == field_name), None)
            if not field:
                continue

            field_value = getattr(obj, field_name)

            if hide_none and field_value is None:
                continue

            if hide_default and field_value == field.default:
                continue

            if field_name in field_formatters:
                field_value = field_formatters[field_name](field_value)
            row.append(str(field_value))
        table.add_row(*row)

    return table


def seconds_to_time(seconds: int) -> str:
    """Convert seconds to time."""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    ret = ""
    if hours > 0:
        ret += f"{hours:02d}h"
    if minutes > 0:
        ret += f"{minutes:02d}m"
    return f"{ret}{seconds:02d}s"
