from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from urllib.parse import quote
import os

DELAY = 30

def send_messages(driver, numbers, message):
    for idx, number in enumerate(numbers):
        number = number.strip()
        if number == "":
            continue

        print(f'\n{idx+1}/{len(numbers)} => Sending message to {number}')

        try:
            url = f'https://web.whatsapp.com/send?phone={number}&text={message}'
            sent = False

            for i in range(3):
                if not sent:
                    driver.get(url)

                    try:
                        click_btn = WebDriverWait(driver, DELAY).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Send']"))
                        )
                    except Exception:
                        print(f"Retry ({i+1}/3) for {number}")
                        print("Check internet or WhatsApp alerts.")
                    else:
                        sleep(2)
                        click_btn.click()
                        sent = True
                        print(f'✅ Message sent to: {number}')
                        sleep(10)  # 🔥 delay to avoid ban

        except Exception as e:
            print(f'❌ Failed for {number}: {e}')


def print_intro():
    print("\n**********************************************************")
    print("*****  THANK YOU FOR USING WHATSAPP BULK MESSENGER  ******")
    print("**********************************************************")


def get_message():
    with open("message.txt", "r", encoding="utf8") as f:
        message = f.read()

    print('\n📩 Your message:')
    print(message)

    return quote(message)


def get_numbers():
    numbers = []
    with open("numbers.txt", "r") as f:
        for line in f.read().splitlines():
            if line.strip():
                numbers.append(line.strip())

    return numbers


def get_driver():
    options = Options()

    # 🔥 FIXED CRASH OPTIONS
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    # ✅ Optional: keep login session (safe path)
    options.add_argument("user-data-dir=C:/temp/chrome-profile")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    return driver


def login_whatsapp(driver):
    print('\n🔐 Opening WhatsApp Web...')
    driver.get('https://web.whatsapp.com')

    input("👉 After scanning QR and chats load, press ENTER...")


def main():
    print_intro()

    message = get_message()
    numbers = get_numbers()

    print(f"\n📱 Found {len(numbers)} numbers.")

    driver = get_driver()

    login_whatsapp(driver)

    send_messages(driver, numbers, message)

    driver.quit()

    print("\n✅ All done! Messages sent successfully.")


if __name__ == "__main__":
    main()