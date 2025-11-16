#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""File type detection"""

from pathlib import Path
from typing import Tuple, Optional, Dict
from config.settings import FILE_TYPE_MAP
from utils.logger import get_logger

logger = get_logger()

class FileDetector:
    """Detect file type and metadata"""
    
    def detect(self, file_path: str) -> Tuple[str, str, str, Dict]:
        """
        Detect file type
        
        Args:
            file_path: Path to file
        
        Returns:
            Tuple of (file_type, tool_name, icon, formats_dict)
        """
        try:
            ext = Path(file_path).suffix.lower()
            
            for file_type, config in FILE_TYPE_MAP.items():
                if ext in config['extensions']:
                    logger.debug(f"Detected '{file_path}' as {file_type}")
                    return (
                        file_type,
                        config['tool'],
                        config['icon'],
                        config.get('formats', {})
                    )
            
            logger.warning(f"Unknown file type for: {file_path}")
            return 'unknown', 'Unknown', '', {}
            
        except Exception as e:
            logger.error(f"Error detecting file type: {e}")
            return 'unknown', 'Unknown', '', {}
    
    def get_file_info(self, file_path: str) -> Optional[Dict]:
        """
        Get detailed file information
        
        Args:
            file_path: Path to file
        
        Returns:
            Dict with file information or None
        """
        try:
            path = Path(file_path)
            if not path.exists():
                logger.error(f"File not found: {file_path}")
                return None
            
            file_type, tool, icon, formats = self.detect(file_path)
            stat = path.stat()
            
            info = {
                'name': path.name,
                'path': str(path.absolute()),
                'type': file_type,
                'tool': tool,
                'icon': icon,
                'size_bytes': stat.st_size,
                'size_mb': stat.st_size / 1024 / 1024,
                'formats': formats
            }
            
            # Add image-specific info
            if file_type == 'image':
                try:
                    from PIL import Image
                    img = Image.open(file_path)
                    info['width'] = img.width
                    info['height'] = img.height
                    info['mode'] = img.mode
                except Exception as e:
                    logger.debug(f"Could not read image metadata: {e}")
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            return None
