from flask import Flask
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


user = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"

app = Flask(__name__)

@app.route('/')
def scrape():
    # Set up Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"User-Agent={user}")

    # Initialize the WebDriver (Chrome)
    driver = webdriver.Chrome(options=chrome_options)

    # Open a website (example: Google)
    driver.get("https://www.google.com")

    # Get the title of the page
    title = driver.title

    # Close the WebDriver
    driver.quit()

    # Return the title as a response
    return f"Page title: {title}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
