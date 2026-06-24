from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import os
import random
import time
from utils import (
    random_delay, 
    type_like_human, 
    simulate_mouse_movement, 
    configure_stealth_options, 
    apply_stealth_cdp
)

DELAY = 30

def send_text_message(driver, message):
    """Send text message using typing simulation."""
    try:
        input_selectors = [
            "//div[@data-testid='conversation-compose-box-input']",
            "//div[@contenteditable='true' and @data-tab='1']",
            "//div[contains(@class, 'copyable-text') and @contenteditable='true']",
            "//footer//div[@contenteditable='true']"
        ]
        
        input_box = None
        for selector in input_selectors:
            try:
                input_box = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                break
            except:
                continue
        
        if not input_box:
            raise Exception("Could not find message input box")
        
        type_like_human(input_box, message)
        random_delay(0.5, 1.2)
        
        # Click send or press Enter
        try:
            send_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='send']"))
            )
            try:
                from selenium.webdriver.common.action_chains import ActionChains
                ActionChains(driver).move_to_element(send_btn).perform()
                random_delay(0.1, 0.4)
            except:
                pass
            send_btn.click()
        except:
            input_box.send_keys(Keys.RETURN)
        
        random_delay(1.5, 3.0)
    except Exception as e:
        print(f"❌ Error sending message text: {e}")
        raise


def send_messages(driver, numbers, message):
    total = len(numbers)
    batch_limit = random.randint(5, 8)
    sent_in_batch = 0

    for idx, number in enumerate(numbers):
        number = number.strip().replace("+", "").replace(" ", "").replace("-", "")
        if not number.startswith("91") and len(number) == 10:
            number = "91" + number

        if number == "":
            continue

        print(f'\n{"="*60}')
        print(f'📱 {idx+1}/{total} => Processing +{number}')
        print(f'{"="*60}')

        try:
            simulate_mouse_movement(driver)
            random_delay(1.0, 2.5)

            # 1. Click search button
            print("🔍 Clicking new chat/search button...")
            try:
                search_btn = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div/div[3]/div/div[3]/header/header/div/span/div/div[1]/span/div/button/div/div/div[1]/span'))
                )
                try:
                    from selenium.webdriver.common.action_chains import ActionChains
                    ActionChains(driver).move_to_element(search_btn).perform()
                    random_delay(0.2, 0.6)
                except:
                    pass
                search_btn.click()
            except Exception as e:
                print("⚠️ Could not click search button")
            random_delay(1.5, 3.0)

            # 2. Fill number in search bar
            print("⌨️  Typing number in search bar...")
            search_bar = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div/div/div[3]/div/div[2]/div[1]/div/span/div/span/div/div[1]/div/div/div/div/div/div[2]/input'))
            )
            search_bar.click()
            random_delay(0.2, 0.5)
            search_bar.send_keys(Keys.CONTROL + "a")
            random_delay(0.1, 0.3)
            search_bar.send_keys(Keys.DELETE)
            random_delay(0.3, 0.7)
            for char in number:
                search_bar.send_keys(char)
                random_delay(0.05, 0.18)
            random_delay(3.5, 5.5)

            # 3. Click the contact result
            print("👆 Clicking the contact result...")
            try:
                result = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div/div[3]/div/div[2]/div[1]/div/span/div/span/div/div[3]/div[2]/div[2]/div[2]/div[2]/div'))
                )
                try:
                    from selenium.webdriver.common.action_chains import ActionChains
                    ActionChains(driver).move_to_element(result).perform()
                    random_delay(0.2, 0.5)
                except:
                    pass
                result.click()
                print("✅ Chat loaded")
                random_delay(1.5, 3.0)
            except Exception as e:
                print("❌ Contact not found or clickable")
                continue

            # 4. Send Message
            send_text_message(driver, message)
            print(f'✅ Message sent to: +{number}')
            sent_in_batch += 1

            # Anti-ban delay & batch cooldown between contacts
            if idx < total - 1:
                if sent_in_batch >= batch_limit:
                    cooldown = random.uniform(75.0, 150.0)
                    print(f"\n☕ Batch limit of {batch_limit} reached. Taking a longer cooldown of {cooldown:.2f}s...")
                    time.sleep(cooldown)
                    batch_limit = random.randint(5, 8)
                    sent_in_batch = 0
                else:
                    wait_time = random.uniform(15.0, 28.0)
                    print(f"⏳ Waiting {wait_time:.2f}s before next contact...")
                    time.sleep(wait_time)

        except Exception as e:
            print(f'❌ Failed for +{number}: {e}')


def print_intro():
    print("\n**********************************************************")
    print("*****  THANK YOU FOR USING WHATSAPP BULK MESSENGER  ******")
    print("**********************************************************")


def get_message():
    with open("message.txt", "r", encoding="utf8") as f:
        message = f.read()

    print('\n📩 Your message:')
    print(message)

    return message.strip()


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
    # options.add_experimental_option("excludeSwitches", ["enable-logging"])

    # ✅ Optional: keep login session (safe path)
    options.add_argument("user-data-dir=C:/temp/chrome-profile")

    # Apply anti-bot stealth options
    options = configure_stealth_options(options)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    # Apply CDP stealth script
    apply_stealth_cdp(driver)

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