#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""File information service with enhanced UI"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from pathlib import Path

from core.file_detector import FileDetector
from core.tool_checker import ToolChecker
from ui.file_picker import FilePicker
from ui.display import Display
from utils.logger import get_logger

console = Console()
logger = get_logger()


class FileInfoService:
    """Handle file information display with beautiful UI"""
    
    def __init__(self):
        self.detector = FileDetector()
        self.tool_checker = ToolChecker()
        self.file_picker = FilePicker()
        self.display = Display()
    
    def run(self):
        """Run file information workflow"""
        try:
            console.clear()
            
            # Show header
            header = Panel(
                "[bold cyan]🔍 File Information[/bold cyan]\n"
                "[dim]View detailed metadata about any file[/dim]",
                border_style="cyan",
                padding=(1, 2)
            )
            console.print(header)
            console.print()
            
            # Pick file
            console.print("[cyan]📂 Select a file to inspect[/cyan]\n")
            console.print("[dim]Opening file picker...[/dim]\n")
            
            file_path = self.file_picker.pick_file()
            
            if not file_path:
                console.print("\n[yellow]⚠️  No file selected[/yellow]")
                input("\n[dim]Press Enter to continue...[/dim]")
                return
            
            logger.info(f"User selected file for info: {file_path}")
            
            # Get file info
            file_info = self.detector.get_file_info(file_path)
            
            if not file_info:
                self.display.show_error(
                    "Could not read file information!\n\n"
                    "The file may be corrupted or inaccessible.",
                    "File Read Error"
                )
                input("\n[dim]Press Enter to continue...[/dim]")
                return
            
            console.clear()
            
            # Check if tool is available
            tool_available = self.tool_checker.is_available(file_info['tool'])
            
            # Display detailed file information
            self._show_detailed_info(file_info, tool_available)
            
            # Show conversion capabilities
            self._show_conversion_capabilities(file_info, tool_available)
            
            input("\n[dim]Press Enter to continue...[/dim]")
            
        except KeyboardInterrupt:
            logger.info("File info cancelled by user (Ctrl+C)")
            console.print("\n\n[yellow]⚠️  Cancelled[/yellow]")
            input("\n[dim]Press Enter to continue...[/dim]")
            
        except Exception as e:
            logger.error(f"File info error: {e}", exc_info=True)
            self.display.show_error(
                f"An unexpected error occurred:\n{str(e)[:200]}",
                "Error"
            )
            input("\n[dim]Press Enter to continue...[/dim]")
    
    def _show_detailed_info(self, file_info: dict, tool_available: bool):
        """Display detailed file information"""
        
        # Create main info table
        info_table = Table(show_header=False, box=None, padding=(0, 2))
        info_table.add_column(style="cyan bold", width=18)
        info_table.add_column(style="white")
        
        # Basic information
        info_table.add_row("📄 File Name:", file_info['name'])
        info_table.add_row("📁 Location:", str(Path(file_info['path']).parent))
        info_table.add_row(
            f"{file_info['icon']} File Type:",
            file_info['type'].capitalize()
        )
        
        # File size with multiple units
        size_bytes = file_info['size_bytes']
        if size_bytes < 1024:
            size_display = f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            size_display = f"{size_bytes / 1024:.2f} KB ({size_bytes:,} bytes)"
        elif size_bytes < 1024 * 1024 * 1024:
            size_display = f"{size_bytes / (1024 * 1024):.2f} MB ({size_bytes:,} bytes)"
        else:
            size_display = f"{size_bytes / (1024 * 1024 * 1024):.2f} GB ({size_bytes:,} bytes)"
        
        info_table.add_row("💾 File Size:", size_display)
        
        # Tool information
        tool_status = "✅ Installed" if tool_available else "❌ Not Installed"
        tool_color = "green" if tool_available else "red"
        info_table.add_row(
            "🛠️  Required Tool:",
            f"{file_info['tool']} [{tool_color}]{tool_status}[/{tool_color}]"
        )
        
        # Image-specific information
        if 'width' in file_info and 'height' in file_info:
            info_table.add_row(
                "📐 Resolution:",
                f"{file_info['width']}x{file_info['height']} pixels"
            )
            
            # Calculate megapixels
            megapixels = (file_info['width'] * file_info['height']) / 1_000_000
            info_table.add_row(
                "📊 Megapixels:",
                f"{megapixels:.2f} MP"
            )
            
            # Aspect ratio
            from math import gcd
            width_gcd = gcd(file_info['width'], file_info['height'])
            aspect_w = file_info['width'] // width_gcd
            aspect_h = file_info['height'] // width_gcd
            info_table.add_row(
                "📏 Aspect Ratio:",
                f"{aspect_w}:{aspect_h}"
            )
            
            if 'mode' in file_info:
                info_table.add_row(
                    "🎨 Color Mode:",
                    file_info['mode']
                )
        
        # File path (full)
        info_table.add_row(
            "🔗 Full Path:",
            f"[dim]{file_info['path']}[/dim]"
        )
        
        # Create panel
        panel = Panel(
            info_table,
            title="[bold cyan]📋 File Details[/bold cyan]",
            border_style="cyan",
            padding=(1, 2)
        )
        
        console.print(panel)
        console.print()
    
    def _show_conversion_capabilities(self, file_info: dict, tool_available: bool):
        """Show what conversions are possible for this file"""
        
        formats = file_info.get('formats', {})
        
        if not formats:
            # No conversion options
            no_conversion_panel = Panel(
                "[yellow]⚠️  No conversion options available for this file type[/yellow]",
                border_style="yellow",
                padding=(0, 2)
            )
            console.print(no_conversion_panel)
            return
        
        # Create conversion options table
        conv_table = Table(
            show_header=True,
            header_style="bold cyan",
            box=None,
            padding=(0, 2)
        )
        conv_table.add_column("Output Format", style="green bold", width=20)
        conv_table.add_column("Extension", style="cyan", width=15)
        conv_table.add_column("Status", style="white", width=20)
        
        for format_name, extension in formats.items():
            if tool_available:
                status = "[green]✓ Available[/green]"
            else:
                status = f"[red]✗ Requires {file_info['tool']}[/red]"
            
            conv_table.add_row(format_name, f".{extension}", status)
        
        # Create panel
        if tool_available:
            title = "[bold green]✨ Available Conversions[/bold green]"
            border_style = "green"
            subtitle = "[dim]Ready to convert[/dim]"
        else:
            title = "[bold yellow]⚠️  Potential Conversions[/bold yellow]"
            border_style = "yellow"
            subtitle = f"[dim]Install {file_info['tool']} to enable[/dim]"
        
        panel = Panel(
            conv_table,
            title=title,
            subtitle=subtitle,
            border_style=border_style,
            padding=(1, 2)
        )
        
        console.print(panel)
        
        # Show recommendation if tool is not available
        if not tool_available:
            console.print()
            recommendation = self._get_installation_recommendation(file_info['tool'])
            if recommendation:
                info_panel = Panel(
                    recommendation,
                    title="[bold cyan]💡 Installation Guide[/bold cyan]",
                    border_style="cyan",
                    padding=(1, 2)
                )
                console.print(info_panel)
    
    def _get_installation_recommendation(self, tool: str) -> str:
        """Get installation recommendation for a tool"""
        
        recommendations = {
            'FFmpeg': (
                "[bold]Windows:[/bold]\n"
                "  choco install ffmpeg\n\n"
                "[bold]Linux (Ubuntu/Debian):[/bold]\n"
                "  sudo apt-get install ffmpeg\n\n"
                "[bold]macOS:[/bold]\n"
                "  brew install ffmpeg"
            ),
            'PIL/ImageMagick': (
                "[bold]Python Package:[/bold]\n"
                "  pip install Pillow\n\n"
                "[bold]Or ImageMagick:[/bold]\n"
                "  Windows: choco install imagemagick\n"
                "  Linux: sudo apt-get install imagemagick\n"
                "  macOS: brew install imagemagick"
            ),
            'Pandoc': (
                "[bold]Windows:[/bold]\n"
                "  choco install pandoc\n\n"
                "[bold]Linux (Ubuntu/Debian):[/bold]\n"
                "  sudo apt-get install pandoc\n\n"
                "[bold]macOS:[/bold]\n"
                "  brew install pandoc"
            ),
            'LibreOffice': (
                "[bold]Windows:[/bold]\n"
                "  choco install libreoffice\n\n"
                "[bold]Linux (Ubuntu/Debian):[/bold]\n"
                "  sudo apt-get install libreoffice\n\n"
                "[bold]macOS:[/bold]\n"
                "  brew install --cask libreoffice"
            ),
            'Calibre': (
                "[bold]Windows:[/bold]\n"
                "  choco install calibre\n\n"
                "[bold]Linux (Ubuntu/Debian):[/bold]\n"
                "  sudo apt-get install calibre\n\n"
                "[bold]macOS:[/bold]\n"
                "  brew install --cask calibre"
            ),
        }
        
        return recommendations.get(tool, "")
