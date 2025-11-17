# browphish/src/cli/menus/__init__.py

# Importa tutti i menu disponibili
from . import web_page_menu
from . import captured_data_menu
from . import email_campaign_menu
from . import reports_menu
from . import system_options_menu
from . import campaign_menu

__all__ = [
    'web_page_menu',
    'captured_data_menu',
    'email_campaign_menu',
    'reports_menu',
    'system_options_menu',
    'campaign_menu'
]
