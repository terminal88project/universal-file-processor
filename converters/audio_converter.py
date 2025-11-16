#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audio converter using FFmpeg with beautiful notifications"""

import subprocess
import time
from typing import Tuple, Dict, Any, Optional
from pathlib import Path
from converters.base_converter import BaseConverter
from config.settings import QUALITY_PRESETS, CONVERSION_TIMEOUT
from ui.notifications import Notifications


class AudioConverter(BaseConverter):
    """Convert audio files using FFmpeg with enhanced UI feedback"""
    
    def convert(self, input_file: str, output_file: str, settings: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Convert audio file with progress notifications
        
        Args:
            input_file: Path to input audio file
            output_file: Path to output audio file
            settings: Conversion settings (quality, bitrate, etc.)
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
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
            
            cmd = [
                'ffmpeg',
                '-i', input_file,
                '-b:a', preset['audio_bitrate'],
                '-y', output_file
            ]
            
            self.logger.info(f"Converting audio: {Path(input_file).name} -> {Path(output_file).name}")
            self.logger.debug(f"Quality: {quality_name}, Bitrate: {preset['audio_bitrate']}")
            
            # Show progress notification
            Notifications.show_progress_notification(
                f"Converting audio: {Path(input_file).name}",
                icon="🎵"
            )
            
            # Execute
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=CONVERSION_TIMEOUT
            )
            
            # Calculate duration
            duration = time.time() - start_time
            
            if result.returncode == 0:
                self.logger.info(f"Audio conversion successful in {duration:.2f}s")
                
                # Show success notification
                Notifications.show_conversion_complete(
                    input_file,
                    output_file,
                    duration
                )
                
                return True, None
            else:
                error = result.stderr[:300] if result.stderr else result.stdout[:300]
                self.logger.error(f"FFmpeg failed: {error}")
                Notifications.show_conversion_failed(input_file, error)
                return False, error
                
        except subprocess.TimeoutExpired:
            error_msg = f"Conversion timeout (>{CONVERSION_TIMEOUT}s)"
            self.logger.error(error_msg)
            Notifications.show_conversion_failed(input_file, "⏱️ Timeout: Conversion took too long")
            return False, error_msg
            
        except FileNotFoundError:
            error_msg = "FFmpeg not found. Please install FFmpeg first."
            self.logger.error(error_msg)
            Notifications.show_conversion_failed(input_file, error_msg)
            return False, error_msg
            
        except Exception as e:
            error_msg = str(e)[:300]
            self.logger.error(f"Audio conversion exception: {error_msg}")
            Notifications.show_conversion_failed(input_file, error_msg)
            return False, error_msg
