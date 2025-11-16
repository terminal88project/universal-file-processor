#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Enhanced display utilities with beautiful UI components - STABLE"""

from __future__ import annotations

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich import box
from pathlib import Path
from typing import Dict, List
from datetime import datetime
from config.settings import LOG_DIR

console = Console()

# -------- Helpers --------
def ellipsis(s: str, max_len: int = 80) -> str:
    return s if len(s) <= max_len else s[:max_len - 3] + "..."

class Display:
    """Enhanced display helper functions with beautiful formatting"""

    @staticmethod
    def show_file_info(file_info: Dict):
        """Display file information as beautiful card"""
        console.clear()
        console.print()

        # Create info text
        info_text = Text()

        # File icon and name
        info_text.append("📄 ", style="bold yellow")
        info_text.append(ellipsis(file_info.get('name', 'Unknown'), 60) + "\n\n", style="bold white")

        # Type
        info_text.append("Type:       ", style="cyan bold")
        info_text.append(f"{file_info.get('icon','')} {file_info.get('type','').capitalize()}\n", style="white")

        # Size
        info_text.append("Size:       ", style="cyan bold")
        size_mb = file_info.get('size_mb', 0.0)
        if size_mb < 1:
            size_text = f"{size_mb * 1024:.2f} KB"
        elif size_mb > 1024:
            size_text = f"{size_mb / 1024:.2f} GB"
        else:
            size_text = f"{size_mb:.2f} MB"
        info_text.append(f"{size_text}\n", style="white")

        # Tool
        info_text.append("Tool:       ", style="cyan bold")
        info_text.append(f"{file_info.get('tool','')}\n", style="white")

        # Path
        info_text.append("Path:       ", style="cyan bold")
        info_text.append(ellipsis(file_info.get('path', 'N/A'), 90) + "\n", style="dim white")

        # Image-specific info
        if 'width' in file_info and 'height' in file_info:
            info_text.append("\n")
            info_text.append("Resolution: ", style="cyan bold")
            info_text.append(f"{file_info['width']}x{file_info['height']}\n", style="white")

            info_text.append("Mode:       ", style="cyan bold")
            info_text.append(f"{file_info.get('mode', 'N/A')}\n", style="white")

            # Calculate megapixels
            megapixels = (file_info['width'] * file_info['height']) / 1_000_000
            info_text.append("Megapixels: ", style="cyan bold")
            info_text.append(f"{megapixels:.2f} MP\n", style="white")

        # Create panel (padding کم برای جلوگیری از wrap)
        panel = Panel(
            info_text,
            title="[bold cyan]📋 File Information[/bold cyan]",
            border_style="cyan",
            padding=(0, 1),
            expand=False
        )

        console.print(panel)
        console.print()

        # توقف استاندارد (بدون چاپ markup خام)
        console.print(Text("Press Enter to continue...", style="dim"), end="")
        try:
            input()
        except KeyboardInterrupt:
            console.print()

    @staticmethod
    def show_tools_status(status: Dict[str, bool]):
        """Display tools status as beautiful cards"""
        console.clear()
        console.print()

        # Title
        title = Text()
        title.append("🛠️  ", style="bold yellow")
        title.append("Installed Tools Status", style="bold cyan")
        console.print(title)
        console.print()

        # Create cards for each tool
        cards: List[Panel] = []

        tools_info = {
            'FFmpeg': {
                'icon': '🎬',
                'name': 'FFmpeg',
                'desc': 'Video & Audio\nconversion',
                'formats': 'MP4, AVI, MKV\nMP3, WAV, FLAC'
            },
            'PIL/ImageMagick': {
                'icon': '🖼️',
                'name': 'PIL/Pillow',
                'desc': 'Image processing\n& conversion',
                'formats': 'PNG, JPG, GIF\nWebP, BMP'
            },
            'Pandoc': {
                'icon': '📝',
                'name': 'Pandoc',
                'desc': 'Document\nconversion',
                'formats': 'PDF, HTML\nDOCX, MD'
            },
            'LibreOffice': {
                'icon': '📊',
                'name': 'LibreOffice',
                'desc': 'Office file\nconversion',
                'formats': 'XLSX, DOCX\nPPTX → PDF'
            },
            'Calibre': {
                'icon': '📚',
                'name': 'Calibre',
                'desc': 'Ebook\nconversion',
                'formats': 'EPUB, MOBI\nAZW3, PDF'
            },
        }

        for tool_key, info in tools_info.items():
            is_available = status.get(tool_key, False)

            card_text = Text()
            card_text.append(f"{info['icon']}\n", style="bold")

            if is_available:
                card_text.append(f"✓ {info['name']}\n", style="bold green")
                card_text.append(f"{info['desc']}\n", style="dim white")
                card_text.append(f"\n{info['formats']}", style="dim cyan")
                border_style = "green"
            else:
                card_text.append(f"✗ {info['name']}\n", style="bold red")
                card_text.append(f"{info['desc']}\n", style="dim white")
                card_text.append("\nNot installed", style="dim red")
                border_style = "red"

            card = Panel(
                card_text,
                border_style=border_style,
                padding=(1, 1),
                width=22,
                expand=False
            )
            cards.append(card)

        # Display cards in columns
        console.print(Columns(cards, equal=True, expand=False, padding=(0, 2)))
        console.print()

        # Summary
        available_count = sum(1 for v in status.values() if v)
        total_count = len(tools_info)

        if available_count == total_count:
            summary_style = "bold green"
            summary_icon = "✅"
            summary_text = f"All {total_count} tools are available!"
        elif available_count > 0:
            summary_style = "bold yellow"
            summary_icon = "⚠️"
            summary_text = f"{available_count} of {total_count} tools available"
        else:
            summary_style = "bold red"
            summary_icon = "❌"
            summary_text = "No tools are installed"

        summary = Panel(
            f"[{summary_style}]{summary_icon} {summary_text}[/{summary_style}]",
            border_style=summary_style.split()[1],
            padding=(0, 2),
            expand=False
        )
        console.print(summary)
        console.print()

        console.print(Text("Press Enter to continue...", style="dim"), end="")
        try:
            input()
        except KeyboardInterrupt:
            console.print()

    @staticmethod
    def show_logs():
        """Display recent logs with syntax highlighting"""
        console.clear()
        console.print()

        # Title
        console.print("[bold cyan]📋 Recent Application Logs[/bold cyan]\n")

        # Find latest log file
        try:
            log_files = list(LOG_DIR.glob("processor_*.log"))
        except Exception:
            log_files = []

        if not log_files:
            no_logs_panel = Panel(
                "[yellow]No log files found[/yellow]\n\n"
                "Logs will be created when you perform conversions.",
                title="[bold yellow]⚠️  No Logs[/bold yellow]",
                border_style="yellow",
                padding=(1, 2)
            )
            console.print(no_logs_panel)
            return

        latest_log = max(log_files, key=lambda p: p.stat().st_mtime)

        # Log file info
        try:
            log_info = latest_log.stat()
            log_time = datetime.fromtimestamp(log_info.st_mtime)

            info_text = Text()
            info_text.append("File: ", style="cyan bold")
            info_text.append(f"{latest_log.name}\n", style="white")
            info_text.append("Modified: ", style="cyan bold")
            info_text.append(f"{log_time.strftime('%Y-%m-%d %H:%M:%S')}\n", style="white")
            info_text.append("Size: ", style="cyan bold")
            info_text.append(f"{log_info.st_size / 1024:.2f} KB", style="white")

            info_panel = Panel(
                info_text,
                title="[bold cyan]📄 Log File Info[/bold cyan]",
                border_style="cyan",
                padding=(0, 2),
                expand=False
            )
            console.print(info_panel)
            console.print()
        except Exception as e:
            console.print(f"[yellow]Could not read log file info: {e}[/yellow]\n")

        # Read and display logs
        try:
            with open(latest_log, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()[-40:]  # Last 40 lines

                log_table = Table(
                    show_header=True,
                    header_style="bold cyan",
                    box=box.MINIMAL,
                    padding=(0, 1),
                    collapse_padding=True,
                    pad_edge=False
                )
                log_table.add_column("Time", style="dim", width=19, no_wrap=True)
                log_table.add_column("Level", width=8, no_wrap=True)
                log_table.add_column("Message", style="white", overflow="fold", max_width=80)

                for line in lines:
                    line = line.strip()
                    if not line or '=' * 10 in line:
                        continue
                    try:
                        parts = line.split(' - ', 2)
                        if len(parts) >= 3:
                            timestamp = parts[0]
                            level = parts[1]
                            message = parts[2] if len(parts) > 2 else ""

                            if len(timestamp) > 19:
                                timestamp = timestamp[-19:]

                            if 'ERROR' in level:
                                level_style = "[bold red]ERROR[/bold red]"
                                msg_style = "red"
                            elif 'WARNING' in level or 'WARN' in level:
                                level_style = "[bold yellow]WARN[/bold yellow]"
                                msg_style = "yellow"
                            elif 'INFO' in level:
                                level_style = "[bold green]INFO[/bold green]"
                                msg_style = "white"
                            elif 'DEBUG' in level:
                                level_style = "[dim cyan]DEBUG[/dim cyan]"
                                msg_style = "dim cyan"
                            else:
                                level_style = level
                                msg_style = "white"

                            if len(message) > 100:
                                message = message[:97] + "..."

                            log_table.add_row(timestamp, level_style, f"[{msg_style}]{message}[/{msg_style}]")
                    except Exception:
                        continue

                logs_panel = Panel(
                    log_table,
                    title="[bold cyan]📖 Recent Entries[/bold cyan]",
                    border_style="cyan",
                    padding=(1, 2)
                )
                console.print(logs_panel)

        except Exception as e:
            error_panel = Panel(
                f"[red]Error reading logs: {e}[/red]",
                title="[bold red]❌ Error[/bold red]",
                border_style="red",
                padding=(1, 2)
            )
            console.print(error_panel)

        console.print()
        try:
            console.print(Text(f"Full log path: {latest_log.absolute()}", style="dim"))
        except Exception:
            pass
        console.print()

        console.print(Text("Press Enter to continue...", style="dim"), end="")
        try:
            input()
        except KeyboardInterrupt:
            console.print()

    @staticmethod
    def show_conversion_summary(success: int, failed: int, total: int, output_folder: str | None = None):
        """Show beautiful conversion summary with statistics"""
        console.print()

        summary_table = Table(show_header=False, box=box.MINIMAL, padding=(0, 2), pad_edge=False)
        summary_table.add_column(style="bold", width=20, no_wrap=True)
        summary_table.add_column(style="", width=18, no_wrap=True)

        summary_table.add_row("✓ Successful:", f"[bold green]{success}[/bold green]")
        summary_table.add_row("✗ Failed:",     f"[bold red]{failed}[/bold red]")
        summary_table.add_row("📊 Total:",     f"[bold cyan]{total}[/bold cyan]")

        if total > 0:
            rate = (success / total) * 100
            if rate >= 80:
                rate_color = "green"; rate_icon = "🎉"
            elif rate >= 50:
                rate_color = "yellow"; rate_icon = "⚠️"
            else:
                rate_color = "red"; rate_icon = "❌"
            summary_table.add_row("📈 Success Rate:", f"[bold {rate_color}]{rate_icon} {rate:.1f}%[/bold {rate_color}]")

        if output_folder:
            summary_table.add_row("📁 Output:", f"[dim cyan]{ellipsis(output_folder, 90)}[/dim cyan]")

        panel = Panel(
            summary_table,
            title="[bold cyan]📊 Conversion Summary[/bold cyan]",
            border_style="cyan",
            padding=(1, 2)
        )

        console.print(panel)
        console.print()

    @staticmethod
    def show_error(message: str, title: str = "Error"):
        panel = Panel(f"[red]{message}[/red]",
                      title=f"[bold red]❌ {title}[/bold red]",
                      border_style="red", padding=(1, 2))
        console.print("\n", panel, "\n")

    @staticmethod
    def show_success(message: str, title: str = "Success"):
        panel = Panel(f"[green]{message}[/green]",
                      title=f"[bold green]✅ {title}[/bold green]",
                      border_style="green", padding=(1, 2))
        console.print("\n", panel, "\n")

    @staticmethod
    def show_warning(message: str, title: str = "Warning"):
        panel = Panel(f"[yellow]{message}[/yellow]",
                      title=f"[bold yellow]⚠️  {title}[/bold yellow]",
                      border_style="yellow", padding=(1, 2))
        console.print("\n", panel, "\n")

    @staticmethod
    def show_info(message: str, title: str = "Information"):
        panel = Panel(f"[cyan]{message}[/cyan]",
                      title=f"[bold cyan]ℹ️  {title}[/bold cyan]",
                      border_style="cyan", padding=(1, 2))
        console.print("\n", panel, "\n")
