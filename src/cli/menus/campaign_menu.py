# browphish/src/cli/menus/campaign_menu.py

from colorama import Fore, Style
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime
from db.manager import DatabaseManager
from cli.utils import prompt_for_input, clear_screen
from modules.campaign_managers import campaign_manager

logger = logging.getLogger("browphish.campaign_menu")

def display_campaign_menu() -> str:
    """Visualizza il menu principale per la gestione delle campagne."""
    print(f"\n{Fore.LIGHTRED_EX}{'═' * 40}")
    print(f"█ {Fore.WHITE}{'GESTIONE CAMPAGNE':^36}{Fore.LIGHTRED_EX} █")
    print(f"{'═' * 40}{Style.RESET_ALL}")
    print(f"{Fore.LIGHTRED_EX}1.{Style.RESET_ALL} Crea nuova campagna")
    print(f"{Fore.LIGHTRED_EX}2.{Style.RESET_ALL} Modifica campagna")
    print(f"{Fore.LIGHTRED_EX}3.{Style.RESET_ALL} Elimina campagna")
    print()
    print(f"{Fore.LIGHTRED_EX}4.{Style.RESET_ALL} Avvia campagna (background)")
    print(f"{Fore.LIGHTRED_EX}5.{Style.RESET_ALL} Arresta campagna")
    print(f"{Fore.LIGHTRED_EX}6.{Style.RESET_ALL} Associa pagina a campagna")
    print()
    print(f"{Fore.LIGHTRED_EX}7.{Style.RESET_ALL} Visualizza tutte le campagne")
    print(f"{Fore.LIGHTRED_EX}8.{Style.RESET_ALL} Dettagli campagna")
    print(f"{Fore.LIGHTRED_EX}9.{Style.RESET_ALL} Campagne in esecuzione")    
    print(f"{Fore.LIGHTRED_EX}10.{Style.RESET_ALL} Configura SSL (cert/key) per campagna/entità")    
    print(f"\n{Fore.LIGHTRED_EX}0.{Style.RESET_ALL} Torna al menu principale")
    return prompt_for_input(f"\n{Fore.LIGHTRED_EX}Scelta: {Style.RESET_ALL}")

def handle_campaign_choice(choice: str, db_manager: DatabaseManager) -> bool:
    """Gestisce la scelta dell'utente nel menu delle campagne."""
    match choice:
        case "1":
            crea_nuova_campagna(db_manager)
        case "2":
            modifica_campagna(db_manager)
        case "3":
            elimina_campagna(db_manager)
        case "4":
            avvia_campagna(db_manager)
        case "5":
            arresta_campagna(db_manager)
        case "6":
            associa_pagina_campagna(db_manager)
        case "7":
            visualizza_tutte_campagne(db_manager)
        case "8":
            dettagli_campagna(db_manager)
        case "9":
            mostra_campagne_in_esecuzione()
        case "10":
            configura_ssl_paths(db_manager)
        case "0":
            return False
        case _:
            print(f"{Fore.RED}Scelta non valida. Riprova.{Style.RESET_ALL}")
    return True


def elimina_campagna(db_manager: DatabaseManager) -> None:
    """Elimina una campagna dal database."""
    campaigns = campaign_manager.get_campaigns(db_manager)
    print(f"\n{Fore.LIGHTRED_EX}{'═' * 50}")
    print(f"█ {Fore.WHITE}{'ELENCO CAMPAGNE':^46}{Fore.LIGHTRED_EX} █")
    print(f"{'═' * 50}{Style.RESET_ALL}")
    if not campaigns:
        print(f"{Fore.YELLOW}Nessuna campagna trovata.{Style.RESET_ALL}")
        return
    try:
        from tabulate import tabulate
        headers = [
            "ID", "Nome", "Descrizione", "Entità", "Tipo", "Status", "Creata il"
        ]
        table = []
        for campaign in campaigns:
            status_color = Fore.GREEN if campaign['status'] == 'active' else Fore.RED
            status = f"{status_color}{campaign['status']}{Style.RESET_ALL}"
            description = (campaign['description'][:30] + "...") if campaign['description'] and len(campaign['description']) > 30 else (campaign['description'] or "-")
            table.append([
                campaign['id'],
                campaign['name'],
                description,
                campaign['entity_name'],
                campaign['entity_type'],
                status,
                campaign['created_at']
            ])
        print(tabulate(table, headers=headers, tablefmt="grid"))
        print(f"\n{Fore.WHITE}Totale campagne: {len(campaigns)}{Style.RESET_ALL}")
    except ImportError:
        print("Lista campagne:")
        for campaign in campaigns:
            print(f"[{campaign['id']}] {campaign['name']} - {campaign['status']} - {campaign['created_at']}")

    id_canc = prompt_for_input(f"\n{Fore.LIGHTRED_EX}ID campagna da eliminare: {Style.RESET_ALL}")
    try:
        id_canc_int = int(id_canc)
        conferma = prompt_for_input(f"{Fore.YELLOW}Sei sicuro di voler eliminare la campagna ID {id_canc_int}? (s/N): {Style.RESET_ALL}")
        if conferma.lower() == 's':
            successo = campaign_manager.delete_campaign(id_canc_int, db_manager)
            if successo:
                print(f"{Fore.GREEN}✓ Campagna ID {id_canc_int} eliminata con successo.{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}✗ Errore nell'eliminazione della campagna ID {id_canc_int}.{Style.RESET_ALL}")
        else:
            print(f"{Fore.WHITE}Eliminazione campagna annullata.{Style.RESET_ALL}")
    except ValueError:
        print(f"{Fore.RED}✗ ID campagna non valido.{Style.RESET_ALL}")
    



def visualizza_tutte_campagne(db_manager: DatabaseManager) -> None:
    """Visualizza tutte le campagne in formato tabellare."""
    print(f"\n{Fore.LIGHTRED_EX}{'═' * 50}")
    print(f"█ {Fore.WHITE}{'ELENCO CAMPAGNE':^46}{Fore.LIGHTRED_EX} █")
    print(f"{'═' * 50}{Style.RESET_ALL}")
    campaigns = campaign_manager.get_campaigns(db_manager)
    if not campaigns:
        print(f"{Fore.YELLOW}Nessuna campagna trovata.{Style.RESET_ALL}")
        return
    try:
        from tabulate import tabulate
        headers = [
            "ID", "Nome", "Descrizione", "Entità", "Tipo", "Status", "Creata il"
        ]
        table = []
        for campaign in campaigns:
            status_color = Fore.GREEN if campaign['status'] == 'active' else Fore.RED
            status = f"{status_color}{campaign['status']}{Style.RESET_ALL}"
            description = (campaign['description'][:30] + "...") if campaign['description'] and len(campaign['description']) > 30 else (campaign['description'] or "-")
            table.append([
                campaign['id'],
                campaign['name'],
                description,
                campaign['entity_name'],
                campaign['entity_type'],
                status,
                campaign['created_at']
            ])
        print(tabulate(table, headers=headers, tablefmt="grid"))
        print(f"\n{Fore.WHITE}Totale campagne: {len(campaigns)}{Style.RESET_ALL}")
    except ImportError:
        print("Lista campagne:")
        for campaign in campaigns:
            print(f"[{campaign['id']}] {campaign['name']} - {campaign['status']} - {campaign['created_at']}")

def crea_nuova_campagna(db_manager: DatabaseManager) -> None:
    """Crea una nuova campagna di phishing."""
    print(f"\n{Fore.LIGHTRED_EX}{'═' * 40}")
    print(f"█ {Fore.WHITE}{'CREA NUOVA CAMPAGNA':^36}{Fore.LIGHTRED_EX} █")
    print(f"{'═' * 40}{Style.RESET_ALL}")
    try:
        nome = prompt_for_input(f"{Fore.WHITE}Nome della campagna: {Style.RESET_ALL}")
        if not nome.strip():
            print(f"{Fore.RED}✗ Il nome della campagna è obbligatorio.{Style.RESET_ALL}")
            return
        descrizione = prompt_for_input(f"{Fore.WHITE}Descrizione (opzionale): {Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Seleziona o crea l'entità per questa campagna:{Style.RESET_ALL}")
        print(f"{Fore.LIGHTRED_EX}1.{Style.RESET_ALL} Usa entità esistente")
        print(f"{Fore.LIGHTRED_EX}2.{Style.RESET_ALL} Crea nuova entità")
        scelta_entita = prompt_for_input(f"{Fore.LIGHTRED_EX}Scelta: {Style.RESET_ALL}")
        entity_id = None
        if scelta_entita == "1":
            entity_id = seleziona_entita_esistente(db_manager)
        elif scelta_entita == "2":
            entity_id = crea_nuova_entita(db_manager)
        else:
            print(f"{Fore.RED}✗ Scelta non valida.{Style.RESET_ALL}")
            return
        if not entity_id:
            print(f"{Fore.RED}✗ Impossibile ottenere l'ID dell'entità.{Style.RESET_ALL}")
            return
        campaign_id = campaign_manager.create_campaign(nome, descrizione if descrizione.strip() else None, entity_id, db_manager)
        print(f"\n{Fore.GREEN}✓ Campagna '{nome}' creata con successo! ID: {campaign_id}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}✗ Errore durante la creazione della campagna: {e}{Style.RESET_ALL}")
        logger.error(f"Errore creazione campagna: {e}")

def seleziona_entita_esistente(db_manager: DatabaseManager) -> Optional[int]:
    """Permette di selezionare un'entità esistente."""
    entities = db_manager.execute_query("SELECT id, name, type FROM entities ORDER BY name")
    if not entities:
        print(f"{Fore.YELLOW}Nessuna entità trovata nel database.{Style.RESET_ALL}")
        return None
    print(f"\n{Fore.WHITE}Entità disponibili:{Style.RESET_ALL}")
    for i, entity in enumerate(entities, 1):
        print(f"{Fore.LIGHTRED_EX}{i}.{Style.RESET_ALL} {entity['name']} ({entity['type']})")
    try:
        scelta = int(prompt_for_input(f"{Fore.LIGHTRED_EX}Seleziona entità (numero): {Style.RESET_ALL}"))
        if 1 <= scelta <= len(entities):
            return entities[scelta - 1]['id']
        else:
            print(f"{Fore.RED}✗ Selezione non valida.{Style.RESET_ALL}")
            return None
    except ValueError:
        print(f"{Fore.RED}✗ Input non valido.{Style.RESET_ALL}")
        return None

def crea_nuova_entita(db_manager: DatabaseManager) -> Optional[int]:
    """Crea una nuova entità."""
    print(f"\n{Fore.WHITE}Tipo di entità:{Style.RESET_ALL}")
    print(f"{Fore.LIGHTRED_EX}1.{Style.RESET_ALL} Dominio (company)")
    print(f"{Fore.LIGHTRED_EX}2.{Style.RESET_ALL} Persona (person)")
    tipo_scelta = prompt_for_input(f"{Fore.LIGHTRED_EX}Scelta: {Style.RESET_ALL}")
    if tipo_scelta == "1":
        dominio = prompt_for_input(f"{Fore.WHITE}Inserisci il dominio (es. example.com): {Style.RESET_ALL}")
        if not dominio.strip():
            print(f"{Fore.RED}✗ Il dominio è obbligatorio.{Style.RESET_ALL}")
            return None
        return db_manager.get_or_create_entity(dominio.strip(), "domain")
    elif tipo_scelta == "2":
        nome = prompt_for_input(f"{Fore.WHITE}Inserisci il nome/email della persona: {Style.RESET_ALL}")
        if not nome.strip():
            print(f"{Fore.RED}✗ Il nome è obbligatorio.{Style.RESET_ALL}")
            return None
        entity_type = "email" if "@" in nome else "username"
        return db_manager.get_or_create_entity(nome.strip(), entity_type)
    else:
        print(f"{Fore.RED}✗ Scelta non valida.{Style.RESET_ALL}")
        return None

def modifica_campagna(db_manager: DatabaseManager) -> None:
    """Modifica una campagna esistente."""
    print(f"\n{Fore.LIGHTRED_EX}{'═' * 40}")
    print(f"█ {Fore.WHITE}{'MODIFICA CAMPAGNA':^36}{Fore.LIGHTRED_EX} █")
    print(f"{'═' * 40}{Style.RESET_ALL}")
    campaigns = campaign_manager.get_campaigns(db_manager)
    if not campaigns:
        print(f"{Fore.YELLOW}Nessuna campagna trovata.{Style.RESET_ALL}")
        return
    print(f"\n{Fore.WHITE}Campagne disponibili:{Style.RESET_ALL}")
    for campaign in campaigns:
        status_color = Fore.GREEN if campaign['status'] == 'active' else Fore.RED
        print(f"{Fore.LIGHTRED_EX}[{campaign['id']}]{Style.RESET_ALL} {campaign['name']} - {status_color}{campaign['status']}{Style.RESET_ALL}")
    try:
        campaign_id = int(prompt_for_input(f"\n{Fore.LIGHTRED_EX}ID della campagna da modificare: {Style.RESET_ALL}"))
        campaign = campaign_manager.get_campaign_by_id(campaign_id, db_manager)
        if not campaign:
            print(f"{Fore.RED}✗ Campagna non trovata.{Style.RESET_ALL}")
            return
        print(f"\n{Fore.WHITE}Campagna selezionata: {campaign['name']}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Descrizione attuale: {campaign['description'] or 'N/A'}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Status attuale: {campaign['status']}{Style.RESET_ALL}")
        nuovo_nome = prompt_for_input(f"\n{Fore.WHITE}Nuovo nome (premi INVIO per mantenere '{campaign['name']}'): {Style.RESET_ALL}")
        if not nuovo_nome.strip():
            nuovo_nome = campaign['name']
        nuova_descrizione = prompt_for_input(f"{Fore.WHITE}Nuova descrizione (premi INVIO per mantenere): {Style.RESET_ALL}")
        if not nuova_descrizione.strip():
            nuova_descrizione = campaign['description']
        ok = campaign_manager.update_campaign(campaign_id, nuovo_nome, nuova_descrizione, db_manager)
        if ok:
            print(f"\n{Fore.GREEN}✓ Campagna aggiornata con successo!{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ Nessuna modifica effettuata.{Style.RESET_ALL}")
    except ValueError:
        print(f"{Fore.RED}✗ ID non valido.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}✗ Errore durante l'aggiornamento: {e}{Style.RESET_ALL}")
        logger.error(f"Errore modifica campagna: {e}")

def termina_campagna(db_manager: DatabaseManager) -> None:
    """Termina una campagna attiva."""
    print(f"\n{Fore.LIGHTRED_EX}{'═' * 40}")
    print(f"█ {Fore.WHITE}{'TERMINA CAMPAGNA':^36}{Fore.LIGHTRED_EX} █")
    print(f"{'═' * 40}{Style.RESET_ALL}")
    campaigns = [c for c in campaign_manager.get_campaigns(db_manager) if c['status'] == 'active']
    if not campaigns:
        print(f"{Fore.YELLOW}Nessuna campagna attiva trovata.{Style.RESET_ALL}")
        return
    print(f"\n{Fore.WHITE}Campagne attive:{Style.RESET_ALL}")
    for campaign in campaigns:
        print(f"{Fore.LIGHTRED_EX}[{campaign['id']}]{Style.RESET_ALL} {campaign['name']}")
    try:
        campaign_id = int(prompt_for_input(f"\n{Fore.LIGHTRED_EX}ID della campagna da terminare: {Style.RESET_ALL}"))
        campaign = campaign_manager.get_campaign_by_id(campaign_id, db_manager)
        if not campaign:
            print(f"{Fore.RED}✗ Campagna non trovata.{Style.RESET_ALL}")
            return
        if campaign['status'] != 'active':
            print(f"{Fore.YELLOW}⚠ La campagna '{campaign['name']}' non è attiva.{Style.RESET_ALL}")
            return
        conferma = prompt_for_input(f"\n{Fore.YELLOW}Sei sicuro di voler terminare la campagna '{campaign['name']}'? (s/N): {Style.RESET_ALL}")
        if conferma.lower() != 's':
            print(f"{Fore.WHITE}Operazione annullata.{Style.RESET_ALL}")
            return
        ok = campaign_manager.terminate_campaign(campaign_id, db_manager)
        if ok:
            print(f"\n{Fore.GREEN}✓ Campagna '{campaign['name']}' terminata con successo!{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ Nessuna modifica effettuata.{Style.RESET_ALL}")
    except ValueError:
        print(f"{Fore.RED}✗ ID non valido.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}✗ Errore durante la terminazione: {e}{Style.RESET_ALL}")
        logger.error(f"Errore terminazione campagna: {e}")

def elimina_campagna(db_manager: DatabaseManager) -> None:
    """Elimina una campagna dal database."""
    print(f"\n{Fore.LIGHTRED_EX}{'═' * 40}")
    print(f"█ {Fore.WHITE}{'ELIMINA CAMPAGNA':^36}{Fore.LIGHTRED_EX} █")
    print(f"{'═' * 40}{Style.RESET_ALL}")
    campaigns = campaign_manager.get_campaigns(db_manager)
    if not campaigns:
        print(f"{Fore.YELLOW}Nessuna campagna trovata.{Style.RESET_ALL}")
        return
    print(f"\n{Fore.WHITE}Campagne disponibili:{Style.RESET_ALL}")
    for campaign in campaigns:
        status_color = Fore.GREEN if campaign['status'] == 'active' else Fore.RED
        print(f"{Fore.LIGHTRED_EX}[{campaign['id']}]{Style.RESET_ALL} {campaign['name']} - {status_color}{campaign['status']}{Style.RESET_ALL}")
    try:
        campaign_id = int(prompt_for_input(f"\n{Fore.LIGHTRED_EX}ID della campagna da eliminare: {Style.RESET_ALL}"))
        campaign = campaign_manager.get_campaign_by_id(campaign_id, db_manager)
        if not campaign:
            print(f"{Fore.RED}✗ Campagna non trovata.{Style.RESET_ALL}")
            return
        print(f"\n{Fore.RED}⚠ ATTENZIONE: Eliminando questa campagna verranno eliminati anche:{Style.RESET_ALL}")
        print(f"  - Tutte le pagine phishing associate")
        print(f"  - Tutte le credenziali catturate")
        print(f"  - Tutti i dati correlati")
        conferma = prompt_for_input(f"\n{Fore.RED}Confermare cancellazione della campagna '{campaign['name']}'? (s/N): {Style.RESET_ALL}")
        if conferma.lower() != 's':
            print(f"{Fore.WHITE}Operazione annullata.{Style.RESET_ALL}")
            return
        ok = campaign_manager.delete_campaign(campaign_id, db_manager)
        if ok:
            print(f"\n{Fore.GREEN}✓ Campagna '{campaign['name']}' eliminata con successo!{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ Nessuna modifica effettuata.{Style.RESET_ALL}")
    except ValueError:
        print(f"{Fore.RED}✗ ID non valido.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}✗ Errore durante l'eliminazione: {e}{Style.RESET_ALL}")
        logger.error(f"Errore eliminazione campagna: {e}")

def dettagli_campagna(db_manager: DatabaseManager) -> None:
    """Mostra i dettagli completi di una campagna."""
    print(f"\n{Fore.LIGHTRED_EX}{'═' * 40}")
    print(f"█ {Fore.WHITE}{'DETTAGLI CAMPAGNA':^36}{Fore.LIGHTRED_EX} █")
    print(f"{'═' * 40}{Style.RESET_ALL}")
    campaigns = campaign_manager.get_campaigns(db_manager)
    if not campaigns:
        print(f"{Fore.YELLOW}Nessuna campagna trovata.{Style.RESET_ALL}")
        return
    print(f"\n{Fore.WHITE}Campagne disponibili:{Style.RESET_ALL}")
    for campaign in campaigns:
        print(f"{Fore.LIGHTRED_EX}[{campaign['id']}]{Style.RESET_ALL} {campaign['name']}")
    try:
        campaign_id = int(prompt_for_input(f"\n{Fore.LIGHTRED_EX}ID della campagna: {Style.RESET_ALL}"))
        campaign = campaign_manager.get_campaign_by_id(campaign_id, db_manager)
        if not campaign:
            print(f"{Fore.RED}✗ Campagna non trovata.{Style.RESET_ALL}")
            return
        stats = campaign_manager.get_campaign_stats(campaign_id, db_manager)
        pages = campaign_manager.get_campaign_pages(campaign_id, db_manager)
        status_color = Fore.GREEN if campaign['status'] == 'active' else Fore.RED
        print(f"\n{Fore.WHITE}═══ DETTAGLI CAMPAGNA ═══{Style.RESET_ALL}")
        print(f"{Fore.LIGHTRED_EX}ID:{Style.RESET_ALL} {campaign['id']}")
        print(f"{Fore.LIGHTRED_EX}Nome:{Style.RESET_ALL} {campaign['name']}")
        print(f"{Fore.LIGHTRED_EX}Descrizione:{Style.RESET_ALL} {campaign['description'] or 'N/A'}")
        print(f"{Fore.LIGHTRED_EX}Status:{Style.RESET_ALL} {status_color}{campaign['status']}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTRED_EX}Creata il:{Style.RESET_ALL} {campaign['created_at']}")
        print(f"{Fore.LIGHTRED_EX}Entità:{Style.RESET_ALL} {campaign['entity_name']} ({campaign['entity_type']})")
        if campaign.get('domain'):
            print(f"{Fore.LIGHTRED_EX}Dominio:{Style.RESET_ALL} {campaign['domain']}")
        print(f"\n{Fore.WHITE}═══ STATISTICHE ═══{Style.RESET_ALL}")
        if stats:
            print(f"{Fore.LIGHTRED_EX}Credenziali catturate:{Style.RESET_ALL} {stats['total_credentials']}")
            print(f"{Fore.LIGHTRED_EX}IP unici:{Style.RESET_ALL} {stats['unique_ips']}")
            print(f"{Fore.LIGHTRED_EX}Credenziali oggi:{Style.RESET_ALL} {stats['today_credentials']}")
        print(f"\n{Fore.WHITE}═══ PAGINE ASSOCIATE {Fore.LIGHTRED_EX}({len(pages) if pages else 0}){Style.RESET_ALL} ═══")
        if pages:
            for page in pages:
                print(f"  • {page['name']} ({page['original_url']}) - {page['created_at']}")
        else:
            print(f"  {Fore.YELLOW}Nessuna pagina associata{Style.RESET_ALL}")
    except ValueError:
        print(f"{Fore.RED}✗ ID non valido.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}✗ Errore durante il recupero dei dettagli: {e}{Style.RESET_ALL}")
        logger.error(f"Errore dettagli campagna: {e}")

def associa_pagina_campagna(db_manager: DatabaseManager) -> None:
    """Associa una pagina phishing esistente a una campagna."""
    print(f"\n{Fore.LIGHTRED_EX}{'═' * 40}")
    print(f"█ {Fore.WHITE}{'ASSOCIA PAGINA':^36}{Fore.LIGHTRED_EX} █")
    print(f"{'═' * 40}{Style.RESET_ALL}")
    campaigns = campaign_manager.get_campaigns(db_manager)
    if not campaigns:
        print(f"{Fore.YELLOW}Nessuna campagna trovata.{Style.RESET_ALL}")
        return
    print(f"\n{Fore.WHITE}Campagne disponibili:{Style.RESET_ALL}")
    for campaign in campaigns:
        status_color = Fore.GREEN if campaign['status'] == 'active' else Fore.RED
        print(f"{Fore.LIGHTRED_EX}[{campaign['id']}]{Style.RESET_ALL} {campaign['name']} - {status_color}{campaign['status']}{Style.RESET_ALL}")
    try:
        campaign_id = int(prompt_for_input(f"\n{Fore.LIGHTRED_EX}ID della campagna: {Style.RESET_ALL}"))
        campaign = campaign_manager.get_campaign_by_id(campaign_id, db_manager)
        if not campaign:
            print(f"{Fore.RED}✗ Campagna non trovata.{Style.RESET_ALL}")
            return
        pages_query = """
        SELECT pp.id, pp.name, pp.original_url, e.name as page_entity_name
        FROM phishing_pages pp
        JOIN entities e ON pp.page_entity_id = e.id
        WHERE pp.campaign_entity_id IS NULL OR pp.campaign_entity_id != ?
        ORDER BY pp.name
        """
        pages = db_manager.execute_query(pages_query, (campaign_id,))
        if not pages:
            print(f"{Fore.YELLOW}Nessuna pagina disponibile per l'associazione.{Style.RESET_ALL}")
            return
        print(f"\n{Fore.WHITE}Pagine disponibili:{Style.RESET_ALL}")
        for page in pages:
            print(f"{Fore.LIGHTRED_EX}[{page['id']}]{Style.RESET_ALL} {page['name']} - {page['original_url']}")
        page_id = int(prompt_for_input(f"\n{Fore.LIGHTRED_EX}ID della pagina da associare: {Style.RESET_ALL}"))
        page = db_manager.fetch_one("SELECT name FROM phishing_pages WHERE id = ?", (page_id,))
        if not page:
            print(f"{Fore.RED}✗ Pagina non trovata.{Style.RESET_ALL}")
            return
        ok = campaign_manager.associate_page_to_campaign(campaign_id, page_id, db_manager)
        if ok:
            print(f"\n{Fore.GREEN}✓ Pagina '{page['name']}' associata alla campagna '{campaign['name']}'!{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ Nessuna modifica effettuata.{Style.RESET_ALL}")
    except ValueError:
        print(f"{Fore.RED}✗ ID non valido.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}✗ Errore durante l'associazione: {e}{Style.RESET_ALL}")
        logger.error(f"Errore associazione pagina: {e}")

def avvia_campagna(db_manager: DatabaseManager) -> None:
    """Avvia una campagna in background con il server web."""
    print(f"\n{Fore.LIGHTRED_EX}{'═' * 40}")
    print(f"█ {Fore.WHITE}{'AVVIA CAMPAGNA':^36}{Fore.LIGHTRED_EX} █")
    print(f"{'═' * 40}{Style.RESET_ALL}")


def configura_ssl_paths(db_manager: DatabaseManager) -> None:
    """Interfaccia CLI per impostare/cancellare i percorsi SSL per campagne o entità (domini)."""
    from modules.campaign_managers import campaign_manager

    print(f"\n{Fore.LIGHTRED_EX}{'═' * 40}")
    print(f"█ {Fore.WHITE}{'CONFIGURA SSL PER CAMPAGNA/ENTITÀ':^36}{Fore.LIGHTRED_EX} █")
    print(f"{'═' * 40}{Style.RESET_ALL}")

    print(f"{Fore.LIGHTRED_EX}1.{Style.RESET_ALL} Imposta/aggiorna percorsi per una campagna")
    print(f"{Fore.LIGHTRED_EX}2.{Style.RESET_ALL} Imposta/aggiorna percorsi per un'entità (dominio)")
    print(f"{Fore.LIGHTRED_EX}3.{Style.RESET_ALL} Visualizza percorsi SSL per una campagna")
    print(f"{Fore.RED}0.{Style.RESET_ALL} Annulla")

    choice = prompt_for_input(f"\n{Fore.LIGHTRED_EX}Scelta: {Style.RESET_ALL}")

    try:
        if choice == '1':
            campaigns = campaign_manager.get_campaigns(db_manager)
            if not campaigns:
                print(f"{Fore.YELLOW}Nessuna campagna trovata.{Style.RESET_ALL}")
                return
            print(f"\n{Fore.WHITE}Campagne disponibili:{Style.RESET_ALL}")
            for campaign in campaigns:
                print(f"{Fore.LIGHTRED_EX}[{campaign['id']}]{Style.RESET_ALL} {campaign['name']}")
            campaign_id = int(prompt_for_input(f"\n{Fore.LIGHTRED_EX}ID campagna: {Style.RESET_ALL}"))
            camp = campaign_manager.get_campaign_by_id(campaign_id, db_manager)
            if not camp:
                print(f"{Fore.RED}✗ Campagna non trovata.{Style.RESET_ALL}")
                return
            print(f"\nPercorsi attuali: cert={camp.get('ssl_cert_path') or '-'} key={camp.get('ssl_key_path') or '-'}")
            cert = prompt_for_input(f"Percorso certificato (PATH) o INVIO per mantenere, 'clear' per rimuovere: ")
            key = prompt_for_input(f"Percorso chiave (PATH) o INVIO per mantenere, 'clear' per rimuovere: ")

            new_cert = camp.get('ssl_cert_path') if cert.strip() == '' else (None if cert.strip().lower() == 'clear' else cert.strip())
            new_key = camp.get('ssl_key_path') if key.strip() == '' else (None if key.strip().lower() == 'clear' else key.strip())

            # Verifica esistenza file (se forniti) e richiedi conferma aggiuntiva se non trovati
            from pathlib import Path
            for p_label, p_val in [('cert', new_cert), ('key', new_key)]:
                if p_val and not Path(p_val).exists():
                    warn = prompt_for_input(f"{Fore.YELLOW}Attenzione: il file {p_label} '{p_val}' non esiste. Continuare? (s/N): {Style.RESET_ALL}")
                    if warn.lower() != 's':
                        print(f"{Fore.WHITE}Operazione annullata dall'utente.{Style.RESET_ALL}")
                        return

            confirmed = prompt_for_input(f"Confermi l'aggiornamento? (s/N): ")
            if confirmed.lower() == 's':
                ok = campaign_manager.update_campaign_ssl_paths(campaign_id, new_cert, new_key, db_manager)
                if ok:
                    print(f"{Fore.GREEN}✓ Percorsi aggiornati per la campagna ID {campaign_id}.{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}✗ Nessuna modifica effettuata.{Style.RESET_ALL}")
            else:
                print(f"{Fore.WHITE}Operazione annullata.{Style.RESET_ALL}")

        elif choice == '2':
            entities = db_manager.execute_query("SELECT id, name, type, domain, ssl_cert_path, ssl_key_path FROM entities ORDER BY name")
            if not entities:
                print(f"{Fore.YELLOW}Nessuna entità trovata.{Style.RESET_ALL}")
                return
            print(f"\n{Fore.WHITE}Entità disponibili:{Style.RESET_ALL}")
            for e in entities:
                print(f"{Fore.LIGHTRED_EX}[{e['id']}]{Style.RESET_ALL} {e['name']} ({e['type']}) cert={e.get('ssl_cert_path') or '-'} key={e.get('ssl_key_path') or '-'}")
            entity_id = int(prompt_for_input(f"\n{Fore.LIGHTRED_EX}ID entità: {Style.RESET_ALL}"))
            ent = db_manager.fetch_one("SELECT id, name, ssl_cert_path, ssl_key_path FROM entities WHERE id = ?", (entity_id,))
            if not ent:
                print(f"{Fore.RED}✗ Entità non trovata.{Style.RESET_ALL}")
                return
            print(f"\nPercorsi attuali: cert={ent.get('ssl_cert_path') or '-'} key={ent.get('ssl_key_path') or '-'}")
            cert = prompt_for_input(f"Percorso certificato (PATH) o INVIO per mantenere, 'clear' per rimuovere: ")
            key = prompt_for_input(f"Percorso chiave (PATH) o INVIO per mantenere, 'clear' per rimuovere: ")

            new_cert = ent.get('ssl_cert_path') if cert.strip() == '' else (None if cert.strip().lower() == 'clear' else cert.strip())
            new_key = ent.get('ssl_key_path') if key.strip() == '' else (None if key.strip().lower() == 'clear' else key.strip())

            # Verifica esistenza file (se forniti) e richiedi conferma aggiuntiva se non trovati
            from pathlib import Path
            for p_label, p_val in [('cert', new_cert), ('key', new_key)]:
                if p_val and not Path(p_val).exists():
                    warn = prompt_for_input(f"{Fore.YELLOW}Attenzione: il file {p_label} '{p_val}' non esiste. Continuare? (s/N): {Style.RESET_ALL}")
                    if warn.lower() != 's':
                        print(f"{Fore.WHITE}Operazione annullata dall'utente.{Style.RESET_ALL}")
                        return

            confirmed = prompt_for_input(f"Confermi l'aggiornamento? (s/N): ")
            if confirmed.lower() == 's':
                ok = campaign_manager.update_entity_ssl_paths(entity_id, new_cert, new_key, db_manager)
                if ok:
                    print(f"{Fore.GREEN}✓ Percorsi aggiornati per l'entità ID {entity_id}.{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}✗ Nessuna modifica effettuata.{Style.RESET_ALL}")
            else:
                print(f"{Fore.WHITE}Operazione annullata.{Style.RESET_ALL}")

        elif choice == '3':
            campagne = campaign_manager.get_campaigns(db_manager)
            if not campagne:
                print(f"{Fore.YELLOW}Nessuna campagna trovata.{Style.RESET_ALL}")
                return
            print(f"\n{Fore.WHITE}Campagne disponibili:{Style.RESET_ALL}")
            for c in campagne:
                print(f"{Fore.LIGHTRED_EX}[{c['id']}]{Style.RESET_ALL} {c['name']}")
            campaign_id = int(prompt_for_input(f"\n{Fore.LIGHTRED_EX}ID campagna: {Style.RESET_ALL}"))
            # Recupera campagne con entity join per mostrare valori
            camp = campaign_manager.get_campaign_by_id(campaign_id, db_manager)
            if not camp:
                print(f"{Fore.RED}✗ Campagna non trovata.{Style.RESET_ALL}")
                return
            print(f"\nCampagna: {camp['name']}\n  Cert: {camp.get('ssl_cert_path') or '-'}\n  Key: {camp.get('ssl_key_path') or '-'}\n  Dominio: {camp.get('domain') or '-'}")

        elif choice == '0':
            print(f"{Fore.WHITE}Operazione annullata.{Style.RESET_ALL}")
            return

        else:
            print(f"{Fore.RED}Scelta non valida.{Style.RESET_ALL}")

    except ValueError:
        print(f"{Fore.RED}✗ ID non valido.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}✗ Errore: {e}{Style.RESET_ALL}")
        logger.error(f"Errore configurazione SSL: {e}")
    
    campaigns = campaign_manager.get_campaigns(db_manager)
    if not campaigns:
        print(f"{Fore.YELLOW}Nessuna campagna trovata.{Style.RESET_ALL}")
        return
    
    # Filtra le campagne non in esecuzione
    from modules.campaign_managers.campaign_runner import is_campaign_running
    available = [c for c in campaigns if not is_campaign_running(c['id'])]
    
    if not available:
        print(f"{Fore.YELLOW}Tutte le campagne sono già in esecuzione.{Style.RESET_ALL}")
        return
    
    print(f"\n{Fore.WHITE}Campagne disponibili:{Style.RESET_ALL}")
    for campaign in available:
        pages = campaign_manager.get_campaign_pages(campaign['id'], db_manager)
        pages_info = f"{len(pages) if pages else 0} pagine" if pages else "nessuna pagina"
        print(f"{Fore.LIGHTRED_EX}[{campaign['id']}]{Style.RESET_ALL} {campaign['name']} ({pages_info})")
    
    try:
        campaign_id = int(prompt_for_input(f"\n{Fore.LIGHTRED_EX}ID della campagna da avviare: {Style.RESET_ALL}"))
        campaign = campaign_manager.get_campaign_by_id(campaign_id, db_manager)
        
        if not campaign:
            print(f"{Fore.RED}✗ Campagna non trovata.{Style.RESET_ALL}")
            return
        
        pages = campaign_manager.get_campaign_pages(campaign_id, db_manager)
        if not pages:
            print(f"{Fore.RED}✗ La campagna non ha pagine associate.{Style.RESET_ALL}")
            return
        
        # Richiedi la porta
        port_input = prompt_for_input(f"{Fore.WHITE}Porta per il server (default 5000): {Style.RESET_ALL}")
        port = 5000
        if port_input.strip():
            try:
                port = int(port_input)
            except ValueError:
                print(f"{Fore.YELLOW}⚠ Porta non valida. Usando 5000.{Style.RESET_ALL}")
        
        from modules.campaign_managers.campaign_runner import start_campaign_background
        
        if start_campaign_background(campaign_id, db_manager, port):
            print(f"\n{Fore.GREEN}✓ Campagna '{campaign['name']}' avviata in background!{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}   Server web sulla porta {port}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}   Pagine servite: {', '.join([p['name'] for p in pages])}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}   Il server continuerà in background mentre navighi il menu.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ Errore nell'avvio della campagna.{Style.RESET_ALL}")
    
    except ValueError:
        print(f"{Fore.RED}✗ ID non valido.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}✗ Errore: {e}{Style.RESET_ALL}")
        logger.error(f"Errore avvio campagna: {e}")

def arresta_campagna(db_manager: DatabaseManager) -> None:
    """Arresta una campagna in esecuzione."""
    print(f"\n{Fore.LIGHTRED_EX}{'═' * 40}")
    print(f"█ {Fore.WHITE}{'ARRESTA CAMPAGNA':^36}{Fore.LIGHTRED_EX} █")
    print(f"{'═' * 40}{Style.RESET_ALL}")
    
    from modules.campaign_managers.campaign_runner import get_running_campaigns, stop_campaign_background
    
    running = get_running_campaigns()
    if not running:
        print(f"{Fore.YELLOW}Nessuna campagna in esecuzione.{Style.RESET_ALL}")
        return
    
    print(f"\n{Fore.WHITE}Campagne in esecuzione:{Style.RESET_ALL}")
    for campaign in running:
        status_color = Fore.GREEN if campaign['status'] == 'running' else Fore.YELLOW
        print(f"{Fore.LIGHTRED_EX}[{campaign['campaign_id']}]{Style.RESET_ALL} {campaign['campaign_name']} - {status_color}{campaign['status']}{Style.RESET_ALL} (porta {campaign['port']})")
    
    try:
        campaign_id = int(prompt_for_input(f"\n{Fore.LIGHTRED_EX}ID della campagna da arrestare: {Style.RESET_ALL}"))
        campaign = campaign_manager.get_campaign_by_id(campaign_id, db_manager)
        
        if not campaign:
            print(f"{Fore.RED}✗ Campagna non trovata.{Style.RESET_ALL}")
            return
        
        if stop_campaign_background(campaign_id):
            # Aggiorna lo status nel database
            ok = campaign_manager.terminate_campaign(campaign_id, db_manager)
            if ok:
                print(f"\n{Fore.GREEN}✓ Campagna '{campaign['name']}' arrestata e terminata.{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.GREEN}✓ Campagna '{campaign['name']}' arrestata.{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}⚠ Attenzione: lo status nel database potrebbe non essere aggiornato.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ La campagna non è in esecuzione.{Style.RESET_ALL}")
    
    except ValueError:
        print(f"{Fore.RED}✗ ID non valido.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}✗ Errore: {e}{Style.RESET_ALL}")
        logger.error(f"Errore arresto campagna: {e}")

def mostra_campagne_in_esecuzione() -> None:
    """Visualizza lo stato delle campagne in esecuzione."""
    print(f"\n{Fore.LIGHTRED_EX}{'═' * 50}")
    print(f"█ {Fore.WHITE}{'CAMPAGNE IN ESECUZIONE':^46}{Fore.LIGHTRED_EX} █")
    print(f"{'═' * 50}{Style.RESET_ALL}")
    
    from modules.campaign_managers.campaign_runner import get_running_campaigns
    
    running = get_running_campaigns()
    if not running:
        print(f"{Fore.YELLOW}Nessuna campagna in esecuzione.{Style.RESET_ALL}")
        return
    
    try:
        from tabulate import tabulate
        
        table = []
        for campaign in running:
            status_color = Fore.GREEN if campaign['status'] == 'running' else Fore.YELLOW
            status = f"{status_color}{campaign['status']}{Style.RESET_ALL}"
            started_at = campaign['started_at'].strftime("%H:%M:%S") if campaign['started_at'] else "N/A"
            table.append([
                campaign['campaign_id'],
                campaign['campaign_name'],
                status,
                campaign['port'],
                campaign['pages_count'],
                started_at
            ])
        
        headers = ["ID", "Nome", "Status", "Porta", "Pagine", "Avviata"]
        print(tabulate(table, headers=headers, tablefmt="grid"))
        print(f"\n{Fore.WHITE}Totale campagne in esecuzione: {len(running)}{Style.RESET_ALL}")
    
    except ImportError:
        print(f"{Fore.WHITE}Campagne in esecuzione:{Style.RESET_ALL}")
        for campaign in running:
            print(f"  • {campaign['campaign_name']} (porta {campaign['port']}) - {campaign['status']}")

def termina_campagna(db_manager: DatabaseManager) -> None:
    """Termina una campagna (mark as terminated, non elimina i dati)."""
    print(f"\n{Fore.LIGHTRED_EX}{'═' * 40}")
    print(f"█ {Fore.WHITE}{'TERMINA CAMPAGNA':^36}{Fore.LIGHTRED_EX} █")
    print(f"{'═' * 40}{Style.RESET_ALL}")
    campaigns = [c for c in campaign_manager.get_campaigns(db_manager) if c['status'] == 'active']
    if not campaigns:
        print(f"{Fore.YELLOW}Nessuna campagna attiva trovata.{Style.RESET_ALL}")
        return
    print(f"\n{Fore.WHITE}Campagne attive:{Style.RESET_ALL}")
    for campaign in campaigns:
        print(f"{Fore.LIGHTRED_EX}[{campaign['id']}]{Style.RESET_ALL} {campaign['name']}")
    try:
        campaign_id = int(prompt_for_input(f"\n{Fore.LIGHTRED_EX}ID della campagna da terminare: {Style.RESET_ALL}"))
        campaign = campaign_manager.get_campaign_by_id(campaign_id, db_manager)
        if not campaign:
            print(f"{Fore.RED}✗ Campagna non trovata.{Style.RESET_ALL}")
            return
        if campaign['status'] != 'active':
            print(f"{Fore.YELLOW}⚠ La campagna '{campaign['name']}' non è attiva.{Style.RESET_ALL}")
            return
        conferma = prompt_for_input(f"\n{Fore.YELLOW}Sei sicuro di voler terminare la campagna '{campaign['name']}'? (s/N): {Style.RESET_ALL}")
        if conferma.lower() != 's':
            print(f"{Fore.WHITE}Operazione annullata.{Style.RESET_ALL}")
            return
        ok = campaign_manager.terminate_campaign(campaign_id, db_manager)
        if ok:
            print(f"\n{Fore.GREEN}✓ Campagna '{campaign['name']}' terminata con successo!{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ Nessuna modifica effettuata.{Style.RESET_ALL}")
    except ValueError:
        print(f"{Fore.RED}✗ ID non valido.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}✗ Errore durante la terminazione: {e}{Style.RESET_ALL}")
        logger.error(f"Errore terminazione campagna: {e}")

def elimina_campagna(db_manager: DatabaseManager) -> None:
    """Elimina una campagna dal database."""
    print(f"\n{Fore.LIGHTRED_EX}{'═' * 40}")
    print(f"█ {Fore.WHITE}{'ELIMINA CAMPAGNA':^36}{Fore.LIGHTRED_EX} █")
    print(f"{'═' * 40}{Style.RESET_ALL}")
    campaigns = campaign_manager.get_campaigns(db_manager)
    if not campaigns:
        print(f"{Fore.YELLOW}Nessuna campagna trovata.{Style.RESET_ALL}")
        return
    print(f"\n{Fore.WHITE}Campagne disponibili:{Style.RESET_ALL}")
    for campaign in campaigns:
        status_color = Fore.GREEN if campaign['status'] == 'active' else Fore.RED
        print(f"{Fore.LIGHTRED_EX}[{campaign['id']}]{Style.RESET_ALL} {campaign['name']} - {status_color}{campaign['status']}{Style.RESET_ALL}")
    try:
        campaign_id = int(prompt_for_input(f"\n{Fore.LIGHTRED_EX}ID della campagna da eliminare: {Style.RESET_ALL}"))
        campaign = campaign_manager.get_campaign_by_id(campaign_id, db_manager)
        if not campaign:
            print(f"{Fore.RED}✗ Campagna non trovata.{Style.RESET_ALL}")
            return
        print(f"\n{Fore.RED}⚠ ATTENZIONE: Eliminando questa campagna verranno eliminati anche:{Style.RESET_ALL}")
        print(f"  - Tutte le pagine phishing associate")
        print(f"  - Tutte le credenziali catturate")
        print(f"  - Tutti i dati correlati")
        conferma = prompt_for_input(f"\n{Fore.RED}Sei sicuro di voler eliminare la campagna '{campaign['name']}'? (s/N): {Style.RESET_ALL}")
        if conferma.lower() != 's':
            print(f"{Fore.WHITE}Operazione annullata.{Style.RESET_ALL}")
            return
        ok = campaign_manager.delete_campaign(campaign_id, db_manager)
        if ok:
            print(f"\n{Fore.GREEN}✓ Campagna '{campaign['name']}' eliminata con successo!{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ Nessuna modifica effettuata.{Style.RESET_ALL}")
    except ValueError:
        print(f"{Fore.RED}✗ ID non valido.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}✗ Errore durante l'eliminazione: {e}{Style.RESET_ALL}")
        logger.error(f"Errore eliminazione campagna: {e}")