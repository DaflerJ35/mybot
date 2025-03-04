"""Visual status indicator for JARVIS."""
import tkinter as tk
from typing import Optional, Tuple, Callable
import asyncio
from enum import Enum
import logging

class JarvisStatus(Enum):
    """JARVIS status states."""
    IDLE = "gray"
    LISTENING = "green"
    PROCESSING = "yellow"
    ERROR = "red"

class StatusIndicator:
    """Floating status indicator for JARVIS."""
    
    def __init__(self, size: int = 50, opacity: float = 0.7):
        """Initialize status indicator.
        
        Args:
            size: Size of the indicator in pixels
            opacity: Window opacity (0.0 to 1.0)
        """
        self.size = size
        self.status = JarvisStatus.IDLE
        self.window: Optional[tk.Tk] = None
        self.canvas: Optional[tk.Canvas] = None
        self.circle_id: Optional[int] = None
        self._status_callback: Optional[Callable] = None
        self._dragging = False
        self._drag_start: Tuple[int, int] = (0, 0)
        
    def create_window(self) -> None:
        """Create the floating window."""
        self.window = tk.Tk()
        self.window.title("JARVIS")
        
        # Configure window
        self.window.overrideredirect(True)  # Remove window decorations
        self.window.attributes('-topmost', True)  # Stay on top
        self.window.attributes('-alpha', 0.7)  # Set transparency
        
        # Create canvas and circle
        self.canvas = tk.Canvas(
            self.window, 
            width=self.size, 
            height=self.size,
            bg='black',  # Black background
            highlightthickness=0  # No border
        )
        self.canvas.pack()
        
        # Create the circle with a glow effect
        padding = 5
        self.circle_id = self.canvas.create_oval(
            padding, padding, 
            self.size - padding, self.size - padding,
            fill=self.status.value,
            outline='white',  # White border for glow effect
            width=2
        )
        
        # Bind mouse events for dragging
        self.canvas.bind('<Button-1>', self._start_drag)
        self.canvas.bind('<B1-Motion>', self._on_drag)
        self.canvas.bind('<ButtonRelease-1>', self._stop_drag)
        
        # Position window in bottom right corner
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = screen_width - self.size - 20
        y = screen_height - self.size - 40
        self.window.geometry(f'{self.size}x{self.size}+{x}+{y}')
        
    def set_status(self, status: JarvisStatus) -> None:
        """Update the indicator status.
        
        Args:
            status: New status to display
        """
        if self.circle_id and self.canvas:
            self.status = status
            self.canvas.itemconfig(self.circle_id, fill=status.value)
            
            # Add glow effect based on status
            if status == JarvisStatus.LISTENING:
                self.canvas.itemconfig(self.circle_id, outline='#00ff00')
            elif status == JarvisStatus.PROCESSING:
                self.canvas.itemconfig(self.circle_id, outline='#ffff00')
            else:
                self.canvas.itemconfig(self.circle_id, outline='white')
                
    def _start_drag(self, event: tk.Event) -> None:
        """Start window dragging.
        
        Args:
            event: Mouse event
        """
        self._dragging = True
        self._drag_start = (event.x_root - self.window.winfo_x(),
                          event.y_root - self.window.winfo_y())
        
    def _on_drag(self, event: tk.Event) -> None:
        """Handle window dragging.
        
        Args:
            event: Mouse event
        """
        if self._dragging and self.window:
            x = event.x_root - self._drag_start[0]
            y = event.y_root - self._drag_start[1]
            
            # Keep within screen bounds
            max_x = self.window.winfo_screenwidth() - self.size
            max_y = self.window.winfo_screenheight() - self.size
            x = max(0, min(x, max_x))
            y = max(0, min(y, max_y))
            
            self.window.geometry(f'+{x}+{y}')
            
    def _stop_drag(self, event: tk.Event) -> None:
        """Stop window dragging.
        
        Args:
            event: Mouse event
        """
        self._dragging = False
        
    async def update(self) -> None:
        """Async update loop for the indicator."""
        while True:
            if self.window:
                self.window.update()
            await asyncio.sleep(0.01)  # Small delay to prevent high CPU usage
            
    def close(self) -> None:
        """Close the indicator window."""
        if self.window:
            self.window.destroy()
            self.window = None 