import aiohttp
import asyncio
from bs4 import BeautifulSoup
import os
import re
from urllib.parse import urljoin
from tqdm import tqdm
import json
from colorama import Fore, Style, init
import argparse
import hashlib
import configparser

# Initialize colorama
init(autoreset=True)

# Configuration setup
CONFIG_FILE = os.path.expanduser('~/.noveldownloaderrc')

class ConfigManager:
    @staticmethod
    def get_default_dir():
        """Get the default directory from config file"""
        config = configparser.ConfigParser()
        if os.path.exists(CONFIG_FILE):
            config.read(CONFIG_FILE)
            return os.path.expanduser(config.get('DEFAULT', 'directory', fallback=''))
        return ''

    @staticmethod
    def set_default_dir(path):
        """Save default directory to config file"""
        try:
            config = configparser.ConfigParser()
            config['DEFAULT'] = {'directory': os.path.expanduser(path)}
            with open(CONFIG_FILE, 'w') as f:
                config.write(f)
            print(Fore.GREEN + f"Default directory set to: {os.path.expanduser(path)}")
            return True
        except Exception as e:
            print(Fore.RED + f"Failed to save config: {str(e)}")
            return False

class NovelDownloader:
    # [Keep the existing NovelDownloader class exactly as original]
    # ... (all original methods unchanged)

def parse_args():
    """Argument parsing with original style"""
    parser = argparse.ArgumentParser(description='High-performance novel downloader', add_help=True)
    parser.add_argument('urls', nargs='*', help='Input URL(s) (novel or TOC page)')
    parser.add_argument('-o', '--output', help='Output directory/name')
    parser.add_argument('--set-default-dir', metavar='PATH', help='Set default output directory')
    parser.add_argument('--list', action='store_true', help='List incomplete downloads')
    parser.add_argument('--clean', action='store_true', help='Clean the state file')
    parser.add_argument('--delete', help='Delete state for a specific novel ID')
    return vars(parser.parse_args())

def handle_output_path(output: str) -> str:
    """Handle output path with default directory logic"""
    default_dir = ConfigManager.get_default_dir()
    
    if not output:
        if not default_dir:
            print(Fore.RED + "No default directory set! Use --set-default-dir first.")
            raise SystemExit(1)
        return os.path.expanduser(default_dir)
    
    output = os.path.expanduser(output)
    
    # If output is just a name (no path separators)
    if not os.path.splitdrive(output)[0] and not os.path.sep in output:
        if not default_dir:
            print(Fore.RED + "No default directory set! Use --set-default-dir first.")
            print(Fore.YELLOW + "Either set a default directory or provide a full path")
            raise SystemExit(1)
        return os.path.join(os.path.expanduser(default_dir), output)
    
    return output

async def main_logic(config):
    """Main logic for the CLI tool"""
    # Handle set-default-dir first
    if config['set_default_dir']:
        success = ConfigManager.set_default_dir(config['set_default_dir'])
        if not success:
            raise SystemExit(1)
        return

    # Handle output path
    if config['output']:
        config['output'] = handle_output_path(config['output'])
    else:
        config['output'] = handle_output_path('')

    # Rest of original logic
    if config['list']:
        list_incomplete_downloads()
        return
    elif config['clean']:
        clean_state_file()
        return
    elif config['delete']:
        delete_novel_state(config['delete'])
        return

    if not config['urls']:
        # Original resume logic
        if os.path.exists('.novel_downloads_state.json'):
            with open('.novel_downloads_state.json', 'r') as f:
                state = json.load(f)
            
            if not state:
                print(Fore.YELLOW + "No incomplete downloads found.")
                return

            print(Fore.GREEN + "Incomplete downloads found. Choose one to resume:")
            novels = list(state.items())
            for i, (novel_id, novel_state) in enumerate(novels):
                print(f"{i + 1}. {novel_state['entry_url']} (Output: {novel_state['output_dir']})")

            choice = int(input("Enter the number of the download to resume: ")) - 1
            selected_novel_id, selected_state = novels[choice]
            config['urls'] = [selected_state['current_url']]
            config['output'] = selected_state['output_dir']
            print(Fore.GREEN + f"Resuming download from: {selected_state['current_url']}")
        else:
            print(Fore.YELLOW + "No previous downloads found. Please provide URLs.")
            return

    async with NovelDownloader(config, config['urls'][0]) as downloader:
        await downloader.run()

# [Keep all remaining helper functions identical to original]
# list_incomplete_downloads(), clean_state_file(), delete_novel_state(), main()

def main():
    """Entry point for the CLI tool"""
    config = parse_args()
    asyncio.run(main_logic(config))

if __name__ == "__main__":
    main()
