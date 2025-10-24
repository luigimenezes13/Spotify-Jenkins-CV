import logging
import sys
from datetime import datetime
from typing import Optional


class Logger:
    _instance: Optional['Logger'] = None
    
    def __new__(cls) -> 'Logger':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup_logger()
        return cls._instance
    
    def _setup_logger(self) -> None:
        self.logger = logging.getLogger("spotify-jenkins-cv")
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '[%(levelname)s] %(asctime)s - %(message)s',
                datefmt='%Y-%m-%dT%H:%M:%S.%fZ'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def info(self, message: str, *args) -> None:
        self.logger.info(message, *args)
    
    def error(self, message: str, error: Optional[Exception] = None, *args) -> None:
        if error:
            self.logger.error(f"{message} - {str(error)}", *args, exc_info=error)
        else:
            self.logger.error(message, *args)
    
    def warn(self, message: str, *args) -> None:
        self.logger.warning(message, *args)
    
    def debug(self, message: str, *args) -> None:
        import os
        if os.getenv("NODE_ENV", "development") == "development":
            self.logger.debug(message, *args)


logger = Logger()
