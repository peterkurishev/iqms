#!/usr/bin/env python3
import time
import os
import logging
import requests
from utils.network_tests import run_network_test
from utils.config_loader import load_config, validate_config


logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("InternetMonitorAgent")

def main():
    config = load_config()

    # Валидация
    if not validate_config(config):
        logger.error("Invalid configuration")
        return
        
    # Использование конфигурации
    logger.setLevel(config.log_level)
        
    
    while True:
        try:
            logger.info("Starting network measurement cycle")
            results = run_network_test(config)
            logger.debug(f"Test results: {results}")
            
            requests.post(f"{config.API_URL}/measurements", json=results)
            
            logger.info(f"Measurement completed. Sleeping for {config.MEASUREMENT_INTERVAL} seconds")
            time.sleep(config.MEASUREMENT_INTERVAL)
            
        except Exception as e:
            logger.error(f"Critical error: {str(e)}", exc_info=True)
            time.sleep(60)  # Пауза перед повтором

if __name__ == "__main__":
    main()
