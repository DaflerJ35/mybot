"""Test configuration module."""
import os
from pathlib import Path
import pytest
import yaml

from src.config import Config


@pytest.fixture
def config_dir(tmp_path):
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
        
    return config_path


def test_config_initialization(config_dir):
    """Test Config class initialization."""
    os.environ["JARVIS_CONFIG_DIR"] = str(config_dir)
    config = Config()
    assert config is not None


def test_get_setting(config_dir):
    """Test getting settings from config."""
    os.environ["JARVIS_CONFIG_DIR"] = str(config_dir)
    config = Config()
    
    # Test getting existing setting
    assert config.get_setting("audio", "sample_rate") == 16000
    
    # Test getting nested setting
    assert config.get_setting("paths", "model") == str(config_dir / "models")
    
    # Test getting non-existent setting with default
    assert config.get_setting("audio", "non_existent", default=44100) == 44100


def test_get_response(config_dir):
    """Test getting responses from config."""
    os.environ["JARVIS_CONFIG_DIR"] = str(config_dir)
    config = Config()
    
    # Test getting existing response
    greetings = config.get_response("greetings")
    assert isinstance(greetings, list)
    assert "Hello!" in greetings
    
    # Test getting non-existent response
    assert config.get_response("non_existent", default=["Default"]) == ["Default"]


def test_invalid_config_dir():
    """Test handling of invalid config directory."""
    os.environ["JARVIS_CONFIG_DIR"] = "/non/existent/path"
    with pytest.raises(FileNotFoundError):
        Config() 