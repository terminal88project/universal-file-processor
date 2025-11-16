#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Color theme configuration"""

from rich.theme import Theme

# Custom theme
CUSTOM_THEME = Theme({
    "info": "cyan",
    "warning": "yellow",
    "danger": "red bold",
    "success": "green bold",
    "highlight": "magenta bold",
    "primary": "blue bold",
    "secondary": "white dim",
    "title": "cyan bold underline",
    "subtitle": "white bold",
})

# Gradient colors for different file types
FILE_TYPE_COLORS = {
    'video': 'bold blue',
    'audio': 'bold magenta',
    'image': 'bold cyan',
    'document': 'bold yellow',
    'office': 'bold green',
    'ebook': 'bold red',
}
