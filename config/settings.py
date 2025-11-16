#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Central configuration for Universal File Processor"""

from pathlib import Path

# Directories
BASE_DIR = Path(__file__).parent.parent
LOG_DIR = BASE_DIR / "logs"
OUTPUT_DIR = BASE_DIR / "output"

# Quality settings
QUALITY_PRESETS = {
    'Low': {'crf': '28', 'audio_bitrate': '128k', 'image_quality': 60},
    'Medium': {'crf': '23', 'audio_bitrate': '192k', 'image_quality': 80},
    'High': {'crf': '18', 'audio_bitrate': '256k', 'image_quality': 95},
    'Ultra': {'crf': '15', 'audio_bitrate': '320k', 'image_quality': 100}
}

# File type mappings
FILE_TYPE_MAP = {
    'video': {
        'extensions': ['.mp4', '.avi', '.mkv', '.mov', '.webm', '.flv', '.wmv', '.m4v'],
        'tool': 'FFmpeg',
        'icon': '',
        'formats': {'MP4': 'mp4', 'AVI': 'avi', 'MKV': 'mkv', 'WebM': 'webm', 'MP3': 'mp3'}
    },
    'audio': {
        'extensions': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma', '.opus'],
        'tool': 'FFmpeg',
        'icon': '',
        'formats': {'MP3': 'mp3', 'WAV': 'wav', 'FLAC': 'flac', 'AAC': 'aac', 'OGG': 'ogg'}
    },
    'image': {
        'extensions': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.tiff'],
        'tool': 'PIL/ImageMagick',
        'icon': '',
        'formats': {'PNG': 'png', 'JPG': 'jpg', 'GIF': 'gif', 'WebP': 'webp', 'BMP': 'bmp'}
    },
    'document': {
        'extensions': ['.md', '.html', '.txt', '.tex', '.rst'],
        'tool': 'Pandoc',
        'icon': '',
        'formats': {'PDF': 'pdf', 'HTML': 'html', 'DOCX': 'docx'}
    },
    'office': {
        'extensions': ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'],
        'tool': 'LibreOffice',
        'icon': '',
        'formats': {'PDF': 'pdf', 'DOCX': 'docx'}
    },
    'ebook': {
        'extensions': ['.epub', '.mobi', '.azw3', '.pdf'],
        'tool': 'Calibre',
        'icon': '',
        'formats': {'EPUB': 'epub', 'MOBI': 'mobi', 'PDF': 'pdf'}
    }
}

# Tool commands
TOOL_COMMANDS = {
    'FFmpeg': 'ffmpeg',
    'ImageMagick': 'convert',
    'Pandoc': 'pandoc',
    'LibreOffice': 'soffice',
    'Calibre': 'ebook-convert',
    '7-Zip': '7z'
}

# Advanced options
VIDEO_RESOLUTIONS = ['Original', '1920x1080', '1280x720', '854x480', '640x360']
VIDEO_FRAMERATES = ['Original', '60', '30', '24']
IMAGE_RESIZE_OPTIONS = ['Original', '50%', '75%', '100%', '1920x1080', '1280x720']

# Timeouts (seconds)
CONVERSION_TIMEOUT = 600
