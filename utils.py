import time
import random
import sys
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import pyperclip

def random_delay(min_s=2.0, max_s=5.0):
    """Sleep for a random float duration between min_s and max_s."""
    delay = random.uniform(min_s, max_s)
    time.sleep(delay)
    return delay

def type_like_human(element, text):
    """
    Types text into a selenium element character by character with random delays.
    For longer text, copies to clipboard and pastes it to avoid excessive typing delays, 
    but still wiggles/delays to look human.
    """
    # Focus the element
    element.click()
    random_delay(0.5, 1.2)
    
    # If the text is short, type character-by-character
    if len(text) <= 120:
        print("⌨️  Typing message character-by-character...")
        for char in text:
            element.send_keys(char)
            # Normal keypress delay
            random_delay(0.04, 0.15)
            # Extra delay for punctuation/space to simulate natural cognitive load
            if char in ['.', ',', '!', '?', ';']:
                random_delay(0.3, 0.6)
            elif char == ' ':
                random_delay(0.1, 0.25)
    else:
        # For longer messages, copy & paste is safer to prevent long typing windows, 
        # but we add some preparation delay.
        print("📋 Pasting message with natural preparation delay...")
        pyperclip.copy(text)
        
        # Determine the modifier key (Ctrl for Windows/Linux, Command for macOS)
        modifier = Keys.COMMAND if sys.platform == "darwin" else Keys.CONTROL
        element.send_keys(modifier + "v")
        random_delay(0.8, 1.5)

def simulate_mouse_movement(driver):
    """Simulates realistic mouse movements/scrolling to mimic human presence."""
    try:
        actions = ActionChains(driver)
        
        # First, move to a safe element to establish baseline position
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            # Move to center of body to establish a starting position
            actions.move_to_element(body).perform()
        except:
            pass
        
        steps = random.randint(2, 4)
        print(f"🖱️  Simulating {steps} random mouse movements...")
        
        actions = ActionChains(driver)  # Reset actions
        for _ in range(steps):
            # Use small relative offsets from current position
            x_offset = random.randint(-50, 50)
            y_offset = random.randint(-40, 40)
            try:
                actions.move_by_offset(x_offset, y_offset)
                actions.perform()
            except:
                # If even small offset fails, just skip
                pass
            random_delay(0.2, 0.6)
    except Exception as e:
        print(f"⚠️  Mouse movement simulation skipped: {e}")

def configure_stealth_options(options):
    """Applies browser options to make Selenium less detectable."""
    # Hide automation controlled flag
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Prevent "Chrome is being controlled by automated software" banner
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    # Real-looking user agent to prevent default selenium UA detection
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Other recommendations to make Chrome look natural
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    
    return options

def apply_stealth_cdp(driver):
    """Applies CDP overrides to mask the navigator.webdriver property."""
    print("🕵️  Applying CDP overrides for driver stealth...")
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            window.chrome = {
                runtime: {}
            };
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
        """
    })
