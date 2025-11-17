SCHEMAS = {
    "websites": """
    CREATE TABLE IF NOT EXISTS entities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,
        name TEXT NOT NULL,
        domain TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(type, name, domain)
    );
    
    CREATE TABLE IF NOT EXISTS phishing_campaigns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'active',
        FOREIGN KEY (entity_id) REFERENCES entities(id)
    );
    
    CREATE TABLE IF NOT EXISTS phishing_pages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        campaign_entity_id INTEGER,
        page_entity_id INTEGER NOT NULL,
        domain_entity_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        original_url TEXT NOT NULL,
        cloned_path TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (campaign_entity_id) REFERENCES entities(id),
        FOREIGN KEY (page_entity_id) REFERENCES entities(id),
        FOREIGN KEY (domain_entity_id) REFERENCES entities(id)
    );
    
    CREATE TABLE IF NOT EXISTS captured_credentials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        campaign_entity_id INTEGER,
        page_entity_id INTEGER,
        username TEXT,
        password TEXT,
        email TEXT,
        ip_address TEXT,
        user_agent TEXT,
        additional_data TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (campaign_entity_id) REFERENCES entities(id),
        FOREIGN KEY (page_entity_id) REFERENCES entities(id)
    );
    
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_id INTEGER NOT NULL,
        email TEXT NOT NULL,
        username TEXT,
        password TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (entity_id) REFERENCES entities(id)
    );
    """
}

# Definizioni separate per riferimento (opzionali se usi SCHEMAS)
CREATE_TABLE_PHISHING_CAMPAIGNS = '''
CREATE TABLE IF NOT EXISTS phishing_campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'active',
    FOREIGN KEY (entity_id) REFERENCES entities(id)
);
'''

CREATE_TABLE_PHISHING_PAGES = '''
CREATE TABLE IF NOT EXISTS phishing_pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_entity_id INTEGER,
    page_entity_id INTEGER NOT NULL,
    domain_entity_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    original_url TEXT NOT NULL,
    cloned_path TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_entity_id) REFERENCES entities(id),
    FOREIGN KEY (page_entity_id) REFERENCES entities(id),
    FOREIGN KEY (domain_entity_id) REFERENCES entities(id)
);
'''

CREATE_TABLE_CAPTURED_CREDENTIALS = '''
CREATE TABLE IF NOT EXISTS captured_credentials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_entity_id INTEGER,
    page_entity_id INTEGER,
    username TEXT,
    password TEXT,
    email TEXT,
    ip_address TEXT,
    user_agent TEXT,
    additional_data TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_entity_id) REFERENCES entities(id),
    FOREIGN KEY (page_entity_id) REFERENCES entities(id)
);
'''

CREATE_TABLE_USERS = '''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id INTEGER NOT NULL,
    email TEXT NOT NULL,
    username TEXT,
    password TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (entity_id) REFERENCES entities(id)
);
'''