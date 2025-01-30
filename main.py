"""Main entry point for Ollama Models Manager CLI application."""

import argparse
import sys

from models import get_models_data
from utils import validate_directories
from cli import run, show_models_list

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
    show_only = args.show
    ignore_to_dir= action == "delete" or show_only
        
    # Validate directories
    try:
        from_dir, to_dir = validate_directories(from_dir, to_dir, ignore_to_dir)
    except Exception as e:
        print(f"Error validating directories: {e}")
        sys.exit(1)
        
    # Handle show command
    if show_only:
        print(f"\nShowing models found in {from_dir}\n")
        models = get_models_data(from_dir)
        show_models_list(models)
        sys.exit(0)
        
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
