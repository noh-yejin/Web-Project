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
from dotenv import load_dotenv
import os

load_dotenv()  # .env 파일 로드

api_key = os.getenv("OPENROUTER_API_KEY")

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 비밀번호 해시 함수 / Password hashing function
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# 정적 파일 서빙 설정 / Mount static file directory
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Page Routing
@app.get("/")
async def index_page():
    return FileResponse("frontend/html/login.html")  # 로그인 페이지 반환 / Return login page

@app.get("/signup")
async def signup_page():
    return FileResponse("frontend/html/signup.html")   # 회원가입 페이지 반환 / Return signup page

@app.get("/project")
async def project_page():
    return FileResponse("frontend/html/main.html")   # 메인 프로젝트 페이지 반환 / Return main project page

@app.get("/check_id")    # ID 중복 확인 API / API to check if user_id already exists
async def check_id(user_id: str):
    response = supabase.table("users").select("user_id").eq("user_id", user_id).execute()  # 해당 user_id가 존재하는지 조회 / Query if user_id exists
    exists = len(response.data) > 0  # 결과가 있으면 존재함 / True if user_id is already in DB
    return {"exists": exists}   # 결과 반환 / Return result

# 회원가입 API / Sign-Up API
@app.post("/signup")
async def signup(request: Request):
    data = await request.json()  # JSON 데이터 파싱 / Parse JSON request body
    user_id = data.get("user_id")  # 사용자 ID / User ID
    password = data.get("password")  # 비밀번호 / Password
    password_confirm = data.get("password_confirm")  # 비밀번호 확인 / Password confirmation
    gender = data.get("gender")  # 성별 / Gender
    email = data.get("email")  # 이메일 / Email
    marketing = data.get("marketing", False)  # 마케팅 수신 동의 여부 / Marketing agreement (optional)
    signup_date = date.today().isoformat()  # 오늘 날짜 문자열 / Today's date as string

    if password != password_confirm:  # 비밀번호 불일치 시 오류 반환 / Return error if passwords don't match
        return JSONResponse(status_code=400, content={"message": "Passwords do not match."})

    response = supabase.table("users").select("user_id").eq("user_id", user_id).execute()  # 기존 user_id 존재 여부 확인 / Check if user_id already exists
    if len(response.data) > 0:
        return JSONResponse(status_code=400, content={"message": "The user ID is already taken."})  # 중복 시 오류 / Return error on duplication

    hashed_password = hashlib.sha256(password.encode()).hexdigest()  # 비밀번호 해싱 / Hash the password

    # 사용자 DB에 삽입 / Insert user into database
    supabase.table("users").insert({
        "user_id": user_id,
        "password": hashed_password,
        "gender": gender,
        "email": email,
        "marketing": marketing,
        "signup_date": signup_date
    }).execute()

    return {"message": "Sign-up completed successfully!"}  # 성공 메시지 / Return success message

# 로그인 API / Login API
@app.post("/login")
async def login(request: Request):
    data = await request.json()  # 요청 JSON 파싱 / Parse JSON request
    user_id = data.get("user_id")
    password = data.get("password")

    hashed_password = hashlib.sha256(password.encode()).hexdigest()  # 입력된 비밀번호 해싱 / Hash the input password

    # DB에서 사용자 정보 조회 / Retrieve user record from DB
    response = supabase.table("users") \
        .select("user_id, password") \
        .eq("user_id", user_id) \
        .execute()

    if not response.data:
        return JSONResponse(status_code=401, content={"message": "Incorrect user ID or password."})  # 사용자 없음 / User not found

    user = response.data[0]

    if user["password"] != hashed_password:  # 비밀번호 불일치 / Password mismatch
        return JSONResponse(status_code=401, content={"message": "Incorrect user ID or password."})

    return {"message": "Login successful!", "user_id": user_id}  # 로그인 성공 / Login successful

# 사용자 정보 조회 API / API to get user information
@app.get("/users/{user_id}")
async def get_user_info(user_id: str):
    response = supabase.table("users").select("user_id", "email", "signup_date").eq("user_id", user_id).execute()
    if len(response.data) == 0:
        return JSONResponse(status_code=404, content={"message": "User not found"})  # 사용자 없음 / User not found
    user = response.data[0]
    return {
        "user_id": user["user_id"],
        "email": user["email"],
        "signup_date": user.get("signup_date")
    }

# 사용자 삭제 API / Delete user account
@app.delete("/users/{user_id}")
async def delete_user(user_id: str):
    response = supabase.table("users").delete().eq("user_id", user_id).execute()

    if not response.data:
        return JSONResponse(status_code=404, content={"message": "User not found"})  # 사용자 없음 / User not found

    return {"message": "User deleted successfully"}  # 성공 메시지 / Return success message
# GPT 응답에서 JSON 객체만 추출하는 함수 / Extract JSON object from GPT response text
def extract_json(text: str) -> dict:
    # JSON 형식 추출 (가장 먼저 나오는 {로 시작하고 }로 끝나는 블록)
    matches = re.findall(r"\{[\s\S]*?\}", text.strip())

    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue  # 다음 후보 시도

    # 마지막 수단: {부터 끝까지 붙여서 시도 (단, 너무 불완전한 경우는 제외)
    start = text.find("{")
    if start != -1:
        json_str = text[start:]
        if not json_str.endswith("}"):
            json_str += "}"
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print("⚠️ Fallback JSONDecodeError:", e)

    raise ValueError("❌ Could not extract valid JSON from GPT output.")



@app.post("/analyze")
async def analyze(request: Request):
    body = await request.json()
    user_input = body["text"]   # 사용자가 작성한 글 / User input text
    user_id = body.get("user_id", "anonymous")   # 사용자 ID (없으면 anonymous) / Fallback to anonymous
    entry_date = body.get("entry_date")   # 기록 날짜 / Date of journal entry
 
    try:
        gpt_response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization":f"Bearer {api_key}",
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

         # JSON 파싱 / Parse extracted JSON
        try:
            result = extract_json(gpt_text)
        except ValueError as e:
            print("❌ Error during emotion analysis:", e)
            raise

        # 감정 점수 분류 / Classify score
        score = classify_emotion(result.get("emotion", "neutral"))

        # 결과 DB 저장 / Save to DB
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
    
# 감정 점수 분류 함수 / Classify emotional score based on emotion label

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
            "Authorization":f"Bearer {api_key}",
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
        print("⚠️ Parsing error:", e)  # 오류 시 기본값 반환 / Return neutral score on error
        return 0

# 주간 감정 점수 조회 API / Weekly emotion scores API

@app.get("/weekly_emotions")
async def get_weekly_emotions(user_id: str):
    from datetime import datetime, timedelta

    today = datetime.today()
    dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)] # 최근 7일 날짜 리스트 / Last 7 days
    labels = [(today - timedelta(days=i)).strftime("%a") for i in range(6, -1, -1)]  # 요일 라벨 / Day labels

    scores = []  # 일별 감정 점수 리스트 / Daily scores
    for day in dates:
        res = supabase.table("emotions") \
            .select("score") \
            .eq("user_id", user_id) \
            .eq("date", day) \
            .execute()
        if res.data and res.data[0].get("score") is not None:
            scores.append(int(res.data[0]["score"]))   # 점수가 존재하면 추가 / Append if score exists
        else:
            scores.append(None)  # 데이터 없으면 None / Append None if no data

    message = generate_daily_trend_message(scores)   # 추세 메시지 생성 / Generate trend message

    return {
        "labels": labels,   # 요일 리스트 / Days of week
        "scores": scores,   # 감정 점수 리스트 / Scores
        "message": message  # 분석 메시지 / Trend message
    }

# 주간 감정 추세 메시지 생성 함수 / Generate weekly emotion trend message

def generate_daily_trend_message(scores: list) -> str:
    clean = [s for s in scores if s is not None]  # 유효 점수만 필터링 / Filter valid scores

    if not clean:
        return "We couldn't find emotion data for this week. Try writing your journal daily!"
     # 추세 파악 / Determine trend direction
    trend = ""
    if clean[0] < clean[-1]:
        trend = "upward"  # 상승 추세 / Upward
    elif clean[0] > clean[-1]:
        trend = "downward"  # 하락 추세 / Downward
    else:
        trend = "stable"   # 안정 추세 / Stable

    # LLM에게 분석 요청을 보낼 프롬프트 구성 / Prompt to request warm feedback from GPT
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
                "Authorization":f"Bearer {api_key}",
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
        return match.group(1) if match else raw.strip()   # 첫 줄만 추출 / Only first line

    except Exception as e:
        print("⚠️ Error parsing LLM response:", e)
        return "Your emotional journey is important. Keep going, one day at a time!"

# 감정 캘린더 데이터 API / Calendar data API for emotion entries

@app.get("/calendar_data")
async def get_calendar_data(user_id: str, year: int, month: int):
    from datetime import datetime
    
    # 해당 월이 12월이면 다음 해 1월 1일을 종료일로 설정 / If December, set end as Jan 1 of next year
    start_date = datetime(year, month, 1).strftime("%Y-%m-%d")
    if month == 12:
        end_date = datetime(year + 1, 1, 1).strftime("%Y-%m-%d")
    else:
        end_date = datetime(year, month + 1, 1).strftime("%Y-%m-%d")

    # Supabase에서 해당 사용자와 날짜 범위에 해당하는 감정 데이터 조회 / Fetch emotion records for the month
    response = supabase.table("emotions") \
        .select("date, score, emotion") \
        .eq("user_id", user_id) \
        .gte("date", start_date) \
        .lt("date", end_date) \
        .execute()

    results = []  # 응답을 담을 리스트 / Result list to return
    for row in response.data:
        try:
            day = int(row["date"].split("-")[2])  # 날짜에서 '일(day)' 부분만 추출 / Extract day from 'YYYY-MM-DD'
            score = row.get("score")
            if score is not None:
                score = int(score)  # 점수 존재하면 정수 변환 / Convert to int if exists
            else:
                score = None

            results.append({
                "day": day,  # 해당 일(day) / Day of the month
                "score": score,  # 감정 점수 / Emotion score
                "emotion": row.get("emotion", "")  # 감정 레이블 / Emotion label
            })
        except Exception as e:
            print("⚠️ Error parsing row:", row, e) # 파싱 중 오류 발생 시 출력 / Print on error
            continue

    return results  # 캘린더용 감정 결과 리스트 반환 / Return emotion results for calendar display
