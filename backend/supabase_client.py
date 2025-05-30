# backend/supabase_client.py

from supabase import create_client, Client

SUPABASE_URL = "https://msgwxxyntucducvyqyao.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1zZ3d4eHludHVjZHVjdnlxeWFvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY3NzM0NjYsImV4cCI6MjA2MjM0OTQ2Nn0.tTzOiRUPSDFiJTOFZyRtr4_Zuy1N1TCyHV3a-QMuJDM"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
