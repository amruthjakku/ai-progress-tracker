
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_deps")

print("Python version:", sys.version)

try:
    print("Testing pydantic[email]...")
    from pydantic import BaseModel, EmailStr
    class User(BaseModel):
        email: EmailStr
    u = User(email="test@test.com")
    print("✅ Pydantic email verified")
except Exception as e:
    print(f"❌ Pydantic error: {e}")

try:
    print("Testing passlib[bcrypt]...")
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hash = pwd_context.hash("secret")
    print(f"✅ Passlib hash generated: {hash[:10]}...")
    verify = pwd_context.verify("secret", hash)
    print(f"✅ Passlib verification: {verify}")
except Exception as e:
    print(f"❌ Passlib error: {e}")

try:
    print("Testing supabase...")
    from supabase import create_client
    print("✅ Supabase import success")
except Exception as e:
    print(f"❌ Supabase error: {e}")
