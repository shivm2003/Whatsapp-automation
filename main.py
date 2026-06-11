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
import pyperclip

DELAY = 30
IMAGE_PATH = r"C:\Users\shivam\Downloads\whatsapp-bulk-messenger-primary\whatsapp-bulk-messenger-primary\image_converted.jpg"

def send_image_your_way(driver, image_path):
    """Your workflow: + button -> Photos & Videos -> type path -> Enter -> wait 3s -> Enter"""
    try:
        print("📎 Clicking + (attachment) button...")
        
        # Find and click the + / clip / attachment button
        plus_selectors = [
            "//button[@data-testid='clip']",
            "//div[@data-testid='clip']",
            "//span[@data-icon='clip']",
            "//button[contains(@title, 'Attach')]",
            "//div[contains(@title, 'Attach')]",
            "//button[contains(@class, 'attach')]",
            "//span[contains(@data-icon, 'attach')]"
        ]
        
        plus_btn = None
        for selector in plus_selectors:
            try:
                plus_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                break
            except:
                continue
        
        if not plus_btn:
            raise Exception("Could not find + (attachment) button")
        
        plus_btn.click()
        sleep(2)  # Wait for menu to open
        
        # NEW: Select "Photos & Videos" option
        print("🖼️  Selecting 'Photos & Videos' option...")
        
        photos_videos_selectors = [
            "//div[contains(text(), 'Photos & Videos')]",
            "//span[contains(text(), 'Photos & Videos')]",
            "//button[contains(., 'Photos & Videos')]",
            "//div[contains(@data-testid, 'photo')]",
            "//div[contains(@data-testid, 'gallery')]",
            "//span[contains(@data-icon, 'image')]/parent::*/parent::*",
            "//span[contains(@data-icon, 'image')]/ancestor::button",
            "//span[contains(@data-icon, 'image')]/ancestor::div[contains(@role, 'button')]",
            "//div[text()='Photos & Videos']",
            "//*[contains(text(), 'Photos') and contains(text(), 'Videos')]"
        ]
        
        photos_option = None
        for selector in photos_videos_selectors:
            try:
                photos_option = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                break
            except:
                continue
        
        if photos_option:
            photos_option.click()
            print("✅ 'Photos & Videos' selected")
            sleep(2)
        else:
            print("⚠️  Could not find 'Photos & Videos', trying file input directly...")
        
        print("📁 Typing file path...")
        
        # Find the file input (hidden or visible)
        file_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
        
        if not file_inputs:
            raise Exception("No file input found")
        
        # Use the first available file input
        file_input = file_inputs[0]
        
        # Send the file path
        abs_path = os.path.abspath(image_path)
        file_input.send_keys(abs_path)
        
        print(f"✅ Path entered: {abs_path}")
        sleep(1)
        
        # Press Enter to select/open
        print("⏩ Pressing Enter...")
        file_input.send_keys(Keys.RETURN)
        
        # Wait 3 seconds as you requested
        print("⏳ Waiting 3 seconds...")
        sleep(3)
        
        # Press Enter again to confirm/send
        print("⏩ Pressing Enter again to send...")
        
        # Try multiple ways to press Enter
        try:
            # Method 1: Send Enter to body
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.RETURN)
        except:
            pass
            
        try:
            # Method 2: Find send button and click (fallback)
            send_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='send'] | //div[@data-testid='send-media']"))
            )
            send_btn.click()
        except:
            # Method 3: Action chains Enter key
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(driver)
            actions.send_keys(Keys.RETURN).perform()
        
        print("📸 Image sent!")
        sleep(3)  # Wait for image to actually send
        
    except Exception as e:
        print(f"❌ Error in image sending: {e}")
        raise

def send_text_message(driver, message):
    """Send text message after image"""
    try:
        print("💬 Typing message...")
        
        # Find message input box
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
        
        # Click and type
        input_box.click()
        sleep(1)
        pyperclip.copy(message)
        input_box.send_keys(Keys.CONTROL + "v")
        sleep(1)
        
        # Press Enter or click send
        print("📤 Sending message...")
        
        # Try clicking send button first
        try:
            send_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='send']"))
            )
            send_btn.click()
        except:
            # Fallback to Enter key
            input_box.send_keys(Keys.RETURN)
        
        print("✅ Message sent!")
        sleep(2)
        
    except Exception as e:
        print(f"❌ Error sending text: {e}")
        raise

def validate_number(number):
    """Clean and validate number"""
    number = number.strip().replace("+", "").replace(" ", "").replace("-", "")
    # Add country code if missing (assuming India +91)
    if not number.startswith("91") and len(number) == 10:
        number = "91" + number
    return number

def send_messages(driver, numbers, message, image_path=None):
    total = len(numbers)
    
    for idx, number in enumerate(numbers):
        number = validate_number(number)
        
        if not number:
            continue

        print(f'\n{"="*60}')
        print(f'📱 {idx+1}/{total} => Processing +{number}')
        print(f'{"="*60}')

        try:
            # 1. Click search button
            print("🔍 Clicking new chat/search button...")
            try:
                search_btn = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div/div[3]/div/div[3]/header/header/div/span/div/div[1]/span/div/button/div/div/div[1]/span'))
                )
                search_btn.click()
            except Exception as e:
                print("⚠️ Could not click search button")
            sleep(2)
            
            # 2. Fill number in search bar
            print("⌨️  Typing number in search bar...")
            search_bar = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div/div/div[3]/div/div[2]/div[1]/div/span/div/span/div/div[1]/div/div/div/div/div/div[2]/input'))
            )
            # Clear search bar just in case
            search_bar.send_keys(Keys.CONTROL + "a")
            search_bar.send_keys(Keys.DELETE)
            search_bar.send_keys(number)
            sleep(4)  # Wait for results to load
            
            # 3. Click the result
            print("👆 Clicking the contact result...")
            try:
                result = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div/div[3]/div/div[2]/div[1]/div/span/div/span/div/div[3]/div[2]/div[2]/div[2]/div[2]/div'))
                )
                result.click()
                print("✅ Chat loaded")
                sleep(2) # Wait for chat to open
            except Exception as e:
                print("❌ Contact not found or clickable")
                continue
            
            # 3. Send Text Message
            if message:
                send_text_message(driver, message)
            
            print(f'✅ Completed for +{number}')
            
            # Anti-ban delay between contacts
            wait_time = 12
            print(f"⏳ Waiting {wait_time}s before next contact...")
            sleep(wait_time)

        except Exception as e:
            print(f'❌ Failed for +{number}: {str(e)[:100]}')
            try:
                driver.save_screenshot(f"error_{number}.png")
                print("📸 Screenshot saved")
            except:
                pass
            continue

def get_driver():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("user-data-dir=C:/temp/chrome-profile")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver

def main():
    print("\n" + "="*60)
    print("WHATSAPP BULK SENDER - IMAGE THEN TEXT")
    print("="*60)
    
    # Check files
    if not os.path.exists("numbers.txt"):
        print("❌ numbers.txt not found!")
        return
    
    if not os.path.exists("message.txt"):
        print("❌ message.txt not found!")
        return
    
    if not os.path.exists(IMAGE_PATH):
        print(f"⚠️  Image not found at: {IMAGE_PATH}")
        send_image = False
    else:
        print(f"✅ Image found: {os.path.basename(IMAGE_PATH)}")
        send_image = True

    # Read files
    with open("numbers.txt", "r") as f:
        numbers = [line.strip() for line in f.readlines() if line.strip() and not line.startswith("#")]
    
    with open("message.txt", "r", encoding="utf8") as f:
        message = f.read().strip()

    print(f"\n📱 Numbers: {len(numbers)}")
    print(f"📝 Message: {message[:50]}..." if len(message) > 50 else f"📝 Message: {message}")
    print(f"🖼️  Image: {'Yes' if send_image else 'No'}")
    print("\n" + "-"*60)

    driver = get_driver()
    
    print("🔐 Opening WhatsApp Web...")
    driver.get('https://web.whatsapp.com')
    
    input("\n👉 Scan QR code and press ENTER when ready...")

    send_messages(driver, numbers, message, IMAGE_PATH if send_image else None)

    driver.quit()
    print("\n" + "="*60)
    print("✅ ALL MESSAGES SENT!")
    print("="*60)


if __name__ == "__main__":
    main()