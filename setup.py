"""JARVIS setup configuration."""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="jarvis-assistant",
    version="0.1.0",
    author="Jeremy",
    description="An intelligent voice assistant with advanced capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/jarvis",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.10",
        "Topic :: Desktop Environment :: Desktop Environment",
    ],
    python_requires=">=3.10",
    install_requires=[
        # Core Voice Processing
        "pyttsx3>=2.90",
        "vosk>=0.3.45",
        "pyaudio>=0.2.13",
        "sounddevice>=0.4.6",
        "soundfile>=0.12.1",
        "webrtcvad>=2.0.10",
        "whisper>=1.1.10",
        
        # AI and NLP
        "transformers>=4.37.2",
        "torch>=2.1.2",
        "sentence-transformers>=2.2.2",
        "spacy>=3.7.2",
        "faiss-cpu>=1.7.4",
        
        # System and Utils
        "psutil>=5.9.6",
        "pyyaml>=6.0.1",
        "python-dotenv>=1.0.0",
        "aiohttp>=3.9.1",
        "apscheduler>=3.10.4",
        "colorama>=0.4.6",
        "tqdm>=4.66.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "black>=23.11.0",
            "ruff>=0.1.0",
        ],
        "windows": [
            "pywin32>=306",
            "wmi>=1.5.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "jarvis=core.main:main",
        ],
    },
) 