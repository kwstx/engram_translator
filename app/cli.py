import os
import yaml
import sys
import argparse

def init_config():
    """Generates the initial config.yaml in ~/.engram/."""
    config_dir = os.path.expanduser("~/.engram/")
    os.makedirs(config_dir, exist_ok=True)
    
    config_path = os.path.join(config_dir, "config.yaml")
    
    config_content = {
        "model_provider": "openai",
        "base_url": "http://localhost:8000",
        "default_personality": "optimistic"
    }
    
    with open(config_path, "w") as f:
        yaml.dump(config_content, f, default_flow_style=False)
    
    print(f"Initialized Engram config at {config_path}")

def main():
    parser = argparse.ArgumentParser(description="Engram CLI tool.")
    subparsers = parser.add_subparsers(dest="command")
    
    # Init command
    subparsers.add_parser("init", help="Initialize configuration")
    
    args = parser.parse_args()
    
    if args.command == "init":
        init_config()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
