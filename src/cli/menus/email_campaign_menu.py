# browphish/src/cli/menus/email_campaign_menu.py

import logging
from colorama import Fore, Style
from cli.utils import prompt_for_input
from modules.email.email_sender import invia_email_phishing

logger = logging.getLogger("browphish.cli.email_campaign_menu")

def display_email_campaign_menu() -> str:
    """Visualizza il menu per la gestione delle campagne email (mailing)."""
    print(f"\n{Fore.LIGHTRED_EX}{'═' * 50}")
    print(f"█ {Fore.WHITE}{'GESTIONE CAMPAGNE MAILING':^46}{Fore.LIGHTRED_EX} █")
    print(f"{'═' * 50}{Style.RESET_ALL}")
    print(f"{Fore.LIGHTRED_EX}1.{Style.RESET_ALL} Invia Email di Phishing")
    print(f"{Fore.LIGHTRED_EX}2.{Style.RESET_ALL} Crea Nuova Campagna Mailing")
    print(f"{Fore.LIGHTRED_EX}3.{Style.RESET_ALL} Visualizza Campagne Mailing")
    print(f"{Fore.LIGHTRED_EX}4.{Style.RESET_ALL} Gestisci Template Email")
    print(f"\n{Fore.LIGHTRED_EX}0.{Style.RESET_ALL} Torna al Menu Principale")
    return prompt_for_input(f"{Fore.LIGHTRED_EX}\nScelta: {Style.RESET_ALL}")

def handle_email_campaign_choice(choice: str, db_manager) -> bool:
    """Gestisce la scelta dell'utente nel menu delle campagne email (mailing)."""
    match choice:
        case "1":
            send_phishing_email()
            return True
        case "2":
            create_new_mailing_campaign(db_manager)
            return True
        case "3":
            view_mailing_campaigns(db_manager)
            return True
        case "4":
            manage_email_templates()
            return True
        case "0":
            return False
        case _:
            print(f"{Fore.RED}Scelta non valida. Riprova.{Style.RESET_ALL}")
            return True

def send_phishing_email() -> None:
    """Gestisce l'invio di email di phishing."""
    print(f"\n{Fore.RED}--- INVIO EMAIL PHISHING ---{Style.RESET_ALL}")
    destinatario = prompt_for_input("Email destinatario: ")
    oggetto = prompt_for_input("Oggetto email: ")
    corpo = prompt_for_input("Corpo email: ")
    try:
        invia_email_phishing(destinatario, oggetto, corpo)
        print(f"{Fore.LIGHTRED_EX}✓ Email inviata con successo (simulato).{Style.RESET_ALL}")
    except Exception as e:
        logger.error(f"Errore durante l'invio dell'email: {e}", exc_info=True)
        print(f"{Fore.RED}✗ Errore durante l'invio dell'email: {e}{Style.RESET_ALL}")

def create_new_mailing_campaign(db_manager) -> None:
    """Crea una nuova campagna mailing (solo nome, demo)."""
    print(f"\n{Fore.LIGHTRED_EX}--- CREA NUOVA CAMPAGNA MAILING ---{Style.RESET_ALL}")
    campaign_name = prompt_for_input("Nome per la nuova campagna mailing: ")
    if campaign_name:
        # Qui puoi aggiungere la logica di salvataggio nel DB se vuoi
        print(f"{Fore.LIGHTRED_EX}✓ Campagna mailing '{campaign_name}' creata (demo).{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}✗ Nome non valido.{Style.RESET_ALL}")

def view_mailing_campaigns(db_manager) -> None:
    """Visualizza le campagne mailing (demo)."""
    print(f"\n{Fore.LIGHTRED_EX}--- CAMPAGNE MAILING ---{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Funzionalità in sviluppo...{Style.RESET_ALL}")

def manage_email_templates() -> None:
    """Gestisce i template delle email."""
    print(f"\n{Fore.LIGHTRED_EX}--- GESTIONE TEMPLATE EMAIL ---{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Funzionalità in sviluppo...{Style.RESET_ALL}") 