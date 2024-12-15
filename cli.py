"""Command-line interface for Ollama Models Manager."""

from typing import List, Optional
from enum import Enum, auto

from utils import exist_path_check, validate_input, validate_selection_range
from models import find_models, show_models_list, get_all_hashes, ModelInfo
from operations import copy_model, delete_model, move_model

class Action(Enum):
    """Supported actions for model management."""
    COPY = auto()
    DELETE = auto()
    MOVE = auto()
    
    @classmethod
    def from_str(cls, value: str) -> 'Action':
        """Convert string to Action enum.
        
        Args:
            value: String value of action
            
        Returns:
            Action: Corresponding Action enum value
            
        Raises:
            ValueError: If value is not a valid action
        """
        try:
            return {
                "copy": cls.COPY,
                "delete": cls.DELETE,
                "move": cls.MOVE
            }[value.lower()]
        except KeyError:
            raise ValueError(f"Invalid action: {value}")

def get_user_choice(choices: List[str], choice_text: str) -> str:
    """Get user choice for prompts.
    
    Args:
        choices: List of valid choices
        choice_text: Text to display for choice prompt
        
    Returns:
        str: User's validated choice
    """
    while True:
        prompt_choice = input(choice_text).strip().upper()
        if prompt_choice in choices:
            return prompt_choice
        print("\nInvalid choice. Please try again.")

def get_target_models(models: List[ModelInfo], action: str) -> List[str]:
    """Get list of target models from user input.
    
    Args:
        models: List of available models
        action: Action to perform on models
        
    Returns:
        List[str]: List of selected model names
    """
    print("\nWhat would you like to do?")
    user_choice = get_user_choice(
        ['A', 'B'],
        f"A) {action} all models\nB) Select models to {action}\n\n>> "
    )
    
    if user_choice == 'A':
        return [model.model_name for model in models]
    
    show_models_list(models)
    print(f"\nWhich models do you want to {action}?")
    user_input = input("\nEnter a comma separated list of model numbers to use (e.g., 1,2,3):\n\n>> ")
    print(f"You have chosen {user_input}")
    
    try:
        user_input = validate_input(user_input)
        if not validate_selection_range(user_input, len(models)):
            return []
        return [models[int(i)-1].model_name for i in user_input.split(',')]
    except ValueError as e:
        print(f"\nError: {e}")
        return []

def run(
    action: str,
    from_dir: str,
    to_dir: str,
    all_models: bool,
    target_models: List[str],
    always_replace: bool
) -> None:
    """Run the main CLI operation.
    
    Args:
        action: Action to perform (copy, delete, move)
        from_dir: Source directory
        to_dir: Destination directory
        all_models: Whether to process all models
        target_models: List of specific models to process
        always_replace: Whether to always replace existing files
    """
    # Validate directories
    exist_path_check(from_dir + "blobs")
    exist_path_check(from_dir + "manifests")
    
    # Get available models
    models = find_models(from_dir)
    
    # Get target models if not specified
    if not all_models and not target_models:
        target_models = get_target_models(models, action)
        if not target_models:
            return
            
    # Use all models if specified
    if all_models:
        target_models = [model.model_name for model in models]
    
    # Add :latest tag if version not specified
    target_models = [
        model_name if ":" in model_name else f"{model_name}:latest"
        for model_name in target_models
    ]
    
    # Find matching models
    found_models = [
        model for model in models
        if model.model_name in target_models
    ]
    
    if not found_models:
        print("\nNo models found matching your selection. Please try again.")
        return
        
    # Get all hashes if needed
    all_hashes = None
    if action in ["delete", "move"]:
        all_hashes = get_all_hashes(from_dir)
        
    # Process each model
    try:
        action_enum = Action.from_str(action)
        for model in found_models:
            if action_enum == Action.COPY:
                copy_model(from_dir, to_dir, model, always_replace)
            elif action_enum == Action.DELETE:
                delete_model(from_dir, model, all_hashes)
            elif action_enum == Action.MOVE:
                move_model(from_dir, to_dir, model, all_hashes, always_replace)
    except Exception as e:
        print(f"Error processing models: {e}")
        return