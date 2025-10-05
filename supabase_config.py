# Supabase Configuration
import os
from supabase import create_client, Client

# Supabase credentials - Use environment variables in production
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://btifkbhcpilyijejszcf.supabase.co")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ0aWZrYmhjcGlseWlqZWpzemNmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTcyNzkwMjEsImV4cCI6MjA3Mjg1NTAyMX0.lp7-VcEJ6sSRl-zfp8IVMYWk0JhCYjHFvyffKgsrbco")

# Create Supabase client
def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# Test connection
def test_supabase_connection():
    """Test Supabase connection"""
    try:
        supabase = get_supabase_client()
        # Try to fetch from a system table
        result = supabase.table('companies').select('*').limit(1).execute()
        print(f"Supabase connection successful! Found {len(result.data)} companies.")
        return True
    except Exception as e:
        print(f"Supabase connection failed: {e}")
        return False

if __name__ == "__main__":
    test_supabase_connection()
