#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Image converter using PIL/Pillow with beautiful notifications"""

import time
from typing import Tuple, Dict, Any, Optional
from pathlib import Path
from converters.base_converter import BaseConverter
from config.settings import QUALITY_PRESETS
from ui.notifications import Notifications

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class ImageConverter(BaseConverter):
    """Convert image files using PIL/Pillow with enhanced UI feedback"""
    
    def __init__(self):
        super().__init__()
        if not HAS_PIL:
            self.logger.warning("PIL/Pillow not available - image conversion will fail")
    
    def convert(self, input_file: str, output_file: str, settings: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Convert image file with progress notifications
        
        Args:
            input_file: Path to input image file
            output_file: Path to output image file
            settings: Conversion settings (quality, resize, etc.)
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        if not HAS_PIL:
            error_msg = "PIL/Pillow not installed. Install with: pip install Pillow"
            Notifications.show_conversion_failed(input_file, error_msg)
            return False, error_msg
        
        if not self.validate_input(input_file):
            error_msg = "Input file not found"
            Notifications.show_conversion_failed(input_file, error_msg)
            return False, error_msg
        
        self.ensure_output_dir(output_file)
        
        # Start timing
        start_time = time.time()
        
        try:
            # Get quality settings
            quality_name = settings.get('quality', 'Medium')
            preset = QUALITY_PRESETS.get(quality_name, QUALITY_PRESETS['Medium'])
            quality = preset['image_quality']
            
            self.logger.info(f"Converting image: {Path(input_file).name} -> {Path(output_file).name}")
            
            # Show progress notification
            Notifications.show_progress_notification(
                f"Converting image: {Path(input_file).name}",
                icon="🖼️"
            )
            
            # Open image
            img = Image.open(input_file)
            original_size = img.size
            self.logger.debug(f"Original: {img.mode} {img.size}")
            
            # Resize if specified
            if settings.get('resize') and settings['resize'] != 'Original':
                img = self._resize_image(img, settings['resize'])
                self.logger.debug(f"Resized to: {img.size}")
            
            # Convert RGBA to RGB for JPG
            if img.mode in ('RGBA', 'LA', 'P') and output_file.lower().endswith(('.jpg', '.jpeg')):
                self.logger.debug(f"Converting {img.mode} to RGB for JPEG")
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[3])
                else:
                    background.paste(img)
                img = background
            
            # Save with optimization
            save_kwargs = {'optimize': True}
            
            if output_file.lower().endswith(('.jpg', '.jpeg')):
                save_kwargs['quality'] = quality
            elif output_file.lower().endswith('.png'):
                save_kwargs['compress_level'] = 9 if quality > 90 else 6
            
            img.save(output_file, **save_kwargs)
            
            # Calculate duration
            duration = time.time() - start_time
            
            self.logger.info(f"Image conversion successful in {duration:.2f}s")
            
            # Show success notification
            Notifications.show_conversion_complete(
                input_file,
                output_file,
                duration
            )
            
            return True, None
            
        except Exception as e:
            error_msg = str(e)[:300]
            self.logger.error(f"Image conversion exception: {error_msg}")
            Notifications.show_conversion_failed(input_file, error_msg)
            return False, error_msg
    
    def _resize_image(self, img: Image.Image, resize_option: str) -> Image.Image:
        """Resize image based on option"""
        if '%' in resize_option:
            # Percentage resize
            percent = int(resize_option.rstrip('%'))
            new_width = int(img.width * percent / 100)
            new_height = int(img.height * percent / 100)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.logger.info(f"Resized to {percent}%: {img.size}")
        elif 'x' in resize_option.lower():
            # Dimension resize
            try:
                width, height = map(int, resize_option.lower().split('x'))
                img = img.resize((width, height), Image.Resampling.LANCZOS)
                self.logger.info(f"Resized to: {img.size}")
            except ValueError:
                self.logger.warning(f"Invalid resize option: {resize_option}")
        
        return img
