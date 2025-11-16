#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Base converter class"""

from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any, Optional
from pathlib import Path
from utils.logger import get_logger

logger = get_logger()

class BaseConverter(ABC):
    """Abstract base class for all converters"""
    
    def __init__(self):
        self.logger = get_logger()
    
    @abstractmethod
    def convert(self, input_file: str, output_file: str, settings: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Convert file
        
        Args:
            input_file: Path to input file
            output_file: Path to output file
            settings: Conversion settings (quality, resolution, etc.)
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        pass
    
    def validate_input(self, input_file: str) -> bool:
        """Validate input file exists"""
        if not Path(input_file).exists():
            self.logger.error(f"Input file not found: {input_file}")
            return False
        return True
    
    def ensure_output_dir(self, output_file: str) -> None:
        """Ensure output directory exists"""
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
