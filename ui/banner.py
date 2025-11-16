#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Beautiful ASCII art banner"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ██╗   ██╗███████╗██████╗                                  ║
║   ██║   ██║██╔════╝██╔══██╗                                 ║
║   ██║   ██║█████╗  ██████╔╝                                 ║
║   ██║   ██║██╔══╝  ██╔═══╝                                  ║
║   ╚██████╔╝██║     ██║                                      ║
║    ╚═════╝ ╚═╝     ╚═╝                                      ║
║                                                              ║
║        Universal File Processor Pro v2.0                    ║
║        Professional Modular Conversion Tool                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""

GRADIENT_BANNER = r"""
    __  __      _                          __   _____ __   
   / / / /___  (_)   _____  _____________ _/ /  / ___// /   
  / / / / __ \/ / | / / _ \/ ___/ ___/ __  /   \__ \/ /    
 / /_/ / / / / /| |/ /  __/ /  (__  ) /_/ /   ___/ / /___  
 \____/_/ /_/_/ |___/\___/_/  /____/\__,_/   /____/_____/  
                                                            
           🎬 Video  🎵 Audio  🖼️ Image  📝 Document
"""

def show_banner():
    """Display animated banner"""
    console.clear()
    
    # Gradient colors
    colors = ["cyan", "blue", "magenta", "cyan"]
    
    # Animated text
    text = Text()
    lines = GRADIENT_BANNER.split('\n')
    
    for i, line in enumerate(lines):
        color = colors[i % len(colors)]
        text.append(line + '\n', style=f"bold {color}")
    
    console.print(Panel(
        text,
        border_style="bold cyan",
        padding=(1, 2)
    ))

def show_welcome():
    """Show welcome message with stats"""
    from rich.table import Table
    
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="cyan bold")
    table.add_column(style="white")
    
    table.add_row("🎬 Video", "MP4, AVI, MKV, WebM, MOV")
    table.add_row("🎵 Audio", "MP3, WAV, FLAC, AAC, OGG")
    table.add_row("🖼️  Image", "PNG, JPG, GIF, WebP, BMP")
    table.add_row("📝 Document", "PDF, HTML, DOCX, Markdown")
    table.add_row("📊 Office", "Excel, PowerPoint, Word → PDF")
    table.add_row("📚 Ebook", "EPUB, MOBI, AZW3, PDF")
    
    console.print("\n")
    console.print(table)
    console.print("\n")
