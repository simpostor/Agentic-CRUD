import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

# Pull from .env - no hardcoding
key = os.getenv("FERNET_KEY")

if not key:
    raise ValueError("FERNET_KEY not found in .env")

# Initialize the cipher
cipher_suite = Fernet(key.encode())

def encrypt_key(plain_text: str) -> str:
    """Encrypts the API key before DB storage."""
    return cipher_suite.encrypt(plain_text.encode()).decode()

def decrypt_key(encrypted_text: str) -> str:
    """Decrypts the API key for Agent use."""
    return cipher_suite.decrypt(encrypted_text.encode()).decode()