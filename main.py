"""Main entry point for Ollama Models Manager CLI application."""

import argparse
import sys
from typing import List, Optional

from models import find_models
from utils import exist_path_check
from cli import run, Action

# Default installation directory for Ollama
LOCAL_INSTALL_DIR = "/usr/share/ollama/.ollama/models/"

def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser.
    
    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description="Ollama Models Manager - Tool for managing Ollama models",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "--from",
        default=LOCAL_INSTALL_DIR,
        type=str,
        help=f"Source directory (must end in 'models/')"
    )
    
    parser.add_argument(
        "--to",
        default=LOCAL_INSTALL_DIR,
        type=str,
        help=f"Target directory (must end in 'models/')"
    )
    
    parser.add_argument(
        "--action",
        default="copy",
        choices=['copy', 'delete', 'move'],
        help="Action to perform"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all models"
    )
    
    parser.add_argument(
        "--models",
        default=[],
        nargs='+',
        help="List of models to process (space-separated)"
    )
    
    parser.add_argument(
        "--always-replace",
        action="store_true",
        help="Always replace existing files"
    )
    
    parser.add_argument(
        "--show",
        action="store_true",
        help="Show all models available in the source directory"
    )
    
    return parser

def validate_directories(from_dir: str, to_dir: str, action: str) -> None:
    """Validate source and target directories.
    
    Args:
        from_dir: Source directory
        to_dir: Target directory
        action: Action to perform
        
    Raises:
        SystemExit: If directories are invalid
    """
    # Ensure directories end with trailing slash
    from_dir = from_dir if from_dir.endswith("/") else f"{from_dir}/"
    to_dir = to_dir if to_dir.endswith("/") else f"{to_dir}/"
    
    if action != "delete" and from_dir == to_dir:
        print("Error: Source and Target directories are the same")
        sys.exit(1)
        
    # Validate directory names
    if not from_dir.endswith("models/"):
        print(f"Error: Source directory {from_dir} must end in 'models/'")
        sys.exit(1)
        
    if not to_dir.endswith("models/"):
        print(f"Error: Target directory {to_dir} must end in 'models/'")
        sys.exit(1)
        
    # Check if directories exist
    exist_path_check(from_dir)
    exist_path_check(to_dir)
    
    return from_dir, to_dir

def main() -> None:
    """Main entry point for the application."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Extract arguments
    action = args.action
    from_dir = getattr(args, "from")
    to_dir = args.to
    all_models = args.all
    target_models = args.models
    always_replace = args.always_replace
    
    # Handle show command
    if args.show:
        print(f"\nShowing models found in {from_dir}\n")
        models = find_models(from_dir)
        from cli import show_models_list
        show_models_list(models)
        sys.exit(0)
        
    # Validate directories
    try:
        from_dir, to_dir = validate_directories(from_dir, to_dir, action)
    except Exception as e:
        print(f"Error validating directories: {e}")
        sys.exit(1)
        
    # Validate arguments
    if all_models and target_models:
        print("Error: Cannot use --all and --models together")
        sys.exit(1)
        
    # Run main operation
    try:
        run(action, from_dir, to_dir, all_models, target_models, always_replace)
    except Exception as e:
        print(f"Error running operation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
