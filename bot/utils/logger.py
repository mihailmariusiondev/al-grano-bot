import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict
from pathlib import Path
from dotenv import load_dotenv

class Logger:
    _instance = None
    _loggers: Dict[str, logging.Logger] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.log_level = logging.INFO
            cls._instance.log_dir = None
            cls._instance.log_format = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
            cls._instance.max_file_size = 10 * 1024 * 1024
            cls._instance.backup_count = 5
            cls._instance._init_logger()
        return cls._instance

    def _init_logger(self):
        """Initialize logger configuration"""
        try:
            # Asegurarse de que las variables de entorno están cargadas
            load_dotenv()

            self.log_dir = Path("logs")
            self.log_dir.mkdir(parents=True, exist_ok=True)

            # Obtener nivel de log de variable de entorno
            log_level_name = os.getenv('LOG_LEVEL', 'INFO').upper()
            self.log_level = getattr(logging, log_level_name, logging.INFO)

            # Si DEBUG_MODE está activo, forzar nivel DEBUG
            if os.getenv('DEBUG_MODE', 'false').lower() == 'true':
                self.log_level = logging.DEBUG

            # Log inicial para verificar la configuración
            root_logger = logging.getLogger()
            root_logger.setLevel(self.log_level)
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(logging.Formatter(self.log_format))
            root_logger.addHandler(console_handler)
            root_logger.info(f"Logger initialized with level: {log_level_name}")

        except Exception as e:
            print(f"Error initializing logger: {e}")
            # Fallback to console-only logging
            self.log_dir = None

    def get_logger(self, name: str) -> logging.Logger:
        if name not in self._loggers:
            logger = logging.getLogger(name)
            logger.setLevel(self.log_level)

            if not logger.handlers:
                # Always add console handler
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setFormatter(logging.Formatter(self.log_format))
                logger.addHandler(console_handler)

                # Add file handler only if log directory is available
                if self.log_dir:
                    try:
                        file_handler = RotatingFileHandler(
                            filename=self.log_dir / f"{name}.log",
                            maxBytes=self.max_file_size,
                            backupCount=self.backup_count,
                            encoding='utf-8'
                        )
                        file_handler.setFormatter(logging.Formatter(self.log_format))
                        logger.addHandler(file_handler)
                    except Exception as e:
                        logger.error(f"Failed to create file handler: {e}")

            logger.propagate = False
            self._loggers[name] = logger

        return self._loggers[name]

logger = Logger()  # Single instance