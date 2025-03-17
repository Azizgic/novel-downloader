from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="novel-downloader",
    version="1.0.0",
    author="Azizgic",
    author_email="azizgichki3@gmail.com",
    description="A Python tool to download novels from the web.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Azizgic/novel-downloader",
    packages=find_packages(),
    install_requires=[
        "aiohttp",
        "beautifulsoup4",
        "tqdm",
        "colorama",
    ],
    entry_points={
        "console_scripts": [
            "novel-downloader=novel_downloader.downloader:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
