# JARVIS Voice Assistant

An intelligent voice assistant with advanced capabilities including voice interaction, task automation, and system monitoring.

## Features

- 🎤 Voice Interaction
  - Wake word detection ("Hey Jarvis")
  - Natural speech recognition using Whisper
  - High-quality text-to-speech synthesis
  - Voice activity detection

- 🧠 AI & NLP Capabilities
  - Natural language understanding
  - Intent classification
  - Sentiment analysis
  - Entity recognition
  - Semantic search

- 💻 System Integration
  - Task scheduling and automation
  - System resource monitoring
  - Configurable settings
  - Cross-platform support (Windows focus)

## Installation

### Prerequisites

- Python 3.10 or higher
- [PyAudio dependencies](https://people.csail.mit.edu/hubert/pyaudio/):
  - Windows: No additional requirements
  - Linux: `sudo apt-get install python3-pyaudio portaudio19-dev`
  - macOS: `brew install portaudio`

### Quick Install

```bash
# Clone the repository
git clone https://github.com/DaflerJ35/mybot.git
cd mybot

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install dependencies
pip install -e ".[dev]"  # Include development tools
pip install -e ".[windows]"  # Windows-specific dependencies
```

### Model Downloads

```bash
# Download required models
python -m spacy download en_core_web_sm
# Additional model downloads will be prompted on first run
```

## Usage

1. Start JARVIS:
```bash
jarvis
# or
python -m src.main
```

2. Wake JARVIS by saying "Hey Jarvis"
3. Speak your command
4. Watch for the status indicator:
   - 🔘 Gray: Idle
   - 🟢 Green: Listening
   - 🟡 Yellow: Processing
   - 🔴 Red: Error

## Configuration

### Settings

Edit `config/settings.yaml` to customize:
- Audio parameters
- System monitoring thresholds
- File paths
- Model configurations

### Responses

Edit `config/responses.yaml` to customize JARVIS's personality and responses.

## Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Code Quality Tools

- **Ruff**: Modern Python linter
  ```bash
  ruff check .
  ruff format .
  ```

- **Black**: Code formatting
  ```bash
  black src tests
  ```

- **MyPy**: Type checking
  ```bash
  mypy src
  ```

### Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=src tests/
```

### Project Structure

```
mybot/
├── src/
│   ├── core/           # Core functionality
│   ├── ui/            # User interface components
│   ├── utils/         # Utility functions
│   └── main.py        # Entry point
├── config/
│   ├── settings.yaml  # Configuration
│   └── responses.yaml # Response templates
├── tests/            # Test suite
└── setup.py         # Package configuration
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI's Whisper for speech recognition
- Vosk for wake word detection
- Transformers library for NLP capabilities
