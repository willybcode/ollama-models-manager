"""Utility functions for the Ollama Manager."""

import os
import math
import re
from typing import Union, Optional

def path_check(path: str) -> bool:
    """Check if a path exists.
    
    Args:
        path: Path to check
        
    Returns:
        bool: True if path exists, False otherwise
    """
    return os.path.exists(path)

def exist_path_check(path: str) -> None:
    """Check if a path exists and exit if it doesn't.
    
    Args:
        path: Path to check
        
    Raises:
        SystemExit: If path doesn't exist
    """
    if not path_check(path):
        print(f"{path} does not exist")
        exit(1)

def validate_input(user_input: str) -> str:
    """Remove spaces and validate input format.
    
    Args:
        user_input: User input string containing numbers and commas
        
    Returns:
        str: Validated input string
        
    Raises:
        ValueError: If input contains invalid characters
    """
    user_input = user_input.replace(" ", "")
    if not re.match("^[0-9,]+$", user_input):
        raise ValueError("Invalid input. Please enter only digits and commas.")
    return user_input 

def validate_selection_range(user_input: str, max_value: int) -> Optional[str]:
    """Validate if all numbers in selection are within valid range.
    
    Args:
        user_input: Comma-separated string of numbers
        max_value: Maximum allowed value
        
    Returns:
        Optional[str]: Validated input string or None if invalid
    """
    for num in user_input.split(','):
        if not 1 <= (num := int(num)) <= max_value:
            print(f"\nError: Invalid selection '{num}'. Please try again.")
            return None
    return user_input

def pretty_print_size(size_bytes: Union[int, float]) -> str:
    """Convert bytes to human readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        str: Human readable size string (e.g., "1.5 GB")
    """
    if size_bytes == 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1000)))
    p = math.pow(1000, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"
