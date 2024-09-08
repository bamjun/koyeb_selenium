import os
import time

from fastapi import FastAPI, Query
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire import webdriver  # Selenium 대신 seleniumwire 사용
import requests
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI on Koyeb!"}


#http://localhost:8000/get-title?user=myUser&password=myPass
@app.get("/get-title")
async def get_page_title(user: str = "user", password: str = "password"):
    if user == "user":
        return {"error": "Invalid"}
    
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"

    # Chrome 옵션 설정
    chrome_options = Options()

    chrome_options.add_argument("--incognito")  # 시크릿 모드 추가
    chrome_options.add_argument('--ignore-certificate-errors')  # 인증서 오류 무시
    chrome_options.add_argument('--ignore-ssl-errors')  # SSL 오류 무시
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.add_argument("--disable-gpu")  # GPU 비활성화 (필요시)
    # chrome_options.add_argument("--window-size=1920,1080")  # 크기 설정
    chrome_options.add_argument(f"User-Agent={user_agent}")

    # Initialize the WebDriver (Chrome)
    driver = webdriver.Chrome(seleniumwire_options={'verify_ssl': False}, options=chrome_options)

    try:
        # Open a website (example: Google)
        # Discord URL로 이동
        driver.get("https://discord.com/login")

        # 명시적 대기로 페이지 로딩 완료 및 로그인 폼 대기
        email_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        password_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )

        # 아이디와 비밀번호 입력
        email_input.send_keys(user)  # 여기에 아이디 입력
        password_input.send_keys(password)  # 여기에 비밀번호 입력

        # 로그인 버튼 클릭 (로그인 버튼의 정확한 클래스 확인 필요)
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[text()='로그인']"))
        )
        login_button.click()

        time.sleep(10)

        # 네트워크 요청 중에서 헤더가 있는 모든 요청을 출력
        for request in driver.requests:
            if 'Authorization' in request.headers:
                authorization_key = request.headers['Authorization']
                break

        # Get the title of the page
        title = driver.title
        
    finally:
        # Close the WebDriver
        driver.quit()

    # Return the title as a response
    return {"Authorization": authorization_key}


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
    url: str = Query("https://discord.com/api/v9/channels/384597925134860289/messages")
):
    # Discord 채널 URL
    # url = "https://discord.com/api/v9/channels/384597925134860289/messages"
    
    # Discord로 보낼 메시지 내용
    data = {
        "content": payload.content
    }
    
    # Authorization 헤더 설정
    headers = {
        "Authorization": password
    }
    
    # Discord로 요청 보내기
    res = requests.post(url, json=data, headers=headers)
    
    # 상태 코드에 따른 반환 메시지
    if res.status_code == 200:
        return {"message": "send message success"}
    elif res.status_code == 401:
        return {"message": "failed to send message: Unauthorized"}
    elif res.status_code == 429:
        return {"message": "failed to send message: Rate limited"}
    else:
        return {"message": f"unexpected error: {res.status_code}"}