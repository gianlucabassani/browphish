# browphish/src/cli/phish_cli.py

import logging
import time
from colorama import Fore, Style

# Importazioni assolute per Browphish
from db.manager import DatabaseManager
from cli.utils import clear_screen, prompt_for_input

# Importa i moduli dei menu
from cli.menus import web_page_menu, captured_data_menu, email_campaign_menu, reports_menu, system_options_menu, campaign_menu
# Importa i moduli tecnici
from modules.web_pages.server_manager import start_phishing_server


logger = logging.getLogger("browphish.cli")

class BrowphishCLI:
    """
    Classe: BrowphishCLI
    Gestisce l'interfaccia a riga di comando per lo strumento di Phishing (ORCHESTRATORE).
    """
    def __init__(self):
        """
        Funzione: __init__
        Inizializza l'interfaccia a riga di comando di Browphish.
        """
        self.db_manager = DatabaseManager.get_instance(db_path="data/websites.db")
        self.db_manager.init_schema() # Inizializza lo schema del DB
        self.running = True # Flag per controllare il ciclo principale

    def show_banner(self):

        banner = fr"""
        {Fore.LIGHTRED_EX}
██████╗ ██████╗  ██████╗ ██╗    ██╗██████╗ ██╗  ██╗██╗███████╗██╗  ██╗
██╔══██╗██╔══██╗██╔═══██╗██║    ██║██╔══██╗██║  ██║██║██╔════╝██║  ██║
██████╔╝██████╔╝██║   ██║██║ █╗ ██║██████╔╝███████║██║███████╗███████║
██╔══██╗██╔══██╗██║   ██║██║███╗██║██╔═══╝ ██╔══██║██║╚════██║██╔══██║
██████╔╝██║  ██║╚██████╔╝╚███╔███╔╝██║     ██║  ██║██║███████║██║  ██║
╚═════╝ ╚═╝  ╚═╝ ╚═════╝  ╚══╝╚══╝ ╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝
        {Style.RESET_ALL}
        {Fore.RED}Phishing & Social Enineering Toolkit{Style.RESET_ALL}
        {Fore.LIGHTRED_EX}Version Pre-Alpha{Style.RESET_ALL}
        
{Fore.LIGHTRED_EX}{'='*60}{Style.RESET_ALL}
        """
        print(banner)
        time.sleep(0.5)
    
    def run(self):
        """
        Funzione: run
        Avvia il ciclo principale dell'applicazione CLI.
        """
        try: 
            self.show_banner()
           
            while self.running:
                try:
                    choice = self._display_main_menu()
                    self._handle_main_menu_choice(choice)

                    if self.running: # Non chiedere di premere INVIO se si sta uscendo
                        #input(f"{Fore.WHITE}\\nPremi INVIO per continuare...{Style.RESET_ALL}")
                        ...
                        
                except KeyboardInterrupt:
                    print(f"\n{Fore.WHITE}Grazie per aver usato Browphish! Arrivederci!{Style.RESET_ALL}")
                    return
        except KeyboardInterrupt:
                print(f"\n{Fore.WHITE}Grazie per aver usato Browphish! Arrivederci!{Style.RESET_ALL}")
                return
        except Exception as e:
                print(f"\n{Fore.RED}✗ Si è verificato un errore imprevisto: {e}{Style.RESET_ALL}")
                return

    def _display_main_menu(self) -> None:
        """Visualizza il menu principale di Browphish."""
        print(f"{Fore.LIGHTRED_EX}{'═' * 40}")
        print(f"█ {Fore.WHITE}{'BROWSINT - MENU PRINCIPALE':^36}{Fore.LIGHTRED_EX} █")
        print(f"{'═' * 40}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTRED_EX}1.{Style.RESET_ALL} Gestione Pagine Phishing")
        print(f"{Fore.LIGHTRED_EX}2.{Style.RESET_ALL} Gestione Campagne")
        print(f"{Fore.LIGHTRED_EX}3.{Style.RESET_ALL} Gestione Mailing")
        print(f"{Fore.LIGHTRED_EX}4.{Style.RESET_ALL} Visualizza Dati Catturati")
        print(f"{Fore.LIGHTRED_EX}5.{Style.RESET_ALL} Avvia Server di Phishing")
        print(f"{Fore.LIGHTRED_EX}6.{Style.RESET_ALL} Report e Statistiche (TODO)")
        print(f"{Fore.LIGHTRED_EX}7.{Style.RESET_ALL} Opzioni di Sistema (ALPHA)(API Keys, Config.)")
        print(f"\n{Fore.LIGHTRED_EX}0.{Style.RESET_ALL} Esci")
        return prompt_for_input(f"{Fore.LIGHTRED_EX}\nScelta: {Style.RESET_ALL}")

    def _handle_main_menu_choice(self, choice: str) -> None:
        """Gestisce la scelta dell'utente nel menu principale."""
        match choice:
            case "1":
                self._web_page_menu()
            case "2":
                self._campaign_menu()
            case "3":
                self._email_campaign_menu()
            case "4":
                self._captured_data_menu()
            case "5":
                self._start_phishing_server()
            case "6":
                self._reports_menu()
            case "7":
                self._system_options_menu()
            case "0":
                print(f"{Fore.RED}Uscita da Browphish. Arrivederci!{Style.RESET_ALL}")
                self.running = False
            case _:
                print(f"{Fore.WHITE}Scelta non valida. Riprova.{Style.RESET_ALL}")

    def _web_page_menu(self) -> None:
        """Menu per le funzionalità di gestione delle pagine web di phishing."""
        while True:
            choice = web_page_menu.display_web_page_menu()
            if choice == "0":
                break
            web_page_menu.handle_web_page_choice(choice)

    def _email_campaign_menu(self) -> None:
        """Menu per la gestione delle campagne email di phishing."""
        while True:
            choice = email_campaign_menu.display_email_campaign_menu()
            if not email_campaign_menu.handle_email_campaign_choice(choice, self.db_manager):
                break

    def _captured_data_menu(self) -> None:
        """Menu per la visualizzazione dei dati catturati suddiviso per tipo."""
        while True:
            choice = captured_data_menu.display_captured_data_menu()
            if not captured_data_menu.handle_captured_data_choice(choice, self.db_manager):
                break

    def _start_phishing_server(self) -> None:
        """Avvia il server di phishing Flask con scelta pagina."""
        start_phishing_server()

    def _reports_menu(self) -> None:
        """Menu per i report e statistiche."""
        while True:
            choice = reports_menu.display_reports_menu()
            if not reports_menu.handle_reports_choice(choice, self.db_manager):
                break

    def _system_options_menu(self) -> None:
        """Menu per le opzioni di sistema."""
        while True:
            choice = system_options_menu.display_system_options_menu()
            if not system_options_menu.handle_system_options_choice(choice, self.db_manager):
                break

    def _campaign_menu(self) -> None:
        """Menu per la gestione delle campagne di phishing."""
        while True:
            choice = campaign_menu.display_campaign_menu()
            if not campaign_menu.handle_campaign_choice(choice, self.db_manager):
                break