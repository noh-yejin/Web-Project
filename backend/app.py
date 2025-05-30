# from fastapi import FastAPI, Request
# from fastapi.middleware.cors import CORSMiddleware  # CORSMiddleware 추가
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse
# from supabase_client import supabase  # 추가

# import requests

# app = FastAPI()

# # CORS 허용 설정 (모든 출처에 대해 허용)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # 모든 출처 허용 (보안을 위해 구체적인 출처로 제한 가능)
#     allow_credentials=True,
#     allow_methods=["*"],  # 모든 HTTP 메소드 허용 (GET, POST, PUT 등)
#     allow_headers=["*"],  # 모든 헤더 허용
# )

# # 정적 파일 서빙
# app.mount("/static", StaticFiles(directory="../frontend"), name="static")

# # @app.get("/")
# # async def root():
# #     return FileResponse("../frontend/index.html")
# @app.get("/calendar")
# async def calendar_page():
#     return FileResponse("../frontend/calendar.html")

# @app.get("/project")
# async def project_page():
#     return FileResponse("../frontend/project.html")


# @app.post("/analyze")
# async def analyze(request: Request):
#     body = await request.json()
#     user_input = body["text"]

#     # GPT 호출
#     gpt_response = requests.post(
#         "https://openrouter.ai/api/v1/chat/completions",
#         headers={
#             "Authorization": "Bearer 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",  # 개인 키
#             "Content-Type": "application/json"
#         },
#         json={
#             "model": "meta-llama/llama-3-8b-instruct",
#             "messages": [
#                 {"role": "user", "content": f"다음 문장에서 감정을 분석하고, 그 감정(emotion)과 위로의 메시지(message)를 JSON으로 응답해줘: {user_input}"},
#                 {"role": "system", "content": "응답 형식은 반드시 다음과 같아야 해: {\"emotion\": \"...\", \"message\": \"...\"}"}
#             ]
#         }
#     )

#     gpt_data = gpt_response.json()
#     try:
#         gpt_text = gpt_data["choices"][0]["message"]["content"]
#         result = eval(gpt_text)  # 문자열을 JSON dict로 변환 (주의: 실서비스에서는 json.loads 사용 권장)
#     except Exception:
#         result = {
#             "emotion": "unknown",
#             "message": "감정 분석을 처리할 수 없습니다."
#         }
    
#     # Supabase에 저장
#     supabase.table("emotion tables").insert({
#         "user_input": user_input,
#         "emotion": result["emotion"],
#         "message": result["message"]
#     }).execute()

#     return result


from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from supabase_client import supabase
import requests

app = FastAPI()

# ✅ CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 정적 파일 서빙
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

# ✅ 메인 (로그인 + 소개) 페이지
@app.get("/")
async def index_page():
    return FileResponse("../frontend/index.html")

# ✅ 회원가입 페이지
@app.get("/signup")
async def signup_page():
    return FileResponse("../frontend/signup.html")

# ✅ 팀 프로젝트 (로그인 성공 후) 페이지
@app.get("/project")
async def project_page():
    return FileResponse("../frontend/team_project.html")

# ✅ 아이디 중복 확인 API
@app.get("/check_id")
async def check_id(user_id: str):
    response = supabase.table("users").select("user_id").eq("user_id", user_id).execute()
    exists = len(response.data) > 0
    return {"exists": exists}

# ✅ 회원가입 API
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
        return JSONResponse(status_code=400, content={"message": "비밀번호가 일치하지 않습니다."})

    response = supabase.table("users").select("user_id").eq("user_id", user_id).execute()
    if len(response.data) > 0:
        return JSONResponse(status_code=400, content={"message": "중복된 아이디입니다."})

    supabase.table("users").insert({
        "user_id": user_id,
        "password": password,
        "gender": gender,
        "email": email,
        "marketing": marketing
    }).execute()

    return {"message": "회원가입이 완료되었습니다!"}

# ✅ 로그인 API
@app.post("/login")
async def login(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    password = data.get("password")

    response = supabase.table("users").select("user_id").eq("user_id", user_id).eq("password", password).execute()
    if len(response.data) > 0:
        return {"message": "로그인 성공!", "user_id": user_id}
    else:
        return JSONResponse(status_code=401, content={"message": "아이디 또는 비밀번호가 올바르지 않습니다."})

# ✅ 감정 분석 API
@app.post("/analyze")
async def analyze(request: Request):
    body = await request.json()
    user_input = body["text"]

    gpt_response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": "Bearer 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",
            "Content-Type": "application/json"
        },
        json={
            "model": "meta-llama/llama-3-8b-instruct",
            "messages": [
                {
                    "role": "user",
                    "content": f"다음 문장에서 감정을 분석하고, 그 감정(emotion)과 위로의 메시지(message)를 JSON으로 응답해줘: {user_input}"
                },
                {
                    "role": "system",
                    "content": "응답 형식은 반드시 다음과 같아야 해: {\"emotion\": \"...\", \"message\": \"...\"}"
                }
            ]
        }
    )

    gpt_data = gpt_response.json()
    try:
        gpt_text = gpt_data["choices"][0]["message"]["content"]
        result = eval(gpt_text)  # (보안상으로는 json.loads를 추천!)
    except Exception:
        result = {
            "emotion": "unknown",
            "message": "감정 분석을 처리할 수 없습니다."
        }

    supabase.table("emotion tables").insert({
        "user_input": user_input,
        "emotion": result["emotion"],
        "message": result["message"]
    }).execute()

    return result
