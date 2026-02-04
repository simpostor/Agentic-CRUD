import os
import google.generativeai as genai
from app.database import pool
from app.security import decrypt_key

def get_gemini_client():
    # 1. Pull the encrypted key from Oracle 23ai
    with pool.acquire() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT encrypted_api_key FROM vault_credentials WHERE service_name = 'GEMINI'")
            row = cursor.fetchone()
            if not row:
                raise ValueError("Gemini key not found in Vault. Please save it via the PWA first.")
            
            # 2. Decrypt it on the fly
            encrypted_key = row[0]
            api_key = decrypt_key(encrypted_key)

    # 3. Configure the SDK
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.0-flash-lite") # Using the 2.5/2.0 lite flash model

def chat_with_agent(prompt: str):
    model = get_gemini_client()
    response = model.generate_content(prompt)
    return response.text

if __name__ == "__main__":
    user_input = input("Enter message for Gemini: ")
    print(f"Response: {chat_with_agent(user_input)}")