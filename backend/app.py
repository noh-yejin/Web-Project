from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from backend.supabase_client import supabase
from fastapi.responses import RedirectResponse
import requests
import json
import hashlib
import re

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# Serve Static Files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Page Routing
@app.get("/")
async def index_page():
    return FileResponse("frontend/html/login.html")

@app.get("/signup")
async def signup_page():
    return FileResponse("frontend/html/signup.html")

@app.get("/project")
async def project_page():
    return FileResponse("frontend/html/main.html")

@app.get("/check_id")
async def check_id(user_id: str):
    response = supabase.table("users").select("user_id").eq("user_id", user_id).execute()
    exists = len(response.data) > 0
    return {"exists": exists}

# Sign-Up API
@app.post("/signup")
async def signup(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    password = data.get("password")
    password_confirm = data.get("password_confirm")
    gender = data.get("gender")
    email = data.get("email")
    marketing = data.get("marketing", False)

    if password != password_confirm:
        return JSONResponse(status_code=400, content={"message": "Passwords do not match."})

    response = supabase.table("users").select("user_id").eq("user_id", user_id).execute()
    if len(response.data) > 0:
        return JSONResponse(status_code=400, content={"message": "The user ID is already taken."})

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    supabase.table("users").insert({
        "user_id": user_id,
        "password": hashed_password,
        "gender": gender,
        "email": email,
        "marketing": marketing
    }).execute()

    return {"message": "Sign-up completed successfully!"}

# Login API
@app.post("/login")
async def login(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    password = data.get("password")

    response = supabase.table("users").select("user_id").eq("user_id", user_id).eq("password", password).execute()
    if len(response.data) > 0:
        return {"message": " Login successful!", "user_id": user_id}
    else:
        return JSONResponse(status_code=401, content={"message": "Incorrect user ID or password."})


@app.post("/analyze")
async def analyze(request: Request):
    body = await request.json()
    user_input = body["text"]
    user_id = body.get("user_id", "anonymous")
    entry_date = body.get("entry_date")

    try:
        gpt_response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": "Bearer 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",   #Bearer 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
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/llama-3-8b-instruct",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a warm, empathetic assistant who gently supports users through emotion journaling.\n\n"
                            "Your job is to analyze the user's sentence and reply in compact JSON with the following 3 fields:\n"
                            "- emotion: one-word emotion label (e.g., 'sadness', 'joy', 'anger', etc.)\n"
                            "- message: a warm, comforting message that acknowledges their feelings and validates them\n"
                            "- recommendation: a soft, caring suggestion that could help with their emotional state\n\n"
                            "⚠️ Important:\n"
                            "- Do not summarize their sentence.\n"
                            "- Respond ONLY in JSON format and DO NOT include any explanation or greeting. "
                            "- Speak with kindness and compassion.\n"
                            "- Your response must be strictly valid JSON with no explanations, markdown, or formatting.\n\n"
                            "JSON format:\n"
                            "{\n"
                            "  \"emotion\": \"...\",\n"
                            "  \"message\": \"...\",\n"
                            "  \"recommendation\": \"...\"\n"
                            "}"
                        )
                    },
                    {
                        "role": "user",
                        "content": f'Analyze this sentence: "{user_input}"'
                    }
                ]
            }

        )

        if gpt_response.status_code != 200:
            raise ValueError(f"LLM request failed: {gpt_response.status_code}")

        gpt_data = gpt_response.json()
        gpt_text = gpt_data["choices"][0]["message"]["content"]
        print("🔎 Raw GPT output:", gpt_text)


        json_str_match = re.search(r"\{[\s\S]*?\}", gpt_text)
        if not json_str_match:
            raise ValueError("Could not extract JSON from GPT output.")

        result = json.loads(json_str_match.group(0))

        supabase.table("emotions").insert({
            "user_id": user_id,
            "user_input": user_input,
            "emotion": result.get("emotion", "unknown"),
            "message": result.get("message", ""),
            "recommendation": result.get("recommendation", ""),
            "date": entry_date
        }).execute()

        return result

    except Exception as e:
        print("❌ Error during emotion analysis:", e)
        return JSONResponse(
            status_code=500,
            content={
                "emotion": "unknown",
                "message": "We're having trouble understanding your feelings right now, but you're not alone.",
                "recommendation": "Take a deep breath, and feel free to try again when you're ready."
            }
        )