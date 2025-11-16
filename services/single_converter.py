#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Single file conversion service with enhanced UI"""

from pathlib import Path
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from core.file_detector import FileDetector
from core.tool_checker import ToolChecker
from converters import ConverterFactory
from ui.file_picker import FilePicker
from ui.display import Display
from ui.notifications import Notifications
from config.settings import OUTPUT_DIR, VIDEO_RESOLUTIONS, VIDEO_FRAMERATES, IMAGE_RESIZE_OPTIONS
from utils.logger import get_logger

console = Console()
logger = get_logger()


class SingleFileConverter:
    """Handle single file conversion workflow with beautiful UI"""
    
    def __init__(self):
        self.detector = FileDetector()
        self.tool_checker = ToolChecker()
        self.file_picker = FilePicker()
        self.display = Display()
    
    def run(self):
        """Run single file conversion workflow"""
        try:
            console.clear()
            
            # Show header
            header = Panel(
                "[bold cyan]📁 Convert Single File[/bold cyan]\n"
                "[dim]Select a file and choose conversion options[/dim]",
                border_style="cyan",
                padding=(1, 2)
            )
            console.print(header)
            console.print()
            
            # Pick file
            console.print("[cyan]📂 Step 1: Select File[/cyan]\n")
            file_path = self.file_picker.pick_file()
            
            if not file_path:
                console.print("\n[yellow]⚠️  No file selected[/yellow]")
                input("\n[dim]Press Enter to continue...[/dim]")
                return
            
            # Get file info
            file_info = self.detector.get_file_info(file_path)
            if not file_info:
                self.display.show_error("Could not read file information!", "File Error")
                input("\n[dim]Press Enter to continue...[/dim]")
                return
            
            console.clear()
            
            # Display file info in beautiful card
            self._show_file_card(file_info)
            
            # Check tool availability
            if not self.tool_checker.is_available(file_info['tool']):
                self.display.show_error(
                    f"{file_info['tool']} is not installed!\n\n"
                    f"Please install {file_info['tool']} to convert this file type.",
                    "Tool Not Found"
                )
                input("\n[dim]Press Enter to continue...[/dim]")
                return
            
            # Select format
            console.print("\n[cyan]📋 Step 2: Choose Output Format[/cyan]\n")
            formats = file_info.get('formats', {})
            
            if not formats:
                self.display.show_warning(
                    "No conversion options available for this file type.",
                    "No Options"
                )
                input("\n[dim]Press Enter to continue...[/dim]")
                return
            
            output_format = questionary.select(
                "Select output format:",
                choices=list(formats.keys()),
                style=questionary.Style([
                    ('qmark', 'fg:#00ff00 bold'),
                    ('question', 'fg:#00ffff bold'),
                    ('answer', 'fg:#00ff00 bold'),
                    ('pointer', 'fg:#00ffff bold'),
                    ('highlighted', 'fg:#00ffff bold'),
                ])
            ).ask()
            
            if not output_format:
                logger.info("User cancelled format selection")
                return
            
            output_ext = formats[output_format]
            
            # Select quality
            console.print("\n[cyan]⚙️  Step 3: Choose Quality[/cyan]\n")
            
            quality_descriptions = {
                'Low': '128k audio / CRF 28 - Smallest size',
                'Medium': '192k audio / CRF 23 - Balanced',
                'High': '256k audio / CRF 18 - Great quality',
                'Ultra': '320k audio / CRF 15 - Maximum quality'
            }
            
            quality_choices = [
                questionary.Choice(
                    title=f"{q} - {quality_descriptions[q]}",
                    value=q
                )
                for q in ['Low', 'Medium', 'High', 'Ultra']
            ]
            
            quality = questionary.select(
                "Select quality preset:",
                choices=quality_choices,
                default='Medium',
                style=questionary.Style([
                    ('qmark', 'fg:#00ff00 bold'),
                    ('question', 'fg:#00ffff bold'),
                    ('answer', 'fg:#00ff00 bold'),
                    ('pointer', 'fg:#00ffff bold'),
                    ('highlighted', 'fg:#00ffff bold'),
                ])
            ).ask()
            
            if not quality:
                logger.info("User cancelled quality selection")
                return
            
            # Advanced settings
            settings = {'quality': quality}
            console.print("\n[cyan]🔧 Step 4: Advanced Options (Optional)[/cyan]\n")
            
            advanced_settings = self._get_advanced_settings(file_info['type'])
            if advanced_settings:
                settings.update(advanced_settings)
                console.print("[green]✓ Advanced settings applied[/green]\n")
            
            # Select output folder
            console.print("[cyan]📁 Step 5: Choose Output Location[/cyan]\n")
            output_folder = self.file_picker.pick_folder()
            
            if not output_folder:
                output_folder = str(OUTPUT_DIR)
                console.print(f"[dim]Using default output folder: {output_folder}[/dim]\n")
            
            Path(output_folder).mkdir(exist_ok=True, parents=True)
            output_file = str(Path(output_folder) / f"{Path(file_path).stem}.{output_ext}")
            
            # Show conversion summary
            self._show_conversion_summary(
                file_info,
                output_format,
                quality,
                settings,
                output_folder
            )
            
            # Confirm conversion
            if not questionary.confirm(
                "\n▶️  Start conversion?",
                default=True,
                style=questionary.Style([
                    ('question', 'fg:#00ffff bold'),
                    ('answer', 'fg:#00ff00 bold'),
                ])
            ).ask():
                console.print("\n[yellow]Conversion cancelled[/yellow]")
                input("\n[dim]Press Enter to continue...[/dim]")
                return
            
            # Perform conversion
            console.print("\n")
            success = self._convert_file(file_path, output_file, file_info['type'], settings)
            
            # Note: Notification is shown inside converter
            # We don't need to show it here
            
            if not success:
                logger.error("Conversion failed")
            
            input("\n[dim]Press Enter to continue...[/dim]")
            
        except KeyboardInterrupt:
            logger.info("Conversion cancelled by user (Ctrl+C)")
            console.print("\n\n[yellow]⚠️  Conversion cancelled[/yellow]")
            input("\n[dim]Press Enter to continue...[/dim]")
            
        except Exception as e:
            logger.error(f"Single file conversion error: {e}", exc_info=True)
            self.display.show_error(
                f"An unexpected error occurred:\n{str(e)[:200]}",
                "Conversion Error"
            )
            input("\n[dim]Press Enter to continue...[/dim]")
    
    def _show_file_card(self, file_info: dict):
        """Display beautiful file information card"""
        
        # Create file info table
        info_table = Table(show_header=False, box=None, padding=(0, 2))
        info_table.add_column(style="cyan bold", width=15)
        info_table.add_column(style="white")
        
        info_table.add_row("📄 Name:", file_info['name'])
        info_table.add_row(
            f"{file_info['icon']} Type:",
            file_info['type'].capitalize()
        )
        info_table.add_row("💾 Size:", f"{file_info['size_mb']:.2f} MB")
        info_table.add_row("🛠️  Tool:", file_info['tool'])
        
        # Add image-specific info
        if 'width' in file_info and 'height' in file_info:
            info_table.add_row(
                "📐 Resolution:",
                f"{file_info['width']}x{file_info['height']}"
            )
            megapixels = (file_info['width'] * file_info['height']) / 1_000_000
            info_table.add_row("📊 Megapixels:", f"{megapixels:.2f} MP")
        
        # Create panel
        panel = Panel(
            info_table,
            title="[bold cyan]📋 File Information[/bold cyan]",
            border_style="cyan",
            padding=(1, 2)
        )
        
        console.print(panel)
    
    def _show_conversion_summary(self, file_info, output_format, quality, settings, output_folder):
        """Show conversion summary before starting"""
        
        summary_table = Table(show_header=False, box=None, padding=(0, 2))
        summary_table.add_column(style="cyan bold", width=18)
        summary_table.add_column(style="white")
        
        summary_table.add_row("📥 Input:", file_info['name'])
        summary_table.add_row("📤 Output Format:", output_format)
        summary_table.add_row("⚙️  Quality:", quality)
        
        # Add advanced settings if any
        if settings.get('resolution'):
            summary_table.add_row("📐 Resolution:", settings['resolution'])
        if settings.get('fps'):
            summary_table.add_row("🎞️  Frame Rate:", f"{settings['fps']} fps")
        if settings.get('resize'):
            summary_table.add_row("🖼️  Resize:", settings['resize'])
        
        summary_table.add_row("📁 Output Folder:", output_folder)
        
        panel = Panel(
            summary_table,
            title="[bold yellow]📊 Conversion Summary[/bold yellow]",
            border_style="yellow",
            padding=(1, 2)
        )
        
        console.print("\n")
        console.print(panel)
    
    def _get_advanced_settings(self, file_type: str) -> dict:
        """Get advanced settings based on file type"""
        settings = {}
        
        try:
            if file_type == 'video':
                if questionary.confirm(
                    "Configure advanced video options?",
                    default=False,
                    style=questionary.Style([
                        ('question', 'fg:#00ffff'),
                        ('answer', 'fg:#00ff00 bold'),
                    ])
                ).ask():
                    
                    console.print("\n[dim]Advanced Video Options:[/dim]\n")
                    
                    # Resolution
                    resolution = questionary.select(
                        "Resolution:",
                        choices=VIDEO_RESOLUTIONS,
                        default='Original',
                        style=questionary.Style([
                            ('qmark', 'fg:#00ff00 bold'),
                            ('question', 'fg:#00ffff'),
                            ('pointer', 'fg:#00ffff bold'),
                            ('highlighted', 'fg:#00ffff bold'),
                        ])
                    ).ask()
                    
                    if resolution and resolution != 'Original':
                        settings['resolution'] = resolution
                    
                    # Frame rate
                    fps = questionary.select(
                        "Frame rate:",
                        choices=VIDEO_FRAMERATES,
                        default='Original',
                        style=questionary.Style([
                            ('qmark', 'fg:#00ff00 bold'),
                            ('question', 'fg:#00ffff'),
                            ('pointer', 'fg:#00ffff bold'),
                            ('highlighted', 'fg:#00ffff bold'),
                        ])
                    ).ask()
                    
                    if fps and fps != 'Original':
                        settings['fps'] = fps
            
            elif file_type == 'image':
                if questionary.confirm(
                    "Configure advanced image options?",
                    default=False,
                    style=questionary.Style([
                        ('question', 'fg:#00ffff'),
                        ('answer', 'fg:#00ff00 bold'),
                    ])
                ).ask():
                    
                    console.print("\n[dim]Advanced Image Options:[/dim]\n")
                    
                    # Resize
                    resize = questionary.select(
                        "Resize:",
                        choices=IMAGE_RESIZE_OPTIONS,
                        default='Original',
                        style=questionary.Style([
                            ('qmark', 'fg:#00ff00 bold'),
                            ('question', 'fg:#00ffff'),
                            ('pointer', 'fg:#00ffff bold'),
                            ('highlighted', 'fg:#00ffff bold'),
                        ])
                    ).ask()
                    
                    if resize and resize != 'Original':
                        settings['resize'] = resize
        
        except KeyboardInterrupt:
            logger.info("Advanced settings cancelled")
            return {}
        
        return settings
    
    def _convert_file(self, input_file: str, output_file: str, file_type: str, settings: dict) -> bool:
        """
        Convert file using appropriate converter
        
        Args:
            input_file: Path to input file
            output_file: Path to output file
            file_type: Type of file (video, audio, image, etc.)
            settings: Conversion settings
        
        Returns:
            True if conversion successful, False otherwise
        """
        # Get converter
        converter = ConverterFactory.get_converter(file_type)
        
        if not converter:
            logger.error(f"No converter available for type: {file_type}")
            self.display.show_error(
                f"No converter available for {file_type} files.",
                "Converter Not Found"
            )
            return False
        
        # Log conversion start
        logger.info(f"Starting conversion: {Path(input_file).name} -> {Path(output_file).name}")
        logger.debug(f"Settings: {settings}")
        
        # Perform conversion
        # Note: Notifications are shown inside the converter
        success, error = converter.convert(input_file, output_file, settings)
        
        # Log result
        if success:
            logger.info("Conversion completed successfully")
        else:
            logger.error(f"Conversion failed: {error}")
        
        return success
