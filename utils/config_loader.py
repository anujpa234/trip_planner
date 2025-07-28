import yaml
import os
from pathlib import Path


def load_config(config_path: str = "config/config.yaml") -> dict:
    """
    Load configuration from a YAML file.
    
    Args:
        config_path (str): Path to the config file, relative to project root
        
    Returns:
        dict: Loaded configuration data
        
    Raises:
        FileNotFoundError: If the config file doesn't exist
        yaml.YAMLError: If the YAML file is malformed
    """
    # Get the project root directory (parent of utils directory)
    current_dir = Path(__file__).parent
    project_root = current_dir.parent
    full_config_path = project_root / config_path
    
    try:
        with open(full_config_path, "r") as file:
            config = yaml.safe_load(file)
        print(f"✅ Successfully loaded config from: {full_config_path}")
        return config
    except FileNotFoundError:
        print(f"❌ Error: Config file not found at: {full_config_path}")
        raise
    except yaml.YAMLError as e:
        print(f"❌ Error: Invalid YAML format in config file: {e}")
        raise
    except Exception as e:
        print(f"❌ Unexpected error loading config: {e}")
        raise


if __name__ == "__main__":
    # Test the config loader when run directly
    try:
        config = load_config("config/config.yaml")
        print("\n📋 Loaded Configuration:")
        print("=" * 50)
        
        # Pretty print the config
        import json
        print(json.dumps(config, indent=2))
        
    except Exception as e:
        print(f"Failed to load configuration: {e}")
