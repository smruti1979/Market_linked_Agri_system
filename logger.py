import logging
import os

LOG_FILE = "server_runtime.log"

def setup_custom_logger():
    """Configures a thread-safe file logger alongside a standard console printer stream."""
    logger = logging.getLogger("AgriIntelLogger")
    
    # Prevent duplicate handlers if the setup function is triggered multiple times
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Define a detailed architectural log format template
        log_format = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [ThreadID:%(thread)d] [%(filename)s:%(lineno)d]: %(message)s'
        )
        
        # 1. File Handler (Writes permanently straight to disk file)
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)
        
        # 2. Console Handler (Streams outputs to your Uvicorn command terminal screen)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_format)
        logger.addHandler(console_handler)
        
    return logger

# Globally accessible logger instance variable token wrapper
app_logger = setup_custom_logger()
