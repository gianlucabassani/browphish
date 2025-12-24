# browphish/src/modules/campaign_managers/campaign_manager.py

"""
Gestione CRUD delle campagne di phishing e associazioni con pagine/template.
"""

def create_campaign(name, description, entity_id, db_manager):
    """Crea una nuova campagna."""
    with db_manager.transaction() as cursor:
        cursor.execute(
            """
            INSERT INTO phishing_campaigns (entity_id, name, description, status)
            VALUES (?, ?, ?, 'active')
            """,
            (entity_id, name, description)
        )
        return cursor.lastrowid

def get_campaigns(db_manager):
    """Restituisce tutte le campagne."""
    query = """
    SELECT pc.id, pc.name, pc.description, pc.created_at, pc.status,
           e.name as entity_name, e.type as entity_type
    FROM phishing_campaigns pc
    JOIN entities e ON pc.entity_id = e.id
    ORDER BY pc.created_at DESC
    """
    return db_manager.execute_query(query)

def get_campaign_by_id(campaign_id, db_manager):
    """Restituisce i dettagli di una campagna."""
    query = """
    SELECT pc.*, e.name as entity_name, e.type as entity_type, e.domain
    FROM phishing_campaigns pc
    JOIN entities e ON pc.entity_id = e.id
    WHERE pc.id = ?
    """
    return db_manager.fetch_one(query, (campaign_id,))

def update_campaign(campaign_id, name, description, db_manager):
    """Modifica nome/descrizione di una campagna."""
    with db_manager.transaction() as cursor:
        cursor.execute(
            """
            UPDATE phishing_campaigns 
            SET name = ?, description = ?
            WHERE id = ?
            """,
            (name, description, campaign_id)
        )
        return cursor.rowcount > 0

def terminate_campaign(campaign_id, db_manager):
    """Termina una campagna (cambia stato)."""
    with db_manager.transaction() as cursor:
        cursor.execute(
            "UPDATE phishing_campaigns SET status = 'terminated' WHERE id = ?",
            (campaign_id,)
        )
        return cursor.rowcount > 0

def delete_campaign(campaign_id, db_manager):
    """Elimina una campagna e i dati associati (conferma a monte)."""
    with db_manager.transaction() as cursor:
        cursor.execute("DELETE FROM captured_credentials WHERE campaign_entity_id = ?", (campaign_id,)) # Eliminare anche le credenziali catturate??
        cursor.execute("DELETE FROM phishing_pages WHERE campaign_entity_id = ?", (campaign_id,))
        cursor.execute("DELETE FROM phishing_campaigns WHERE id = ?", (campaign_id,))
        return cursor.rowcount > 0

def associate_page_to_campaign(campaign_id, page_id, db_manager):
    """Associa una pagina phishing a una campagna."""
    with db_manager.transaction() as cursor:
        cursor.execute(
            "UPDATE phishing_pages SET campaign_entity_id = ? WHERE id = ?",
            (campaign_id, page_id)
        )
        return cursor.rowcount > 0

def associate_email_template_to_campaign(campaign_id, template_id, db_manager):
    """Associa un template email a una campagna. (Stub, da implementare se serve tabella)"""
    # Da implementare: dipende dalla struttura delle tabelle email_template/campaign_template
    return False

def get_campaign_stats(campaign_id, db_manager):
    """Restituisce statistiche di una campagna: totale credenziali, IP unici, credenziali oggi."""
    stats_query = """
    SELECT 
        COUNT(*) as total_credentials,
        COUNT(DISTINCT ip_address) as unique_ips,
        COUNT(CASE WHEN DATE(timestamp) = DATE('now') THEN 1 END) as today_credentials
    FROM captured_credentials 
    WHERE campaign_entity_id = ?
    """
    return db_manager.fetch_one(stats_query, (campaign_id,))

def get_campaign_pages(campaign_id, db_manager):
    """Restituisce le pagine associate a una campagna."""
    pages_query = """
    SELECT pp.id, pp.name, pp.original_url, pp.created_at
    FROM phishing_pages pp
    WHERE pp.campaign_entity_id = ?
    ORDER BY pp.created_at DESC
    """
    return db_manager.execute_query(pages_query, (campaign_id,))


# --- SSL helper functions ---
def update_campaign_ssl_paths(campaign_id, cert_path, key_path, db_manager):
    """Imposta o cancella i percorsi SSL per una specifica campagna.

    Passa cert_path/key_path come stringhe oppure None per rimuovere il valore.
    Ritorna True se la campagna è stata aggiornata, False altrimenti.
    """
    with db_manager.transaction() as cursor:
        cursor.execute(
            "UPDATE phishing_campaigns SET ssl_cert_path = ?, ssl_key_path = ? WHERE id = ?",
            (cert_path, key_path, campaign_id)
        )
        return cursor.rowcount > 0


def update_entity_ssl_paths(entity_id, cert_path, key_path, db_manager):
    """Imposta o cancella i percorsi SSL per un'entità (dominio).

    Passa cert_path/key_path come stringhe oppure None per rimuovere il valore.
    Ritorna True se l'entità è stata aggiornata, False altrimenti.
    """
    with db_manager.transaction() as cursor:
        cursor.execute(
            "UPDATE entities SET ssl_cert_path = ?, ssl_key_path = ? WHERE id = ?",
            (cert_path, key_path, entity_id)
        )
        return cursor.rowcount > 0


def get_ssl_paths_for_campaign(campaign_id, db_manager):
    """Restituisce una tupla (cert_path, key_path) per la campagna considerata.

    Priorità: percorsi impostati nella campagna > percorsi impostati nell'entità (dominio).
    Se non sono presenti percorsi validi (entrambi i file esistenti) viene restituito (None, None).
    """
    query = """
    SELECT pc.ssl_cert_path AS pc_cert, pc.ssl_key_path AS pc_key,
           e.ssl_cert_path AS e_cert, e.ssl_key_path AS e_key
    FROM phishing_campaigns pc
    JOIN entities e ON pc.entity_id = e.id
    WHERE pc.id = ?
    """
    row = db_manager.fetch_one(query, (campaign_id,))
    if not row:
        return (None, None)

    from pathlib import Path

    # Prefer campaign-level if both values present and files exist
    if row.get('pc_cert') and row.get('pc_key'):
        if Path(row['pc_cert']).exists() and Path(row['pc_key']).exists():
            return (row['pc_cert'], row['pc_key'])

    # Otherwise prefer entity/domain-level if both present and exist
    if row.get('e_cert') and row.get('e_key'):
        if Path(row['e_cert']).exists() and Path(row['e_key']).exists():
            return (row['e_cert'], row['e_key'])

    return (None, None)


def get_ssl_paths_for_page(page_name, db_manager):
    """Restituisce (cert_path, key_path) cercando prima la campagna associata, poi il dominio.

    Usa il nome della pagina (nome della riga in phishing_pages.name).
    """
    page_row = db_manager.fetch_one("SELECT campaign_entity_id, domain_entity_id FROM phishing_pages WHERE name = ?", (page_name,))
    if not page_row:
        return (None, None)

    camp_id = page_row.get('campaign_entity_id')
    dom_id = page_row.get('domain_entity_id')

    # Controlla campagna
    if camp_id:
        certs = get_ssl_paths_for_campaign(camp_id, db_manager)
        if certs != (None, None):
            return certs

    # Controlla dominio/entity
    if dom_id:
        row = db_manager.fetch_one("SELECT ssl_cert_path, ssl_key_path FROM entities WHERE id = ?", (dom_id,))
        if row and row.get('ssl_cert_path') and row.get('ssl_key_path'):
            from pathlib import Path
            if Path(row['ssl_cert_path']).exists() and Path(row['ssl_key_path']).exists():
                return (row['ssl_cert_path'], row['ssl_key_path'])

    return (None, None)

