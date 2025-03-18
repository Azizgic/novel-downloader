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

1. Use it **legally and ethically**.
2. Respect **privacy** and **intellectual property rights**.
3. Obtain proper **authorization** before scraping or downloading content.

The developers are **not liable** for misuse or damages. Use responsibly.

## Installation

Follow these steps to install the Novel Downloader:

1. Update your package lists:
    ```bash
    apt update & apt upgrade
    ```
2. Clone the repository:
    ```bash
    git clone https://github.com/Azizgic/novel-downloader.git
    cd novel-downloader
    ```
3. Install Python 3:
    ```bash
    apt install python3
    ```
4. Install required packages:
    ```bash
    pip install -r requirements.txt
    pip install -e .
    ```

## Usage

### Run the tool
```bash
novel-downloader --help
```
### Download a novel
``` bash
novel-downloader https://example.com/novelA -o novelA_output 
 ```

# Features

Resume downloads

Concurrent downloads

Multiple novel support

User-friendly CLI
