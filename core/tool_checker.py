#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tool availability checker"""

import shutil
from typing import Dict
from config.settings import TOOL_COMMANDS
from utils.logger import get_logger

logger = get_logger()

class ToolChecker:
    """Check availability of external tools"""
    
    def __init__(self):
        self._cache = {}
        self._pil_available = self._check_pil()
    
    def _check_pil(self) -> bool:
        """Check if PIL/Pillow is available"""
        try:
            from PIL import Image
            return True
        except ImportError:
            return False
    
    def is_available(self, tool_name: str) -> bool:
        """
        Check if a tool is available
        
        Args:
            tool_name: Name of the tool (e.g., 'FFmpeg', 'Pandoc')
        
        Returns:
            bool: True if tool is available
        """
        # Check cache
        if tool_name in self._cache:
            return self._cache[tool_name]
        
        # Special case for PIL
        if tool_name == 'PIL/ImageMagick':
            available = self._pil_available or shutil.which('convert') is not None
            self._cache[tool_name] = available
            return available
        
        # Check command availability
        cmd = TOOL_COMMANDS.get(tool_name)
        if not cmd:
            logger.warning(f"Unknown tool: {tool_name}")
            return False
        
        available = shutil.which(cmd) is not None
        self._cache[tool_name] = available
        
        logger.debug(f"Tool '{tool_name}': {'Available' if available else 'Not found'}")
        return available
    
    def get_all_tools_status(self) -> Dict[str, bool]:
        """
        Get status of all tools
        
        Returns:
            Dict mapping tool names to availability status
        """
        tools = ['FFmpeg', 'PIL/ImageMagick', 'ImageMagick', 'Pandoc', 'LibreOffice', 'Calibre']
        return {tool: self.is_available(tool) for tool in tools}
    
    @property
    def has_pil(self) -> bool:
        """Check if PIL is available"""
        return self._pil_available
