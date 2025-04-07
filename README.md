# Ollama Models Manager

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python-based utility for managing [Ollama](https://ollama.com) models, allowing you to easily copy, move, and delete models between your local installation and external storage.

## Goals

- Help manage and backup Ollama models when system space is limited
- Simplify the process of copying, moving, and deleting models
- Make it easy to transfer models between different systems

## Features

- Copy/move models from local installation to external storage
- Transfer models between external drives or folders
- Delete models from local installation or external storage
- Manage models within the local installation
- Safe deletion that preserves shared layers between models

## Requirements

- Python 3.x (uses standard library only, no additional dependencies needed)
- Ubuntu-based Linux system (tested on Ubuntu, Pop!_OS)
- Ollama installation is only required if you plan to interact with your local Ollama models
  - Not needed for managing models between external drives/folders

## Usage

```bash
python main.py [options]

Options:
  --from DIR           Source directory (must end in 'models/')
                      Default: /usr/share/ollama/.ollama/models/
  --to DIR            Target directory (must end in 'models/')
                      Default: /usr/share/ollama/.ollama/models/
  --action {copy,delete,move}
                      Action to perform (default: copy)
  --all               Process all models
  --models MODEL [MODEL ...]
                      List of specific models to process
  --always-replace    Always replace existing files
  --show              Show all models available in the source directory
```

### Example Commands

Show available models in local Ollama installation:
```bash
# Both commands are equivalent (no sudo needed for viewing)
python main.py --show
python main.py --from /usr/share/ollama/.ollama/models/ --show
```

Show available models in external storage:
```bash
python main.py --from /path/to/backup/models/ --show
```

#### Managing Local Ollama Models

Copy a specific model from local installation to external storage:
```bash
# Both commands are equivalent (no sudo needed when copying from local)
python main.py --to /path/to/backup/models/ --models llama2
python main.py --from /usr/share/ollama/.ollama/models/ --to /path/to/backup/models/ --models llama2
```

Copy a specific model to local installation (requires sudo):
```bash
# Both commands are equivalent
sudo python main.py --from /path/to/backup/models/ --models llama2
sudo python main.py --from /path/to/backup/models/ --to /usr/share/ollama/.ollama/models/ --models llama2
```

Move all models to external storage:
```bash
# Both commands are equivalent (sudo needed as this modifies local installation)
sudo python main.py --to /path/to/backup/models/ --action move --all
sudo python main.py --from /usr/share/ollama/.ollama/models/ --to /path/to/backup/models/ --action move --all
```

Delete a model from local installation:
```bash
# Both commands are equivalent (sudo needed as this modifies local installation)
sudo python main.py --action delete --models mistral
sudo python main.py --action delete --from /usr/share/ollama/.ollama/models/ --models mistral
```

#### Managing Models Between External Locations (no sudo required)

Copy specific models between external drives:
```bash
python main.py --from /media/drive1/models/ --to /media/drive2/models/ --models llama2 mistral
```

Move all models from one folder to another:
```bash
python main.py --from /backup/old/models/ --to /backup/new/models/ --action move --all
```

Delete models from external storage:
```bash
python main.py --action delete --from /path/to/backup/models/ --models codellama
```

Show models on external drive:
```bash
python main.py --from /media/external/models/ --show
```

## ⚠️ Important Notes and Warnings

1. **Administrative Privileges**
   - Admin/sudo privileges are ONLY required when modifying the local Ollama installation
   - No sudo needed for:
     - Viewing models (--show)
     - Copying models from local installation (if permissions are not restricted)
     - Any operations between external drives/folders (unless permissions are restricted)
   - Sudo required for:
     - Moving models from local installation
     - Deleting models from local installation
     - Copying/Moving models to local installation

2. **Model Deletion**
   - Models copied/moved to local Ollama installation should be removable via `ollama rm <model_name>`
   - Use this script with `--action=delete` to remove models in case `ollama rm` fails
   - Delete operations only affect models in the `--from` directory
   - The script preserves layers shared between models during deletion

3. **Compatibility**
   - Limited testing with multimodal (image+text) models
   - Designed and tested for Ubuntu-based systems only
   - Not tested on other Linux distributions or operating systems

4. **Disclaimer**
   - Use this script at your own risk
   - I am not responsible for any damage to your system
   - Not affiliated with Ollama.ai or any of its affiliates

## What It Doesn't Do

- Does not install Ollama
- Does not download models (no internet connectivity required)
- Does not modify model configurations

## Roadmap

- [ ] Web-based UI (simple HTTP server with HTML interface)
- [ ] Orphaned layer detection and cleanup
- [ ] Extended platform support
- [ ] Multimodal model testing and validation

## Contributing

Contributions are welcome! Here's how you can help:

1. Create an Issue
   - Explain the bug or feature you want to work on
   - Discuss implementation details if needed

2. Fork and Create PR
   - Fork the repository
   - Create your branch using the format:
     - For features: `feature/[ISSUE_ID]-[description]` (e.g., `feature/1-ui_html`)
     - For fixes: `fix/[ISSUE_ID]-[description]` (e.g., `fix/2-typo_fix`)
   - Commit your changes
   - Push to your branch
   - Open a Pull Request targeting the `main` branch referencing the Issue

## Issues

If you encounter any problems or have suggestions:

1. Check existing issues first
2. Open a new issue with:
   - Clear description of the problem
   - Steps to reproduce
   - Expected behavior
   - System information

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Thanks to the Ollama team for their amazing work
