# Supabase 클라이언트 초기화 / Initialize Supabase client

from supabase import create_client, Client  # Supabase SDK에서 클라이언트 생성 함수 및 타입 불러옴 / Import required modules from supabase

# Supabase 프로젝트 URL / Supabase project URL
SUPABASE_URL = "https://msgwxxyntucducvyqyao.supabase.co"

# Supabase 비공개 API 키 (anon 키) / Supabase secret anon key
# ⚠️ 실제 서비스에서는 .env 파일 등으로 분리해 관리하는 것이 안전함 / ⚠️ Should be moved to .env file for security in production
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1zZ3d4eHludHVjZHVjdnlxeWFvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY3NzM0NjYsImV4cCI6MjA2MjM0OTQ2Nn0.tTzOiRUPSDFiJTOFZyRtr4_Zuy1N1TCyHV3a-QMuJDM"

# Supabase 클라이언트 객체 생성 / Create a Supabase client instance
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
