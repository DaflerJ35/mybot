"""Core JARVIS functionality."""
import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..config import Config
from .voice import VoiceManager
from .nlp import NLPManager
from .tasks import TaskManager
from .conversation import ConversationManager
from ..utils.monitoring import SystemMonitor
from ..utils.exceptions import JarvisError
from ..ui.status_indicator import StatusIndicator, JarvisStatus

class Jarvis:
    """Main JARVIS class that coordinates all functionality."""
    
    def __init__(self, config_dir: str = "config"):
        """Initialize JARVIS.
        
        Args:
            config_dir: Directory containing configuration files
        """
        # Initialize configuration
        self.config = Config(config_dir)
        
        # Initialize components
        self.voice = VoiceManager(self.config)
        self.nlp = NLPManager(self.config)
        self.tasks = TaskManager(self.config)
        self.conversation = ConversationManager(self.config)
        self.monitor = SystemMonitor(self.config)
        
        # Initialize UI
        self.status_indicator = StatusIndicator()
        
        # Setup logging
        self._setup_logging()
        
        self.running = False
        self.last_interaction = None
        
    def _setup_logging(self) -> None:
        """Configure logging."""
        log_file = self.config.get_setting('paths', 'log_file')
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('jarvis')
        
    async def start(self) -> None:
        """Start JARVIS."""
        self.running = True
        self.logger.info("JARVIS is starting up...")
        
        # Create and start status indicator
        self.status_indicator.create_window()
        asyncio.create_task(self.status_indicator.update())
        
        # Initial greeting
        await self.speak(
            self.conversation.get_response('greetings', mood='energetic')
        )
        
        try:
            while self.running:
                # Monitor system status
                status = self.monitor.get_system_status()
                if status['cpu_percent'] > 90 or status['memory_percent'] > 90:
                    self.logger.warning("System resources critical!")
                    
                # Listen for wake word or command
                audio = await self.voice.listen(timeout=5.0)
                if audio:
                    if self.voice.detect_wake_word(audio):
                        self.status_indicator.set_status(JarvisStatus.LISTENING)
                        await self.handle_interaction()
                    else:
                        self.status_indicator.set_status(JarvisStatus.IDLE)
                        
                # Small delay to prevent CPU hogging
                await asyncio.sleep(0.1)
                
        except Exception as e:
            self.logger.error(f"Error in main loop: {str(e)}")
            self.status_indicator.set_status(JarvisStatus.ERROR)
            raise
            
    async def stop(self) -> None:
        """Stop JARVIS."""
        self.running = False
        self.logger.info("JARVIS is shutting down...")
        await self.speak(
            self.conversation.get_response('goodbye', mood='neutral')
        )
        self.status_indicator.close()
        
    async def handle_interaction(self) -> None:
        """Handle a user interaction."""
        try:
            # Listen for command
            self.logger.info("Listening for command...")
            audio = await self.voice.listen()
            if not audio:
                self.status_indicator.set_status(JarvisStatus.IDLE)
                return
                
            # Process command
            self.status_indicator.set_status(JarvisStatus.PROCESSING)
            text = await self.voice.transcribe(audio)
            self.logger.info(f"Received command: {text}")
            
            # Update conversation context
            self.conversation.add_to_history('user', text)
            mood = self.conversation.analyze_mood(text)
            self.conversation.update_context(current_mood=mood)
            
            # Analyze intent
            intent = self.nlp.get_intent(text)
            self.logger.info(f"Detected intent: {intent}")
            
            # Execute command
            response = await self.execute_command(text, intent)
            
            # Respond to user
            await self.speak(response)
            self.conversation.add_to_history('jarvis', response)
            
            self.last_interaction = datetime.now()
            self.status_indicator.set_status(JarvisStatus.IDLE)
            
        except Exception as e:
            self.logger.error(f"Error handling interaction: {str(e)}")
            error_response = self.conversation.get_response('errors')
            await self.speak(error_response)
            self.status_indicator.set_status(JarvisStatus.ERROR)
            
    async def execute_command(self, text: str, intent: Dict[str, Any]) -> str:
        """Execute a command based on intent.
        
        Args:
            text: Raw command text
            intent: Parsed intent
            
        Returns:
            Response to user
        """
        category = intent.get('category', 'unknown')
        action = intent.get('action')
        target = intent.get('target')
        
        try:
            if category == 'search':
                results = self.nlp.semantic_search(text)
                return self._format_search_results(results)
                
            elif category == 'launch':
                if target:
                    await self.tasks.run_task(
                        f"launch_{target}",
                        self._launch_application,
                        target
                    )
                    return self.conversation.get_response('success')
                    
            elif category == 'stop':
                if target:
                    self.tasks.cancel_task(f"launch_{target}")
                    return self.conversation.get_response('acknowledgments')
                    
            # Add more command categories as needed
            
            return self.conversation.get_response(
                'unknown_command', 
                mood=self.conversation.context['current_mood']
            )
            
        except Exception as e:
            self.logger.error(f"Error executing command: {str(e)}")
            raise JarvisError(f"Command execution failed: {str(e)}")
            
    async def speak(self, text: str) -> None:
        """Speak a response.
        
        Args:
            text: Text to speak
        """
        try:
            await self.voice.speak(text)
        except Exception as e:
            self.logger.error(f"Error during speech: {str(e)}")
            
    def _format_search_results(self, results: List[Dict[str, Any]]) -> str:
        """Format search results for speech.
        
        Args:
            results: List of search results
            
        Returns:
            Formatted response
        """
        if not results:
            return self.conversation.get_response('no_results')
            
        top_result = results[0]
        return f"I found this: {top_result['text']}"
        
    async def _launch_application(self, app_name: str) -> None:
        """Launch an application.
        
        Args:
            app_name: Name of application to launch
        """
        # TODO: Implement application launching
        pass
        
    def __str__(self) -> str:
        """Get string representation."""
        return "JARVIS AI Assistant" 