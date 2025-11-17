# browphish/src/cli/menus/captured_data_menu.py

import logging
from colorama import Fore, Style
from cli.utils import prompt_for_input

logger = logging.getLogger("browphish.cli.captured_data_menu")

def display_captured_data_menu() -> str:
    """Visualizza il menu per la gestione dei dati catturati."""
    print(f"\n{Fore.LIGHTRED_EX}{'═' * 50}")
    print(f"█ {Fore.WHITE}{'DATI CATTURATI - MENU':^46}{Fore.LIGHTRED_EX} █")
    print(f"{'═' * 50}{Style.RESET_ALL}")
    print(f"{Fore.LIGHTRED_EX}1.{Style.RESET_ALL} Visualizza Log di Accesso")
    print(f"{Fore.LIGHTRED_EX}2.{Style.RESET_ALL} Visualizza Log Credenziali")
    print(f"{Fore.LIGHTRED_EX}3.{Style.RESET_ALL} Statistiche Generali")
    print(f"\n{Fore.LIGHTRED_EX}0.{Style.RESET_ALL} Torna al Menu Principale")
    
    return prompt_for_input(f"{Fore.LIGHTRED_EX}\nScelta: {Style.RESET_ALL}")

def handle_captured_data_choice(choice: str, db_manager) -> bool:
    """Gestisce la scelta dell'utente nel menu dei dati catturati."""
    match choice:
        case "1":
            show_access_logs(db_manager)
            return True
        case "2":
            show_credentials_logs(db_manager)
            return True
        case "3":
            show_general_stats(db_manager)
            return True
        case "0":
            return False
        case _:
            print(f"{Fore.RED}Scelta non valida. Riprova.{Style.RESET_ALL}")
            return True

def show_access_logs(db_manager) -> None:
    """Visualizza i log di accesso senza credenziali."""
    print(f"\n{Fore.LIGHTRED_EX}--- LOG DI ACCESSO ---{Style.RESET_ALL}")
    db_manager.visualizza_log_accesso()

def show_credentials_logs(db_manager) -> None:
    """Visualizza i log delle credenziali catturate."""
    print(f"\n{Fore.LIGHTRED_EX}--- LOG CREDENZIALI ---{Style.RESET_ALL}")
    db_manager.visualizza_dati_catturati()

def show_general_stats(db_manager) -> None:
    """Visualizza statistiche generali."""
    print(f"\n{Fore.LIGHTRED_EX}--- STATISTICHE GENERALI ---{Style.RESET_ALL}")
    stats = db_manager.get_phishing_stats()
    print(f"{Fore.WHITE}Campagne totali: {stats['total_campaigns']}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Pagine totali: {stats['total_pages']}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Credenziali catturate: {stats['total_credentials']}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Credenziali oggi: {stats['today_credentials']}{Style.RESET_ALL}")
    
    # Statistiche aggiuntive per gli accessi
    access_stats = db_manager.get_access_stats()
    print(f"{Fore.YELLOW}Accessi totali: {access_stats['total_accesses']}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Accessi oggi: {access_stats['today_accesses']}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}IP unici: {access_stats['unique_ips']}{Style.RESET_ALL}") 