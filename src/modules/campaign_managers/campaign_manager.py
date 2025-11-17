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
        cursor.execute("DELETE FROM captured_credentials WHERE campaign_entity_id = ?", (campaign_id,))
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

