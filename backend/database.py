import sqlite3
from typing import List, Dict

DB_NAME = "xcom2_mods.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS abilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            template_name TEXT UNIQUE NOT NULL,
            friendly_name TEXT,
            description TEXT,
            help_text TEXT,
            promotion_text TEXT,
            flyover_text TEXT,
            source_file TEXT
        )
    ''')
    # ... (Keep other tables like character_templates same as before) ...
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS character_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character_name TEXT NOT NULL,
            character_class TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS character_abilities (
            character_id INTEGER,
            ability_id INTEGER,
            FOREIGN KEY(character_id) REFERENCES character_templates(id),
            FOREIGN KEY(ability_id) REFERENCES abilities(id),
            PRIMARY KEY (character_id, ability_id)
        )
    ''')
    conn.commit()
    conn.close()

def save_abilities(abilities: List[Dict]):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # LOGIC CHANGE: 
    # We use CASE WHEN to only update fields if the NEW data (excluded) 
    # is actually valid (not empty/Unknown). 
    # This preserves existing data if the new scan is just a "partial patch".
    query = '''
        INSERT INTO abilities (
            template_name, friendly_name, description, 
            help_text, promotion_text, flyover_text, source_file
        )
        VALUES (
            :template_name, :friendly_name, :description, 
            :help_text, :promotion_text, :flyover_text, :source_file
        )
        ON CONFLICT(template_name) DO UPDATE SET
            friendly_name = CASE 
                WHEN excluded.friendly_name != 'Unknown' AND excluded.friendly_name != '' 
                THEN excluded.friendly_name 
                ELSE abilities.friendly_name 
            END,
            description = CASE 
                WHEN excluded.description != '' 
                THEN excluded.description 
                ELSE abilities.description 
            END,
            help_text = CASE 
                WHEN excluded.help_text != '' 
                THEN excluded.help_text 
                ELSE abilities.help_text 
            END,
            promotion_text = CASE 
                WHEN excluded.promotion_text != '' 
                THEN excluded.promotion_text 
                ELSE abilities.promotion_text 
            END,
            flyover_text = CASE 
                WHEN excluded.flyover_text != '' 
                THEN excluded.flyover_text 
                ELSE abilities.flyover_text 
            END,
            source_file = excluded.source_file
    '''
    
    try:
        cursor.executemany(query, abilities)
        conn.commit()
        print(f"Successfully committed {len(abilities)} records to DB.")
    except Exception as e:
        print(f"Database Error: {e}")
    finally:
        conn.close()

# ... (get_all_abilities remains the same) ...
def get_all_abilities(search_term: str | None = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if search_term:
        query = "SELECT * FROM abilities WHERE friendly_name LIKE ? OR template_name LIKE ?"
        wildcard = f"%{search_term}%"
        cursor.execute(query, (wildcard, wildcard))
    else:
        cursor.execute("SELECT * FROM abilities")
        
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]