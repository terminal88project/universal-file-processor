#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Universal File Processor - Main Entry Point
Professional Modular File Conversion Tool v2.0

A beautiful, modular file conversion tool supporting:
- Video/Audio conversion (FFmpeg)
- Image processing (PIL/ImageMagick)
- Document conversion (Pandoc)
- Office files (LibreOffice)
- Ebook conversion (Calibre)
"""

import sys
import os
import io

# UTF-8 encoding setup for Windows compatibility
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

# Import UI components
from ui.menu import MainMenu
from ui.display import Display

# Import services
from services.single_converter import SingleFileConverter
from services.batch_converter import BatchFileConverter
from services.file_info import FileInfoService

# Import core components
from core.tool_checker import ToolChecker
from utils.logger import get_logger

# Initialize console and logger
console = Console()
logger = get_logger()

def show_splash_screen():
    """Display beautiful splash screen on startup"""
    console.clear()
    splash = r"""
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║     ██╗   ██╗███████╗██████╗                                  ║
    ║     ██║   ██║██╔════╝██╔══██╗                                 ║
    ║     ██║   ██║█████╗  ██████╔╝                                 ║
    ║     ██║   ██║██╔══╝  ██╔═══╝                                 ║
    ║     ╚██████╔╝██║     ██║                                     ║
    ║      ╚═════╝ ╚═╝     ╚═╝                                     ║
    ║                                                                ║
    ║           Universal File Processor v2.0                        ║
    ║        Professional Modular Conversion Tool                    ║
    ║                                                                ║
    ║                  🎬 🎵 🖼️  📝 📊 📚                           ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """    
    text = Text(splash, style="bold cyan")
    console.print(Align.center(text))
    console.print()
    console.print(Align.center("[dim]Loading...[/dim]"))    
    import time
    time.sleep(1.2)

def check_dependencies():
    """Check if required Python packages are installed"""
    required_packages = {
        'questionary': 'questionary',
        'rich': 'rich',
        'PIL': 'Pillow'
    }
    missing = []
    for module, package in required_packages.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    if missing:
        console.print("\n[bold red]❌ Missing Dependencies[/bold red]\n")
        console.print("Please install the following packages:\n")
        for pkg in missing:
            console.print(f"  • [cyan]{pkg}[/cyan]")
        console.print("\nInstall with:")
        console.print(f"  [green]pip install {' '.join(missing)}[/green]\n")
        return False    
    return True

def show_startup_info(tool_checker):
    """Display startup information and tool status"""
    console.clear()
    # Better formatted welcome message
    welcome_text = Text()
    welcome_text.append("Welcome to Universal File Processor!\n", style="bold cyan")
    welcome_text.append("\nA professional tool for converting:\n\n", style="white")
    # Format in two lines
    welcome_text.append("  🎬 Videos", style="green")
    welcome_text.append("      ", style="dim")
    welcome_text.append("🎵 Audio", style="green")
    welcome_text.append("       ", style="dim")
    welcome_text.append("🖼️  Images\n", style="green")
    welcome_text.append("  📝 Documents", style="green")
    welcome_text.append("   ", style="dim")
    welcome_text.append("📊 Office", style="green")
    welcome_text.append("      ", style="dim")
    welcome_text.append("📚 Ebooks", style="green")
    welcome_panel = Panel(
        Align.center(welcome_text),
        border_style="cyan",
        padding=(1, 2)
    )
    console.print(welcome_panel)
    console.print()
    # Animated checking with spinner
    with console.status("[bold yellow]🔍 Checking installed tools...[/bold yellow]", spinner="dots12"):
        import time
        status = tool_checker.get_all_tools_status()
        time.sleep(0.7)
    console.print()
    available = sum(1 for v in status.values() if v)
    total = len(status)
    if available == 0:
        console.print("[bold red]⚠️  No conversion tools found![/bold red]\n")
        console.print("[yellow]You can still use the app, but conversions require:[/yellow]")
        console.print("  • FFmpeg (video/audio)")
        console.print("  • Pillow/ImageMagick (images)")
        console.print("  • Pandoc (documents)")
        console.print("  • LibreOffice (office files)")
        console.print("  • Calibre (ebooks)\n")
    elif available < total:
        console.print(f"[yellow]✓ {available}/{total} tools available[/yellow]")
        console.print("[dim]Some features may be limited[/dim]\n")
    else:
        console.print(f"[bold green]✅ All {total} tools available![/bold green]\n")
    console.print("[dim]Press Enter to continue...[/dim]", end="")
    try:
        input()
    except KeyboardInterrupt:
        pass

def main():
    """Main application loop with enhanced error handling"""
    try:
        # Show splash screen
        show_splash_screen()
        # Check dependencies
        if not check_dependencies():
            logger.error("Missing required dependencies")
            sys.exit(1)
        # Initialize services
        logger.info("Initializing services...")
        try:
            single_converter = SingleFileConverter()
            batch_converter = BatchFileConverter()
            file_info_service = FileInfoService()
            tool_checker = ToolChecker()
            display = Display()
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            console.print(f"[red]Initialization error: {e}[/red]")
            sys.exit(1)
        # Show startup info
        show_startup_info(tool_checker)
        logger.info("Application started successfully")
        # Main application loop
        while True:
            try:
                # پاکسازی قبل از هر عمل یا نمایش جدید (مهم برای جلوگیری هم‌افتادگی)
                console.clear()
                choice = MainMenu.show()
                if choice is None:
                    continue
                elif choice == "Convert Single File":
                    console.clear()
                    logger.info("User selected: Convert Single File")
                    try:
                        single_converter.run()
                    except Exception as e:
                        logger.error(f"Error in single file conversion: {e}")
                        console.clear()
                        MainMenu.show_error(f"Conversion failed: {str(e)[:100]}")
                        MainMenu.pause()
                elif choice == "Convert Multiple Files":
                    console.clear()
                    logger.info("User selected: Convert Multiple Files")
                    try:
                        batch_converter.run()
                    except Exception as e:
                        logger.error(f"Error in batch conversion: {e}")
                        console.clear()
                        MainMenu.show_error(f"Batch conversion failed: {str(e)[:100]}")
                        MainMenu.pause()
                elif choice == "File Information":
                    console.clear()
                    logger.info("User selected: File Information")
                    try:
                        file_info_service.run()
                    except Exception as e:
                        logger.error(f"Error showing file info: {e}")
                        console.clear()
                        MainMenu.show_error(f"Could not read file info: {str(e)[:100]}")
                        MainMenu.pause()
                elif choice == "Tools Status":
                    console.clear()
                    logger.info("User selected: Tools Status")
                    try:
                        status = tool_checker.get_all_tools_status()
                        display.show_tools_status(status)
                        MainMenu.pause()
                    except Exception as e:
                        logger.error(f"Error checking tools: {e}")
                        console.clear()
                        MainMenu.show_error(f"Could not check tools: {str(e)[:100]}")
                        MainMenu.pause()
                elif choice == "View Logs":
                    console.clear()
                    logger.info("User selected: View Logs")
                    try:
                        display.show_logs()
                        MainMenu.pause()
                    except Exception as e:
                        logger.error(f"Error viewing logs: {e}")
                        console.clear()
                        MainMenu.show_error(f"Could not read logs: {str(e)[:100]}")
                        MainMenu.pause()
                elif choice == "Exit":
                    logger.info("Application closed by user")
                    console.clear()
                    goodbye_text = Text()
                    goodbye_text.append("\n\n")
                    goodbye_text.append("Thank you for using\n", style="bold cyan")
                    goodbye_text.append("Universal File Processor!\n\n", style="bold white")
                    goodbye_text.append("👋 Goodbye!\n\n", style="bold yellow")
                    console.print(Align.center(goodbye_text))
                    break
                else:
                    logger.warning(f"Unknown menu choice: '{choice}'")
                    console.clear()
                    MainMenu.show_warning(f"Unknown option selected: '{choice}'")
                    MainMenu.pause()
                # پاکسازی مجدد پس از هر اقدام و قبل از نمایش منوی جدید
                console.clear()
            except KeyboardInterrupt:
                if MainMenu.confirm("\nAre you sure you want to exit?", default=False):
                    logger.info("Application closed by user (Ctrl+C)")
                    console.print("\n[yellow]👋 Goodbye![/yellow]\n")
                    break
                else:
                    continue
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
                console.clear()
                MainMenu.show_error(f"An unexpected error occurred: {str(e)[:100]}")
                if not MainMenu.confirm("Continue running?", default=True):
                    break
                console.clear()
    except KeyboardInterrupt:
        logger.info("Application interrupted during startup")
        console.print("\n[yellow]Application interrupted[/yellow]")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        console.print(f"\n[bold red]Fatal Error[/bold red]\n")
        console.print(f"[red]{e}[/red]\n")
        console.print("[dim]Check logs for details[/dim]\n")
        sys.exit(1)
    finally:
        logger.info("Application shutdown complete")

def show_version():
    """Show version information"""
    version_info = """
Universal File Processor v2.0

A professional modular file conversion tool.

Supported formats:
  🎬 Video:    MP4, AVI, MKV, WebM, MOV
  🎵 Audio:    MP3, WAV, FLAC, AAC, OGG
  🖼️  Image:   PNG, JPG, GIF, WebP, BMP
  📝 Document: PDF, HTML, DOCX, Markdown
  📊 Office:   Excel, Word, PowerPoint
  📚 Ebook:    EPUB, MOBI, AZW3, PDF

For more info: [https://github.com/yourusername/universal-file-processor](https://github.com/yourusername/universal-file-processor)
"""
    console.print(version_info)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--version', '-v']:
            show_version()
            sys.exit(0)
        elif sys.argv[1] in ['--help', '-h']:
            console.print("""
Usage: python main.py [OPTIONS]

Options:
  -v, --version    Show version information
  -h, --help       Show this help message
       
Run without arguments to start the interactive menu.
""")
            sys.exit(0)
    main()
