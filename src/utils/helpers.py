import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

# Logging avanzato
LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'tracking.log')

def setup_logger():
    logger = logging.getLogger('browphish')
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(LOG_PATH, maxBytes=1000000, backupCount=3, encoding='utf-8')
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    if not logger.hasHandlers():
        logger.addHandler(handler)
    return logger

# Configurazione
ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')

def load_config():
    load_dotenv(ENV_PATH)
    config = {
        'HUNTERIO_API_KEY': os.getenv('HUNTERIO_API_KEY'),
        'SHODAN_API_KEY': os.getenv('SHODAN_API_KEY'),
        'WHOISXML_API_KEY': os.getenv('WHOISXML_API_KEY'),
        'HIBP_API_KEY': os.getenv('HIBP_API_KEY'),
        'VIRUSTOTAL_API_KEY': os.getenv('VIRUSTOTAL_API_KEY'),
        'SECURITYTRAILS_API_KEY': os.getenv('SECURITYTRAILS_API_KEY'),
    }
    return config 