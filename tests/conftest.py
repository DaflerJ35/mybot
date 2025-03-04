"""Test fixtures for JARVIS tests."""
import asyncio
import os
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
import yaml

from src.core.jarvis_core import Jarvis


@pytest.fixture
def config_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary config directory with test settings."""
    config_path = tmp_path / "config"
    config_path.mkdir()
    
    # Create test settings.yaml
    settings = {
        "audio": {
            "sample_rate": 16000,
            "frames_per_buffer": 8000,
            "clap_threshold": 0.1,
        },
        "system": {
            "rogue_cpu_threshold": 50,
            "rogue_mem_threshold": 30,
        },
        "paths": {
            "model": str(tmp_path / "models"),
            "voice_profile": str(tmp_path / "voice_profile.pkl"),
            "database": str(tmp_path / "jarvis.db"),
            "log_file": str(tmp_path / "jarvis.log"),
        }
    }
    
    with open(config_path / "settings.yaml", "w") as f:
        yaml.dump(settings, f)
        
    # Create test responses.yaml
    responses = {
        "greetings": ["Hello!", "Hi!", "Greetings!"],
        "farewells": ["Goodbye!", "Bye!", "See you later!"],
        "errors": ["Sorry, something went wrong.", "An error occurred."],
    }
    
    with open(config_path / "responses.yaml", "w") as f:
        yaml.dump(responses, f)
        
    yield config_path


@pytest.fixture
async def jarvis(config_dir: Path) -> AsyncGenerator[Jarvis, None]:
    """Create a test instance of JARVIS."""
    # Set environment for testing
    os.environ["JARVIS_CONFIG_DIR"] = str(config_dir)
    
    # Create and yield JARVIS instance
    jarvis = Jarvis()
    yield jarvis
    
    # Cleanup
    await jarvis.stop()


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
