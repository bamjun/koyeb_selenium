from fastapi import FastAPI
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

user = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"

app = FastAPI()



@app.get("/")
async def root():
    return {"message": "Hello from FastAPI on Koyeb!"}


@app.get("/get-title")
async def get_page_title(user: str = "default-agent"):
    # Set up Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")  # GPU 비활성화 (필요시)
    chrome_options.add_argument("--window-size=1920,1080")  # 크기 설정
    chrome_options.add_argument(f"User-Agent={user}")

    # Initialize the WebDriver (Chrome)
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Open a website (example: Google)
        driver.get("https://www.google.com")

        # Get the title of the page
        title = driver.title

    finally:
        # Close the WebDriver
        driver.quit()

    # Return the title as a response
    return {"Page title": title}
