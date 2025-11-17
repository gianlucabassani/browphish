# browphish/src/modules/__init__.py

# Importa tutti i moduli disponibili
from . import campaign_managers
from . import email
from . import web_pages

__all__ = [
    'campaign_managers',
    'email',
    'web_pages'
]
