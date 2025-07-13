import os
from dotenv import load_dotenv

def load_environment_variables():
    """Loads environment variables from .env file."""
    load_dotenv()
    print("Environment variables loaded.")
    print(f"Telegram API ID: {os.getenv('TELEGRAM_API_ID')}")
    print(f"PostgreSQL User: {os.getenv('POSTGRES_USER')}")

if __name__ == "__main__":
    load_environment_variables()
    # You can access variables like:
    # api_id = os.getenv('TELEGRAM_API_ID')
    # db_user = os.getenv('POSTGRES_USER')
