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
from datetime import date
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
    signup_date = date.today().isoformat()

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
        "marketing": marketing,
        "signup_date": signup_date
    }).execute()

    return {"message": "Sign-up completed successfully!"}

# Login API
@app.post("/login")
async def login(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    password = data.get("password")

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    response = supabase.table("users") \
        .select("user_id, password") \
        .eq("user_id", user_id) \
        .execute()

    if not response.data:
        return JSONResponse(status_code=401, content={"message": "Incorrect user ID or password."})

    user = response.data[0]

    if user["password"] != hashed_password:
        return JSONResponse(status_code=401, content={"message": "Incorrect user ID or password."})

    return {"message": "Login successful!", "user_id": user_id}

@app.get("/users/{user_id}")
async def get_user_info(user_id: str):
    response = supabase.table("users").select("user_id", "email", "signup_date").eq("user_id", user_id).execute()
    if len(response.data) == 0:
        return JSONResponse(status_code=404, content={"message": "User not found"})
    user = response.data[0]
    return {
        "user_id": user["user_id"],
        "email": user["email"],
        "signup_date": user.get("signup_date")
    }
@app.delete("/users/{user_id}")
async def delete_user(user_id: str):
    response = supabase.table("users").delete().eq("user_id", user_id).execute()

    if not response.data:
        return JSONResponse(status_code=404, content={"message": "User not found"})

    return {"message": "User deleted successfully"}

def extract_json(text: str) -> dict:
    import json
    import re

    # 기본 JSON 객체를 찾음
    match = re.search(r"\{[\s\S]+?\}", text)
    if not match:
        # 괄호가 열렸지만 닫히지 않은 경우 보정
        start = text.find("{")
        if start == -1:
            raise ValueError("No JSON object found.")
        json_str = text[start:]
        if not json_str.endswith("}"):
            json_str += "}"
    else:
        json_str = match.group(0)

    # 다시 한번 마무리 보정
    if not json_str.endswith("}"):
        json_str += "}"

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print("⚠️ JSONDecodeError:", e)
        raise ValueError("Malformed JSON from GPT output.")


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
                "Authorization": "Bearer ~~",
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/llama-3-8b-instruct",
                "temperature": 0.2,  
                "messages": [
                    {
                        "role": "system",
                        "content": (
                                "You are a warm, empathetic assistant who gently supports users through emotion journaling.\n\n"
                                "Your job is to analyze the user's sentence and reply in **compact valid JSON** with the following 3 fields:\n"
                                "- emotion: one-word emotion label (e.g., 'sadness', 'joy', 'anger', etc.)\n"
                                "- message: a warm, comforting message that acknowledges their feelings and validates them\n"
                                "- recommendation: a soft, caring suggestion that could help with their emotional state\n\n"
                                "⚠️ STRICT RULES:\n"
                                "- DO NOT summarize or explain their sentence.\n"
                                "- DO NOT include any preamble, explanation, greeting, or sign-off.\n"
                                "- DO NOT wrap your output in markdown or code blocks.\n"
                                "- ONLY return a **strictly valid JSON object**.\n"
                                "- Your response MUST start with '{' and MUST end with '}'.\n"
                                "- DO NOT leave out the closing curly brace (}).\n"
                                "- Avoid trailing text or commentary after the JSON object.\n\n"
                                "JSON format example:\n"
                                "{\n"
                                "  \"emotion\": \"sadness\",\n"
                                "  \"message\": \"I'm really sorry you're feeling down. It's okay to feel like this.\",\n"
                                "  \"recommendation\": \"Try writing about what's on your mind. You might find some clarity.\"\n"
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

        # JSON 추출
        json_str_match = re.search(r"\{[\s\S]*?\}", gpt_text)
        if not json_str_match:
            raise ValueError("Could not extract JSON from GPT output.")
        result = json.loads(json_str_match.group(0))

        # 감정 점수 분류
        score = classify_emotion(result.get("emotion", "neutral"))

        # DB 저장
        supabase.table("emotions").insert({
            "user_id": user_id,
            "user_input": user_input,
            "emotion": result.get("emotion", "unknown"),
            "message": result.get("message", ""),
            "recommendation": result.get("recommendation", ""),
            "date": entry_date,
            "score": score  
        }).execute()

        return {
            "emotion": result.get("emotion", "unknown"),
            "message": result.get("message", ""),
            "recommendation": result.get("recommendation", "")
        }

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
    

def classify_emotion(emotion_label: str) -> int:
    prompt = f"""
        You are an assistant that classifies emotions by their emotional valence (positivity or negativity).

        Return ONLY a JSON object that includes:
        - emotion: the original emotion word
        - score: a numeric integer score from -2 to +2
        - meaning: a short description of the emotion

        Scoring rules:
        - +2 = Very Positive (e.g., joy, love)
        - +1 = Positive (e.g., calm, relief)
        -  0 = Neutral (e.g., surprise)
        - -1 = Negative (e.g., sadness, guilt)
        - -2 = Very Negative (e.g., anger, fear)

        Classify this emotion: "{emotion_label}"

        Respond with ONLY a valid JSON like:
        {{
        "emotion": "...",
        "score": ...,
        "meaning": "..."
        }}
        """

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization":"Bearer ~~", 
            "Content-Type": "application/json"
        },
        json={
            "model": "meta-llama/llama-3-8b-instruct",  
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
    )

    if response.status_code != 200:
        print(f"❌ API Error: {response.status_code}")
        return 0  # fallback 중립값

    try:
        raw = response.json()["choices"][0]["message"]["content"]
        print("🔍 Raw LLM output:", raw)

        match = re.search(r"\{[\s\S]*?\}", raw)
        if not match:
            raise ValueError("JSON not found in response.")

        parsed = json.loads(match.group(0))
        return int(parsed.get("score", 0))

    except Exception as e:
        print("⚠️ Parsing error:", e)
        return 0
    
@app.get("/weekly_emotions")
async def get_weekly_emotions(user_id: str):
    from datetime import datetime, timedelta

    today = datetime.today()
    dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]  # 7일 전 ~ 오늘
    labels = [(today - timedelta(days=i)).strftime("%a") for i in range(6, -1, -1)]

    scores = []
    for day in dates:
        res = supabase.table("emotions") \
            .select("score") \
            .eq("user_id", user_id) \
            .eq("date", day) \
            .execute()
        if res.data and res.data[0].get("score") is not None:
            scores.append(int(res.data[0]["score"]))
        else:
            scores.append(None)

    message = generate_daily_trend_message(scores)

    return {
        "labels": labels,
        "scores": scores,
        "message": message
    }

def generate_daily_trend_message(scores: list) -> str:
    clean = [s for s in scores if s is not None]

    if not clean:
        return "We couldn't find emotion data for this week. Try writing your journal daily!"

    trend = ""
    if clean[0] < clean[-1]:
        trend = "upward"
    elif clean[0] > clean[-1]:
        trend = "downward"
    else:
        trend = "stable"

    prompt = (
        f"You are an empathetic assistant.\n"
        f"Given the user's emotional trend over the past 7 days: {scores}, "
        f"summarize in one warm and short sentence reflecting the trend: {trend}. "
        f"Acknowledge their emotional journey and give a kind suggestion or encouragement."
    )

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": "Bearer ~~", 
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/llama-3-8b-instruct",
                "messages": [{"role": "user", "content": prompt}]
            }
        )

        if response.status_code != 200:
            print("❌ LLM API Error:", response.status_code)
            return "We couldn’t analyze your trend today. Try again later."

        raw = response.json()["choices"][0]["message"]["content"]
        match = re.search(r"^(.*?)(\n|$)", raw.strip())
        return match.group(1) if match else raw.strip()

    except Exception as e:
        print("⚠️ Error parsing LLM response:", e)
        return "Your emotional journey is important. Keep going, one day at a time!"


@app.get("/calendar_data")
async def get_calendar_data(user_id: str, year: int, month: int):
    from datetime import datetime

    start_date = datetime(year, month, 1).strftime("%Y-%m-%d")
    if month == 12:
        end_date = datetime(year + 1, 1, 1).strftime("%Y-%m-%d")
    else:
        end_date = datetime(year, month + 1, 1).strftime("%Y-%m-%d")

    response = supabase.table("emotions") \
        .select("date, score, emotion") \
        .eq("user_id", user_id) \
        .gte("date", start_date) \
        .lt("date", end_date) \
        .execute()

    results = []
    for row in response.data:
        try:
            day = int(row["date"].split("-")[2])
            score = row.get("score")
            if score is not None:
                score = int(score)
            else:
                score = None

            results.append({
                "day": day,
                "score": score,
                "emotion": row.get("emotion", "")
            })
        except Exception as e:
            print("⚠️ Error parsing row:", row, e)
            continue

    return results
