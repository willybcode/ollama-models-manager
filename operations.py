"""Operations for managing Ollama models."""

import os
import json
import shutil
from typing import List, Dict, Any

from utils import path_check, pretty_print_size
from models import ModelInfo

def copy_model(from_dir: str, to_dir: str, model: ModelInfo, always_replace: bool) -> None:
    """Copy a model from source to destination directory.
    
    Args:
        from_dir: Source directory
        to_dir: Destination directory
        model: ModelInfo object containing model details
        always_replace: Whether to always replace existing files
        
    Raises:
        SystemExit: If manifest doesn't exist or permission denied
    """
    model_manifest = model.path
    if not path_check(model_manifest):
        print(f"{model_manifest} does not exist")
        exit(1)

    try:
        with open(model_manifest, 'r') as f:
            manifest_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error reading manifest: {e}")
        exit(1)

    if manifest_data["mediaType"] not in {
        "application/vnd.docker.distribution.manifest.v2+json",
        "application/vnd.docker.container.image.v1+json",
    }:
        print(f"Unsupported media type: {manifest_data['mediaType']}")
        exit(1)

    files_data = []
    # Add manifest file
    files_data.append({
        "is_manifest": True,
        "filename": os.path.basename(model.path),
        "filepath": model.path
    })
    
    # Add config file
    config_hash = manifest_data["config"]["digest"].replace(":", "-")
    files_data.append({
        "filename": config_hash,
        "is_manifest": False,
        "filepath": os.path.join(from_dir, "blobs", config_hash)
    })
    
    # Add layer files
    for layer in sorted(manifest_data["layers"], key=lambda x: x["size"], reverse=True):
        layer_hash = layer["digest"].replace(":", "-")
        files_data.append({
            "filename": layer_hash,
            "is_manifest": False,
            "filepath": os.path.join(from_dir, "blobs", layer_hash)
        })

    # Verify all files exist before copying
    for file in files_data:
        if not path_check(file["filepath"]):
            print(f"{file['filepath']} does not exist")
            print(f"Skipping model {model.model_name}")
            return

    print(f"Copying model {model.model_name}")
    
    for file in files_data:
        from_path = file["filepath"]
        to_path = os.path.join(to_dir, "blobs", file["filename"])
        
        if file["is_manifest"]:
            to_path = os.path.join(
                to_dir, "manifests/registry.ollama.ai",
                model.namespace, model.model, model.version
            )

        if path_check(to_path):
            if os.path.getsize(from_path) == os.path.getsize(to_path):
                if always_replace:
                    print(f"Replacing {to_path}")
                else:
                    print(f"Skipped: {file['filename']} ({pretty_print_size(os.path.getsize(from_path))}) already exists in destination.")
                    continue
            else:
                print(f"Soft Replacing {to_path}")

        os.makedirs(os.path.dirname(to_path), exist_ok=True)
        print(f" Copying: {file['filename']} {pretty_print_size(os.path.getsize(from_path))} ({os.path.getsize(from_path)} bytes)")
        
        try:
            shutil.copy(from_path, to_path)
        except PermissionError:
            print("Permission denied. Try running the script with admin privileges.")
            exit(1)
        except Exception as e:
            print(f"Error copying file: {e}")
            exit(1)

    print(f"Model {model.model_name} is copied to {to_dir}")

def delete_model(from_dir: str, model: ModelInfo, all_hashes: List[ModelInfo]) -> None:
    """Delete a model and its associated files.
    
    Args:
        from_dir: Source directory containing the model
        model: ModelInfo object containing model details
        all_hashes: List of all models and their hashes for reference checking
        
    Raises:
        SystemExit: If manifest doesn't exist or permission denied
    """
    # Filter out current model from all_hashes
    all_hashes = [h for h in all_hashes if h.model_name != model.model_name]

    if not path_check(model.path):
        print(f"{model.path} does not exist")
        exit(1)
    
    try:
        with open(model.path, 'r') as f:
            manifest_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error reading manifest: {e}")
        exit(1)

    files_data = []
    # Add manifest file
    files_data.append({
        "is_manifest": True,
        "filename": os.path.basename(model.path),
        "filepath": model.path
    })
    
    # Add config file
    config_hash = manifest_data["config"]["digest"].replace(":", "-")
    files_data.append({
        "filename": config_hash,
        "is_manifest": False,
        "filepath": os.path.join(from_dir, "blobs", config_hash)
    })
    
    # Add layer files
    for layer in manifest_data["layers"]:
        layer_hash = layer["digest"].replace(":", "-")
        files_data.append({
            "filename": layer_hash,
            "is_manifest": False,
            "filepath": os.path.join(from_dir, "blobs", layer_hash)
        })

    # Check permissions before deleting
    for file in files_data:
        from_path = file["filepath"]
        parent_dir = os.path.dirname(from_path)
        if not (os.access(from_path, os.W_OK) or 
                (os.access(parent_dir, os.R_OK | os.X_OK) and os.access(parent_dir, os.W_OK))):
            print(f"Permission denied: {from_path}")
            print("Lacking necessary permissions to delete all files. Exiting.")
            exit(1)

    # Delete files
    for file in files_data:
        from_path = file["filepath"]
        clone_list = []
        
        # Check if file is used by other models
        for h in all_hashes:
            if h.hashes and file["filename"] in h.hashes:
                clone_list.append(h.model_name)
                
        if clone_list:
            print(f"Skipped: {file['filename']} is also used by [{', '.join(clone_list)}]")
            continue
            
        try:
            os.remove(from_path)
            print(f"Deleted: {from_path}")
        except Exception as e:
            print(f"Error deleting {from_path}: {e}")

    # Delete empty manifest directory
    manifest_dir = os.path.dirname(model.path)
    try:
        if os.path.exists(manifest_dir) and not os.listdir(manifest_dir):
            os.rmdir(manifest_dir)
            print(f"Deleted empty directory: {manifest_dir}")
    except Exception as e:
        print(f"Error deleting directory {manifest_dir}: {e}")

    print(f"Deleted model {model.model_name}")

def move_model(from_dir: str, to_dir: str, model: ModelInfo, all_hashes: List[ModelInfo], always_replace: bool) -> None:
    """Move a model from source to destination directory.
    
    Args:
        from_dir: Source directory
        to_dir: Destination directory
        model: ModelInfo object containing model details
        all_hashes: List of all models and their hashes
        always_replace: Whether to always replace existing files
    """
    print(f"Moving model {model.model_name}")
    
    # First copy the model to new location
    copy_model(from_dir, to_dir, model, always_replace)
    
    # Then delete from original location
    delete_model(from_dir, model, all_hashes)
    
    print(f"Model {model.model_name} has been moved from {from_dir} to {to_dir}")
