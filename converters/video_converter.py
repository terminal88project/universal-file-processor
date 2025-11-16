#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Video converter using FFmpeg with beautiful notifications"""

import subprocess
import time
from typing import Tuple, Dict, Any, Optional
from pathlib import Path
from converters.base_converter import BaseConverter
from config.settings import QUALITY_PRESETS, CONVERSION_TIMEOUT
from ui.notifications import Notifications


class VideoConverter(BaseConverter):
    """Convert video files using FFmpeg with enhanced UI feedback"""
    
    def convert(self, input_file: str, output_file: str, settings: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Convert video file with progress notifications
        
        Args:
            input_file: Path to input video file
            output_file: Path to output video file
            settings: Conversion settings (quality, resolution, fps, etc.)
        
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
            
            # Build FFmpeg command
            cmd = [
                'ffmpeg',
                '-i', input_file,
                '-crf', preset['crf'],
                '-b:a', preset['audio_bitrate'],
            ]
            
            # Add resolution if specified
            if settings.get('resolution') and settings['resolution'] != 'Original':
                cmd.extend(['-s', settings['resolution']])
                self.logger.debug(f"Resolution set to: {settings['resolution']}")
            
            # Add FPS if specified
            if settings.get('fps') and settings['fps'] != 'Original':
                cmd.extend(['-r', str(settings['fps'])])
                self.logger.debug(f"FPS set to: {settings['fps']}")
            
            # Add codec if specified
            if settings.get('codec'):
                cmd.extend(['-c:v', settings['codec']])
                self.logger.debug(f"Codec set to: {settings['codec']}")
            
            cmd.extend(['-y', output_file])
            
            self.logger.info(f"Converting video: {Path(input_file).name} -> {Path(output_file).name}")
            self.logger.debug(f"FFmpeg command: {' '.join(cmd)}")
            self.logger.debug(f"Quality: {quality_name}, CRF: {preset['crf']}, Audio: {preset['audio_bitrate']}")
            
            # Show progress notification
            Notifications.show_progress_notification(
                f"Converting video: {Path(input_file).name}",
                icon="🎬"
            )
            
            # Execute FFmpeg
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=CONVERSION_TIMEOUT
            )
            
            # Calculate duration
            duration = time.time() - start_time
            
            if result.returncode == 0:
                self.logger.info(f"Video conversion successful in {duration:.2f}s")
                
                # Show success notification
                Notifications.show_conversion_complete(
                    input_file,
                    output_file,
                    duration
                )
                
                return True, None
            else:
                # Extract meaningful error from FFmpeg output
                error = result.stderr if result.stderr else result.stdout
                
                # Try to extract the actual error message
                error_lines = error.split('\n')
                meaningful_error = None
                
                for line in reversed(error_lines):
                    if 'error' in line.lower() or 'invalid' in line.lower():
                        meaningful_error = line.strip()
                        break
                
                if not meaningful_error:
                    meaningful_error = error[:300]
                
                self.logger.error(f"FFmpeg failed: {meaningful_error}")
                
                # Show failure notification
                Notifications.show_conversion_failed(input_file, meaningful_error)
                
                return False, meaningful_error
                
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            error_msg = f"Conversion timeout after {duration:.0f}s (limit: {CONVERSION_TIMEOUT}s)"
            self.logger.error(error_msg)
            
            # Show timeout notification
            Notifications.show_conversion_failed(
                input_file,
                f"⏱️ Timeout: Conversion took too long (>{CONVERSION_TIMEOUT}s)"
            )
            
            return False, error_msg
            
        except FileNotFoundError:
            error_msg = "FFmpeg not found. Please install FFmpeg first."
            self.logger.error(error_msg)
            Notifications.show_conversion_failed(input_file, error_msg)
            return False, error_msg
            
        except PermissionError:
            error_msg = f"Permission denied: Cannot write to {output_file}"
            self.logger.error(error_msg)
            Notifications.show_conversion_failed(input_file, error_msg)
            return False, error_msg
            
        except Exception as e:
            error_msg = str(e)[:300]
            self.logger.error(f"Video conversion exception: {error_msg}", exc_info=True)
            Notifications.show_conversion_failed(input_file, error_msg)
            return False, error_msg
    
    def get_video_info(self, video_file: str) -> Optional[Dict]:
        """
        Get video file information using FFprobe
        
        Args:
            video_file: Path to video file
        
        Returns:
            Dictionary with video metadata or None
        """
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                video_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                
                # Extract video stream info
                video_stream = next(
                    (s for s in data.get('streams', []) if s.get('codec_type') == 'video'),
                    None
                )
                
                if video_stream:
                    return {
                        'width': video_stream.get('width'),
                        'height': video_stream.get('height'),
                        'codec': video_stream.get('codec_name'),
                        'fps': eval(video_stream.get('r_frame_rate', '0/1')),
                        'duration': float(data.get('format', {}).get('duration', 0)),
                        'bitrate': int(data.get('format', {}).get('bit_rate', 0)),
                    }
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Could not get video info: {e}")
            return None
