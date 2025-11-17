# browphish/src/modules/web_pages/__init__.py

# Importa tutti i moduli web_pages disponibili
from . import page_generator
from . import web_server
from . import server_manager

__all__ = [
    'page_generator',
    'web_server',
    'server_manager'
]
