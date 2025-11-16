#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""File and folder picker dialogs"""

from tkinter import Tk, filedialog
from typing import List
from utils.logger import get_logger

logger = get_logger()

class FilePicker:
    """Handle file and folder selection dialogs"""
    
    @staticmethod
    def _create_root():
        """Create and configure Tk root"""
        root = Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        return root
    
    @staticmethod
    def pick_file() -> str:
        """
        Open file picker dialog
        
        Returns:
            Selected file path or empty string
        """
        try:
            root = FilePicker._create_root()
            
            file_path = filedialog.askopenfilename(
                title="Select a file to convert",
                filetypes=[
                    ("All Files", "*.*"),
                    ("Video", "*.mp4 *.avi *.mkv *.mov *.webm"),
                    ("Audio", "*.mp3 *.wav *.flac *.aac *.ogg"),
                    ("Image", "*.jpg *.png *.gif *.bmp *.webp"),
                    ("Document", "*.md *.html *.txt *.pdf"),
                ]
            )
            
            root.destroy()
            logger.info(f"File selected: {file_path if file_path else 'None'}")
            return file_path
        except Exception as e:
            logger.error(f"Error in file picker: {e}")
            return ""
    
    @staticmethod
    def pick_multiple_files() -> List[str]:
        """
        Pick multiple files
        
        Returns:
            List of selected file paths
        """
        try:
            root = FilePicker._create_root()
            
            files = filedialog.askopenfilenames(
                title="Select files to convert",
                filetypes=[("All Files", "*.*")]
            )
            
            root.destroy()
            logger.info(f"Selected {len(files)} files")
            return list(files)
        except Exception as e:
            logger.error(f"Error picking files: {e}")
            return []
    
    @staticmethod
    def pick_folder() -> str:
        """
        Open folder picker dialog
        
        Returns:
            Selected folder path or empty string
        """
        try:
            root = FilePicker._create_root()
            
            folder_path = filedialog.askdirectory(title="Select output folder")
            root.destroy()
            logger.info(f"Folder selected: {folder_path if folder_path else 'None'}")
            return folder_path
        except Exception as e:
            logger.error(f"Error in folder picker: {e}")
            return ""
