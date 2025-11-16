#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Converter factory with enhanced features and extensibility

This module provides a factory pattern for creating file converters.
New converters can be easily registered and managed.
"""

from typing import Optional, Dict, List, Type
from converters.base_converter import BaseConverter
from converters.video_converter import VideoConverter
from converters.audio_converter import AudioConverter
from converters.image_converter import ImageConverter
from converters.document_converter import DocumentConverter
from utils.logger import get_logger

logger = get_logger()


class ConverterFactory:
    """
    Factory for creating appropriate converters
    
    This factory uses the factory pattern to instantiate the correct
    converter based on file type. New converters can be registered
    dynamically.
    """
    
    # Built-in converter registry
    _converters: Dict[str, Type[BaseConverter]] = {
        'video': VideoConverter,
        'audio': AudioConverter,
        'image': ImageConverter,
        'document': DocumentConverter,
    }
    
    # Custom converter registry (for plugins/extensions)
    _custom_converters: Dict[str, Type[BaseConverter]] = {}
    
    @classmethod
    def get_converter(cls, file_type: str) -> Optional[BaseConverter]:
        """
        Get appropriate converter for file type
        
        Args:
            file_type: Type of file (video, audio, image, document, etc.)
        
        Returns:
            Converter instance or None if no converter found
        
        Example:
            >>> converter = ConverterFactory.get_converter('video')
            >>> if converter:
            ...     success, error = converter.convert(input_file, output_file, settings)
        """
        # Check custom converters first (allows overriding built-in ones)
        converter_class = cls._custom_converters.get(file_type)
        
        # Fall back to built-in converters
        if not converter_class:
            converter_class = cls._converters.get(file_type)
        
        if converter_class:
            try:
                instance = converter_class()
                logger.debug(f"Created converter instance for type: {file_type}")
                return instance
            except Exception as e:
                logger.error(f"Failed to create converter for {file_type}: {e}")
                return None
        else:
            logger.warning(f"No converter available for file type: {file_type}")
            return None
    
    @classmethod
    def register_converter(cls, file_type: str, converter_class: Type[BaseConverter]) -> bool:
        """
        Register a custom converter for a file type
        
        This allows plugins and extensions to add new converters
        or override existing ones.
        
        Args:
            file_type: Type of file (e.g., 'video', 'audio')
            converter_class: Converter class (must inherit from BaseConverter)
        
        Returns:
            True if registration successful, False otherwise
        
        Example:
            >>> class MyCustomConverter(BaseConverter):
            ...     def convert(self, input_file, output_file, settings):
            ...         # Custom conversion logic
            ...         pass
            >>> 
            >>> ConverterFactory.register_converter('custom', MyCustomConverter)
        """
        if not issubclass(converter_class, BaseConverter):
            logger.error(
                f"Cannot register {converter_class.__name__}: "
                f"must inherit from BaseConverter"
            )
            return False
        
        cls._custom_converters[file_type] = converter_class
        logger.info(f"Registered custom converter for type: {file_type}")
        return True
    
    @classmethod
    def unregister_converter(cls, file_type: str) -> bool:
        """
        Unregister a custom converter
        
        Args:
            file_type: Type of file to unregister
        
        Returns:
            True if unregistration successful, False otherwise
        """
        if file_type in cls._custom_converters:
            del cls._custom_converters[file_type]
            logger.info(f"Unregistered custom converter for type: {file_type}")
            return True
        else:
            logger.warning(f"No custom converter found for type: {file_type}")
            return False
    
    @classmethod
    def get_supported_types(cls) -> List[str]:
        """
        Get list of all supported file types
        
        Returns:
            List of supported file type names
        
        Example:
            >>> types = ConverterFactory.get_supported_types()
            >>> print(types)
            ['video', 'audio', 'image', 'document']
        """
        # Combine built-in and custom converters
        all_types = set(cls._converters.keys()) | set(cls._custom_converters.keys())
        return sorted(list(all_types))
    
    @classmethod
    def is_supported(cls, file_type: str) -> bool:
        """
        Check if a file type is supported
        
        Args:
            file_type: Type of file to check
        
        Returns:
            True if supported, False otherwise
        
        Example:
            >>> if ConverterFactory.is_supported('video'):
            ...     print("Video conversion is supported!")
        """
        return (file_type in cls._converters or 
                file_type in cls._custom_converters)
    
    @classmethod
    def get_converter_info(cls, file_type: str) -> Optional[Dict[str, str]]:
        """
        Get information about a converter
        
        Args:
            file_type: Type of file
        
        Returns:
            Dictionary with converter info or None
        
        Example:
            >>> info = ConverterFactory.get_converter_info('video')
            >>> print(info['name'])
            'VideoConverter'
        """
        converter_class = (cls._custom_converters.get(file_type) or 
                          cls._converters.get(file_type))
        
        if converter_class:
            return {
                'name': converter_class.__name__,
                'module': converter_class.__module__,
                'docstring': converter_class.__doc__ or 'No description available',
                'type': file_type,
                'is_custom': file_type in cls._custom_converters
            }
        return None
    
    @classmethod
    def list_all_converters(cls) -> Dict[str, Dict[str, str]]:
        """
        Get information about all available converters
        
        Returns:
            Dictionary mapping file types to converter info
        
        Example:
            >>> converters = ConverterFactory.list_all_converters()
            >>> for file_type, info in converters.items():
            ...     print(f"{file_type}: {info['name']}")
        """
        result = {}
        for file_type in cls.get_supported_types():
            info = cls.get_converter_info(file_type)
            if info:
                result[file_type] = info
        return result
    
    @classmethod
    def reset_custom_converters(cls):
        """
        Remove all custom converters
        
        This resets the factory to only use built-in converters.
        Useful for testing or resetting configuration.
        """
        cls._custom_converters.clear()
        logger.info("All custom converters have been reset")


# Convenience functions for backward compatibility
def get_converter(file_type: str) -> Optional[BaseConverter]:
    """
    Convenience function to get a converter
    
    Args:
        file_type: Type of file
    
    Returns:
        Converter instance or None
    """
    return ConverterFactory.get_converter(file_type)


def is_supported(file_type: str) -> bool:
    """
    Convenience function to check if file type is supported
    
    Args:
        file_type: Type of file
    
    Returns:
        True if supported, False otherwise
    """
    return ConverterFactory.is_supported(file_type)


# Export main classes and functions
__all__ = [
    'ConverterFactory',
    'BaseConverter',
    'VideoConverter',
    'AudioConverter',
    'ImageConverter',
    'DocumentConverter',
    'get_converter',
    'is_supported',
]


# Example usage (for documentation)
if __name__ == '__main__':
    # List all supported types
    print("Supported file types:")
    for file_type in ConverterFactory.get_supported_types():
        print(f"  - {file_type}")
    
    # Get converter info
    print("\nConverter details:")
    for file_type, info in ConverterFactory.list_all_converters().items():
        print(f"  {file_type}: {info['name']}")
    
    # Check if type is supported
    if ConverterFactory.is_supported('video'):
        print("\nVideo conversion is supported!")
        
        # Get a converter
        converter = ConverterFactory.get_converter('video')
        if converter:
            print(f"Created converter: {converter.__class__.__name__}")
