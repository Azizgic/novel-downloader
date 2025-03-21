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
    """Downloader with resume capability and caching for multiple novels"""
    
    def __init__(self, config: dict, entry_url: str):
        self.config = config
        self.entry_url = entry_url
        self.state_file = '.novel_downloads_state.json'
        self.novel_id = hashlib.md5(entry_url.encode()).hexdigest()
        self.processed_urls = set()
        self.current_url = entry_url
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}
        self.session = None
        self._load_state()

    def _load_state(self):
        """Load state for the current novel from the shared state file"""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                state = json.load(f)
                if self.novel_id in state:
                    novel_state = state[self.novel_id]
                    self.processed_urls = set(novel_state.get('processed', []))
                    self.current_url = novel_state.get('current_url', self.entry_url)
                    if 'output_dir' in novel_state:
                        self.config['output'] = novel_state['output_dir']

    def _save_state(self):
        """Save state for the current novel to the shared state file"""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                state = json.load(f)
        else:
            state = {}

        state[self.novel_id] = {
            'processed': list(self.processed_urls),
            'output_dir': self.config['output'],
            'current_url': self.current_url,
            'entry_url': self.entry_url  # Store entry URL for display in resume menu
        }

        with open(self.state_file, 'w') as f:
            json.dump(state, f)

    def _cleanup_state(self):
        """Remove the current novel's state if the download is complete"""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                state = json.load(f)
            if self.novel_id in state:
                del state[self.novel_id]
                with open(self.state_file, 'w') as f:
                    json.dump(state, f)

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, *exc):
        await self.session.close()

    async def fetch(self, url: str) -> str:
        """Fetch content with retries and timeout"""
        if url in self.processed_urls:
            return ""
        
        retries = 3
        timeout = aiohttp.ClientTimeout(total=30)
        for attempt in range(retries):
            try:
                async with self.session.get(url, timeout=timeout) as response:
                    response.raise_for_status()
                    return await response.text()
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt < retries - 1:
                    wait = 2 ** attempt
                    print(Fore.YELLOW + f"Retrying ({attempt+1}/{retries}) {url} in {wait}s...")
                    await asyncio.sleep(wait)
                else:
                    print(Fore.RED + f"Failed to fetch {url}: {str(e)}")
                    raise
        return ""

    async def process_chapter(self, url: str):
        """Process and save a single chapter"""
        content = await self.fetch(url)
        soup = BeautifulSoup(content, 'lxml')
        title = re.sub(r'[\\/*?:"<>|]', '', soup.title.string).strip()[:80] if soup.title else "untitled"
        
        # Save chapter content
        path = os.path.join(self.config['output'], f"{title}.html")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.processed_urls.add(url)
        return self.find_next_url(soup, url)

    def find_next_url(self, soup: BeautifulSoup, base: str) -> str:
        """Find next chapter URL"""
        for selector in ['a[rel=next]', '#next_chap', '.next', 'link[rel=next]',  
                 '.next-chapter', '#nextChapter', '.chapter-next', '#next_chap',  
                 '.chap-next', '.next-episode', '#next-episode', '.episode-next']:  
            if link := soup.select_one(selector):
                return urljoin(base, link['href'])
        return None

    async def run(self):
        """Main processing pipeline"""
        current_url = self.current_url
        pbar = tqdm(desc="Downloading", unit="chap", colour="green")
        
        try:
            while current_url:
                next_url = await self.process_chapter(current_url)
                self.current_url = next_url
                self._save_state()
                pbar.update(1)
                current_url = next_url if next_url and next_url not in self.processed_urls else None
        finally:
            pbar.close()
            # Cleanup state if download completes fully
            if not current_url:
                self._cleanup_state()

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

def list_incomplete_downloads():
    """List all incomplete downloads from the state file"""
    if os.path.exists('.novel_downloads_state.json'):
        with open('.novel_downloads_state.json', 'r') as f:
            state = json.load(f)
        
        if not state:
            print(Fore.YELLOW + "No incomplete downloads found.")
            return

        print(Fore.GREEN + "Incomplete downloads:")
        for i, (novel_id, novel_state) in enumerate(state.items()):
            print(f"{i + 1}. {novel_state['entry_url']} (Output: {novel_state['output_dir']})")
    else:
        print(Fore.YELLOW + "No previous downloads found.")

def clean_state_file():
    """Remove completed or stale entries from the state file"""
    if os.path.exists('.novel_downloads_state.json'):
        with open('.novel_downloads_state.json', 'r') as f:
            state = json.load(f)
        
        # Remove entries with no current URL (completed downloads)
        state = {k: v for k, v in state.items() if v.get('current_url')}
        
        with open('.novel_downloads_state.json', 'w') as f:
            json.dump(state, f)
        print(Fore.GREEN + "State file cleaned.")
    else:
        print(Fore.YELLOW + "No state file found.")

def delete_novel_state(novel_id: str):
    """Remove a specific novel's state from the state file"""
    if os.path.exists('.novel_downloads_state.json'):
        with open('.novel_downloads_state.json', 'r') as f:
            state = json.load(f)
            
            statel = list(state.copy().items())
        if len(statel) > int(novel_id)-1:
            del statel[int(novel_id) - 1]
            with open('.novel_downloads_state.json', 'w') as f:
                json.dump(dict(statel), f)
            print(Fore.GREEN + f"Deleted state for novel ID: {novel_id}")
        else:
            print(Fore.YELLOW + f"No state found for novel ID: {novel_id}")
    else:
        print(Fore.YELLOW + "No state file found.")

def main():
    """Entry point for the CLI tool"""
    config = parse_args()
    asyncio.run(main_logic(config))

if __name__ == "__main__":
    main()
