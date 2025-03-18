# Novel Downloader  

A high-performance Python tool to download novels from the web.  

## Table of Contents  
1. [Disclaimer](#disclaimer)  
2. [Installation](#installation)  
3. [Usage](#usage)  
4. [Features](#features)  
5. [Contributing](#contributing)  
6. [License](#license)  
7. [Contact](#contact)  

## Disclaimer  

This software is intended **solely for educational purposes**. By using it, you agree to:  

- Use it **legally and ethically**.  
- Respect **privacy** and **intellectual property rights**.  
- Obtain proper **authorization** before scraping or downloading content.  

The developers are **not liable** for misuse or damages. Use responsibly.  

## Installation  

Follow these steps to install **Novel Downloader**:  

```sh  
# Update your package lists  
apt update && apt upgrade  

# Clone the repository  
git clone https://github.com/Azizgic/novel-downloader.git  
cd novel-downloader  

# Install Python 3 (if not installed)  
apt install python3  

# Install required dependencies  
pip install -r requirements.txt  

# Install the tool  
pip install -e .  
```  

## Usage  

### Display Help  
```sh  
novel-downloader --help  
```  

### Download a Novel  
```sh  
novel-downloader https://example.com/novelA -o novelA_output  
```

### Resume Download
```sh
novel-downloader
```
The tool will display a list of available novels that can be resumed. Simply enter the ID of the novel you want to continue downloading, and it will resume from where it left off.

## Features  

- **Resume downloads** – Continue from where you left off.  
- **Concurrent downloads** – Speeds up the process with multiple threads.  
- **Multiple novel support** – Download multiple novels simultaneously.  
- **User-friendly CLI** – Simple and easy-to-use command-line interface.  

## Contributing  

Contributions are welcome! Feel free to submit issues and pull requests.  

## License  

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.  

## Contact  

For questions or issues, reach out via [GitHub Issues](https://github.com/Azizgic/novel-downloader/issues).  
