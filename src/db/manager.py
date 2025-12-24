"""
Modulo semplificato: DatabaseManager (db/manager.py)

Gestore database SQLite per Browphish:
- Connessione e chiusura
- Inizializzazione schema
- Query di base (execute, fetch)
- Gestione entità
"""

import logging
import os
import sqlite3
from pathlib import Path
from typing import Any, List, Optional, cast
from contextlib import contextmanager

from .schema import SCHEMAS

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("DatabaseManager")

class DatabaseManager:
    _instance: Optional["DatabaseManager"] = None

    @classmethod
    def get_instance(cls, db_path: Optional[str] = None) -> "DatabaseManager":
        if cls._instance is None:
            cls._instance = cls(db_path)
        elif db_path and cls._instance.db_path != db_path:
            cls._instance.db_path = db_path
            logger.info(f"Percorso database aggiornato a {db_path}")
        return cls._instance

    def __init__(self, db_path: Optional[str] = None) -> None:
        base_dir = Path(__file__).parent.parent.parent
        data_dir = os.path.join(base_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        self.db_path = db_path or os.path.join(data_dir, "websites.db")
        self.connection: Optional[sqlite3.Connection] = None

    def connect(self) -> bool:
        if self.connection:
            return True
        try:
            self.connection = sqlite3.connect(
                self.db_path,
                timeout=10.0,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
                check_same_thread=False  
            )
            self.connection.execute("PRAGMA journal_mode=WAL")
            self.connection.execute("PRAGMA foreign_keys=ON")
            self.connection.row_factory = sqlite3.Row
            logger.info(f"Connessione a database completata: {self.db_path}")
            return True
        except sqlite3.Error as error:
            logger.error(f"Errore connessione database: {error}")
            return False

    def disconnect(self) -> None:
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Connessione database chiusa")

    def init_schema(self) -> bool:
        if not self.connect():
            logger.error("Impossibile connettersi al database")
            return False
        schema_queries = SCHEMAS.get("websites", "")
        if not schema_queries:
            logger.warning("Nessuno schema definito per 'websites'")
            return False
        try:
            for query in schema_queries.split(";"):
                if query.strip():
                    self.connection.execute(query)
            self.connection.commit()
            logger.info("Schema inizializzato per 'websites'")

            # --- Migrazione: aggiungi colonne SSL se mancanti (per compatibilità retroattiva)
            try:
                cursor = self.connection.cursor()
                # Helper to check and add a column if it doesn't exist
                def ensure_column(table, column, column_def):
                    cursor.execute("PRAGMA table_info(%s)" % table)
                    cols = [row[1] for row in cursor.fetchall()]
                    if column not in cols:
                        logger.info(f"Aggiungo colonna '{column}' a '{table}'")
                        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_def}")

                ensure_column('entities', 'ssl_cert_path', 'TEXT')
                ensure_column('entities', 'ssl_key_path', 'TEXT')
                ensure_column('phishing_campaigns', 'ssl_cert_path', 'TEXT')
                ensure_column('phishing_campaigns', 'ssl_key_path', 'TEXT')
                self.connection.commit()
            except sqlite3.Error as e:
                logger.error(f"Errore durante migrazione colonne SSL: {e}")

            return True
        except sqlite3.Error as error:
            logger.error(f"Errore inizializzazione schema: {error}")
            self.connection.rollback()
            return False

    def get_connection(self):
        conn = sqlite3.connect(
            self.db_path,
            timeout=10.0,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
            check_same_thread=False
        )
        conn.execute("PRAGMA foreign_keys=ON")
        conn.row_factory = sqlite3.Row
        return conn

    @contextmanager
    def transaction(self, database_name: str = "websites"):
        """Context manager per le transazioni con cursore."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Errore durante transazione: {e}")
            raise
        finally:
            conn.close()

    def get_or_create_entity(self, identifier: str, entity_type: str) -> int:
        """
        Registra una nuova entità nel database o recupera l'ID di un'entità esistente.
        
        Args:
            identifier: L'identificativo univoco dell'entità (es. dominio, email, username)
            entity_type: Il tipo di entità ("domain", "email", "username")
            
        Returns:
            L'ID univoco dell'entità nel database
        """
        # Assicurati che la tabella entities esista
        if not self.table_exists("entities"):
            self._create_entities_table()
        
        db_entity_type = "company" if entity_type == "domain" else "person"
        domain_value = identifier if entity_type == "domain" else None
        
        with self.transaction() as cursor:
            cursor.execute(
                """
                INSERT OR IGNORE INTO entities (type, name, domain) 
                VALUES (?, ?, ?)
                """,
                (db_entity_type, identifier, domain_value),
            )
            
            entity_id: Optional[int] = None
            if cursor.rowcount > 0:
                entity_id = cursor.lastrowid
                if entity_id is None:
                    logger.error(f"CRITICAL: rowcount > 0 but lastrowid is None for entity '{identifier}'.")
                    raise ValueError(f"Failed to get lastrowid for new entity '{identifier}'")
                logger.debug(f"Created new entity: ID {entity_id}, Name '{identifier}', Type '{db_entity_type}'")
                return cast(int, entity_id)
            else:
                logger.debug(f"Entity '{identifier}' (type: {db_entity_type}) likely already exists. Fetching its ID.")
                
                if db_entity_type == "company" and domain_value:
                    cursor.execute(
                        "SELECT id FROM entities WHERE name=? AND type=? AND domain=?", 
                        (identifier, db_entity_type, domain_value)
                    )
                elif db_entity_type == "person" and domain_value is None:
                    cursor.execute(
                        "SELECT id FROM entities WHERE name=? AND type=? AND domain IS NULL", 
                        (identifier, db_entity_type)
                    )
                else:
                    logger.warning(f"Attempting generic SELECT for entity: Name '{identifier}', Type '{db_entity_type}', Domain '{domain_value}'")
                    cursor.execute(
                        "SELECT id FROM entities WHERE name=? AND type=?", 
                        (identifier, db_entity_type)
                    )
                
                result = cursor.fetchone()
                if not result:
                    logger.error(f"CRITICAL: Entity '{identifier}' (type: {db_entity_type}) was IGNORED on insert but NOT FOUND on select.")
                    raise ValueError(f"Entity '{identifier}' exists (was ignored) but its ID could not be retrieved.")
                
                entity_id = result['id']
                logger.debug(f"Found existing entity: ID {entity_id}, Name '{identifier}', Type '{db_entity_type}'")
                return cast(int, entity_id)

    def _create_entities_table(self):
        """Crea la tabella entities se non esiste."""
        create_entities_sql = """
        CREATE TABLE IF NOT EXISTS entities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            name TEXT NOT NULL,
            domain TEXT,
            ssl_cert_path TEXT,
            ssl_key_path TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(type, name, domain)
        );
        """
        try:
            conn = self.get_connection()
            conn.execute(create_entities_sql)
            conn.commit()
            conn.close()
            logger.info("Tabella entities creata")
        except sqlite3.Error as error:
            logger.error(f"Errore creazione tabella entities: {error}")

    def execute_query(self, query: str, params: Optional[tuple[Any, ...]] = None) -> Optional[List[dict[str, Any]]]:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            if query.strip().upper().startswith("SELECT"):
                results = cursor.fetchall()
                conn.close()
                return [dict(row) for row in results]
            else:
                conn.commit()
                rowcount = cursor.rowcount
                conn.close()
                return [{"rowcount": rowcount}]
        except sqlite3.Error as error:
            logger.error(f"Errore esecuzione query: {error}")
            return None

    def fetch_one(self, query: str, params: Optional[tuple[Any, ...]] = None) -> Optional[dict[str, Any]]:
        results = self.execute_query(query, params)
        return results[0] if results else None

    def fetch_all(self, query: str, params: Optional[tuple[Any, ...]] = None) -> List[dict[str, Any]]:
        results = self.execute_query(query, params)
        return results if results else []

    def table_exists(self, table_name: str) -> bool:
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?;"
        result = self.fetch_one(query, (table_name,))
        return result is not None

    def get_tables(self) -> List[str]:
        results = self.execute_query("SELECT name FROM sqlite_master WHERE type='table';")
        return [row["name"] for row in results] if results else []
    
    def get_all_table_names(self) -> List[str]:
        """Alias for get_tables() for compatibility"""
        return self.get_tables()

    def visualizza_log_accesso(self):
        """Stampa i log di accesso (senza credenziali) in formato tabellare."""
        from colorama import Fore, Style
        import shutil
        
        query = """
        SELECT cc.id, cc.ip_address, cc.user_agent, cc.timestamp,
               e_campaign.name as campaign_name,
               e_page.name as page_name,
               cc.additional_data
        FROM captured_credentials cc
        LEFT JOIN entities e_campaign ON cc.campaign_entity_id = e_campaign.id
        LEFT JOIN entities e_page ON cc.page_entity_id = e_page.id
        WHERE (cc.username IS NULL OR cc.username = '') 
           AND (cc.password IS NULL OR cc.password = '') 
           AND (cc.email IS NULL OR cc.email = '')
        ORDER BY cc.timestamp DESC;
        """
        
        results = self.execute_query(query)
        if not results:
            print(f"{Fore.YELLOW}Nessun log di accesso trovato.{Style.RESET_ALL}")
            return

        try:
            from tabulate import tabulate
            
            headers = [
                "ID", "Campagna", "Pagina", 
                f"{Fore.LIGHTRED_EX}IP Address{Style.RESET_ALL}", 
                "User Agent", "Timestamp", "Dati Aggiuntivi"
            ]
            
            table = []
            for row in results:
                ip_address = f"{Fore.LIGHTRED_EX}{row['ip_address']}{Style.RESET_ALL}" if row['ip_address'] else "-"
                user_agent = (row["user_agent"][:40] + "...") if row["user_agent"] and len(row["user_agent"]) > 43 else (row["user_agent"] or "-")
                additional_data = (row["additional_data"][:30] + "...") if row["additional_data"] and len(row["additional_data"]) > 33 else (row["additional_data"] or "-")
                
                table.append([
                    row["id"],
                    row["campaign_name"] or "-",
                    row["page_name"] or "-",
                    ip_address,
                    user_agent,
                    row["timestamp"] or "-",
                    additional_data
                ])
            
            # Smart rendering: mostra solo le prime e ultime 2 righe se >10
            n = len(table)
            if n > 10:
                display_table = table[:2] + [["...", *(["..."]*(len(headers)-1))]] + table[-2:]
            else:
                display_table = table
            
            print(tabulate(display_table, headers=headers, tablefmt="grid", maxcolwidths=[15]*len(headers)))
            print(f"\n{Fore.WHITE}Totale accessi: {n}{Style.RESET_ALL}")
            
        except ImportError:
            print("Log di accesso:")
            for row in results:
                print(f"ID: {row['id']}, IP: {row['ip_address']}, Timestamp: {row['timestamp']}")

    def get_access_stats(self) -> dict:
        """Restituisce statistiche sui log di accesso."""
        stats = {}
        
        # Numero totale di accessi (senza credenziali)
        total_accesses = self.fetch_one("""
            SELECT COUNT(*) as count FROM captured_credentials 
            WHERE (username IS NULL OR username = '') 
               AND (password IS NULL OR password = '') 
               AND (email IS NULL OR email = '')
        """)
        stats['total_accesses'] = total_accesses['count'] if total_accesses else 0
        
        # Accessi oggi
        today_accesses = self.fetch_one("""
            SELECT COUNT(*) as count FROM captured_credentials 
            WHERE DATE(timestamp) = DATE('now')
               AND (username IS NULL OR username = '') 
               AND (password IS NULL OR password = '') 
               AND (email IS NULL OR email = '')
        """)
        stats['today_accesses'] = today_accesses['count'] if today_accesses else 0
        
        # IP unici
        unique_ips = self.fetch_one("""
            SELECT COUNT(DISTINCT ip_address) as count FROM captured_credentials 
            WHERE ip_address IS NOT NULL
        """)
        stats['unique_ips'] = unique_ips['count'] if unique_ips else 0
        
        return stats

    def get_phishing_stats(self) -> dict:
        """Restituisce statistiche generali del phishing."""
        stats = {}
        
        # Campagne totali
        total_campaigns = self.fetch_one("SELECT COUNT(*) as count FROM phishing_campaigns")
        stats['total_campaigns'] = total_campaigns['count'] if total_campaigns else 0
        
        # Pagine totali
        total_pages = self.fetch_one("SELECT COUNT(*) as count FROM phishing_pages")
        stats['total_pages'] = total_pages['count'] if total_pages else 0
        
        # Credenziali totali
        total_credentials = self.fetch_one("""
            SELECT COUNT(*) as count FROM captured_credentials 
            WHERE (username IS NOT NULL AND username != '') 
               OR (password IS NOT NULL AND password != '') 
               OR (email IS NOT NULL AND email != '')
        """)
        stats['total_credentials'] = total_credentials['count'] if total_credentials else 0
        
        # Credenziali oggi
        today_credentials = self.fetch_one("""
            SELECT COUNT(*) as count FROM captured_credentials 
            WHERE DATE(timestamp) = DATE('now')
               AND ((username IS NOT NULL AND username != '') 
               OR (password IS NOT NULL AND password != '') 
               OR (email IS NOT NULL AND email != ''))
        """)
        stats['today_credentials'] = today_credentials['count'] if today_credentials else 0
        
        return stats

    def submit_credentials_or_log_access(self, campaign_entity_id: Optional[int], page_entity_id: Optional[int], 
                                       username: Optional[str], password: Optional[str], email: Optional[str],
                                       ip_address: str, user_agent: str, additional_data: str) -> bool:
        """
        Salva credenziali catturate o log di accesso nel database.
        
        Args:
            campaign_entity_id: ID dell'entità campagna (opzionale)
            page_entity_id: ID dell'entità pagina (opzionale)
            username: Username catturato (opzionale)
            password: Password catturata (opzionale)
            email: Email catturata (opzionale)
            ip_address: Indirizzo IP del visitatore
            user_agent: User agent del browser
            additional_data: Dati aggiuntivi in formato JSON
            
        Returns:
            True se salvato con successo, False altrimenti
        """
        try:
            with self.transaction() as cursor:
                cursor.execute("""
                    INSERT INTO captured_credentials 
                    (campaign_entity_id, page_entity_id, username, password, email, 
                     ip_address, user_agent, additional_data, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    campaign_entity_id, page_entity_id, username, password, email,
                    ip_address, user_agent, additional_data
                ))
                
                logger.info(f"Credenziali/accesso salvate nel database. IP: {ip_address}")
                return True
                
        except Exception as e:
            logger.error(f"Errore nel salvataggio credenziali: {e}")
            return False

    def get_original_url_for_page(self, page_name: str) -> Optional[str]:
        """
        Recupera l'URL originale di una pagina clonata.
        
        Args:
            page_name: Nome della pagina clonata
            
        Returns:
            URL originale se trovato, None altrimenti
        """
        try:
            query = """
                SELECT pp.original_url 
                FROM phishing_pages pp
                JOIN entities e ON pp.page_entity_id = e.id
                WHERE e.name = ?
                ORDER BY pp.created_at DESC
                LIMIT 1
            """
            result = self.fetch_one(query, (page_name,))
            return result['original_url'] if result else None
            
        except Exception as e:
            logger.error(f"Errore nel recupero URL originale per {page_name}: {e}")
            return None

    def visualizza_dati_catturati(self):
        """Stampa SOLO i dati con credenziali catturate dalla tabella captured_credentials."""
        from colorama import Fore, Style
        import shutil
        
        query = """
        SELECT cc.id, cc.campaign_entity_id, cc.username, cc.password, cc.email, 
               cc.ip_address, cc.user_agent, cc.timestamp,
               e_campaign.name as campaign_name,
               e_page.name as page_name
        FROM captured_credentials cc
        LEFT JOIN entities e_campaign ON cc.campaign_entity_id = e_campaign.id
        LEFT JOIN entities e_page ON cc.page_entity_id = e_page.id
        WHERE (cc.username IS NOT NULL AND cc.username != '') 
           OR (cc.password IS NOT NULL AND cc.password != '') 
           OR (cc.email IS NOT NULL AND cc.email != '')
        ORDER BY cc.timestamp DESC;
        """
        
        results = self.execute_query(query)
        if not results:
            print(f"{Fore.YELLOW}Nessuna credenziale catturata.{Style.RESET_ALL}")
            return

        try:
            from tabulate import tabulate
            
            headers = [
                "ID", "Campagna", "Pagina", 
                f"{Fore.LIGHTRED_EX}Username{Style.RESET_ALL}", 
                f"{Fore.MAGENTA}Email{Style.RESET_ALL}", 
                f"{Fore.RED}Password{Style.RESET_ALL}", 
                "IP", "User Agent", "Timestamp"
            ]
            
            table = []
            for row in results:
                username = (row["username"] or "").strip()
                email = (row["email"] or "").strip()
                password = (row["password"] or "").strip()
                
                # Colora i campi sensibili
                username = f"{Fore.LIGHTRED_EX}{username}{Style.RESET_ALL}" if username else "-"
                email = f"{Fore.MAGENTA}{email}{Style.RESET_ALL}" if email else "-"
                password = f"{Fore.RED}{password}{Style.RESET_ALL}" if password else "-"
                
                table.append([
                    row["id"],
                    row["campaign_name"] or "-",
                    row["page_name"] or "-",
                    username,
                    email,
                    password,
                    row["ip_address"] or "-",
                    (row["user_agent"][:30] + "...") if row["user_agent"] and len(row["user_agent"]) > 33 else (row["user_agent"] or "-"),
                    row["timestamp"] or "-"
                ])
            
            # Smart rendering: mostra solo le prime e ultime 2 righe se >10
            n = len(table)
            if n > 10:
                display_table = table[:2] + [["...", *(["..."]*(len(headers)-1))]] + table[-2:]
            else:
                display_table = table
            
            print(tabulate(display_table, headers=headers, tablefmt="grid", maxcolwidths=[20]*len(headers)))
            print(f"\n{Fore.WHITE}Totale credenziali: {n}{Style.RESET_ALL}")
            
        except ImportError:
            print("Credenziali catturate:")
            for row in results:
                print(f"ID: {row['id']}, Username: {row['username']}, Email: {row['email']}, Password: {row['password']}")

    def __del__(self) -> None:
        self.disconnect()

# Esempio di utilizzo
if __name__ == "__main__":
    db = DatabaseManager.get_instance()
    db.init_schema()
    
    # Test del sistema di entità
    try:
        domain_id = db.get_or_create_entity("example.com", "domain")
        print(f"Domain entity ID: {domain_id}")
        
        email_id = db.get_or_create_entity("test@example.com", "email")
        print(f"Email entity ID: {email_id}")
        
        # Visualizza statistiche
        stats = db.get_phishing_stats()
        print(f"Stats: {stats}")
        
    except Exception as e:
        print(f"Errore: {e}")
    
    db.disconnect()