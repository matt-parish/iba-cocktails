import logging
import sys
from datetime import datetime
from pathlib import Path


def setup_logging(log_level: str = "INFO", log_file: str = None) -> logging.Logger:
    """Set up logging configuration."""
    
    # Create logs directory if logging to file
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(exist_ok=True)
    
    # Configure logging format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Set up root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


class ProgressTracker:
    """Track scraping progress and statistics."""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.total_cocktails = 0
        self.completed_cocktails = 0
        self.failed_cocktails = 0
        self.current_cocktail = ""
        self.logger = logging.getLogger(__name__)
    
    def set_total(self, total: int):
        """Set total number of cocktails to process."""
        self.total_cocktails = total
        self.logger.info(f"Starting to process {total} cocktails")
    
    def start_cocktail(self, name: str):
        """Mark start of processing a cocktail."""
        self.current_cocktail = name
        self.logger.info(f"Processing ({self.completed_cocktails + 1}/{self.total_cocktails}): {name}")
    
    def complete_cocktail(self, success: bool = True):
        """Mark completion of a cocktail."""
        if success:
            self.completed_cocktails += 1
        else:
            self.failed_cocktails += 1
            self.logger.warning(f"Failed to process: {self.current_cocktail}")
    
    def get_progress(self) -> dict:
        """Get current progress statistics."""
        elapsed = datetime.now() - self.start_time
        processed = self.completed_cocktails + self.failed_cocktails
        
        return {
            "total": self.total_cocktails,
            "completed": self.completed_cocktails,
            "failed": self.failed_cocktails,
            "remaining": self.total_cocktails - processed,
            "progress_percent": (processed / self.total_cocktails * 100) if self.total_cocktails > 0 else 0,
            "elapsed_time": str(elapsed).split('.')[0],  # Remove microseconds
            "success_rate": (self.completed_cocktails / processed * 100) if processed > 0 else 0
        }
    
    def print_summary(self):
        """Print final summary."""
        progress = self.get_progress()
        self.logger.info("=" * 50)
        self.logger.info("SCRAPING COMPLETED")
        self.logger.info("=" * 50)
        self.logger.info(f"Total cocktails: {progress['total']}")
        self.logger.info(f"Successfully scraped: {progress['completed']}")
        self.logger.info(f"Failed: {progress['failed']}")
        self.logger.info(f"Success rate: {progress['success_rate']:.1f}%")
        self.logger.info(f"Total time: {progress['elapsed_time']}")
        self.logger.info("=" * 50)