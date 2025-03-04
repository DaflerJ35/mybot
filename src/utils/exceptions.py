"""Custom exceptions for JARVIS."""

class JarvisError(Exception):
    """Base exception class for JARVIS errors."""
    pass

class ConfigError(JarvisError):
    """Raised when there is a configuration error."""
    pass

class VoiceError(JarvisError):
    """Raised when there is an error with voice processing."""
    pass

class SecurityError(JarvisError):
    """Raised when there is a security violation."""
    pass

class TaskError(JarvisError):
    """Raised when there is an error executing a task."""
    pass

class ConversationError(JarvisError):
    """Raised when there is an error in conversation handling."""
    pass

class LearningError(JarvisError):
    """Raised when there is an error in the learning process."""
    pass

class MonitoringError(JarvisError):
    """Raised when there is an error in system monitoring."""
    pass 