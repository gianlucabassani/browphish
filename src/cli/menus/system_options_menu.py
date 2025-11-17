# browphish/src/cli/menus/system_options_menu.py

import logging
import os
from pathlib import Path
from colorama import Fore, Style
from cli.utils import prompt_for_input, clear_screen
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from db.manager import DatabaseManager

logger = logging.getLogger("browphish.cli.system_options_menu")

def display_system_options_menu() -> str:
    """Visualizza il menu per le opzioni di sistema."""
    print(f"\n{Fore.LIGHTRED_EX}{'═' * 50}")
    print(f"█ {Fore.WHITE}{'OPZIONI DI SISTEMA':^46}{Fore.LIGHTRED_EX} █")
    print(f"{'═' * 50}{Style.RESET_ALL}")
    print(f"{Fore.LIGHTRED_EX}1.{Style.RESET_ALL} Gestione API Keys")
    print(f"{Fore.LIGHTRED_EX}2.{Style.RESET_ALL} Configurazione Server")
    print(f"{Fore.LIGHTRED_EX}3.{Style.RESET_ALL} Gestione Backup Database")
    print(f"{Fore.LIGHTRED_EX}4.{Style.RESET_ALL} Log e Debug")
    print(f"{Fore.LIGHTRED_EX}5.{Style.RESET_ALL} Impostazioni Avanzate")
    print(f"\n{Fore.LIGHTRED_EX}0.{Style.RESET_ALL} Torna al Menu Principale")
    
    return prompt_for_input(f"{Fore.LIGHTRED_EX}\nScelta: {Style.RESET_ALL}")

def handle_system_options_choice(choice: str, db_manager) -> bool:
    """Gestisce la scelta dell'utente nel menu delle opzioni di sistema."""
    match choice:
        case "1":
            api_keys_menu()
            return True
        case "2":
            configure_server_settings()
            return True
        case "3":
            display_backup_menu(db_manager)
            return True
        case "4":
            log_and_debug_settings()
            return True
        case "5":
            advanced_settings()
            return True
        case "0":
            return False
        case _:
            print(f"{Fore.RED}Scelta non valida. Riprova.{Style.RESET_ALL}")
            return True

def api_keys_menu() -> None:
    """Menu per la gestione delle API keys."""
    while True:
        print(f"\n{Fore.LIGHTRED_EX}{'═' * 40}")
        print(f"█ {Fore.WHITE}{'GESTIONE API KEYS':^36}{Fore.LIGHTRED_EX} █")
        print(f"{'═' * 40}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTRED_EX}1.{Style.RESET_ALL} Visualizza API Keys configurate")
        print(f"{Fore.LIGHTRED_EX}2.{Style.RESET_ALL} Aggiungi/Aggiorna API Key")
        print(f"{Fore.LIGHTRED_EX}3.{Style.RESET_ALL} Rimuovi API Key")
        print(f"{Fore.LIGHTRED_EX}4.{Style.RESET_ALL} Test API Keys")
        print(f"\n{Fore.LIGHTRED_EX}0.{Style.RESET_ALL} Torna al menu Opzioni Generali")

        choice = prompt_for_input("\nScelta: ")
        
        match choice:
            case "1": 
                show_api_keys()
            case "2": 
                add_api_key()
            case "3": 
                remove_api_key()
            case "4": 
                test_api_keys()
            case "0": 
                break
            case _:
                print(f"{Fore.RED}✗ Scelta non valida")
                input(f"{Fore.LIGHTRED_EX}\nPremi INVIO per continuare...{Style.RESET_ALL}")

def display_db_info(db_manager: 'DatabaseManager') -> None:
    """Mostra informazioni sui database."""
    while True:
        print(f"\n{Fore.LIGHTRED_EX}{'═' * 40}")
        print(f"█ {Fore.WHITE}{'INFORMAZIONI DATABASE':^36}{Fore.LIGHTRED_EX} █")
        print(f"{'═' * 40}{Style.RESET_ALL}")
        
        print(f"{Fore.LIGHTRED_EX}1.{Style.RESET_ALL} Mostra info database phishing")
        print(f"{Fore.LIGHTRED_EX}2.{Style.RESET_ALL} Statistiche tabelle")
        print(f"{Fore.LIGHTRED_EX}0.{Style.RESET_ALL} Torna al menu precedente")
        
        choice = prompt_for_input("\nScelta: ").strip()
        
        if choice == "1":
            try:
                db_path = "data/browphish.db"
                if os.path.exists(db_path):
                    size_mb = os.path.getsize(db_path) / (1024 * 1024)
                    print(f"\n{Fore.LIGHTRED_EX}Database Phishing:{Style.RESET_ALL}")
                    print(f"  Percorso: {db_path}")
                    print(f"  Dimensione: {size_mb:.2f} MB")
                    
                    # Mostra le tabelle disponibili
                    tables = db_manager.get_all_table_names()
                    if tables:
                        print(f"  Tabelle ({len(tables)}):")
                        for table in tables:
                            try:
                                row_count = db_manager.fetch_one(f"SELECT COUNT(*) as count FROM {table}")
                                count = row_count['count'] if row_count else 0
                                print(f"    - {table} ({count} righe)")
                            except Exception as e:
                                print(f"    - {table} (errore lettura)")
                    else:
                        print(f"  {Fore.YELLOW}Nessuna tabella trovata{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}Database non trovato{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}Errore lettura info database: {e}{Style.RESET_ALL}")
            input(f"\n{Fore.LIGHTRED_EX}Premi INVIO per continuare...{Style.RESET_ALL}")
            
        elif choice == "2":
            try:
                tables = db_manager.get_all_table_names()
                if tables:
                    print(f"\n{Fore.LIGHTRED_EX}Statistiche Tabelle:{Style.RESET_ALL}")
                    for table in tables:
                        try:
                            row_count = db_manager.fetch_one(f"SELECT COUNT(*) as count FROM {table}")
                            count = row_count['count'] if row_count else 0
                            print(f"  {table}: {count} righe")
                        except Exception as e:
                            print(f"  {table}: errore lettura")
                else:
                    print(f"{Fore.YELLOW}Nessuna tabella trovata{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}Errore statistiche: {e}{Style.RESET_ALL}")
            input(f"\n{Fore.LIGHTRED_EX}Premi INVIO per continuare...{Style.RESET_ALL}")
            
        elif choice == "0":
            break

def display_backup_menu(db_manager):
    while True:
        print(f"\n{Fore.BLUE}{'═' * 40}")
        print(f"█ {Fore.WHITE}{'GESTIONE BACKUP':^36}{Fore.BLUE} █")
        print(f"{'═' * 40}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}1.{Style.RESET_ALL} Elenca backup disponibili")
        print(f"{Fore.YELLOW}2.{Style.RESET_ALL} Crea nuovo backup")
        print(f"{Fore.YELLOW}3.{Style.RESET_ALL} Ripristina da backup")
        print(f"{Fore.YELLOW}4.{Style.RESET_ALL} Elimina backup")
        print(f"\n{Fore.YELLOW}0.{Style.RESET_ALL} Torna al menu precedente")
        choice = prompt_for_input("Scelta: ").strip()
        if choice == "1":
            list_available_backups()
        elif choice == "2":
            perform_db_backup(db_manager)
        elif choice == "3":
            restore_from_backup(db_manager)
        elif choice == "4":
            delete_backup()
        elif choice == "0":
            break

def perform_db_backup(db_manager) -> None:
    clear_screen()
    print(f"\n{Fore.CYAN}--- CREA BACKUP ---{Style.RESET_ALL}")
    try:
        print(f"{Fore.CYAN}Creazione backup in corso...{Style.RESET_ALL}")
        db_path = getattr(db_manager, 'db_path', None) or "data/browphish.db"
        backup_dir = Path("data/databases/backups")
        backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"browphish_backup_{timestamp}.db"
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"{Fore.GREEN}✓ Backup creato con successo!{Style.RESET_ALL}")
        print(f"  Percorso: {backup_path}")
        logger.info(f"Database backup created: {backup_path}")
    except Exception as e:
        print(f"{Fore.RED}Errore imprevisto: {e}{Style.RESET_ALL}")
        logger.error(f"Unexpected error in backup: {e}", exc_info=True)
    prompt_for_input(f"\n{Fore.CYAN}Premi INVIO per continuare...{Style.RESET_ALL}")

def clear_query_cache(db_manager: 'DatabaseManager') -> None:
    """Svuota la cache delle query."""
    print(f"\n{Fore.LIGHTRED_EX}{'═' * 40}")
    print(f"█ {Fore.WHITE}{'GESTIONE CACHE':^36}{Fore.LIGHTRED_EX} █")
    print(f"{'═' * 40}{Style.RESET_ALL}")
    
    try:
        # Per ora, questa è una funzione placeholder
        # In futuro potrebbe gestire cache di query complesse
        print(f"{Fore.LIGHTRED_EX}✓ Cache delle query svuotata con successo{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}✗ Errore pulizia cache: {e}{Style.RESET_ALL}")
    
    input(f"\n{Fore.LIGHTRED_EX}Premi INVIO per continuare...{Style.RESET_ALL}")

def clear_specific_table(db_manager: 'DatabaseManager') -> None:
    """Svuota le tabelle del database."""
    while True:
        print(f"\n{Fore.LIGHTRED_EX}{'═' * 40}")
        print(f"█ {Fore.WHITE}{'GESTIONE TABELLE':^36}{Fore.LIGHTRED_EX} █")
        print(f"{'═' * 40}{Style.RESET_ALL}")
        
        print(f"{Fore.LIGHTRED_EX}1.{Style.RESET_ALL} Svuota tutte le tabelle")
        print(f"{Fore.LIGHTRED_EX}2.{Style.RESET_ALL} Svuota una tabella specifica")
        print(f"{Fore.LIGHTRED_EX}0.{Style.RESET_ALL} Torna al menu precedente")
        
        choice = prompt_for_input("\nScelta: ").strip()
        
        if choice == "1":
            print(f"{Fore.RED}⚠️ ATTENZIONE: Stai per eliminare TUTTI i dati dal database!{Style.RESET_ALL}")
            
            try:
                tables = db_manager.get_all_table_names()
                if tables:
                    print(f"\n{Fore.LIGHTRED_EX}Tabelle che verranno svuotate:{Style.RESET_ALL}")
                    for table in tables:
                        row_count = db_manager.fetch_one(f"SELECT COUNT(*) as count FROM {table}")
                        count = row_count['count'] if row_count else 0
                        print(f"  - {table} ({count} righe)")
                else:
                    print(f"{Fore.YELLOW}Nessuna tabella trovata{Style.RESET_ALL}")
                    input(f"\n{Fore.LIGHTRED_EX}Premi INVIO per continuare...{Style.RESET_ALL}")
                    continue
                    
                confirm = prompt_for_input(f"\n{Fore.RED}⚠️ Confermi di voler eliminare TUTTI i dati? (s/N): ").strip().lower()
                
                if confirm == 's':
                    double_confirm = prompt_for_input(f"{Fore.RED}⚠️ Questa azione non può essere annullata! Conferma nuovamente: (s/N) ").strip().lower()
                    if double_confirm == 's':
                        for table in tables:
                            try:
                                db_manager.execute_query(f"DELETE FROM {table}")
                                print(f"{Fore.LIGHTRED_EX}✓ Tabella {table} svuotata{Style.RESET_ALL}")
                            except Exception as e:
                                print(f"{Fore.RED}✗ Errore svuotamento {table}: {e}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}Operazione annullata{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}Operazione annullata{Style.RESET_ALL}")
                    
            except Exception as e:
                print(f"{Fore.RED}✗ Errore: {e}{Style.RESET_ALL}")
            
            input(f"\n{Fore.LIGHTRED_EX}Premi INVIO per continuare...{Style.RESET_ALL}")
            
        elif choice == "2":
            try:
                tables = db_manager.get_all_table_names()
                if not tables:
                    print(f"{Fore.YELLOW}Nessuna tabella trovata{Style.RESET_ALL}")
                    input(f"\n{Fore.LIGHTRED_EX}Premi INVIO per continuare...{Style.RESET_ALL}")
                    continue
                    
                print(f"\n{Fore.LIGHTRED_EX}Tabelle disponibili:{Style.RESET_ALL}")
                for i, table in enumerate(tables, 1):
                    row_count = db_manager.fetch_one(f"SELECT COUNT(*) as count FROM {table}")
                    count = row_count['count'] if row_count else 0
                    print(f"{i}. {table} ({count} righe)")
                
                table_choice = prompt_for_input("\nSeleziona numero tabella (0 per annullare): ").strip()
                
                if table_choice.isdigit() and 0 < int(table_choice) <= len(tables):
                    table_name = tables[int(table_choice)-1]
                    confirm = prompt_for_input(f"{Fore.RED}⚠️ Confermi di voler svuotare {table_name}? (s/N): ").strip().lower()
                    
                    if confirm == 's':
                        try:
                            db_manager.execute_query(f"DELETE FROM {table_name}")
                            print(f"{Fore.LIGHTRED_EX}✓ Tabella {table_name} svuotata con successo{Style.RESET_ALL}")
                        except Exception as e:
                            print(f"{Fore.RED}✗ Errore durante lo svuotamento: {e}{Style.RESET_ALL}")
                
            except Exception as e:
                print(f"{Fore.RED}✗ Errore: {e}{Style.RESET_ALL}")
            input(f"\n{Fore.LIGHTRED_EX}Premi INVIO per continuare...{Style.RESET_ALL}")
            
        elif choice == "0":
            break

def show_api_keys() -> None:
    """Visualizza le API keys configurate."""
    print(f"\n{Fore.LIGHTRED_EX}API Keys Configurate:{Style.RESET_ALL}")
    
    # Per ora, questa è una funzione placeholder
    # In futuro gestirà le API keys per servizi di phishing
    supported_services = [
        "email_sender", "smtp_server", "webhook_url", 
        "telegram_bot", "discord_webhook", "slack_webhook"
    ]
    
    print(f"{Fore.YELLOW}Funzionalità in sviluppo...{Style.RESET_ALL}")
    print(f"Servizi supportati: {', '.join(supported_services)}")
    
    input(f"\n{Fore.LIGHTRED_EX}Premi INVIO per continuare...{Style.RESET_ALL}")

def add_api_key() -> None:
    """Permette all'utente di aggiungere o modificare una API key."""
    print(f"\n{Fore.LIGHTRED_EX}Aggiungi/Modifica API Key{Style.RESET_ALL}")
    
    supported_services = {
        "email_sender": "EMAIL_SENDER_API_KEY",
        "smtp_server": "SMTP_SERVER_CONFIG",
        "webhook_url": "WEBHOOK_URL",
        "telegram_bot": "TELEGRAM_BOT_TOKEN",
        "discord_webhook": "DISCORD_WEBHOOK_URL",
        "slack_webhook": "SLACK_WEBHOOK_URL"
    }
    
    print("\nServizi supportati:")
    for i, (service, env_var) in enumerate(supported_services.items(), 1):
        print(f"{i}. {service} ({env_var})")
    
    print(f"{Fore.YELLOW}Funzionalità in sviluppo...{Style.RESET_ALL}")
    
    input(f"\n{Fore.LIGHTRED_EX}Premi INVIO per continuare...{Style.RESET_ALL}")

def remove_api_key() -> None:
    """Permette all'utente di rimuovere una API key."""
    print(f"\n{Fore.LIGHTRED_EX}Rimuovi API Key{Style.RESET_ALL}")
    
    print(f"{Fore.YELLOW}Funzionalità in sviluppo...{Style.RESET_ALL}")
    
    input(f"\n{Fore.LIGHTRED_EX}Premi INVIO per continuare...{Style.RESET_ALL}")

def test_api_keys() -> None:
    """Testa le API keys configurate."""
    print(f"\n{Fore.LIGHTRED_EX}Test API Keys{Style.RESET_ALL}")
    
    print(f"{Fore.YELLOW}Funzionalità in sviluppo...{Style.RESET_ALL}")
    
    input(f"\n{Fore.LIGHTRED_EX}Premi INVIO per continuare...{Style.RESET_ALL}")

def configure_server_settings() -> None:
    """Configura le impostazioni del server."""
    print(f"\n{Fore.LIGHTRED_EX}--- CONFIGURAZIONE SERVER ---{Style.RESET_ALL}")
    
    while True:
        print(f"\n{Fore.LIGHTRED_EX}{'═' * 40}")
        print(f"█ {Fore.WHITE}{'CONFIGURAZIONE SERVER':^36}{Fore.LIGHTRED_EX} █")
        print(f"{'═' * 40}{Style.RESET_ALL}")
        
        print(f"{Fore.LIGHTRED_EX}1.{Style.RESET_ALL} Impostazioni Porta Server")
        print(f"{Fore.LIGHTRED_EX}2.{Style.RESET_ALL} Configurazione SSL/TLS")
        print(f"{Fore.LIGHTRED_EX}3.{Style.RESET_ALL} Impostazioni Firewall")
        print(f"{Fore.LIGHTRED_EX}4.{Style.RESET_ALL} Configurazione Proxy")
        print(f"{Fore.LIGHTRED_EX}0.{Style.RESET_ALL} Torna al menu precedente")
        
        choice = prompt_for_input("\nScelta: ").strip()
        
        if choice == "1":
            print(f"{Fore.YELLOW}Configurazione porta server...{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Funzionalità in sviluppo...{Style.RESET_ALL}")
        elif choice == "2":
            print(f"{Fore.YELLOW}Configurazione SSL/TLS...{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Funzionalità in sviluppo...{Style.RESET_ALL}")
        elif choice == "3":
            print(f"{Fore.YELLOW}Configurazione firewall...{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Funzionalità in sviluppo...{Style.RESET_ALL}")
        elif choice == "4":
            print(f"{Fore.YELLOW}Configurazione proxy...{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Funzionalità in sviluppo...{Style.RESET_ALL}")
        elif choice == "0":
            break
        else:
            print(f"{Fore.RED}Scelta non valida{Style.RESET_ALL}")
        
        input(f"\n{Fore.LIGHTRED_EX}Premi INVIO per continuare...{Style.RESET_ALL}")

def list_available_backups() -> None:
    clear_screen()
    print(f"\n{Fore.CYAN}--- BACKUP DISPONIBILI ---{Style.RESET_ALL}")
    backup_dir = Path("data/databases/backups")
    if not backup_dir.exists():
        print(f"{Fore.YELLOW}Cartella backup non trovata.{Style.RESET_ALL}")
        prompt_for_input(f"\n{Fore.CYAN}Premi INVIO per continuare...{Style.RESET_ALL}")
        return
    backup_files = list(backup_dir.glob("*.db"))
    if not backup_files:
        print(f"{Fore.YELLOW}Nessun backup trovato.{Style.RESET_ALL}")
        prompt_for_input(f"\n{Fore.CYAN}Premi INVIO per continuare...{Style.RESET_ALL}")
        return
    backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    print(f"\n{Fore.BLUE}Backup trovati:{Style.RESET_ALL}")
    for i, backup_file in enumerate(backup_files, 1):
        size_mb = backup_file.stat().st_size / (1024 * 1024)
        creation_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
        date_str = creation_time.strftime('%d/%m/%Y alle %H:%M')
        print(f"{i}. {backup_file.name}")
        print(f"   Dimensione: {size_mb:.1f} MB")
        print(f"   Creato: {date_str}")
        print()
    prompt_for_input(f"\n{Fore.CYAN}Premi INVIO per continuare...{Style.RESET_ALL}")

def restore_from_backup(db_manager) -> None:
    clear_screen()
    print(f"\n{Fore.CYAN}--- RIPRISTINA DATABASE ---{Style.RESET_ALL}")
    backup_dir = Path("data/databases/backups")
    if not backup_dir.exists():
        print(f"{Fore.YELLOW}Cartella backup non trovata.{Style.RESET_ALL}")
        prompt_for_input(f"\n{Fore.CYAN}Premi INVIO per continuare...{Style.RESET_ALL}")
        return
    backup_files = list(backup_dir.glob("*.db"))
    if not backup_files:
        print(f"{Fore.YELLOW}Nessun backup disponibile.{Style.RESET_ALL}")
        prompt_for_input(f"\n{Fore.CYAN}Premi INVIO per continuare...{Style.RESET_ALL}")
        return
    backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    print(f"\n{Fore.BLUE}Scegli quale backup ripristinare:{Style.RESET_ALL}")
    for i, backup_file in enumerate(backup_files, 1):
        size_mb = backup_file.stat().st_size / (1024 * 1024)
        creation_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
        date_str = creation_time.strftime('%d/%m/%Y alle %H:%M')
        print(f"{i}. {backup_file.name} ({size_mb:.1f} MB) - {date_str}")
    try:
        choice = prompt_for_input(f"\n{Fore.CYAN}Numero del backup da ripristinare (0 per annullare): {Style.RESET_ALL}")
        if choice == "0":
            print(f"{Fore.YELLOW}Operazione annullata.{Style.RESET_ALL}")
            prompt_for_input(f"\n{Fore.CYAN}Premi INVIO per continuare...{Style.RESET_ALL}")
            return
        backup_number = int(choice)
        if backup_number < 1 or backup_number > len(backup_files):
            print(f"{Fore.RED}Numero non valido.{Style.RESET_ALL}")
            prompt_for_input(f"\n{Fore.CYAN}Premi INVIO per continuare...{Style.RESET_ALL}")
            return
        selected_backup = backup_files[backup_number - 1]
        print(f"\n{Fore.YELLOW}ATTENZIONE:{Style.RESET_ALL}")
        print(f"Il database attuale verrà sostituito con il backup '{selected_backup.name}'")
        print(f"Tutti i dati non salvati andranno persi!")
        confirm = prompt_for_input(f"\n{Fore.CYAN}Sei sicuro di voler procedere? (scrivi 'SI' per confermare): {Style.RESET_ALL}")
        if confirm.upper() != 'SI':
            print(f"{Fore.YELLOW}Operazione annullata.{Style.RESET_ALL}")
            prompt_for_input(f"\n{Fore.CYAN}Premi INVIO per continuare...{Style.RESET_ALL}")
            return
        print(f"\n{Fore.CYAN}Ripristino in corso...{Style.RESET_ALL}")
        db_manager.disconnect()  # Chiude tutte le connessioni
        main_db_path = getattr(db_manager, 'db_path', None) or "data/browphish.db"
        import shutil
        shutil.copy2(selected_backup, main_db_path)
        db_manager.init_schema()  # Riconnette e re-inizializza
        print(f"{Fore.GREEN}✓ Database ripristinato con successo!{Style.RESET_ALL}")
        logger.info(f"Database restored from backup: {selected_backup.name}")
    except ValueError:
        print(f"{Fore.RED}Devi inserire un numero.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Errore durante il ripristino: {e}{Style.RESET_ALL}")
        logger.error(f"Error during restore: {e}", exc_info=True)
        try:
            db_manager.init_schema()
        except:
            pass
    prompt_for_input(f"\n{Fore.CYAN}Premi INVIO per continuare...{Style.RESET_ALL}")

def delete_backup() -> None:
    clear_screen()
    print(f"\n{Fore.CYAN}--- ELIMINA BACKUP ---{Style.RESET_ALL}")
    backup_dir = Path("data/databases/backups")
    if not backup_dir.exists():
        print(f"{Fore.YELLOW}Cartella backup non trovata.{Style.RESET_ALL}")
        prompt_for_input(f"\n{Fore.CYAN}Premi INVIO per continuare...{Style.RESET_ALL}")
        return
    backup_files = list(backup_dir.glob("*.db"))
    if not backup_files:
        print(f"{Fore.YELLOW}Nessun backup da eliminare.{Style.RESET_ALL}")
        prompt_for_input(f"\n{Fore.CYAN}Premi INVIO per continuare...{Style.RESET_ALL}")
        return
    backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    print(f"\n{Fore.BLUE}Scegli quale backup eliminare:{Style.RESET_ALL}")
    for i, backup_file in enumerate(backup_files, 1):
        size_mb = backup_file.stat().st_size / (1024 * 1024)
        creation_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
        date_str = creation_time.strftime('%d/%m/%Y alle %H:%M')
        print(f"{i}. {backup_file.name} ({size_mb:.1f} MB) - {date_str}")
    try:
        choice = prompt_for_input(f"\n{Fore.CYAN}Numero del backup da eliminare (0 per annullare): {Style.RESET_ALL}")
        if choice == "0":
            print(f"{Fore.YELLOW}Operazione annullata.{Style.RESET_ALL}")
            prompt_for_input(f"\n{Fore.CYAN}Premi INVIO per continuare...{Style.RESET_ALL}")
            return
        backup_number = int(choice)
        if backup_number < 1 or backup_number > len(backup_files):
            print(f"{Fore.RED}Numero non valido.{Style.RESET_ALL}")
            prompt_for_input(f"\n{Fore.CYAN}Premi INVIO per continuare...{Style.RESET_ALL}")
            return
        backup_to_delete = backup_files[backup_number - 1]
        print(f"\n{Fore.YELLOW}Stai per eliminare: {backup_to_delete.name}{Style.RESET_ALL}")
        confirm = prompt_for_input(f"{Fore.CYAN}Sei sicuro? (scrivi 'SI' per confermare): {Style.RESET_ALL}")
        if confirm.upper() != 'SI':
            print(f"{Fore.YELLOW}Operazione annullata.{Style.RESET_ALL}")
            prompt_for_input(f"\n{Fore.CYAN}Premi INVIO per continuare...{Style.RESET_ALL}")
            return
        backup_to_delete.unlink()
        print(f"{Fore.GREEN}✓ Backup eliminato con successo.{Style.RESET_ALL}")
        logger.info(f"Backup deleted: {backup_to_delete.name}")
    except ValueError:
        print(f"{Fore.RED}Devi inserire un numero.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Errore durante l'eliminazione: {e}{Style.RESET_ALL}")
        logger.error(f"Error deleting backup: {e}", exc_info=True)
    prompt_for_input(f"\n{Fore.CYAN}Premi INVIO per continuare...{Style.RESET_ALL}")

def log_and_debug_settings() -> None:
    """Configura i log e le impostazioni di debug."""
    print(f"\n{Fore.LIGHTRED_EX}--- LOG E DEBUG ---{Style.RESET_ALL}")
    
    while True:
        print(f"\n{Fore.LIGHTRED_EX}{'═' * 40}")
        print(f"█ {Fore.WHITE}{'LOG E DEBUG':^36}{Fore.LIGHTRED_EX} █")
        print(f"{'═' * 40}{Style.RESET_ALL}")
        
        print(f"{Fore.LIGHTRED_EX}1.{Style.RESET_ALL} Visualizza Log Recenti")
        print(f"{Fore.LIGHTRED_EX}2.{Style.RESET_ALL} Configura Livello Log")
        print(f"{Fore.LIGHTRED_EX}3.{Style.RESET_ALL} Pulisci Log")
        print(f"{Fore.LIGHTRED_EX}4.{Style.RESET_ALL} Debug Mode")
        print(f"{Fore.LIGHTRED_EX}0.{Style.RESET_ALL} Torna al menu precedente")
        
        choice = prompt_for_input("\nScelta: ").strip()
        
        if choice == "1":
            show_recent_logs()
        elif choice == "2":
            configure_log_level()
        elif choice == "3":
            clear_logs()
        elif choice == "4":
            toggle_debug_mode()
        elif choice == "0":
            break
        else:
            print(f"{Fore.RED}Scelta non valida{Style.RESET_ALL}")

def show_recent_logs() -> None:
    """Mostra i log recenti."""
    print(f"\n{Fore.LIGHTRED_EX}Log Recenti:{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Funzionalità in sviluppo...{Style.RESET_ALL}")
    
    input(f"\n{Fore.LIGHTRED_EX}Premi INVIO per continuare...{Style.RESET_ALL}")

def configure_log_level() -> None:
    """Configura il livello dei log."""
    print(f"\n{Fore.LIGHTRED_EX}Configura Livello Log{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Funzionalità in sviluppo...{Style.RESET_ALL}")
    
    input(f"\n{Fore.LIGHTRED_EX}Premi INVIO per continuare...{Style.RESET_ALL}")

def clear_logs() -> None:
    """Pulisce i log."""
    print(f"\n{Fore.LIGHTRED_EX}Pulisci Log{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Funzionalità in sviluppo...{Style.RESET_ALL}")
    
    input(f"\n{Fore.LIGHTRED_EX}Premi INVIO per continuare...{Style.RESET_ALL}")

def toggle_debug_mode() -> None:
    """Attiva/disattiva la modalità debug."""
    print(f"\n{Fore.LIGHTRED_EX}Debug Mode{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Funzionalità in sviluppo...{Style.RESET_ALL}")
    
    input(f"\n{Fore.LIGHTRED_EX}Premi INVIO per continuare...{Style.RESET_ALL}")

def advanced_settings() -> None:
    """Impostazioni avanzate."""
    print(f"\n{Fore.LIGHTRED_EX}--- IMPOSTAZIONI AVANZATE ---{Style.RESET_ALL}")
    
    while True:
        print(f"\n{Fore.LIGHTRED_EX}{'═' * 40}")
        print(f"█ {Fore.WHITE}{'IMPOSTAZIONI AVANZATE':^36}{Fore.LIGHTRED_EX} █")
        print(f"{'═' * 40}{Style.RESET_ALL}")
        
        print(f"{Fore.LIGHTRED_EX}1.{Style.RESET_ALL} Configurazione Avanzata Database")
        print(f"{Fore.LIGHTRED_EX}2.{Style.RESET_ALL} Impostazioni Sicurezza")
        print(f"{Fore.LIGHTRED_EX}3.{Style.RESET_ALL} Configurazione Performance")
        print(f"{Fore.LIGHTRED_EX}4.{Style.RESET_ALL} Impostazioni Rete")
        print(f"{Fore.LIGHTRED_EX}0.{Style.RESET_ALL} Torna al menu precedente")
        
        choice = prompt_for_input("\nScelta: ").strip()
        
        if choice == "1":
            print(f"{Fore.YELLOW}Configurazione avanzata database...{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Funzionalità in sviluppo...{Style.RESET_ALL}")
        elif choice == "2":
            print(f"{Fore.YELLOW}Impostazioni sicurezza...{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Funzionalità in sviluppo...{Style.RESET_ALL}")
        elif choice == "3":
            print(f"{Fore.YELLOW}Configurazione performance...{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Funzionalità in sviluppo...{Style.RESET_ALL}")
        elif choice == "4":
            print(f"{Fore.YELLOW}Impostazioni rete...{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Funzionalità in sviluppo...{Style.RESET_ALL}")
        elif choice == "0":
            break
        else:
            print(f"{Fore.RED}Scelta non valida{Style.RESET_ALL}")
        
        input(f"\n{Fore.LIGHTRED_EX}Premi INVIO per continuare...{Style.RESET_ALL}") 