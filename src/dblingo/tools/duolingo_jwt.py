import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as BraveService
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.service import Service as ChromiumService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.core.os_manager import ChromeType

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

USER_NAME = os.environ.get('DUOLINGO_USER_NAME')
PASSWORD = os.environ.get('DUOLINGO_PASSWORD')

def get_webdriver():
    try:
        return webdriver.Chrome(service=BraveService(ChromeDriverManager(chrome_type=ChromeType.BRAVE).install()))
    except Exception as e:
        print("Failed to find brave", e)
    try:
        return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    except Exception as e:
        print("Failed to find chrome", e)
    try:
        return webdriver.Chrome(service=ChromeService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()))
    except Exception as e:
        print("Failed to find chromium", e)
    try: 
        return webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
    except:
        raise Exception("Failed to find any browser")

def get_jwt_token(user_name, password):
    """Get JWT token from duolingo"""
    if not user_name or not password:
        print("missing username or password")
        return ''
    driver = get_webdriver()

    driver.get("https://www.duolingo.com")
    accept_cookies = driver.find_element(By.ID, 'onetrust-accept-btn-handler')
    accept_cookies.click()
    have_account = driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/header/div[2]/div[2]/div/button/span")
    have_account.click()

    email_field = driver.find_element(By.XPATH, '//*[@id="overlays"]/div[3]/div/div/form/div[1]/div[1]/div[1]/input')
    email_field.send_keys(user_name)
    password_field = driver.find_element(By.XPATH, '//*[@id="overlays"]/div[3]/div/div/form/div[1]/div[1]/div[2]/input')
    password_field.send_keys(password)
    login_button = driver.find_element(By.XPATH, '//*[@id="overlays"]/div[3]/div/div/form/div[1]/button')
    login_button.click()

    jwt_cookie = driver.get_cookie('jwt_token')
    jwt_token = jwt_cookie['value']
    print(f"your JWT token is {jwt_token}")
    driver.close()
    return jwt_token

if __name__ == "__main__":
    if not USER_NAME or not PASSWORD:
        print("Please set DUOLINGO_USER_NAME and DUOLINGO_PASSWORD environment variables to run this automatically.")
        USER_NAME = input("Enter your duolingo username: ")
        PASSWORD = input("Enter your duolingo password: ")
    get_jwt_token(user_name=USER_NAME, password=PASSWORD)
