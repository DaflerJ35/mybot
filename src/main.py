"""JARVIS main entry point.

This module serves as the entry point for the JARVIS voice assistant.
It handles initialization, startup, and graceful shutdown of the system.
"""
import asyncio
import logging
import sys
from pathlib import Path
from typing import NoReturn, Optional

from core.jarvis_core import Jarvis
from utils.exceptions import JarvisError

async def main() -> Optional[NoReturn]:
    """Main entry point for JARVIS.
    
    This function initializes and runs the JARVIS voice assistant.
    It performs the following tasks:
    1. Verifies the existence of required configuration files
    2. Initializes the JARVIS system
    3. Handles graceful shutdown on keyboard interrupt
    4. Manages error logging for fatal errors
    
    Returns:
        Optional[NoReturn]: None on successful completion, NoReturn on fatal error
        
    Raises:
        JarvisError: If configuration directory or files are missing
        SystemExit: On fatal errors
    """
    try:
        # Ensure config directory exists
        config_dir = Path("config")
        if not config_dir.exists():
            raise JarvisError(
                "Config directory not found. Please ensure the config directory "
                "exists and contains settings.yaml and responses.yaml"
            )
            
        # Initialize and start JARVIS
        jarvis = Jarvis()
        print("Starting JARVIS...")
        print("Say 'Hey Jarvis' or any other wake phrase to begin!")
        
        await jarvis.start()
        
    except KeyboardInterrupt:
        print("\nShutting down JARVIS...")
        if 'jarvis' in locals():
            await jarvis.stop()
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass  # Clean exit on Ctrl+C 