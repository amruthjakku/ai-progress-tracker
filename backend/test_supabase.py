
from dotenv import load_dotenv
import os
from supabase import create_client

load_dotenv("backend/.env")

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print(f"URL: {url}")
print(f"Key length: {len(key) if key else 0}")

try:
    supabase = create_client(url, key)
    print("✅ Client created")
    
    print("Attempting to select from users table...")
    response = supabase.table("users").select("count", count="exact").limit(1).execute()
    print(f"✅ Success! Response: {response}")
except Exception as e:
    print(f"❌ Error: {e}")
