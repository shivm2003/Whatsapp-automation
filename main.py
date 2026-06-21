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
import random
import time
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc
from utils import (
    random_delay, 
    type_like_human_advanced, 
    simulate_mouse_movement, 
    apply_advanced_stealth_cdp,
    parse_spintax,
    get_fingerprint_options,
    anti_detection_delay,
    should_rotate_session,
    apply_network_conditions,
    apply_canvas_stealth,
    apply_audio_stealth,
    apply_font_stealth,
    apply_visibility_stealth,
    apply_media_stealth,
    apply_webrtc_stealth,
    get_proxy
)

DELAY = 30
IMAGE_PATH = r"C:\Users\shivam\Downloads\whatsapp-bulk-messenger-primary\whatsapp-bulk-messenger-primary\image_converted.jpg"

def send_image_stealth(driver, image_path):
    """Send image - most reliable method, avoids menu navigation"""
    try:
        # Method 1: Direct file input injection (most reliable)
        print("📎 Finding file input element...")
        
        # The file input is always present, just hidden
        file_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
        )
        
        # Scroll to it first (safest)
        driver.execute_script("arguments[0].scrollIntoView(true);", file_input)
        random_delay(0.5, 1.0)
        
        # Send the file path
        abs_path = os.path.abspath(image_path)
        file_input.send_keys(abs_path)
        
        # Wait for preview to load
        print("⏳ Waiting for image preview...")
        random_delay(4.0, 6.0)
        
        # Click send
        print("📤 Sending image...")
        send_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='send'], [data-testid='send-media']"))
        )
        
        actions = ActionChains(driver)
        actions.move_to_element(send_btn).pause(random.uniform(0.4, 1.0)).click().perform()
        
        print("✅ Image sent")
        random_delay(5.0, 8.0)
        
    except Exception as e:
        print(f"⚠️ Method 1 failed ({e}), trying method 2...")
        
        try:
            # Method 2: Click clip button then use file input
            clip = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='clip'], [data-icon='clip']"))
            )
            clip.click()
            random_delay(1.5, 3.0)
            
            # Now find file input (it becomes active)
            file_input = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
            )
            file_input.send_keys(os.path.abspath(image_path))
            random_delay(4.0, 6.0)
            
            send_btn = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='send']"))
            )
            actions = ActionChains(driver)
            actions.move_to_element(send_btn).pause(random.uniform(0.4, 1.0)).click().perform()
            print("✅ Image sent (method 2)")
            random_delay(5.0, 8.0)
        except Exception as e2:
            print(f"❌ All image methods failed: {e2}")
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
            "//div[contains(@class, 'lexical-rich-text-input')]//div[@contenteditable='true']",
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
        
        # Type message like human with typos
        type_like_human_advanced(input_box, message)
        random_delay(0.5, 1.2)
        
        # Press Enter or click send
        print("📤 Sending message...")
        
        # Try clicking send button first
        try:
            send_btn_xpath = "//button[@data-testid='send'] | //span[@data-icon='send']/.. | //button[@aria-label='Send']"
            send_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, send_btn_xpath))
            )
            # Hover/move to button briefly before clicking
            try:
                from selenium.webdriver.common.action_chains import ActionChains
                ActionChains(driver).move_to_element(send_btn).perform()
                random_delay(0.1, 0.4)
            except:
                pass
            send_btn.click()
        except:
            # Fallback to Enter key
            input_box.send_keys(Keys.RETURN)
        
        print("✅ Message sent!")
        random_delay(1.5, 3.0)
        
    except Exception as e:
        print(f"❌ Error sending text: {e}")
        raise

def validate_number(number):
    """Clean and validate number"""
    number = number.strip().replace("+", "").replace(" ", "").replace("-", "")
    return number

def move_number_to_delivered(number):
    """Move processed number from numbers.txt to delivered.txt"""
    try:
        with open("delivered.txt", "a", encoding="utf-8") as f:
            f.write(number + "\n")
            
        if os.path.exists("numbers.txt"):
            with open("numbers.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            with open("numbers.txt", "w", encoding="utf-8") as f:
                for line in lines:
                    if line.strip() and not line.startswith("#"):
                        cleaned_line = validate_number(line)
                        if cleaned_line == number:
                            continue  # Skip this number to remove it
                    f.write(line)
    except Exception as e:
        print(f"⚠️ Error updating numbers/delivered files: {e}")

def random_human_behavior(driver):
    """Occasionally click around like a real user"""
    if random.random() > 0.1:  # 10% chance
        return
    
    print("👀 Simulating human behavior: Checking around...")
    try:
        actions = ActionChains(driver)
        
        # Scroll down slowly
        body = driver.find_element(By.TAG_NAME, "body")
        actions.move_to_element(body).perform()
        
        # Random scroll
        driver.execute_script(f"window.scrollBy(0, {random.randint(50, 200)});")
        random_delay(0.5, 1.0)
        
        # Click somewhere safe (like a chat header)
        elements_to_click = driver.find_elements(
            By.CSS_SELECTOR, 
            "[data-testid='conversation-header'], [data-testid='chat-list-search']"
        )
        if elements_to_click and random.random() < 0.3:
            target = random.choice(elements_to_click)
            actions.move_to_element(target).pause(0.3).click().perform()
            random_delay(1.0, 2.0)
            
    except:
        pass

def send_messages(driver, numbers, base_message, image_path=None):
    total = len(numbers)
    
    # Initialize batch settings
    batch_limit = random.randint(10, 15)
    sent_in_batch = 0
    failures = 0
    
    for idx, number in enumerate(numbers):
        number = validate_number(number)
        
        if not number:
            continue

        print(f'\n{"="*60}')
        print(f'📱 {idx+1}/{total} => Processing {number}')
        print(f'{"="*60}')

        try:
            # Random human behavior
            random_human_behavior(driver)

            # Simulate random mouse movement/wiggles before starting contact search
            simulate_mouse_movement(driver)
            random_delay(1.0, 2.5)

            # 1. Click search button
            print("🔍 Clicking new chat/search button...")
            search_selectors = (
                "button[data-testid='new-chat'], "
                "div[data-testid='new-chat'], "
                "span[data-icon='new-chat'], "
                "span[data-icon='new-chat-outline'], "
                "span[data-icon='chat'], "
                "div[aria-label='New chat'], "
                "[title='New chat']"
            )
            
            try:
                search_btn = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, search_selectors))
                )
            except:
                # If still fails, try to find it via presence instead of clickability
                search_btn = driver.find_element(By.CSS_SELECTOR, search_selectors)
                
            ActionChains(driver).move_to_element(search_btn).perform()
            random_delay(0.2, 0.6)
            try:
                search_btn.click()
            except:
                driver.execute_script("arguments[0].click();", search_btn)
            random_delay(1.5, 3.0)
            
            # 2. Fill number in search bar
            print("⌨️  Typing number in search bar...")
            search_bar_selectors = (
                "input[aria-label='Search name or number'], "
                "input[placeholder='Search name or number'], "
                "input[aria-label='Search or start a new chat'], "
                "div[contenteditable='true'][data-tab='3'], "
                "div[data-testid='chat-list-search'], "
                "div[contenteditable='true'][aria-label='Search name or number'], "
                "div[contenteditable='true'][data-lexical-editor='true'], "
                "div.lexical-rich-text-input div[contenteditable='true']"
            )
            search_bar = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, search_bar_selectors))
            )
            # Clear search bar just in case
            search_bar.click()
            random_delay(0.2, 0.5)
            search_bar.send_keys(Keys.CONTROL + "a")
            random_delay(0.1, 0.3)
            search_bar.send_keys(Keys.DELETE)
            random_delay(0.3, 0.7)
            # Type phone number character by character
            for char in number:
                search_bar.send_keys(char)
                random_delay(0.05, 0.18)
            random_delay(3.5, 5.5)  # Wait for results to load
            
            # 3. Click the result
            print("👆 Clicking the contact result...")
            try:
                result_selectors = (
                    "div[data-testid^='list-item-'], "
                    "div[data-testid='cell-frame-container'], "
                    "div[role='listitem']"
                )
                result = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, result_selectors))
                )
                ActionChains(driver).move_to_element(result).perform()
                random_delay(0.2, 0.5)
                result.click()
                print("✅ Chat loaded")
                random_delay(1.5, 3.0) # Wait for chat to open
            except Exception as e:
                print("❌ Contact not found or clickable")
                continue
            
            # Send Image (if specified) and/or Text Message
            if image_path:
                send_image_stealth(driver, image_path)
            
            # Prepare dynamic message
            message = parse_spintax(base_message) if base_message else None
            
            if message:
                send_text_message(driver, message)
            
            print(f'✅ Completed for {number}')
            sent_in_batch += 1
            failures = 0 # Reset failures on success
            
            move_number_to_delivered(number)
            
            # Anti-ban delay & batch cooldown between contacts
            if idx < total - 1:  # Only sleep if we have more contacts to process
                anti_detection_delay(driver, idx + 1, sent_in_batch)

        except Exception as e:
            print(f'❌ Failed for {number}: {str(e)[:100]}')
            try:
                driver.save_screenshot(f"error_{number}.png")
                with open(f"error_{number}.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                print("📸 Screenshot and HTML saved")
            except:
                pass
            failures += 1
            
            move_number_to_delivered(number)
            
            if failures >= 3:
                print("⚠️ Too many failures in a row, aborting batch to rotate session.")
                return idx + 1 # Return number of contacts processed
            continue
            
    return total

def get_driver_with_rotation(session_num=1):
    """Get a fresh driver, optionally rotating profile"""
    options = get_fingerprint_options()
    
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    
    # Proxy configuration (Optional)
    proxy = get_proxy()
    if proxy:
        options.add_argument(f'--proxy-server={proxy}')
        print(f"🌐 Using proxy: {proxy}")
    
    # Use persistent profile directory with rotation
    profile_base = os.path.join(os.path.dirname(__file__), "profiles")
    os.makedirs(profile_base, exist_ok=True)
    profile_dir = os.path.join(profile_base, f"profile_{session_num}")
    os.makedirs(profile_dir, exist_ok=True)
    options.add_argument(f"--user-data-dir={profile_dir}")
    
    driver = uc.Chrome(options=options)
    
    # Apply ALL stealth patches
    apply_advanced_stealth_cdp(driver)
    apply_canvas_stealth(driver)
    apply_audio_stealth(driver)
    apply_font_stealth(driver)
    apply_visibility_stealth(driver)
    apply_media_stealth(driver)
    apply_webrtc_stealth(driver)
    apply_network_conditions(driver)
    
    driver.implicitly_wait(10)
    return driver, profile_dir

def main():
    print("\n" + "="*60)
    print("WHATSAPP BULK SENDER - ADVANCED STEALTH")
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

    total_sent = 0
    session_num = 1
    
    while total_sent < len(numbers):
        driver, profile = get_driver_with_rotation(session_num)
        print(f"\n🔄 Starting session #{session_num} with profile: {profile}")
        
        driver.get('https://web.whatsapp.com')
        
        # Check if already logged in by looking for chat list
        logged_in = False
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='chat-list'], [aria-label='Chat list']"))
            )
            print("✅ Session restored from persistent profile")
            logged_in = True
        except:
            pass
            
        if not logged_in:
            input("🔐 Scan QR code and press ENTER when chats are visible...")
        
        # Process batch (rotate session every 80-120 numbers)
        batch_size = random.randint(80, 120)
        batch = numbers[total_sent:total_sent + batch_size]
        
        processed_count = send_messages(driver, batch, message, IMAGE_PATH if send_image else None)
        
        total_sent += processed_count
        print(f"✅ Session #{session_num} done: Processed up to {total_sent}/{len(numbers)} total")
        driver.quit()
        session_num += 1
    
    print("\n" + "="*60)
    print(f"✅ ALL {total_sent} MESSAGES SENT ACROSS {session_num - 1} SESSIONS!")
    print("="*60)


if __name__ == "__main__":
    main()