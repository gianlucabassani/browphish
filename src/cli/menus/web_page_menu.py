# browphish/src/cli/menus/web_page_menu.py

import logging
from colorama import Fore, Style
from pathlib import Path

# Importa le funzioni dal modulo di generazione pagine
from modules.web_pages.page_generator import clone_webpage, save_phishing_page_to_db # useremo una funzione di salvataggio nel db
from cli.utils import clear_screen, prompt_for_input
from db.manager import DatabaseManager

logger = logging.getLogger("browphish.cli.web_page_menu")

db_manager = DatabaseManager.get_instance()

def display_web_page_menu() -> str:
    """Visualizza il menu di gestione delle pagine web di phishing."""
    #clear_screen()
    print(f"{Fore.LIGHTRED_EX}{'═' * 40}")
    print(f"█ {Fore.WHITE}{'GESTIONE PAGINE PHISHING':^36}{Fore.LIGHTWHITE_EX} █")
    print(f"{'═' * 40}{Style.RESET_ALL}")
    print(f"{Fore.LIGHTRED_EX}1.{Style.RESET_ALL} Clona Pagina Web (Genera Pagina Phishing)")
    print(f"{Fore.LIGHTRED_EX}2.{Style.RESET_ALL} Visualizza Pagine Esistenti")
    print(f"{Fore.LIGHTRED_EX}3.{Style.RESET_ALL} Elimina Pagina Phishing")
    print(f"{Fore.LIGHTRED_EX}0.{Style.RESET_ALL} Torna al Menu Principale")
    return prompt_for_input("\nScelta: ")

def handle_web_page_choice(choice: str):
    """Gestisce la scelta dell'utente nel menu delle pagine web."""
    match choice:
        case "1":
            clone_and_generate_page(choice)
        case "2":
            list_existing_pages(choice)
        case "3":
            delete_phishing_page(choice)
        case "0":
            print(f"{Fore.LIGHTRED_EX}Tornando al menu principale...{Style.RESET_ALL}")
            return
        case _:
            print(f"{Fore.RED}Scelta non valida. Riprova.{Style.RESET_ALL}")

def clone_and_generate_page(choice: str):
    """Funzione per clonare una pagina web e generare una pagina di phishing."""
    print(f"\n{Fore.LIGHTRED_EX}--- CLONA PAGINA WEB ---{Style.RESET_ALL}")
    original_url = prompt_for_input(f"{Fore.WHITE}Inserisci l'URL della pagina da clonare (es. https://example.com/login): ")
    if not original_url:
        print(f"{Fore.RED}URL non specificato. Operazione annullata.{Style.RESET_ALL}")
        return

    save_dir = Path("data/captured_pages")
    save_dir.mkdir(parents=True, exist_ok=True)

    page_name = prompt_for_input(f"{Fore.WHITE}Nome per la pagina di phishing (es. 'google_login_phish'): ")
    if not page_name:
        print(f"{Fore.RED}Nome pagina non specificato. Operazione annullata.{Style.RESET_ALL}")
        return

    try:
        cloned_file_path = clone_webpage(original_url, page_name, save_dir)
        if cloned_file_path:
            print(f"{Fore.WHITE}✓ Pagina '{page_name}' clonata e salvata in: {cloned_file_path}{Style.RESET_ALL}")
            campaign_id = None
            save_phishing_page_to_db(db_manager, campaign_id, page_name, original_url, str(cloned_file_path))
            print(f"{Fore.WHITE}✓ Dettagli pagina salvati nel database.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ Impossibile clonare la pagina.{Style.RESET_ALL}")
    except Exception as e:
        logger.error(f"Errore durante la clonazione della pagina: {e}", exc_info=True)
        print(f"{Fore.RED}✗ Si è verificato un errore: {e}{Style.RESET_ALL}")

def list_existing_pages(choice: str):
    """Visualizza le pagine di phishing esistenti dal database."""
    print(f"\n{Fore.LIGHTRED_EX}--- PAGINE PHISHING ESISTENTI ---{Style.RESET_ALL}")
    query = "SELECT id, name, original_url, cloned_path, created_at FROM phishing_pages;"
    pages = db_manager.execute_query(query)

    if not pages:
        print(f"{Fore.YELLOW}Nessuna pagina di phishing trovata.{Style.RESET_ALL}")
        return

    from tabulate import tabulate
    headers = ["ID", "Nome Pagina", "URL Originale", "Percorso Clonazione", "Creata Il"]
    table_data = [
        [page['id'], page['name'], page['original_url'], page['cloned_path'], page['created_at']]
        for page in pages
    ]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

def delete_phishing_page(choice: str):
    """Elimina una pagina di phishing dal database e dal filesystem."""
    list_existing_pages(choice)
    pages = db_manager.execute_query("SELECT id FROM phishing_pages;")
    if not pages:
        return

    page_id = prompt_for_input("Inserisci l'ID della pagina da eliminare (0 per annullare): ")
    try:
        page_id = int(page_id)
        if page_id == 0:
            print(f"{Fore.YELLOW}Operazione annullata.{Style.RESET_ALL}")
            return
    except ValueError:
        print(f"{Fore.RED}ID non valido. Operazione annullata.{Style.RESET_ALL}")
        return

    query = "SELECT cloned_path FROM phishing_pages WHERE id = ?;"
    result = db_manager.execute_query(query, (page_id,))
    if not result:
        print(f"{Fore.RED}Pagina con ID {page_id} non trovata.{Style.RESET_ALL}")
        return

    cloned_path_str = result[0]['cloned_path']
    cloned_file_path = Path(cloned_path_str)

    confirm = prompt_for_input(
        f"{Fore.YELLOW}Confermi l'eliminazione della pagina e del file '{cloned_file_path.name}'? (s/N): {Style.RESET_ALL}"
    ).lower()
    if confirm != 's':
        print(f"{Fore.YELLOW}Operazione annullata.{Style.RESET_ALL}")
        return

    try:
        if cloned_file_path.exists():
            cloned_file_path.unlink()
            print(f"{Fore.WHITE}✓ File {cloned_file_path.name} eliminato.{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠ File non trovato sul disco, solo eliminazione dal database.{Style.RESET_ALL}")

        delete_query = "DELETE FROM phishing_pages WHERE id = ?;"
        db_manager.execute_query(delete_query, (page_id,))
        print(f"{Fore.WHITE}✓ Pagina con ID {page_id} eliminata dal database.{Style.RESET_ALL}")

    except Exception as e:
        logger.error(f"Errore durante l'eliminazione della pagina: {e}", exc_info=True)
        print(f"{Fore.RED}✗ Si è verificato un errore durante l'eliminazione: {e}{Style.RESET_ALL}")

