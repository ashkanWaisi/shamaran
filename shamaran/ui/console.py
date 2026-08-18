"""Rich presentation kept separate from application behavior."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .theme import SHAMARAN_THEME


console = Console(theme=SHAMARAN_THEME)


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
