"""Task management and scheduling for JARVIS."""
import asyncio
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Union
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from ..config import Config
from ..utils.exceptions import TaskError

class TaskManager:
    """Manage and schedule tasks."""
    
    def __init__(self, config: Config):
        """Initialize task manager.
        
        Args:
            config: JARVIS configuration instance
        """
        self.config = config
        self.scheduler = AsyncIOScheduler()
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.task_history: List[Dict[str, Any]] = []
        
        # Start the scheduler
        self.scheduler.start()
        
    async def run_task(self, name: str, 
                      func: Callable, 
                      *args, 
                      **kwargs) -> Any:
        """Run a task asynchronously.
        
        Args:
            name: Task name
            func: Function to run
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func
            
        Returns:
            Task result
            
        Raises:
            TaskError: If task execution fails
        """
        try:
            # Create and store the task
            task = asyncio.create_task(func(*args, **kwargs))
            self.active_tasks[name] = task
            
            # Wait for completion
            result = await task
            
            # Record in history
            self.task_history.append({
                'name': name,
                'status': 'completed',
                'timestamp': datetime.now(),
                'duration': task.get_coro().cr_frame.f_locals.get('_start_time'),
                'result': str(result)
            })
            
            return result
            
        except Exception as e:
            # Record failure in history
            self.task_history.append({
                'name': name,
                'status': 'failed',
                'timestamp': datetime.now(),
                'error': str(e)
            })
            raise TaskError(f"Task {name} failed: {str(e)}")
            
        finally:
            # Cleanup
            if name in self.active_tasks:
                del self.active_tasks[name]
                
    def schedule_task(self, 
                     name: str,
                     func: Callable,
                     trigger: Union[str, CronTrigger, IntervalTrigger],
                     *args,
                     **kwargs) -> str:
        """Schedule a task for future execution.
        
        Args:
            name: Task name
            func: Function to schedule
            trigger: When to run the task
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func
            
        Returns:
            Job ID
            
        Raises:
            TaskError: If scheduling fails
        """
        try:
            job = self.scheduler.add_job(
                func=func,
                trigger=trigger,
                args=args,
                kwargs=kwargs,
                id=name,
                name=name
            )
            return job.id
        except Exception as e:
            raise TaskError(f"Failed to schedule task {name}: {str(e)}")
            
    def cancel_task(self, name: str) -> None:
        """Cancel a running or scheduled task.
        
        Args:
            name: Task name to cancel
            
        Raises:
            TaskError: If task cannot be cancelled
        """
        # Try to cancel running task
        if name in self.active_tasks:
            try:
                self.active_tasks[name].cancel()
                del self.active_tasks[name]
            except Exception as e:
                raise TaskError(f"Failed to cancel running task {name}: {str(e)}")
                
        # Try to remove scheduled task
        try:
            self.scheduler.remove_job(name)
        except Exception as e:
            raise TaskError(f"Failed to cancel scheduled task {name}: {str(e)}")
            
    def get_task_status(self, name: str) -> Dict[str, Any]:
        """Get status of a task.
        
        Args:
            name: Task name
            
        Returns:
            Dictionary containing task status
        """
        # Check active tasks
        if name in self.active_tasks:
            task = self.active_tasks[name]
            return {
                'name': name,
                'status': 'running' if not task.done() else 'completed',
                'done': task.done(),
                'cancelled': task.cancelled()
            }
            
        # Check scheduled tasks
        job = self.scheduler.get_job(name)
        if job:
            return {
                'name': name,
                'status': 'scheduled',
                'next_run': job.next_run_time,
                'trigger': str(job.trigger)
            }
            
        # Check history
        for entry in reversed(self.task_history):
            if entry['name'] == name:
                return entry
                
        return {'name': name, 'status': 'not_found'}
        
    def get_all_tasks(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get status of all tasks.
        
        Returns:
            Dictionary containing lists of active, scheduled and completed tasks
        """
        return {
            'active': [self.get_task_status(name) for name in self.active_tasks],
            'scheduled': [
                self.get_task_status(job.id) 
                for job in self.scheduler.get_jobs()
            ],
            'history': self.task_history[-10:]  # Last 10 completed tasks
        }
        
    def __del__(self):
        """Cleanup task manager."""
        try:
            self.scheduler.shutdown()
            for task in self.active_tasks.values():
                task.cancel()
        except:
            pass 