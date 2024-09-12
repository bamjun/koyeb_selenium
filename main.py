import requests
from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI on Koyeb!"}


    # POST /send-message?password=YOUR_DISCORD_AUTH_TOKEN&url=https://discord.com/api/v9/channels/NEW_CHANNEL_ID/messages HTTP/1.1
    # Host: localhost:8000
    # Content-Type: application/json
    # {
    #     "content": "This is a test message with query params and body"
    # }

# 요청 바디로 받을 데이터 모델 정의
class MessageContent(BaseModel):
    content: str

# Discord 메시지를 보내는 함수
@app.post("/send-message")
async def send_message(
    payload: MessageContent,  # 바디로 받는 content
    password: str = Query("password"),  # 쿼리 파라미터로 받는 password
    url: str = Query("https://discord.com/channels/384541991289094147/384546383207858186"),  # Discord 채널 URL
):
    # URL에서 채널 ID 추출 ("/channels/" 뒤에 있는 ID 값을 추출)
    if "/channels/" in url:
        try:
            channel_id = url.split("/channels/")[1].split("/")[1]
            api_url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
        except IndexError:
            return {"error": "Invalid URL format"}
    else:
        return {"error": "URL must contain /channels/"}

    # Discord로 보낼 메시지 내용
    data = {"content": payload.content}

    # Authorization 헤더 설정
    headers = {"Authorization": password}

    # Discord로 요청 보내기
    res = requests.post(api_url, json=data, headers=headers)

    # 상태 코드에 따른 반환 메시지
    if res.status_code == 200:
        return {"message": "send message success"}
    elif res.status_code == 401:
        return {"message": "failed to send message: Unauthorized"}
    elif res.status_code == 429:
        return {"message": "failed to send message: Rate limited"}
    else:
        return {"message": f"unexpected error: {res.status_code}"}