"""Rich presentation kept separate from application behavior."""

import re

import arabic_reshaper
from bidi import get_display
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .theme import SHAMARAN_THEME


console = Console(theme=SHAMARAN_THEME)
_RTL_CHARACTER = re.compile(r"[\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff]")
_MARKDOWN_HEADING = re.compile(r"^\s{0,3}#{1,6}\s+")
_MARKDOWN_LINK = re.compile(r"\[([^]]+)]\([^)]+\)")


def contains_rtl(text: str) -> bool:
    """Return whether text contains Arabic-script characters, including Persian."""
    return bool(_RTL_CHARACTER.search(text))


def _plain_markdown_line(line: str) -> str:
    line = _MARKDOWN_HEADING.sub("", line)
    line = _MARKDOWN_LINK.sub(r"\1", line)
    return line.replace("**", "").replace("__", "").replace("`", "")


def rtl_display(text: str) -> str:
    """Shape and reorder one logical line for terminals without native RTL layout."""
    reshaped = arabic_reshaper.reshape(_plain_markdown_line(text))
    return get_display(reshaped, base_dir="R")


def print_assistant_answer(answer: str) -> None:
    """Render Markdown normally or provide readable Persian terminal output."""
    if not contains_rtl(answer):
        console.print(Markdown(answer))
        return
    for line in answer.splitlines() or [""]:
        if not line:
            console.print()
            continue
        console.print(Text(rtl_display(line), justify="right", overflow="fold"))


def show_banner() -> None:
    console.print(
        Panel.fit(
            "[shamaran.title]SHAMARAN[/shamaran.title]\n"
            "[shamaran.muted]Local AI Agent[/shamaran.muted]\n\n"
            "[shamaran.accent]Think · Build · Remember · Act[/shamaran.accent]",
            width=47,
            padding=(1, 8),
            border_style="bright_blue",
        )
    )


def status_table(rows: list[tuple[str, str]]) -> Table:
    table = Table(show_header=False, box=None, pad_edge=False)
    table.add_column(style="shamaran.muted", width=12)
    table.add_column(style="white")
    for key, value in rows:
        table.add_row(key, value)
    return table
