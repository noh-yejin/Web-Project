# backend/supabase_client.py

from supabase import create_client, Client
from dotenv import load_dotenv
from supabase import create_client, Client
import os
load_dotenv()  # .env 파일 로드

SUPABASE_URL = os.getenv("SUPABASE_URL")  # Supabase 프로젝트 URL / Supabase project URL
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # Supabase 비공개 API 키 (anon 키) / Supabase secret anon key

# Supabase 클라이언트 객체 생성 / Create a Supabase client instance

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
