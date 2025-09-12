import logging
import os
import time
import tkinter as tk
import subprocess
from datetime import datetime
from typing import Optional, Dict, Any


class LoggerManager:
    """Manages logging for bulk production mode with both GUI and file output."""
    
    def __init__(self, log_file_path: str, gui_log_box: tk.Text):
        """Initialize the logger manager with file and GUI output targets.
        
        Args:
            log_file_path: Path to the log file
            gui_log_box: Tkinter Text widget for GUI logging
        """
        self.log_file_path = log_file_path
        self.gui_log_box = gui_log_box
        self.logger = None
        self.setup_logging()
        
    def setup_logging(self) -> logging.Logger:
        """Configure Python logging with formatters and handlers."""
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger('bulk_production')
        self.logger.setLevel(logging.DEBUG)
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Create file handler
        file_handler = logging.FileHandler(self.log_file_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Create formatter
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(file_handler)
        
        return self.logger
    
    def log_to_gui_and_file(self, message: str, level: str = 'INFO'):
        """Log message to both GUI and file with appropriate level.
        
        Args:
            message: The message to log
            level: Log level (DEBUG, INFO, WARNING, ERROR)
        """
        # Log to file
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(message)
        
        # Log to GUI (only INFO and above)
        if level in ['INFO', 'WARNING', 'ERROR']:
            self.gui_log_box.config(state="normal")
            self.gui_log_box.insert(tk.END, message + "\n")
            self.gui_log_box.see(tk.END)
            self.gui_log_box.config(state="disabled")
            self.gui_log_box.update_idletasks()
    
    def log_bulk_start(self, total_files: int):
        """Log the start of bulk processing with file count."""
        message = f"🚀 Starting bulk production: {total_files} files to process"
        self.log_to_gui_and_file(message, 'INFO')
        
    def log_file_processing_start(self, index: int, filename: str, total: int):
        """Log the start of individual file processing.
        
        Args:
            index: Current file index (1-based)
            filename: Name of the file being processed
            total: Total number of files
        """
        message = f"[{index}/{total}] Processing {os.path.basename(filename)}..."
        self.log_to_gui_and_file(message, 'INFO')
        
    def log_step(self, step_name: str, details: Optional[Dict[str, Any]] = None):
        """Log a processing step with optional details.
        
        Args:
            step_name: Name of the processing step
            details: Optional dictionary of step details
        """
        message = f"  → {step_name}"
        if details:
            detail_str = ", ".join([f"{k}={v}" for k, v in details.items()])
            message += f" ({detail_str})"
        
        self.log_to_gui_and_file(message, 'INFO')
        
        # Log detailed information to file only
        if details:
            debug_message = f"Step details for {step_name}: {details}"
            self.log_to_gui_and_file(debug_message, 'DEBUG')
    
    def log_error(self, error: Exception, context: str, filename: Optional[str] = None):
        """Log error with full context and continue processing.
        
        Args:
            error: The exception that occurred
            context: Context where the error occurred
            filename: Optional filename being processed when error occurred
        """
        file_info = f" (file: {filename})" if filename else ""
        message = f"❌ Error in {context}{file_info}: {str(error)}"
        self.log_to_gui_and_file(message, 'ERROR')
        
        # Log full exception details to file only
        import traceback
        full_error = f"Full error details for {context}: {traceback.format_exc()}"
        self.log_to_gui_and_file(full_error, 'DEBUG')
    
    def log_performance(self, operation: str, duration: float, file_size: Optional[int] = None, **kwargs):
        """Log performance metrics for an operation.
        
        Args:
            operation: Name of the operation
            duration: Duration in seconds
            file_size: Optional file size in bytes
            **kwargs: Additional performance metrics
        """
        message = f"⏱️  {operation}: {duration:.2f}s"
        if file_size:
            size_mb = file_size / (1024 * 1024)
            rate = size_mb / duration if duration > 0 else 0
            message += f" ({size_mb:.1f}MB, {rate:.1f}MB/s)"
        
        self.log_to_gui_and_file(message, 'INFO')
        
        # Log detailed metrics to file
        metrics = {'operation': operation, 'duration': duration, 'file_size': file_size}
        metrics.update(kwargs)
        debug_message = f"Performance metrics: {metrics}"
        self.log_to_gui_and_file(debug_message, 'DEBUG')
    
    def log_summary(self, successful: int, failed: int, total_time: float):
        """Log final processing summary.
        
        Args:
            successful: Number of successfully processed files
            failed: Number of failed files
            total_time: Total processing time in seconds
        """
        total = successful + failed
        success_rate = (successful / total * 100) if total > 0 else 0
        avg_time = total_time / successful if successful > 0 else 0
        
        message = f"🎉 Bulk production complete! {successful}/{total} files successful ({success_rate:.1f}%)"
        self.log_to_gui_and_file(message, 'INFO')
        
        time_message = f"⏱️  Total time: {total_time:.1f}s, Average per file: {avg_time:.1f}s"
        self.log_to_gui_and_file(time_message, 'INFO')
        
        if failed > 0:
            error_message = f"⚠️  {failed} files failed processing - check log for details"
            self.log_to_gui_and_file(error_message, 'WARNING')


class ProcessingContext:
    """Context manager for tracking individual file processing with timing and error handling."""
    
    def __init__(self, logger_manager: LoggerManager, filename: str, index: int, total: int):
        """Initialize processing context.
        
        Args:
            logger_manager: LoggerManager instance
            filename: Name of file being processed
            index: Current file index (1-based)
            total: Total number of files
        """
        self.logger = logger_manager
        self.filename = filename
        self.index = index
        self.total = total
        self.start_time = None
        self.success = False
        
    def __enter__(self):
        """Start timing and log processing start."""
        self.start_time = time.time()
        self.logger.log_file_processing_start(self.index, self.filename, self.total)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Handle completion logging and error handling."""
        duration = time.time() - self.start_time if self.start_time else 0
        
        if exc_type is None:
            # Success
            self.success = True
            self.logger.log_performance(f"File {self.index} processing", duration)
            message = f"✅ Completed {os.path.basename(self.filename)} in {duration:.1f}s"
            self.logger.log_to_gui_and_file(message, 'INFO')
        else:
            # Error occurred
            self.logger.log_error(exc_val, "file processing", self.filename)
            # Return True to suppress the exception and continue processing
            return True
    
    def log_step(self, step_name: str, **kwargs):
        """Log a processing step within this file's context.
        
        Args:
            step_name: Name of the processing step
            **kwargs: Additional step details
        """
        self.logger.log_step(step_name, kwargs if kwargs else None)


def logged_subprocess_run(cmd: list, logger_manager: LoggerManager, operation: str, **kwargs) -> subprocess.CompletedProcess:
    """Wrapper for subprocess.run with comprehensive logging.
    
    Args:
        cmd: Command list to execute
        logger_manager: LoggerManager instance for logging
        operation: Description of the operation being performed
        **kwargs: Additional arguments passed to subprocess.run
        
    Returns:
        CompletedProcess result
        
    Raises:
        subprocess.CalledProcessError: If command fails and check=True
    """
    # Log command at DEBUG level
    cmd_str = ' '.join(cmd)
    logger_manager.log_to_gui_and_file(f"Executing {operation}: {cmd_str}", 'DEBUG')
    
    # Set default arguments
    kwargs.setdefault('capture_output', True)
    kwargs.setdefault('text', True)
    
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, **kwargs)
        duration = time.time() - start_time
        
        # Log success
        logger_manager.log_performance(f"{operation} subprocess", duration)
        
        # Log output if present (DEBUG level)
        if result.stdout:
            logger_manager.log_to_gui_and_file(f"{operation} stdout: {result.stdout[:200]}...", 'DEBUG')
        if result.stderr:
            logger_manager.log_to_gui_and_file(f"{operation} stderr: {result.stderr[:200]}...", 'DEBUG')
            
        return result
        
    except subprocess.CalledProcessError as e:
        duration = time.time() - start_time
        
        # Log detailed error information
        error_details = {
            'command': cmd_str,
            'return_code': e.returncode,
            'duration': duration,
            'stdout': e.stdout[:500] if e.stdout else None,
            'stderr': e.stderr[:500] if e.stderr else None
        }
        
        logger_manager.log_error(e, f"{operation} subprocess", None)
        logger_manager.log_to_gui_and_file(f"Command failed: {error_details}", 'DEBUG')
        
        raise
    except Exception as e:
        duration = time.time() - start_time
        logger_manager.log_error(e, f"{operation} subprocess execution", None)
        raise


def create_log_filename() -> str:
    """Create a timestamped log filename for bulk production.
    
    Returns:
        Log file path with timestamp
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"logs/bulk_production_{timestamp}.log"