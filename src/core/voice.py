"""Voice processing and management for JARVIS."""
import os
import tempfile
from typing import Any, Dict, List, Optional, Tuple
import asyncio
import wave
import numpy as np

import pyaudio
import webrtcvad
import sounddevice as sd
import soundfile as sf
import pyttsx3
import whisper
from vosk import Model, KaldiRecognizer

from ..config import Config
from ..utils.exceptions import VoiceError

class VoiceManager:
    """Handle voice input/output and audio processing."""
    
    def __init__(self, config: Config):
        """Initialize voice manager.
        
        Args:
            config: JARVIS configuration instance
        """
        self.config = config
        self.sample_rate = config.get_setting('audio', 'sample_rate', default=16000)
        self.frames_per_buffer = config.get_setting('audio', 'frames_per_buffer', default=8000)
        
        # Initialize audio components
        self.vad = webrtcvad.Vad(3)  # Aggressive VAD mode
        self.audio = pyaudio.PyAudio()
        self.tts_engine = pyttsx3.init()
        
        # Load Whisper model for advanced speech recognition
        self.whisper_model = whisper.load_model("base")
        
        # Initialize Vosk model for wake word detection
        model_path = config.get_setting('paths', 'model')
        if not os.path.exists(model_path):
            raise VoiceError(f"Vosk model not found at {model_path}")
        self.vosk_model = Model(model_path)
        
        # Configure TTS properties
        self._configure_tts()
        
    def _configure_tts(self) -> None:
        """Configure text-to-speech properties."""
        voices = self.tts_engine.getProperty('voices')
        # Select a male voice if available
        male_voice = next((v for v in voices if 'male' in v.name.lower()), voices[0])
        self.tts_engine.setProperty('voice', male_voice.id)
        self.tts_engine.setProperty('rate', 175)  # Slightly faster than default
        
    async def listen(self, timeout: float = None) -> Optional[str]:
        """Listen for voice input.
        
        Args:
            timeout: Optional timeout in seconds
            
        Returns:
            Transcribed text or None if no speech detected
            
        Raises:
            VoiceError: If there's an error processing audio
        """
        try:
            # Open audio stream
            stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.frames_per_buffer
            )
            
            frames = []
            silent_frames = 0
            max_silent_frames = int(self.sample_rate / self.frames_per_buffer * 2)  # 2 seconds
            
            while True:
                if timeout and len(frames) * self.frames_per_buffer / self.sample_rate > timeout:
                    break
                    
                data = stream.read(self.frames_per_buffer)
                frame = np.frombuffer(data, dtype=np.float32)
                frames.append(frame)
                
                # Check for voice activity
                is_speech = self.vad.is_speech(data, self.sample_rate)
                if not is_speech:
                    silent_frames += 1
                else:
                    silent_frames = 0
                    
                # Stop if silence threshold reached
                if silent_frames > max_silent_frames and len(frames) > max_silent_frames:
                    break
            
            stream.stop_stream()
            stream.close()
            
            if not frames:
                return None
                
            # Convert frames to audio file
            audio_data = np.concatenate(frames)
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                sf.write(temp_file.name, audio_data, self.sample_rate)
                # Use Whisper for high-quality transcription
                result = self.whisper_model.transcribe(temp_file.name)
                os.unlink(temp_file.name)
                
            return result['text'].strip()
            
        except Exception as e:
            raise VoiceError(f"Error during voice input: {str(e)}")
            
    async def speak(self, text: str) -> None:
        """Convert text to speech.
        
        Args:
            text: Text to speak
            
        Raises:
            VoiceError: If there's an error during speech synthesis
        """
        try:
            # Run TTS in a thread pool to avoid blocking
            await asyncio.get_event_loop().run_in_executor(
                None, self.tts_engine.say, text
            )
            await asyncio.get_event_loop().run_in_executor(
                None, self.tts_engine.runAndWait
            )
        except Exception as e:
            raise VoiceError(f"Error during speech synthesis: {str(e)}")
            
    def detect_wake_word(self, audio_data: bytes) -> bool:
        """Detect wake word in audio stream.
        
        Args:
            audio_data: Raw audio data
            
        Returns:
            True if wake word detected, False otherwise
        """
        try:
            rec = KaldiRecognizer(self.vosk_model, self.sample_rate)
            rec.AcceptWaveform(audio_data)
            result = rec.Result()
            # Check for wake word in transcription
            return "jarvis" in result.lower()
        except Exception as e:
            raise VoiceError(f"Error during wake word detection: {str(e)}")
            
    def adjust_for_noise(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply noise reduction to audio data.
        
        Args:
            audio_data: Input audio data
            
        Returns:
            Noise-reduced audio data
        """
        # TODO: Implement more sophisticated noise reduction
        # For now, just apply simple normalization
        return audio_data / np.max(np.abs(audio_data))
        
    def __del__(self):
        """Cleanup audio resources."""
        try:
            self.audio.terminate()
            self.tts_engine.stop()
        except:
            pass 