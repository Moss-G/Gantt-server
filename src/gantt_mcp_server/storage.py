#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Storage logic for Gantt chart data persistence

import os
import json
from typing import Dict, Any
from datetime import datetime

# Default data file location
DEFAULT_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data')
DEFAULT_DATA_FILE = os.path.join(DEFAULT_DATA_DIR, 'gantt_data.json')

def ensure_data_dir_exists(data_dir: str = DEFAULT_DATA_DIR) -> None:
    """
    Ensure that the data directory exists.
    
    Args:
        data_dir: Directory path to check/create
    """
    os.makedirs(data_dir, exist_ok=True)

def save_data(data: Dict[str, Any], file_path: str = DEFAULT_DATA_FILE) -> None:
    """
    Save Gantt chart data to a JSON file.
    
    Args:
        data: Gantt chart data to save
        file_path: Path to the JSON file to save to
    """
    # Ensure data directory exists
    ensure_data_dir_exists(os.path.dirname(file_path))
    
    # Create a copy of the data to avoid modifying the original
    data_copy = data.copy()
    
    # Add a timestamp to track when data was last saved
    metadata = {
        "last_saved": datetime.now().isoformat(),
        "version": "1.0"
    }
    
    # Create the structure to save
    save_structure = {
        "metadata": metadata,
        "projects": data_copy
    }
    
    # Write the data to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(save_structure, f, indent=2, ensure_ascii=False)

def load_data(file_path: str = DEFAULT_DATA_FILE) -> Dict[str, Any]:
    """
    Load Gantt chart data from a JSON file.
    
    Args:
        file_path: Path to the JSON file to load from
        
    Returns:
        The loaded Gantt chart data, or an empty dict if the file doesn't exist
    """
    try:
        # Check if the file exists
        if not os.path.exists(file_path):
            return {}
        
        # Read the data from the file
        with open(file_path, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        # Extract just the projects data
        if isinstance(loaded_data, dict) and "projects" in loaded_data:
            return loaded_data["projects"]
        
        # Handle the case of an older format without the metadata wrapper
        return loaded_data
    except (json.JSONDecodeError, IOError) as e:
        # If there's an error loading the file, log it and return an empty dict
        print(f"Error loading data from {file_path}: {str(e)}")
        return {} 