#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Batch file conversion service with enhanced UI and progress tracking"""

from pathlib import Path
import questionary
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn, MofNCompleteColumn
from rich.text import Text

from core.file_detector import FileDetector
from core.tool_checker import ToolChecker
from converters import ConverterFactory
from ui.file_picker import FilePicker
from ui.display import Display
from ui.notifications import Notifications
from config.settings import OUTPUT_DIR
from utils.logger import get_logger

console = Console()
logger = get_logger()


class BatchFileConverter:
    """Handle batch file conversion workflow with beautiful UI"""
    
    def __init__(self):
        self.detector = FileDetector()
        self.tool_checker = ToolChecker()
        self.file_picker = FilePicker()
        self.display = Display()
    
    def run(self):
        """Run batch file conversion workflow"""
        try:
            console.clear()
            
            # Show header
            header = Panel(
                "[bold cyan]📂 Convert Multiple Files[/bold cyan]\n"
                "[dim]Batch process multiple files at once[/dim]",
                border_style="cyan",
                padding=(1, 2)
            )
            console.print(header)
            console.print()
            
            # Step 1: Pick files
            console.print("[cyan]📂 Step 1: Select Files[/cyan]\n")
            console.print("[dim]Opening file picker...[/dim]\n")
            
            files = self.file_picker.pick_multiple_files()
            
            if not files:
                console.print("\n[yellow]⚠️  No files selected[/yellow]")
                input("\n[dim]Press Enter to continue...[/dim]")
                return
            
            logger.info(f"Selected {len(files)} files for batch conversion")
            console.clear()
            
            # Show selected files count
            count_panel = Panel(
                f"[bold green]✓ Selected {len(files)} file{'s' if len(files) > 1 else ''}[/bold green]",
                border_style="green",
                padding=(0, 2)
            )
            console.print(count_panel)
            console.print()
            
            # Display file list
            self._display_file_list(files)
            
            # Confirm selection
            if not questionary.confirm(
                "\n▶️  Proceed with these files?",
                default=True,
                style=questionary.Style([
                    ('question', 'fg:#00ffff bold'),
                    ('answer', 'fg:#00ff00 bold'),
                ])
            ).ask():
                logger.info("Batch conversion cancelled by user")
                console.print("\n[yellow]Conversion cancelled[/yellow]")
                input("\n[dim]Press Enter to continue...[/dim]")
                return
            
            console.clear()
            
            # Step 2: Select output folder
            console.print("[cyan]📁 Step 2: Choose Output Location[/cyan]\n")
            output_folder = self.file_picker.pick_folder()
            
            if not output_folder:
                output_folder = str(OUTPUT_DIR)
                console.print(f"\n[dim]Using default output folder: {output_folder}[/dim]\n")
            else:
                console.print(f"\n[green]✓ Output folder selected[/green]\n")
            
            Path(output_folder).mkdir(exist_ok=True, parents=True)
            
            # Step 3: Select quality
            console.print("[cyan]⚙️  Step 3: Choose Quality for All Files[/cyan]\n")
            
            quality_descriptions = {
                'Low': 'Smallest size - 128k audio / CRF 28',
                'Medium': 'Balanced - 192k audio / CRF 23 (Recommended)',
                'High': 'Great quality - 256k audio / CRF 18',
                'Ultra': 'Maximum quality - 320k audio / CRF 15'
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
            
            # Step 4: Get format configuration
            console.print("\n[cyan]📋 Step 4: Configure Output Formats[/cyan]\n")
            format_config = self._get_format_config(files)
            
            if not format_config:
                self.display.show_warning(
                    "No valid file types found or format selection cancelled.",
                    "No Formats"
                )
                input("\n[dim]Press Enter to continue...[/dim]")
                return
            
            console.clear()
            
            # Show batch summary
            self._show_batch_summary(len(files), quality, format_config, output_folder)
            
            # Final confirmation
            if not questionary.confirm(
                "\n🚀 Start batch conversion?",
                default=True,
                style=questionary.Style([
                    ('question', 'fg:#00ffff bold'),
                    ('answer', 'fg:#00ff00 bold'),
                ])
            ).ask():
                console.print("\n[yellow]Batch conversion cancelled[/yellow]")
                input("\n[dim]Press Enter to continue...[/dim]")
                return
            
            # Perform batch conversion
            console.print("\n")
            success_count, failed_count = self._convert_batch(
                files,
                output_folder,
                quality,
                format_config
            )
            
            # Note: Batch completion notification is shown in _convert_batch
            
            input("\n[dim]Press Enter to continue...[/dim]")
            
        except KeyboardInterrupt:
            logger.info("Batch conversion cancelled by user (Ctrl+C)")
            console.print("\n\n[yellow]⚠️  Batch conversion cancelled[/yellow]")
            input("\n[dim]Press Enter to continue...[/dim]")
            
        except Exception as e:
            logger.error(f"Batch conversion error: {e}", exc_info=True)
            self.display.show_error(
                f"An unexpected error occurred:\n{str(e)[:200]}",
                "Batch Conversion Error"
            )
            input("\n[dim]Press Enter to continue...[/dim]")
    
    def _display_file_list(self, files):
        """Display list of selected files in a beautiful table"""
        
        # Create table
        table = Table(
            title="📋 Selected Files",
            show_header=True,
            header_style="bold cyan",
            title_style="bold cyan"
        )
        table.add_column("#", style="dim", width=5)
        table.add_column("File Name", style="white", width=50)
        table.add_column("Type", style="green", width=15)
        table.add_column("Size", style="cyan", width=12)
        
        # Add files to table (show first 15)
        display_limit = 15
        
        for idx, f in enumerate(files[:display_limit], 1):
            ftype, tool, icon, _ = self.detector.detect(f)
            name = Path(f).name
            
            # Truncate long names
            if len(name) > 45:
                name = name[:42] + "..."
            
            # Get file size
            try:
                size_bytes = Path(f).stat().st_size
                if size_bytes < 1024:
                    size = f"{size_bytes} B"
                elif size_bytes < 1024 * 1024:
                    size = f"{size_bytes / 1024:.1f} KB"
                elif size_bytes < 1024 * 1024 * 1024:
                    size = f"{size_bytes / (1024 * 1024):.1f} MB"
                else:
                    size = f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
            except:
                size = "N/A"
            
            table.add_row(
                str(idx),
                f"{icon} {name}",
                ftype.capitalize(),
                size
            )
        
        # Add "more files" row if needed
        if len(files) > display_limit:
            remaining = len(files) - display_limit
            table.add_row(
                "...",
                f"[dim]+ {remaining} more file{'s' if remaining > 1 else ''}[/dim]",
                "",
                ""
            )
        
        console.print(table)
        
        # Show total size
        try:
            total_size = sum(Path(f).stat().st_size for f in files)
            if total_size < 1024 * 1024 * 1024:
                total_str = f"{total_size / (1024 * 1024):.2f} MB"
            else:
                total_str = f"{total_size / (1024 * 1024 * 1024):.2f} GB"
            
            console.print(f"\n[dim]Total size: {total_str}[/dim]")
        except:
            pass
    
    def _show_batch_summary(self, file_count, quality, format_config, output_folder):
        """Show batch conversion summary"""
        
        summary_table = Table(show_header=False, box=None, padding=(0, 2))
        summary_table.add_column(style="cyan bold", width=20)
        summary_table.add_column(style="white")
        
        summary_table.add_row("📊 Total Files:", str(file_count))
        summary_table.add_row("⚙️  Quality:", quality)
        
        # Show format configurations
        for ftype, fmt in format_config.items():
            summary_table.add_row(
                f"📝 {ftype.capitalize()} →",
                fmt.upper()
            )
        
        summary_table.add_row("📁 Output Folder:", output_folder)
        
        panel = Panel(
            summary_table,
            title="[bold yellow]📊 Batch Conversion Summary[/bold yellow]",
            border_style="yellow",
            padding=(1, 2)
        )
        
        console.print(panel)
    
    def _get_format_config(self, files):
        """Get output format configuration for each file type"""
        
        format_config = {}
        file_types_present = {}
        
        # Detect all file types
        for fp in files:
            ftype, tool, icon, formats = self.detector.detect(fp)
            if ftype not in file_types_present and ftype != 'unknown' and formats:
                file_types_present[ftype] = (tool, icon, formats)
        
        if not file_types_present:
            return {}
        
        console.print(f"[dim]Found {len(file_types_present)} different file type(s)[/dim]\n")
        
        # Ask for format for each type
        for ftype, (tool, icon, formats) in file_types_present.items():
            if formats:
                try:
                    out_fmt = questionary.select(
                        f"{icon} {ftype.capitalize()} files → Convert to:",
                        choices=list(formats.keys()),
                        style=questionary.Style([
                            ('qmark', 'fg:#00ff00 bold'),
                            ('question', 'fg:#00ffff bold'),
                            ('answer', 'fg:#00ff00 bold'),
                            ('pointer', 'fg:#00ffff bold'),
                            ('highlighted', 'fg:#00ffff bold'),
                        ])
                    ).ask()
                    
                    if out_fmt:
                        format_config[ftype] = formats[out_fmt]
                        console.print(f"[green]✓ {ftype.capitalize()}: {out_fmt}[/green]\n")
                    else:
                        logger.info(f"Format selection cancelled for {ftype}")
                        return {}
                        
                except KeyboardInterrupt:
                    return {}
        
        return format_config
    
    def _convert_batch(self, files, output_folder, quality, format_config):
        """
        Convert batch of files with beautiful progress tracking
        
        Args:
            files: List of file paths
            output_folder: Output directory
            quality: Quality preset
            format_config: Format configuration dict
        
        Returns:
            Tuple of (success_count, failed_count)
        """
        success_count = 0
        failed_count = 0
        skipped_count = 0
        
        # Start timing
        start_time = time.time()
        
        # Create enhanced progress bar
        with Progress(
            SpinnerColumn(spinner_name="dots12", style="cyan"),
            TextColumn("[bold blue]{task.description}", justify="left"),
            BarColumn(
                bar_width=40,
                style="cyan",
                complete_style="green",
                finished_style="bold green"
            ),
            MofNCompleteColumn(),
            TextColumn("•", style="dim"),
            TimeRemainingColumn(),
            console=console,
            transient=False
        ) as progress:
            
            task = progress.add_task(
                f"[cyan]Converting {len(files)} files...",
                total=len(files)
            )
            
            for idx, fp in enumerate(files, 1):
                fp_path = Path(fp)
                ftype, tool, icon, _ = self.detector.detect(str(fp))
                
                # Update progress description
                progress.update(
                    task,
                    description=f"[cyan]Converting ({idx}/{len(files)}): {fp_path.name[:30]}..."
                )
                
                # Skip if unknown type or tool not available
                if ftype == 'unknown':
                    logger.warning(f"Skipping unknown file type: {fp_path.name}")
                    skipped_count += 1
                    progress.update(task, advance=1)
                    continue
                
                if not self.tool_checker.is_available(tool):
                    logger.warning(f"Skipping {fp_path.name} - {tool} not installed")
                    skipped_count += 1
                    progress.update(task, advance=1)
                    continue
                
                # Get output format
                output_ext = format_config.get(ftype)
                if not output_ext:
                    logger.warning(f"No format configured for {ftype}: {fp_path.name}")
                    skipped_count += 1
                    progress.update(task, advance=1)
                    continue
                
                output_file = str(Path(output_folder) / f"{fp_path.stem}.{output_ext}")
                
                # Get converter
                converter = ConverterFactory.get_converter(ftype)
                if not converter:
                    logger.error(f"No converter for {ftype}: {fp_path.name}")
                    failed_count += 1
                    progress.update(task, advance=1)
                    continue
                
                # Convert (notifications are suppressed during batch)
                settings = {'quality': quality, 'batch_mode': True}
                success, error = converter.convert(str(fp), output_file, settings)
                
                if success:
                    success_count += 1
                    logger.info(f"✓ Converted: {fp_path.name}")
                else:
                    failed_count += 1
                    logger.error(f"✗ Failed: {fp_path.name} - {error[:100] if error else 'Unknown error'}")
                
                progress.update(task, advance=1)
        
        # Calculate total duration
        duration = time.time() - start_time
        
        # Show batch completion notification
        Notifications.show_batch_complete(
            success_count,
            failed_count,
            len(files),
            duration
        )
        
        # Show detailed summary if there were skipped files
        if skipped_count > 0:
            console.print(f"\n[yellow]⚠️  {skipped_count} file(s) were skipped[/yellow]")
            console.print("[dim]Check logs for details[/dim]")
        
        # Log summary
        logger.info(
            f"Batch conversion complete: "
            f"{success_count} success, {failed_count} failed, "
            f"{skipped_count} skipped out of {len(files)} total"
        )
        
        return success_count, failed_count
