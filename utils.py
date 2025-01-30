"""Utility functions for the Ollama Manager."""

import os
import math
import re
import sys
from typing import Union, Optional
import shutil

def trailing_slash(dir: str) -> str:
    return dir if dir.endswith("/") else f"{dir}/"

def abs_path(path: str) -> str:
    return os.path.abspath(path)

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

def validate_directories(from_dir: str, to_dir: str, ignore_to_dir: bool) -> None:
    """Validate source and target directories.
    
    Args:
        from_dir: Source directory
        to_dir: Target directory
        ignore_to_dir: Whether to ignore target directory
        
    Raises:
        SystemExit: If directories are invalid
    """
    # Ensure directories end with trailing slash
    from_dir = trailing_slash(from_dir)
    to_dir = trailing_slash(to_dir)
    
    if not from_dir.endswith("models/"):
        print(f"Error: Source directory {from_dir} must end in 'models/'")
        sys.exit(1)
    exist_path_check(from_dir)
    from_abs= abs_path(from_dir)
    show_disk_space(from_abs)
    
    if not ignore_to_dir:
        if from_dir == to_dir:
            print("Error: Source and Target directories are the same")
            sys.exit(1)
        if not to_dir.endswith("models/"):
            print(f"Error: Target directory {to_dir} must end in 'models/'")
            sys.exit(1)
        exist_path_check(to_dir)
        to_abs= abs_path(to_dir)
        
        # Check if absolute paths are the same
        if from_abs == to_abs:
            print("Error: Source and Target paths are the same")
            sys.exit(1)
        to_dir= trailing_slash(to_abs)
        show_disk_space(to_abs)
        
    from_dir= trailing_slash(from_abs)
    return from_dir, to_dir    

def show_disk_space(path):
    try :
        total, used, free = shutil.disk_usage(path)
        
        # Convert to base 10 (GB)
        total_space = total / 1000**3
        used_space = used / 1000**3
        free_space = free / 1000**3
        
        # # Convert to base 2 (GiB)
        # total_space = total / 1024**3
        # used_space = used / 1024**3
        # free_space = free / 1024**3
        
        print(f"Disk space info for {path}:")
        # print("+--------------+----------------+")
        # print("| Property     |     Value      |")
        print("+--------------+----------------+")
        print(f"| Total        | {total_space:11.2f} GB |")
        # print(f"| Used         | {used_space:11.2f} GB |")
        print(f"| Free(usable) | {free_space:11.2f} GB |")
        print("+--------------+----------------+")
    except OSError:
        print(f"Error accessing {path}")
        return
    except PermissionError:
        print(f"Permission denied for {path}")
        return