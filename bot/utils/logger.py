# bot/utils/logger.py

import logging
import sys
import os

# ¡Importante! Añadir TimedRotatingFileHandler
from logging.handlers import TimedRotatingFileHandler
from typing import Dict
from pathlib import Path
from dotenv import load_dotenv


class Logger:
    _instance = None
    _loggers: Dict[str, logging.Logger] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.log_level = logging.INFO
            cls._instance.log_dir = Path("logs")
            # Un formato un poco más limpio para la consola y los archivos
            cls._instance.log_format = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(funcName)s() - %(message)s"
            # Ya no necesitamos max_file_size, pero sí backup_count
            cls._instance.backup_count = 7  # 7 días de historial
            cls._instance._init_logger()
        return cls._instance

    def _init_logger(self):
        """Initialize a centralized logger configuration with daily rotation."""
        try:
            load_dotenv()
            self.log_dir.mkdir(parents=True, exist_ok=True)
            log_level_name = os.getenv("LOG_LEVEL", "INFO").upper()
            self.log_level = getattr(logging, log_level_name, logging.INFO)

            root_logger = logging.getLogger()
            root_logger.setLevel(self.log_level)

            if root_logger.hasHandlers():
                root_logger.handlers.clear()

            # 1. Handler para la consola (sin cambios)
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(logging.Formatter(self.log_format))
            root_logger.addHandler(console_handler)

            # 2. Handler de archivo principal (bot.log) con rotación diaria
            main_file_handler = TimedRotatingFileHandler(
                filename=self.log_dir / "bot.log",
                when="midnight",  # Rota cada día a medianoche
                interval=1,  # Intervalo de 1 día
                backupCount=self.backup_count,  # Mantiene 7 archivos de log antiguos (bot.log.2023-10-26, etc.)
                encoding="utf-8",
            )
            main_file_handler.setFormatter(logging.Formatter(self.log_format))
            root_logger.addHandler(main_file_handler)

            # 3. Handler de archivo para errores (errors.log) con rotación diaria
            error_file_handler = TimedRotatingFileHandler(
                filename=self.log_dir / "errors.log",
                when="midnight",
                interval=1,
                backupCount=self.backup_count,
                encoding="utf-8",
            )
            error_file_handler.setLevel(logging.ERROR)  # Solo captura ERROR y CRITICAL
            error_file_handler.setFormatter(logging.Formatter(self.log_format))
            root_logger.addHandler(error_file_handler)

            # Silenciar librerías externas
            logging.getLogger("apscheduler").setLevel(logging.WARNING)
            logging.getLogger("telegram").setLevel(logging.WARNING)
            logging.getLogger("httpx").setLevel(logging.WARNING)

            root_logger.info("=== DAILY-ROTATING LOGGING SYSTEM INITIALIZED ===")
            root_logger.info(f"Log level set to: {log_level_name}")
            root_logger.info(
                f"Logs will be rotated daily at midnight. Keeping {self.backup_count} days of history."
            )

        except Exception as e:
            logging.basicConfig(
                level=self.log_level, format=self.log_format, stream=sys.stdout
            )
            logging.critical(
                f"Error initializing file-based logger: {e}. Falling back to console logging."
            )

    def get_logger(self, name: str) -> logging.Logger:
        """Gets a logger instance. Configuration is inherited from the root."""
        if name not in self._loggers:
            self._loggers[name] = logging.getLogger(name)
        return self._loggers[name]

    # Los métodos de ayuda se mantienen igual
    def log_function_entry(self, logger_instance, func_name: str, **kwargs):
        if self.log_level > logging.DEBUG:
            return
        params = ", ".join([f"{k}={v!r}" for k, v in kwargs.items()])
        logger_instance.debug(f"--> ENTERING {func_name}({params})")

    def log_function_exit(self, logger_instance, func_name: str, result=None):
        if self.log_level > logging.DEBUG:
            return
        if result is not None:
            logger_instance.debug(
                f"<-- EXITING {func_name}() -> {type(result).__name__}"
            )
        else:
            logger_instance.debug(f"<-- EXITING {func_name}()")


logger = Logger()  # Single instance
