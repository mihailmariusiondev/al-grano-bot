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
            cls._instance.log_format = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(funcName)s() - %(message)s"
            cls._instance.max_file_size = 20 * 1024 * 1024
            cls._instance.backup_count = 10
            cls._instance._init_logger()
        return cls._instance

    def _init_logger(self):
        """Initialize logger configuration"""
        try:
            # Asegurarse de que las variables de entorno están cargadas
            load_dotenv()

            self.log_dir = Path("logs")
            self.log_dir.mkdir(parents=True, exist_ok=True)

            # Obtener nivel de log de variable de entorno, por defecto INFO
            log_level_name = os.getenv('LOG_LEVEL', 'INFO').upper()
            self.log_level = getattr(logging, log_level_name, logging.INFO)

            # DEBUG_MODE ya no fuerza el nivel - se respeta LOG_LEVEL
            debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'

            # Configurar el root logger con el nivel apropiado
            root_logger = logging.getLogger()
            root_logger.setLevel(self.log_level)

            # Limpiar handlers existentes para evitar duplicados
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)

            # Console handler mejorado
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level)
            console_handler.setFormatter(logging.Formatter(self.log_format))
            root_logger.addHandler(console_handler)

            # Handler de archivo para el root logger
            if self.log_dir:
                try:
                    root_file_handler = RotatingFileHandler(
                        filename=self.log_dir / "bot_master.log",
                        maxBytes=self.max_file_size,
                        backupCount=self.backup_count,
                        encoding='utf-8'
                    )
                    root_file_handler.setLevel(self.log_level)
                    root_file_handler.setFormatter(logging.Formatter(self.log_format))
                    root_logger.addHandler(root_file_handler)
                except Exception as e:
                    print(f"Error creating root file handler: {e}")

            # Log inicial para verificar la configuración
            root_logger.info(f"=== LOGGING SYSTEM INITIALIZED ===")
            root_logger.info(f"Log level: {log_level_name} ({self.log_level})")
            root_logger.info(f"Log directory: {self.log_dir}")
            root_logger.info(f"Debug mode: {debug_mode}")
            root_logger.info(f"Respecting LOG_LEVEL environment variable: {log_level_name}")

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
                console_handler.setLevel(self.log_level)
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
                        file_handler.setLevel(self.log_level)
                        file_handler.setFormatter(logging.Formatter(self.log_format))
                        logger.addHandler(file_handler)
                    except Exception as e:
                        logger.error(f"Failed to create file handler for {name}: {e}")

            logger.propagate = False
            self._loggers[name] = logger

        return self._loggers[name]

    def log_function_entry(self, logger_instance, func_name: str, **kwargs):
        """Helper method to log function entry with parameters"""
        if kwargs:
            params = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
            logger_instance.debug(f"ENTERING {func_name}({params})")
        else:
            logger_instance.debug(f"ENTERING {func_name}()")

    def log_function_exit(self, logger_instance, func_name: str, result=None):
        """Helper method to log function exit with result"""
        if result is not None:
            logger_instance.debug(f"EXITING {func_name}() -> {type(result).__name__}")
        else:
            logger_instance.debug(f"EXITING {func_name}()")

logger = Logger()  # Single instance