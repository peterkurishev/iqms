# app/core/logger.py
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional
from core.config import settings

def setup_logger(
    name: str = "internet-monitor",
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Настройка логгера с ротацией логов
    
    Args:
        name: Имя логгера
        log_level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Путь к файлу логов (None для вывода только в консоль)
        max_bytes: Максимальный размер файла перед ротацией
        backup_count: Количество сохраняемых лог-файлов
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level.upper())
    
    # Форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Файловый обработчик (если указан файл)
    if log_file:
        # Создаем директорию для логов, если ее нет
        log_path = Path(log_file).parent
        log_path.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# Инициализация глобального логгера
logger = setup_logger(
    log_level=settings.LOG_LEVEL,
    log_file=settings.LOG_FILE if settings.LOG_FILE else None
)
