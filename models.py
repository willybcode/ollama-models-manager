"""Model management functionality for Ollama Manager."""

import os
import json
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

from utils import path_check

@dataclass
class ModelInfo:
    """Data class for model information."""
    namespace: str
    model: str
    version: str
    path: str
    model_name: str
    hashes: Optional[List[str]] = None

def find_models(internal_dir: str) -> List[ModelInfo]:
    """Find all models in the given directory.
    
    Args:
        internal_dir: Directory containing Ollama models
        
    Returns:
        List[ModelInfo]: List of found models
        
    Raises:
        SystemExit: If no models or namespaces found
    """
    namespaces = None
    models = []
    
    manifest_path = os.path.join(internal_dir, "manifests/registry.ollama.ai/")
    if not path_check(manifest_path):
        print(f"Could not find manifests directory in {internal_dir}")
        exit(1)
        
    namespaces = os.listdir(manifest_path)
    if not namespaces:
        print("No namespaces found")
        exit(1)
        
    total = 0
    for namespace in namespaces:
        namespace_path = os.path.join(manifest_path, namespace)
        for model in os.listdir(namespace_path):
            model_path = os.path.join(namespace_path, model)
            for version in os.listdir(model_path):
                ns = "" if namespace == "library" else f"{namespace}/"
                model_name = f"{ns}{model}:{version}"
                models.append(ModelInfo(
                    namespace=namespace,
                    model=model,
                    version=version,
                    path=os.path.join(model_path, version),
                    model_name=model_name
                ))
                total += 1
                
    if total == 0:
        print(f"No models found in {internal_dir}")
        exit(1)
        
    print(f"Namespaces: {namespaces}")
    print(f"Total models: {total}")
    return models

def show_models_list(models: List[ModelInfo]) -> None:
    """Display list of models in a formatted way.
    
    Args:
        models: List of ModelInfo objects to display
    """
    print("\nModels found:\n")
    for i, model in enumerate(models, 1):
        print(f"{i}. {model.model_name}")

def get_all_hashes(internal_dir: str) -> List[ModelInfo]:
    """Get all file hashes for models in the directory.
    
    Args:
        internal_dir: Directory containing Ollama models
        
    Returns:
        List[ModelInfo]: List of models with their associated hashes
        
    Raises:
        SystemExit: If no models or namespaces found
    """
    models = []
    manifest_path = os.path.join(internal_dir, "manifests/registry.ollama.ai/")
    
    if not path_check(manifest_path):
        print(f"Could not find manifests directory in {internal_dir}")
        exit(1)
        
    namespaces = os.listdir(manifest_path)
    if not namespaces:
        print("No namespaces found")
        exit(1)
        
    total_models = 0
    total_hashes = 0
    
    for namespace in namespaces:
        namespace_path = os.path.join(manifest_path, namespace)
        for model in os.listdir(namespace_path):
            model_path = os.path.join(namespace_path, model)
            for version in os.listdir(model_path):
                ns = "" if namespace == "library" else f"{namespace}/"
                model_name = f"{ns}{model}:{version}"
                version_path = os.path.join(model_path, version)
                
                try:
                    with open(version_path, 'r') as f:
                        manifest_data = json.load(f)
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Error reading manifest for {model_name}: {e}")
                    continue
                    
                hashes = []
                config_hash = manifest_data["config"]["digest"].replace(":", "-")
                hashes.append(config_hash)
                total_hashes += 1
                
                for layer in manifest_data["layers"]:
                    layer_hash = layer["digest"].replace(":", "-")
                    hashes.append(layer_hash)
                    total_hashes += 1
                    
                models.append(ModelInfo(
                    namespace=namespace,
                    model=model,
                    version=version,
                    path=version_path,
                    model_name=model_name,
                    hashes=hashes
                ))
                total_models += 1
                
    if total_models == 0:
        print(f"No models found in {internal_dir}")
        exit(1)
        
    print(f"Namespaces: {namespaces}")
    print(f"Total models: {total_models}")
    print(f"Total hashes: {total_hashes}")
    return models
