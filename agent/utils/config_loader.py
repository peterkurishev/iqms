# app/utils/config_loader.py
import os
import json
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
from pydantic import BaseSettings, Field, validator
from pydantic.env_settings import SettingsSourceCallable
import toml

logger = logging.getLogger(__name__)

class AgentConfig(BaseSettings):
    """Модель конфигурации агента"""
    
    # Основные настройки
    agent_id: str = Field(..., env="AGENT_ID")
    api_url: str = Field("http://localhost:8000/api/v1", env="API_URL")
    api_key: str = Field(..., env="API_KEY")
    
    # Настройки тестирования
    test_interval: int = Field(300, env="TEST_INTERVAL", ge=60)  # секунды, минимум 60
    test_server: str = Field("https://httpbin.org", env="TEST_SERVER")
    test_timeout: int = Field(30, env="TEST_TIMEOUT")
    
    # Настройки логирования
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field(None, env="LOG_FILE")
    log_rotation: bool = Field(True, env="LOG_ROTATION")
    
    # Настройки сети
    max_retries: int = Field(3, env="MAX_RETRIES")
    retry_delay: int = Field(5, env="RETRY_DELAY")
    
    # Дополнительные настройки
    enable_detailed_metrics: bool = Field(False, env="ENABLE_DETAILED_METRICS")
    data_retention_days: int = Field(7, env="DATA_RETENTION_DAYS")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        @classmethod
        def customise_sources(
                cls,
                init_settings: SettingsSourceCallable,
                env_settings: SettingsSourceCallable,
                file_secret_settings: SettingsSourceCallable,
        ):
            return (
                init_settings,
                env_settings,
                config_file_settings,
                file_secret_settings,
            )
    
    @validator('log_level')
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()
    
    @validator('api_url')
    def validate_api_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError("API URL must start with http:// or https://")
        return v.rstrip('/')

def config_file_settings(settings: BaseSettings) -> Dict[str, Any]:
    """Загрузка конфигурации из файлов"""
    config_dirs = [
        Path.cwd() / "config",
        Path.home() / ".config" / "internet-monitor",
        Path("/etc/internet-monitor")
    ]
    
    config_files = []
    for config_dir in config_dirs:
        if config_dir.exists():
            for ext in ['.json', '.yaml', '.yml', '.toml']:
                config_file = config_dir / f"config{ext}"
                if config_file.exists():
                    config_files.append(config_file)
    
    config_data = {}
    for config_file in config_files:
        try:
            if config_file.suffix == '.json':
                with open(config_file, 'r') as f:
                    config_data.update(json.load(f))
            elif config_file.suffix in ['.yaml', '.yml']:
                with open(config_file, 'r') as f:
                    config_data.update(yaml.safe_load(f))
            elif config_file.suffix == '.toml':
                with open(config_file, 'r') as f:
                    config_data.update(toml.load(f))
            
            logger.info(f"Loaded config from {config_file}")
            
        except Exception as e:
            logger.warning(f"Failed to load config from {config_file}: {e}")
    
    return config_data

def load_config(config_path: Optional[Union[str, Path]] = None) -> AgentConfig:
    """
    Загрузка конфигурации из различных источников
    
    Приоритет источников (от высшего к низшему):
    1. Аргументы командной строки
    2. Переменные окружения
    3. Файлы конфигурации
    4. Значения по умолчанию
    """
    try:
        # Если указан путь к конфигурационному файлу
        if config_path:
            config_path = Path(config_path)
            if config_path.exists():
                global config_file_settings
                original_settings = config_file_settings
                
                def custom_config_settings(settings: BaseSettings) -> Dict[str, Any]:
                    config_data = {}
                    try:
                        if config_path.suffix == '.json':
                            with open(config_path, 'r') as f:
                                config_data.update(json.load(f))
                        elif config_path.suffix in ['.yaml', '.yml']:
                            with open(config_path, 'r') as f:
                                config_data.update(yaml.safe_load(f))
                        elif config_path.suffix == '.toml':
                            with open(config_path, 'r') as f:
                                config_data.update(toml.load(f))
                        logger.info(f"Loaded config from {config_path}")
                    except Exception as e:
                        logger.error(f"Failed to load config from {config_path}: {e}")
                    return config_data
                
                # Временно заменяем функцию для загрузки из указанного файла
                config_file_settings = custom_config_settings
                config = AgentConfig()
                config_file_settings = original_settings
                return config
        
        # Стандартная загрузка
        return AgentConfig()
        
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise

def save_config(config: AgentConfig, config_path: Union[str, Path]) -> bool:
    """Сохранение конфигурации в файл"""
    try:
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        config_dict = config.dict()
        
        if config_path.suffix == '.json':
            with open(config_path, 'w') as f:
                json.dump(config_dict, f, indent=2)
        elif config_path.suffix in ['.yaml', '.yml']:
            with open(config_path, 'w') as f:
                yaml.dump(config_dict, f, default_flow_style=False)
        elif config_path.suffix == '.toml':
            with open(config_path, 'w') as f:
                toml.dump(config_dict, f)
        else:
            raise ValueError("Unsupported config file format")
        
        logger.info(f"Configuration saved to {config_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save configuration: {e}")
        return False

def generate_config_template(output_path: Union[str, Path]) -> bool:
    """Генерация шаблона конфигурационного файла"""
    template = {
        "agent_id": "your-agent-id",
        "api_url": "https://your-monitoring-server.com/api/v1",
        "api_key": "your-secret-api-key",
        "test_interval": 300,
        "test_server": "https://httpbin.org",
        "test_timeout": 30,
        "log_level": "INFO",
        "log_file": None,
        "log_rotation": True,
        "max_retries": 3,
        "retry_delay": 5,
        "enable_detailed_metrics": False,
        "data_retention_days": 7
    }
    
    try:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if output_path.suffix == '.json':
            with open(output_path, 'w') as f:
                json.dump(template, f, indent=2)
        elif output_path.suffix in ['.yaml', '.yml']:
            with open(output_path, 'w') as f:
                yaml.dump(template, f, default_flow_style=False)
        elif output_path.suffix == '.toml':
            with open(output_path, 'w') as f:
                toml.dump(template, f)
        else:
            raise ValueError("Unsupported config file format")
        
        logger.info(f"Config template generated at {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to generate config template: {e}")
        return False

def validate_config(config: AgentConfig) -> bool:
    """Валидация конфигурации"""
    try:
        # Проверка обязательных полей
        if not config.agent_id or not config.api_key:
            logger.error("Agent ID and API Key are required")
            return False
        
        # Проверка URL
        if not config.api_url.startswith(('http://', 'https://')):
            logger.error("API URL must be a valid HTTP/HTTPS URL")
            return False
        
        # Проверка интервала тестирования
        if config.test_interval < 60:
            logger.warning("Test interval is very short (minimum 60 seconds)")
        
        return True
        
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        return False

# Утилитарные функции
def get_config_path() -> Optional[Path]:
    """Поиск существующего файла конфигурации"""
    config_locations = [
        Path.cwd() / "config" / "config.yaml",
        Path.cwd() / "config.yaml",
        Path.home() / ".config" / "internet-monitor" / "config.yaml",
        Path("/etc/internet-monitor/config.yaml")
    ]
    
    for config_path in config_locations:
        if config_path.exists():
            return config_path
    return None

def print_config(config: AgentConfig) -> None:
    """Вывод текущей конфигурации (без чувствительных данных)"""
    config_dict = config.dict()
    # Маскируем чувствительные данные
    if config_dict.get('api_key'):
        config_dict['api_key'] = '***' + config_dict['api_key'][-4:]
    
    print("Current configuration:")
    for key, value in config_dict.items():
        print(f"  {key}: {value}")

# Пример использования
if __name__ == "__main__":
    # Загрузка конфигурации
    config = load_config()
    
    if validate_config(config):
        print_config(config)
    else:
        print("Invalid configuration")
        exit(1)
