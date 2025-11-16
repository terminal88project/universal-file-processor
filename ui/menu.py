#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Enhanced main menu interface with animations - FIXED & TESTED"""

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.table import Table
import time
import sys

console = Console()


class MainMenu:
    """Enhanced main menu handler with beautiful UI"""
    
    # Menu options - key بدون آیکون
    MENU_OPTIONS = [
        {
            "key": "Convert Single File",
            "emoji": "📁",
            "desc": "Convert one file with advanced options",
            "color": "cyan"
        },
        {
            "key": "Convert Multiple Files",
            "emoji": "📂",
            "desc": "Batch process multiple files at once",
            "color": "blue"
        },
        {
            "key": "File Information",
            "emoji": "🔍",
            "desc": "View detailed file metadata",
            "color": "magenta"
        },
        {
            "key": "Tools Status",
            "emoji": "🛠️",
            "desc": "Check installed conversion tools",
            "color": "green"
        },
        {
            "key": "View Logs",
            "emoji": "📋",
            "desc": "Review conversion history",
            "color": "yellow"
        },
        {
            "key": "Exit",
            "emoji": "❌",
            "desc": "Close application",
            "color": "red"
        }
    ]
    
    @staticmethod
    def show() -> str:
        """Display enhanced main menu with animation"""
        console.clear()
        
        # Show header banner
        MainMenu._show_header()
        
        # Show feature highlights
        MainMenu._show_features()
        
        try:
            # Create menu choices
            choices = [
                questionary.Choice(
                    title=f"{opt['emoji']} {opt['key']}",
                    value=opt['key']
                )
                for opt in MainMenu.MENU_OPTIONS
            ]
            
            choice = questionary.select(
                "What would you like to do?",
                choices=choices,
                style=questionary.Style([
                    ('qmark', 'fg:#00ff00 bold'),
                    ('question', 'fg:#00ffff bold'),
                    ('answer', 'fg:#00ff00 bold'),
                    ('pointer', 'fg:#00ffff bold'),
                    ('highlighted', 'fg:#00ffff bold'),
                    ('selected', 'fg:#00ff00'),
                    ('separator', 'fg:#555555'),
                    ('instruction', 'fg:#888888'),
                    ('text', ''),
                ])
            ).ask()
            
            # Show loading animation
            if choice and choice != "Exit":
                MainMenu._show_loading(choice)
            
            return choice
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Operation cancelled[/yellow]")
            return None
        except Exception as e:
            console.print(f"\n[red]Menu error: {e}[/red]")
            return None
    
    @staticmethod
    def _show_header():
        """Display beautiful header banner"""
        logo = r"""
  ██╗   ██╗███████╗██████╗ 
  ██║   ██║██╔════╝██╔══██╗
  ██║   ██║█████╗  ██████╔╝
  ██║   ██║██╔══╝  ██╔═══╝ 
  ╚██████╔╝██║     ██║     
   ╚═════╝ ╚═╝     ╚═╝     
"""
        
        header_text = Text()
        header_text.append(logo, style="bold cyan")
        header_text.append("\n")
        header_text.append("Universal File Processor", style="bold white")
        header_text.append("\n")
        header_text.append("Professional Modular Conversion Tool v2.0", style="dim white")
        
        panel = Panel(
            Align.center(header_text),
            border_style="cyan",
            padding=(1, 2)
        )
        
        console.print(panel)
        console.print()
    
    @staticmethod
    def _show_features():
        """Display supported features"""
        table = Table(show_header=False, box=None, padding=(0, 3), collapse_padding=True)
        table.add_column(style="bold", width=16, no_wrap=True)
        table.add_column(style="dim white", width=30)
        
        features = [
            ("🎬 Video", "MP4, AVI, MKV, WebM, MOV"),
            ("🎵 Audio", "MP3, WAV, FLAC, AAC, OGG"),
            ("🖼️  Image", "PNG, JPG, GIF, WebP, BMP"),
            ("📝 Document", "PDF, HTML, DOCX, Markdown"),
            ("📊 Office", "Excel, Word, PowerPoint"),
            ("📚 Ebook", "EPUB, MOBI, AZW3, PDF")
        ]
        
        for icon_text, formats in features:
            table.add_row(icon_text, formats)
        
        console.print(Align.center(table))
        console.print()
    
    @staticmethod
    def _show_loading(action: str):
        """Show loading animation"""
        with console.status(f"[bold cyan]Loading {action}...[/bold cyan]", spinner="dots12"):
            time.sleep(0.3)
    
    @staticmethod
    def show_error(message: str):
        """Display error message"""
        panel = Panel(
            f"[bold red]❌ Error[/bold red]\n\n{message}",
            border_style="red",
            padding=(1, 2)
        )
        console.print("\n", panel, "\n")
    
    @staticmethod
    def show_success(message: str):
        """Display success message"""
        panel = Panel(
            f"[bold green]✅ Success[/bold green]\n\n{message}",
            border_style="green",
            padding=(1, 2)
        )
        console.print("\n", panel, "\n")
    
    @staticmethod
    def show_info(message: str):
        """Display info message"""
        panel = Panel(
            f"[bold cyan]ℹ️  Information[/bold cyan]\n\n{message}",
            border_style="cyan",
            padding=(1, 2)
        )
        console.print("\n", panel, "\n")
    
    @staticmethod
    def show_warning(message: str):
        """Display warning message"""
        panel = Panel(
            f"[bold yellow]⚠️  Warning[/bold yellow]\n\n{message}",
            border_style="yellow",
            padding=(1, 2)
        )
        console.print("\n", panel, "\n")
    
    @staticmethod
    def confirm(question: str, default: bool = True) -> bool:
        """Ask user for confirmation"""
        try:
            return questionary.confirm(
                question,
                default=default,
                style=questionary.Style([
                    ('question', 'fg:#00ffff bold'),
                    ('answer', 'fg:#00ff00 bold'),
                ])
            ).ask()
        except KeyboardInterrupt:
            return False
    
    @staticmethod
    def pause(message: str = None):
        """
        Pause and wait for user input
        
        Args:
            message: Custom message (supports Rich markup) or None for default
        """
        try:
            if message is None:
                # ✅ FIXED: بدون f-string
                console.print("\n[dim]Press Enter to continue...[/dim]", end="")
            else:
                # برای پیام‌های سفارشی
                console.print(f"\n{message}", end="")
            input()
        except KeyboardInterrupt:
            console.print()
    
    @staticmethod
    def get_choice(question: str, choices: list, default: str = None) -> str:
        """Get user choice from list"""
        try:
            return questionary.select(
                question,
                choices=choices,
                default=default,
                style=questionary.Style([
                    ('qmark', 'fg:#00ff00 bold'),
                    ('question', 'fg:#00ffff bold'),
                    ('answer', 'fg:#00ff00 bold'),
                    ('pointer', 'fg:#00ffff bold'),
                    ('highlighted', 'fg:#00ffff bold'),
                    ('selected', 'fg:#00ff00'),
                ])
            ).ask()
        except KeyboardInterrupt:
            return None
    
    @staticmethod
    def get_text(question: str, default: str = "") -> str:
        """Get text input from user"""
        try:
            return questionary.text(
                question,
                default=default,
                style=questionary.Style([
                    ('question', 'fg:#00ffff bold'),
                    ('answer', 'fg:#00ff00 bold'),
                ])
            ).ask()
        except KeyboardInterrupt:
            return None
    
    @staticmethod
    def clear():
        """Clear console screen"""
        console.clear()
    
    @staticmethod
    def print_separator(char: str = "─", style: str = "dim"):
        """Print separator line"""
        width = console.width
        console.print(char * width, style=style)


# Example usage & tests
if __name__ == "__main__":
    console.print("[bold cyan]Testing MainMenu...[/bold cyan]\n")
    
    while True:
        choice = MainMenu.show()
        
        if choice is None:
            continue
        elif choice == "Exit":
            MainMenu.show_success("Thank you for using Universal File Processor!")
            break
        else:
            MainMenu.show_info(f"You selected: [bold]{choice}[/bold]")
            MainMenu.pause()  # ✅ استفاده از pause بدون پارامتر
