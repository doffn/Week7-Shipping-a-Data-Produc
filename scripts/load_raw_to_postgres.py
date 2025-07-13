import os
import json
import glob
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATA_LAKE_PATH = "data/raw/telegram_messages"

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        database=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD')
    )

def create_raw_table(conn):
    """Creates the raw_telegram_messages table if it doesn't exist."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE SCHEMA IF NOT EXISTS raw;
            CREATE TABLE IF NOT EXISTS raw.telegram_messages (
                id BIGINT PRIMARY KEY,
                channel_id BIGINT,
                message_data JSONB,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
    print("Raw table 'raw.telegram_messages' ensured.")

def load_json_to_postgres(file_path):
    """Loads a single JSON file into the raw.telegram_messages table."""
    conn = None
    try:
        conn = get_db_connection()
        create_raw_table(conn)

        with open(file_path, 'r', encoding='utf-8') as f:
            messages = json.load(f)

        with conn.cursor() as cur:
            for message in messages:
                # Extract relevant fields for primary key and channel_id
                message_id = message.get('id')
                peer_id = message.get('peer_id', {})
                channel_id = peer_id.get('channel_id') if peer_id.get('_') == 'PeerChannel' else None

                if message_id is None:
                    print(f"Skipping message due to missing ID: {message}")
                    continue

                # Upsert logic: Try to insert, if conflict (id exists), do nothing or update
                cur.execute("""
                    INSERT INTO raw.telegram_messages (id, channel_id, message_data)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (id) DO NOTHING;
                """, (message_id, channel_id, json.dumps(message)))
            conn.commit()
        print(f"Loaded {len(messages)} messages from {file_path} into PostgreSQL.")
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def main():
    """Scans the data lake and loads new JSON files into PostgreSQL."""
    print("Starting raw data loading to PostgreSQL...")
    json_files = glob.glob(os.path.join(DATA_LAKE_PATH, '**/*.json'), recursive=True)
    for file_path in json_files:
        load_json_to_postgres(file_path)
    print("Raw data loading complete.")

if __name__ == "__main__":
    main()
