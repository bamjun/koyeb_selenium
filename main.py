import os
import time

import requests
from fastapi import FastAPI, Query
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire import webdriver  # Selenium 대신 seleniumwire 사용
import configparser
config = configparser.ConfigParser()
config.read("config.ini")
# 2Captcha API key


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello from FastAPI on Koyeb!"}


# 2Captcha API key
API_KEY = config["key"]["capcha_api"]

# hCaptcha 처리 함수
def handle_hcaptcha(driver):
    try:
        # hCaptcha iframe 탐색 및 전환
        hcaptcha_frame = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//iframe[contains(@title, 'hCaptcha')]"))
        )
        driver.switch_to.frame(hcaptcha_frame)

        # hCaptcha의 sitekey 가져오기
        sitekey = driver.find_element(By.XPATH, "//div[@class='h-captcha']").get_attribute("data-sitekey")

        # 2Captcha API를 사용하여 hCaptcha 해결 요청 보내기
        captcha_id = requests.post(
            f"http://2captcha.com/in.php?key={API_KEY}&method=hcaptcha&sitekey={sitekey}&pageurl={driver.current_url}"
        ).text.split('|')[1]

        # 2Captcha API로부터 응답을 기다림
        while True:
            captcha_response = requests.get(
                f"http://2captcha.com/res.php?key={API_KEY}&action=get&id={captcha_id}"
            ).text
            if 'CAPCHA_NOT_READY' in captcha_response:
                time.sleep(5)  # 5초 대기 후 다시 확인
            else:
                break

        # CAPTCHA 솔루션 받기
        captcha_solution = captcha_response.split('|')[1]

        # 해결된 CAPTCHA 솔루션을 hCaptcha에 입력
        driver.execute_script(f"document.getElementById('g-recaptcha-response').style.display = 'block';")
        driver.execute_script(f"document.getElementById('g-recaptcha-response').innerHTML = '{captcha_solution}';")

        # hCaptcha 제출
        submit_button = driver.find_element(By.ID, "submit")
        submit_button.click()

        # 제출 후 처리 대기
        WebDriverWait(driver, 10).until(EC.url_changes(driver.current_url))

    except Exception as e:
        print(f"hCaptcha 처리 중 오류 발생: {e}")
        return False

    return True


# http://localhost:8000/get-title?user=myUser&password=myPass
@app.get("/get-title")
async def get_page_title(user: str = "user", password: str = "password"):
    if user == "user":
        return {"error": "Invalid"}

    # Chrome 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
    chrome_options.add_argument("accept=text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7")
    chrome_options.add_argument("accept-language=ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7")
    chrome_options.add_argument("sec-fetch-site=none")
    chrome_options.add_argument("sec-fetch-mode=navigate")
    chrome_options.add_argument("sec-fetch-user=?1")
    chrome_options.add_argument("sec-fetch-dest=document")
    chrome_options.add_argument("--incognito")  # 시크릿 모드 추가
    chrome_options.add_argument("--ignore-certificate-errors")  # 인증서 오류 무시
    chrome_options.add_argument("--ignore-ssl-errors")  # SSL 오류 무시
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize the WebDriver (Chrome)
    driver = webdriver.Chrome(seleniumwire_options={"verify_ssl": False}, options=chrome_options)

    try:
        # Open a website (example: Discord)
        driver.get("https://discord.com/login")

        # 명시적 대기로 페이지 로딩 완료 및 로그인 폼 대기
        email_input = WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.NAME, "email")))
        password_input = WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.NAME, "password")))

        # 아이디와 비밀번호 입력
        email_input.send_keys(user)
        password_input.send_keys(password)

        time.sleep(20)

        # 로그인 버튼 클릭
        login_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and contains(@class, 'button_dd4f85')]"))
        )
        login_button.click()
        
        # 로그인 후 스크린샷 찍기
        screenshot_path = "login_page1.png"  # 저장할 경로 설정
        driver.save_screenshot(screenshot_path)
        time.sleep(10)

        # hCaptcha 존재 시 해결
        if handle_hcaptcha(driver):
            print("hCaptcha 처리 완료")

        time.sleep(10)
        # 로그인 후 스크린샷 찍기
        screenshot_path = "login_page2.png"  # 저장할 경로 설정
        driver.save_screenshot(screenshot_path)

        # 네트워크 요청 중에서 헤더가 있는 모든 요청을 출력
        authorization_key = ""
        for request in driver.requests:
            if "Authorization" in request.headers:
                authorization_key += request.headers["Authorization"]
        
        # 로그인 후 스크린샷 찍기
        screenshot_path = "login_page3.png"  # 저장할 경로 설정
        driver.save_screenshot(screenshot_path)

    except Exception as e:
        # 오류가 발생했을 때 스크린샷 찍기
        error_screenshot_path = "error_page.png"
        driver.save_screenshot(error_screenshot_path)

        # 현재 페이지의 전체 HTML 가져오기
        page_source = driver.page_source

        driver.quit()
        return {"error": str(e), "screenshot": error_screenshot_path, "page_source": page_source}

    finally:
        # Close the WebDriver
        driver.quit()

    # Return the authorization key as a response
    return {"Authorization": authorization_key, "screenshot": screenshot_path}

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
    url: str = Query("https://discord.com/api/v9/channels/384597925134860289/messages"),
):
    # Discord 채널 URL
    # url = "https://discord.com/api/v9/channels/384597925134860289/messages"

    # Discord로 보낼 메시지 내용
    data = {"content": payload.content}

    # Authorization 헤더 설정
    headers = {"Authorization": password}

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
