#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Logging utilities"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from config.settings import LOG_DIR

class LoggerManager:
    """Centralized logger management"""
    
    _instance = None
    _logger = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._logger is None:
            self._setup_logger()
    
    def _setup_logger(self):
        """Setup logging configuration"""
        LOG_DIR.mkdir(exist_ok=True)
        log_file = LOG_DIR / f"processor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # Create logger
        self._logger = logging.getLogger('UniversalFileProcessor')
        self._logger.setLevel(logging.DEBUG)
        
        # File handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)
        
        self._logger.info("=" * 60)
        self._logger.info(" Universal File Processor Started")
        self._logger.info(f"Log file: {log_file}")
        self._logger.info("=" * 60)
    
    def get_logger(self):
        """Get logger instance"""
        return self._logger

# Singleton instance
def get_logger():
    """Get global logger"""
    return LoggerManager().get_logger()
