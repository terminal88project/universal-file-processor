#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Beautiful notification system with enhanced animations"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.table import Table
from pathlib import Path
import time

console = Console()


class Notifications:
    """Beautiful notification messages with enhanced UI"""
    
    @staticmethod
    def show_conversion_complete(input_file: str, output_file: str, duration: float = None):
        """
        Show beautiful completion notification with file details
        
        Args:
            input_file: Input file path
            output_file: Output file path
            duration: Conversion duration in seconds
        """
        console.print("\n")
        
        # Create notification text
        text = Text()
        text.append("🎉 ", style="bold yellow")
        text.append("Conversion Complete!", style="bold green")
        text.append("\n\n")
        
        # Input file
        text.append("📥 Input:    ", style="cyan bold")
        text.append(f"{Path(input_file).name}\n", style="white")
        
        # Output file
        text.append("📤 Output:   ", style="green bold")
        text.append(f"{Path(output_file).name}\n", style="white")
        
        # Output location
        output_path = Path(output_file).parent
        text.append("📁 Location: ", style="cyan bold")
        
        # Truncate long paths
        path_str = str(output_path)
        if len(path_str) > 50:
            path_str = "..." + path_str[-47:]
        text.append(f"{path_str}\n", style="dim white")
        
        # File size comparison
        try:
            input_size = Path(input_file).stat().st_size
            output_size = Path(output_file).stat().st_size
            
            # Format sizes
            def format_size(size_bytes):
                if size_bytes < 1024:
                    return f"{size_bytes} B"
                elif size_bytes < 1024 * 1024:
                    return f"{size_bytes / 1024:.2f} KB"
                elif size_bytes < 1024 * 1024 * 1024:
                    return f"{size_bytes / (1024 * 1024):.2f} MB"
                else:
                    return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
            
            output_size_str = format_size(output_size)
            text.append("💾 Size:     ", style="cyan bold")
            text.append(f"{output_size_str}", style="white")
            
            # Show size difference
            if input_size > 0:
                size_diff = ((output_size - input_size) / input_size) * 100
                if abs(size_diff) > 1:  # Only show if difference is > 1%
                    if size_diff > 0:
                        text.append(f" (+{size_diff:.1f}%)", style="yellow")
                    else:
                        text.append(f" ({size_diff:.1f}%)", style="green")
            
            text.append("\n")
        except Exception:
            pass
        
        # Duration
        if duration:
            text.append("⏱️  Duration: ", style="cyan bold")
            if duration < 1:
                time_str = f"{duration * 1000:.0f}ms"
            elif duration < 60:
                time_str = f"{duration:.2f}s"
            else:
                minutes = int(duration // 60)
                seconds = duration % 60
                time_str = f"{minutes}m {seconds:.1f}s"
            text.append(f"{time_str}", style="white")
        
        # Create panel
        panel = Panel(
            Align.center(text),
            title="[bold green]✨ Success ✨[/bold green]",
            subtitle="[dim]File saved successfully[/dim]",
            border_style="green",
            padding=(1, 2)
        )
        
        console.print(panel)
        console.print()
    
    @staticmethod
    def show_conversion_failed(input_file: str, error: str):
        """
        Show failure notification with error details
        
        Args:
            input_file: Input file path
            error: Error message
        """
        console.print("\n")
        
        text = Text()
        text.append("❌ ", style="bold red")
        text.append("Conversion Failed", style="bold red")
        text.append("\n\n")
        
        text.append("📄 File: ", style="cyan bold")
        text.append(f"{Path(input_file).name}\n\n", style="white")
        
        text.append("🔴 Error:\n", style="red bold")
        
        # Format error message (wrap long lines)
        error_text = error[:300]  # Limit error length
        error_lines = error_text.split('\n')
        for line in error_lines[:5]:  # Show max 5 lines
            if line.strip():
                text.append(f"   {line.strip()}\n", style="yellow")
        
        panel = Panel(
            Align.center(text),
            title="[bold red]⚠️  Failed ⚠️[/bold red]",
            subtitle="[dim]Check logs for full error details[/dim]",
            border_style="red",
            padding=(1, 2)
        )
        
        console.print(panel)
        console.print()
    
    @staticmethod
    def show_batch_complete(success: int, failed: int, total: int, duration: float = None):
        """
        Show batch conversion completion with statistics
        
        Args:
            success: Number of successful conversions
            failed: Number of failed conversions
            total: Total files processed
            duration: Total duration in seconds
        """
        console.print("\n")
        
        # Create statistics table
        stats_table = Table(show_header=False, box=None, padding=(0, 3))
        stats_table.add_column(style="bold", justify="right", width=20)
        stats_table.add_column(style="bold", justify="left")
        
        stats_table.add_row("✅ Successful:", f"[green]{success}[/green]")
        stats_table.add_row("❌ Failed:", f"[red]{failed}[/red]")
        stats_table.add_row("📊 Total:", f"[cyan]{total}[/cyan]")
        
        # Success rate
        if total > 0:
            rate = (success / total) * 100
            if rate >= 80:
                rate_style = "bold green"
                rate_icon = "🎉"
            elif rate >= 50:
                rate_style = "bold yellow"
                rate_icon = "⚠️"
            else:
                rate_style = "bold red"
                rate_icon = "❌"
            
            stats_table.add_row(
                "📈 Success Rate:",
                f"[{rate_style}]{rate_icon} {rate:.1f}%[/{rate_style}]"
            )
        
        # Duration
        if duration:
            if duration < 60:
                time_str = f"{duration:.2f}s"
            elif duration < 3600:
                minutes = int(duration // 60)
                seconds = duration % 60
                time_str = f"{minutes}m {seconds:.0f}s"
            else:
                hours = int(duration // 3600)
                minutes = int((duration % 3600) // 60)
                time_str = f"{hours}h {minutes}m"
            
            stats_table.add_row("⏱️  Total Time:", f"[white]{time_str}[/white]")
        
        # Calculate average time per file
        if duration and total > 0:
            avg_time = duration / total
            if avg_time < 1:
                avg_str = f"{avg_time * 1000:.0f}ms"
            else:
                avg_str = f"{avg_time:.2f}s"
            stats_table.add_row("⚡ Avg per File:", f"[dim]{avg_str}[/dim]")
        
        # Determine border style and title
        if success == total and total > 0:
            border_style = "green"
            title = "[bold green]✨ Perfect! All files converted ✨[/bold green]"
            subtitle = "[dim green]🎉 100% success rate[/dim green]"
        elif success > 0:
            border_style = "yellow"
            title = "[bold yellow]⚡ Batch Conversion Completed ⚡[/bold yellow]"
            subtitle = f"[dim]{success} succeeded, {failed} failed[/dim]"
        else:
            border_style = "red"
            title = "[bold red]⚠️  All Conversions Failed ⚠️[/bold red]"
            subtitle = "[dim]Check logs for error details[/dim]"
        
        panel = Panel(
            Align.center(stats_table),
            title=title,
            subtitle=subtitle,
            border_style=border_style,
            padding=(1, 2)
        )
        
        console.print(panel)
        console.print()
        
        # Show celebration if perfect
        if success == total and total > 0:
            Notifications.show_celebration()
    
    @staticmethod
    def show_progress_notification(message: str, icon: str = "⏳"):
        """
        Show inline progress notification
        
        Args:
            message: Progress message
            icon: Icon to display (default: hourglass)
        """
        text = f"{icon} [cyan]{message}[/cyan]"
        console.print(text)
    
    @staticmethod
    def show_celebration():
        """Show celebration animation with emojis"""
        celebration = "🎉 🎊 ✨ 🎈 🎁 ✨ 🎊 🎉"
        console.print(f"[bold yellow]{celebration}[/bold yellow]", justify="center")
    
    @staticmethod
    def show_warning(message: str, title: str = "Warning"):
        """
        Show warning notification
        
        Args:
            message: Warning message
            title: Warning title
        """
        console.print("\n")
        
        panel = Panel(
            f"[yellow]{message}[/yellow]",
            title=f"[bold yellow]⚠️  {title}[/bold yellow]",
            border_style="yellow",
            padding=(1, 2)
        )
        
        console.print(panel)
        console.print()
    
    @staticmethod
    def show_info(message: str, title: str = "Information"):
        """
        Show info notification
        
        Args:
            message: Info message
            title: Info title
        """
        console.print("\n")
        
        panel = Panel(
            f"[cyan]{message}[/cyan]",
            title=f"[bold cyan]ℹ️  {title}[/bold cyan]",
            border_style="cyan",
            padding=(1, 2)
        )
        
        console.print(panel)
        console.print()
    
    @staticmethod
    def show_success(message: str, title: str = "Success"):
        """
        Show success notification (simple)
        
        Args:
            message: Success message
            title: Success title
        """
        console.print("\n")
        
        panel = Panel(
            f"[green]{message}[/green]",
            title=f"[bold green]✅ {title}[/bold green]",
            border_style="green",
            padding=(1, 2)
        )
        
        console.print(panel)
        console.print()
    
    @staticmethod
    def show_error(message: str, title: str = "Error"):
        """
        Show error notification (simple)
        
        Args:
            message: Error message
            title: Error title
        """
        console.print("\n")
        
        panel = Panel(
            f"[red]{message}[/red]",
            title=f"[bold red]❌ {title}[/bold red]",
            border_style="red",
            padding=(1, 2)
        )
        
        console.print(panel)
        console.print()


# Example usage for testing
if __name__ == '__main__':
    # Test conversion complete
    Notifications.show_conversion_complete(
        "video.mp4",
        "output/video.avi",
        15.5
    )
    
    time.sleep(1)
    
    # Test conversion failed
    Notifications.show_conversion_failed(
        "image.png",
        "FFmpeg error: Invalid codec parameters"
    )
    
    time.sleep(1)
    
    # Test batch complete
    Notifications.show_batch_complete(
        success=8,
        failed=2,
        total=10,
        duration=125.3
    )
    
    time.sleep(1)
    
    # Test other notifications
    Notifications.show_warning("This is a warning message")
    Notifications.show_info("This is an info message")
    Notifications.show_success("Operation completed successfully!")
    Notifications.show_error("Something went wrong!")
