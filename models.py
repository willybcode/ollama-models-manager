"""Model management functionality for Ollama Manager."""

import os
import json
from typing import List, Optional
from dataclasses import dataclass

from utils import path_check, pretty_print_size

@dataclass
class ModelInfo:
    """Data class for model information."""
    namespace: str
    model: str
    version: str
    path: str
    model_name: str
    hashes: Optional[List[str]] = None
    model_size: Optional[int] = None

def show_models_list(models: List[ModelInfo]) -> None:
    """Display list of models in a formatted way.

    Args:
        models: List of ModelInfo objects to display
    """
    print("\nModels found:\n")
    max_length = max(len(model.model_name) for model in models)
    max_index_length = len(str(len(models)))
    for i, model in enumerate(models, 1):
        index_str = str(i).rjust(max_index_length)
        model_name = model.model_name.ljust(max_length+2)
        print(f"{index_str}. {model_name} {pretty_print_size(model.model_size)}")


def get_models_data(internal_dir: str,muted: bool = False) -> List[ModelInfo]:
    """Find all models and data in the directory.
    
    Args:
        internal_dir: Directory containing Ollama models
        
    Returns:
        List[ModelInfo]: List of models with their associated data
        
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
    total_size = 0
    known_hashes = set()
    deduplicate_size = 0
    
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
                if config_hash in known_hashes:
                    deduplicate_size += manifest_data["config"]["size"]
                else:
                    known_hashes.add(config_hash)
                total_hashes += 1
                model_size = manifest_data["config"]["size"]
                
                for layer in manifest_data["layers"]:
                    layer_hash = layer["digest"].replace(":", "-")
                    if layer_hash in known_hashes:
                        deduplicate_size += layer["size"]
                    else:
                        known_hashes.add(layer_hash)
                    model_size += layer["size"]
                    hashes.append(layer_hash)
                    total_hashes += 1
                    
                models.append(ModelInfo(
                    namespace=namespace,
                    model=model,
                    version=version,
                    path=version_path,
                    model_name=model_name,
                    hashes=hashes,
                    model_size=model_size
                ))
                total_models += 1
                total_size += model_size
    total_size -= deduplicate_size
    if total_models == 0:
        print(f"No models found in {internal_dir}")
        exit(1)
        
    if not muted:
        print(f"Namespaces: {namespaces}")
        print(f"Total models: {total_models}")
        print(f"Total hashes: {total_hashes}")
        print(f"Total size: (approx) {pretty_print_size(total_size)}")
        
    return models
