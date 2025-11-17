# browphish/src/cli/menus/reports_menu.py

import logging
from colorama import Fore, Style
from cli.utils import prompt_for_input

logger = logging.getLogger("browphish.cli.reports_menu")

def display_reports_menu() -> str:
    """Visualizza il menu per i report e statistiche."""
    print(f"\n{Fore.LIGHTRED_EX}{'═' * 50}")
    print(f"█ {Fore.WHITE}{'REPORT E STATISTICHE':^46}{Fore.LIGHTRED_EX} █")
    print(f"{'═' * 50}{Style.RESET_ALL}")
    print(f"{Fore.LIGHTRED_EX}1.{Style.RESET_ALL} Report Campagne")
    print(f"{Fore.LIGHTRED_EX}2.{Style.RESET_ALL} Statistiche Dettagliate")
    print(f"{Fore.LIGHTRED_EX}3.{Style.RESET_ALL} Export Dati")
    print(f"{Fore.LIGHTRED_EX}4.{Style.RESET_ALL} Grafici e Visualizzazioni")
    print(f"\n{Fore.LIGHTRED_EX}0.{Style.RESET_ALL} Torna al Menu Principale")
    
    return prompt_for_input(f"{Fore.LIGHTRED_EX}\nScelta: {Style.RESET_ALL}")

def handle_reports_choice(choice: str, db_manager) -> bool:
    """Gestisce la scelta dell'utente nel menu dei report."""
    match choice:
        case "1":
            show_campaign_reports(db_manager)
            return True
        case "2":
            show_detailed_stats(db_manager)
            return True
        case "3":
            export_data(db_manager)
            return True
        case "4":
            show_charts_and_visualizations(db_manager)
            return True
        case "0":
            return False
        case _:
            print(f"{Fore.RED}Scelta non valida. Riprova.{Style.RESET_ALL}")
            return True

def show_campaign_reports(db_manager) -> None:
    """Mostra i report delle campagne."""
    print(f"\n{Fore.LIGHTRED_EX}--- REPORT CAMPAGNE ---{Style.RESET_ALL}")
    
    try:
        query = """
        SELECT 
            pc.id, pc.name, pc.status,
            COUNT(DISTINCT pp.id) as total_pages,
            COUNT(DISTINCT cc.id) as total_credentials,
            COUNT(DISTINCT cc.ip_address) as unique_ips,
            MAX(cc.timestamp) as last_capture
        FROM phishing_campaigns pc
        LEFT JOIN phishing_pages pp ON pc.id = pp.campaign_entity_id
        LEFT JOIN captured_credentials cc ON pc.id = cc.campaign_entity_id
        GROUP BY pc.id
        ORDER BY total_credentials DESC
        """
        
        campaigns = db_manager.execute_query(query)
        
        if not campaigns:
            print(f"{Fore.YELLOW}Nessuna campagna trovata.{Style.RESET_ALL}")
            return
        
        from tabulate import tabulate
        
        headers = ["ID", "Name", "Status", "Pages", "Credentials", "Unique IPs", "Last Capture"]
        table = []
        
        for c in campaigns:
            status_color = Fore.GREEN if c['status'] == 'active' else Fore.RED
            status = f"{status_color}{c['status']}{Style.RESET_ALL}"
            table.append([
                c['id'],
                c['name'],
                status,
                c['total_pages'] or 0,
                c['total_credentials'] or 0,
                c['unique_ips'] or 0,
                c['last_capture'] or 'N/A'
            ])
        
        print(tabulate(table, headers=headers, tablefmt="grid"))
        
    except ImportError:
        for c in campaigns:
            print(f"[{c['id']}] {c['name']} - {c['total_credentials'] or 0} credentials")
    except Exception as e:
        logger.error(f"Error generating campaign reports: {e}")
        print(f"{Fore.RED}✗ Errore: {e}{Style.RESET_ALL}")

def show_detailed_stats(db_manager) -> None:
    """Mostra statistiche dettagliate."""
    print(f"\n{Fore.LIGHTRED_EX}--- STATISTICHE DETTAGLIATE ---{Style.RESET_ALL}")
    
    try:
        # General stats
        stats = db_manager.get_phishing_stats()
        
        print(f"\n{Fore.LIGHTRED_EX}Statistiche Generali:{Style.RESET_ALL}")
        print(f"  Campagne totali: {stats.get('total_campaigns', 0)}")
        print(f"  Pagine totali: {stats.get('total_pages', 0)}")
        print(f"  Credenziali catturate: {stats.get('total_credentials', 0)}")
        print(f"  Credenziali oggi: {stats.get('today_credentials', 0)}")
        
        # IP statistics
        ip_stats = db_manager.fetch_one("""
            SELECT COUNT(DISTINCT ip_address) as unique_ips,
                   COUNT(*) as total_accesses
            FROM captured_credentials
        """)
        
        if ip_stats:
            print(f"\n{Fore.LIGHTRED_EX}Statistiche IP:{Style.RESET_ALL}")
            print(f"  IP unici: {ip_stats['unique_ips']}")
            print(f"  Accessi totali: {ip_stats['total_accesses']}")
        
        # Access stats
        access_stats = db_manager.get_access_stats()
        print(f"\n{Fore.LIGHTRED_EX}Statistiche Accessi:{Style.RESET_ALL}")
        print(f"  Accessi totali: {access_stats.get('total_accesses', 0)}")
        print(f"  Accessi oggi: {access_stats.get('today_accesses', 0)}")
        print(f"  IP unici: {access_stats.get('unique_ips', 0)}")
        
    except Exception as e:
        logger.error(f"Error generating detailed stats: {e}")
        print(f"{Fore.RED}✗ Errore: {e}{Style.RESET_ALL}")

def export_data(db_manager) -> None:
    """Esporta i dati in vari formati."""
    print(f"\n{Fore.LIGHTRED_EX}--- EXPORT DATI ---{Style.RESET_ALL}")
    
    print(f"{Fore.YELLOW}Formato di esportazione:{Style.RESET_ALL}")
    print(f"1. CSV")
    print(f"2. JSON")
    print(f"0. Annulla")
    
    choice = prompt_for_input(f"{Fore.LIGHTRED_EX}Scelta: {Style.RESET_ALL}").strip()
    
    if choice == "1":
        export_to_csv(db_manager)
    elif choice == "2":
        export_to_json(db_manager)
    elif choice == "0":
        print(f"{Fore.YELLOW}Operazione annullata.{Style.RESET_ALL}")

def export_to_csv(db_manager) -> None:
    """Export credentials to CSV"""
    try:
        import csv
        from datetime import datetime
        
        filename = f"browphish_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        credentials = db_manager.execute_query("""
            SELECT username, email, password, ip_address, timestamp
            FROM captured_credentials
            WHERE username IS NOT NULL OR password IS NOT NULL OR email IS NOT NULL
            ORDER BY timestamp DESC
        """)
        
        if not credentials:
            print(f"{Fore.YELLOW}Nessuna credenziale da esportare.{Style.RESET_ALL}")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Username', 'Email', 'Password', 'IP Address', 'Timestamp'])
            for c in credentials:
                writer.writerow([
                    c['username'] or '',
                    c['email'] or '',
                    c['password'] or '',
                    c['ip_address'] or '',
                    c['timestamp'] or ''
                ])
        
        print(f"{Fore.GREEN}✓ Dati esportati in: {filename}{Style.RESET_ALL}")
        logger.info(f"Data exported to CSV: {filename}")
        
    except Exception as e:
        logger.error(f"Error exporting to CSV: {e}")
        print(f"{Fore.RED}✗ Errore esportazione: {e}{Style.RESET_ALL}")

def export_to_json(db_manager) -> None:
    """Export credentials to JSON"""
    try:
        import json
        from datetime import datetime
        
        filename = f"browphish_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        credentials = db_manager.execute_query("""
            SELECT username, email, password, ip_address, timestamp
            FROM captured_credentials
            WHERE username IS NOT NULL OR password IS NOT NULL OR email IS NOT NULL
            ORDER BY timestamp DESC
        """)
        
        if not credentials:
            print(f"{Fore.YELLOW}Nessuna credenziale da esportare.{Style.RESET_ALL}")
            return
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump([dict(c) for c in credentials], f, indent=2)
        
        print(f"{Fore.GREEN}✓ Dati esportati in: {filename}{Style.RESET_ALL}")
        logger.info(f"Data exported to JSON: {filename}")
        
    except Exception as e:
        logger.error(f"Error exporting to JSON: {e}")
        print(f"{Fore.RED}✗ Errore esportazione: {e}{Style.RESET_ALL}")

def show_charts_and_visualizations(db_manager) -> None:
    """Mostra grafici e visualizzazioni."""
    print(f"\n{Fore.LIGHTRED_EX}--- VISUALIZZAZIONI ---{Style.RESET_ALL}")
    
    try:
        # Top campaigns by credentials
        query = """
        SELECT pc.name, COUNT(cc.id) as count
        FROM phishing_campaigns pc
        LEFT JOIN captured_credentials cc ON pc.id = cc.campaign_entity_id
        GROUP BY pc.id
        ORDER BY count DESC
        LIMIT 5
        """
        
        campaigns = db_manager.execute_query(query)
        
        if not campaigns:
            print(f"{Fore.YELLOW}Nessun dato da visualizzare.{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.LIGHTRED_EX}Top 5 Campagne per Credenziali Catturate:{Style.RESET_ALL}\n")
        
        max_count = max(c['count'] or 0 for c in campaigns)
        
        for c in campaigns:
            count = c['count'] or 0
            bar_length = int((count / max_count * 30)) if max_count > 0 else 0
            bar = "█" * bar_length
            print(f"{c['name'][:20]:20} | {bar:30} | {count}")
        
    except Exception as e:
        logger.error(f"Error generating visualizations: {e}")
        print(f"{Fore.RED}✗ Errore: {e}{Style.RESET_ALL}") 
 