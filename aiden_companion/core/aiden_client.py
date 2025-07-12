# aiden_companion/src/core/aiden_client.py

import os
from functools import lru_cache
from dotenv import load_dotenv
from fellow_aiden import FellowAiden

load_dotenv()

@lru_cache(maxsize=1)
def get_aiden_client() -> FellowAiden:
    """
    Initializes and returns a singleton instance of the FellowAiden client.
    Uses LRU cache to ensure the client is only created once.
    """
    email = os.environ.get("FELLOW_EMAIL")
    password = os.environ.get("FELLOW_PASSWORD")

    if not email or not password:
        raise ValueError("FELLOW_EMAIL and FELLOW_PASSWORD must be set in your .env file.")

    print("Authenticating with Fellow API...")
    try:
        client = FellowAiden(email, password)
        print(f"Successfully authenticated. Brewer: {client.get_display_name()}")
        return client
    except Exception as e:
        print(f"Error authenticating with Fellow API: {e}")
        raise