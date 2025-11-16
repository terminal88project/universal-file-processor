#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Beautiful progress bars"""

from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TimeRemainingColumn,
    TimeElapsedColumn,
    MofNCompleteColumn
)
from rich.console import Console

console = Console()

def get_conversion_progress():
    """Create beautiful progress bar for conversions"""
    return Progress(
        SpinnerColumn(spinner_name="dots12", style="cyan"),
        TextColumn("[bold blue]{task.description}", justify="left"),
        BarColumn(
            bar_width=40,
            style="cyan",
            complete_style="green",
            finished_style="bold green"
        ),
        MofNCompleteColumn(),
        TextColumn("•"),
        TimeElapsedColumn(),
        TextColumn("•"),
        TimeRemainingColumn(),
        console=console,
        transient=False
    )

def show_success_animation(message: str):
    """Show success animation"""
    console.print(f"\n✨ [bold green]{message}[/bold green] ✨\n")

def show_error_animation(message: str):
    """Show error animation"""
    console.print(f"\n❌ [bold red]{message}[/bold red] ❌\n")
