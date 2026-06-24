#!/usr/bin/env python3
"""
WhatsApp Bulk Sender — Advanced Anti-Detection Edition
Authorized penetration testing use only.
"""

import os
import sys
import random
import time
import json

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver

import undetected_chromedriver as uc
import pyperclip

from complete_stealth import apply_complete_stealth, get_random_profile

from utils import (
    random_delay,
    smart_wait,
    simulate_mouse_movement,
    get_fingerprint_options,
    apply_stealth,
    apply_network_conditions,
    parse_spintax,
    type_like_human,
    anti_detection_delay,
    should_rotate_session,
    get_proxy,
    maybe_perform_distraction,
    maybe_click_wrong_contact,
    maybe_simulate_typo_in_message,
    MIN_BATCH_PER_SESSION,
    MAX_BATCH_PER_SESSION,
    MIN_SESSION_COOLDOWN,
    MAX_SESSION_COOLDOWN,
)

# =============================================================================
# OVERLAY / DIALOG DISMISSAL
# =============================================================================

def dismiss_overlays(driver):
    """Wait for and dismiss any blocking overlays."""
    overlay_selectors = [
        "div.x1n2onr6.xupqr0c",           # The specific overlay from the error
        "div[data-testid='drawer-overlay']",
        "div[role='dialog']",              # Generic dialog overlay
        "div[aria-modal='true']",
    ]
    for sel in overlay_selectors:
        try:
            overlay = driver.find_element(By.CSS_SELECTOR, sel)
            if overlay.is_displayed():
                print(f"[*] Dismissing overlay: {sel}")
                ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                random_delay(0.5, 1.0)
        except Exception:
            pass
    # Wait for any animated overlays to settle
    smart_wait(driver, 1.0, 2.0)


def wait_for_chat_to_load(driver, timeout=15):
    """
    After clicking a contact, wait for the chat view to fully render.
    This waits for both the overlay to disappear AND the message input to appear.
    """
    print("[*] Waiting for chat view to fully load...")

    # Step 1: Wait for blocking overlay to disappear
    try:
        WebDriverWait(driver, timeout).until_not(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.x1n2onr6.xupqr0c"))
        )
    except Exception:
        pass

    random_delay(1.0, 2.0)

    # Step 2: Press Escape once more to dismiss any lingering dialog
    try:
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        random_delay(0.5, 1.0)
    except Exception:
        pass

    # Step 3: Wait for ANY of these indicators that the chat is loaded
    chat_loaded_selectors = [
        "div[data-testid='conversation-compose-box-input']",
        "div[contenteditable='true'][data-tab='1']",
        "div[data-testid='conversation-info-header']",
        "header[data-testid='conversation-header']",
        "div[data-testid='conversation-panel-messages']",
    ]

    for sel in chat_loaded_selectors:
        try:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, sel))
            )
            print(f"[+] Chat loaded — detected by: {sel}")
            return True
        except Exception:
            continue

    # Step 4: If still not loaded, try clicking the result one more time
    print("[*] Chat not fully loaded yet, attempting re-click...")
    return False


# =============================================================================
# NAVIGATION HELPERS
# =============================================================================

def click_back_button(driver):
    """Return to the main chat list from any open chat."""
    selectors = [
        "[data-testid='back-refreshed']",
        "[data-icon='back-refreshed']",
        "[aria-label='Back']",
        "button[aria-label='Back']",
    ]
    for sel in selectors:
        try:
            btn = WebDriverWait(driver, 4).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, sel))
            )
            try:
                btn.click()
            except Exception:
                driver.execute_script("arguments[0].click();", btn)
            random_delay(1.0, 2.0)
            return True
        except Exception:
            continue
    # XPath fallback
    try:
        btn = driver.find_element(By.XPATH,
            "//header//div[@role='button']"
        )
        try:
            btn.click()
        except Exception:
            driver.execute_script("arguments[0].click();", btn)
        random_delay(1.0, 2.0)
        return True
    except Exception:
        pass
    return False


def click_new_chat(driver):
    """Click the 'New chat' / search button."""
    print("[*] Clicking 'New Chat' / search button...")
    # Dismiss overlays first
    dismiss_overlays(driver)

    selectors = (
        "button[data-testid='new-chat'], "
        "div[data-testid='new-chat'], "
        "span[data-icon='new-chat'], "
        "span[data-icon='new-chat-outline'], "
        "span[data-icon='chat'], "
        "div[aria-label='New chat'], "
        "[title='New chat']"
    )
    btn = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, selectors))
    )
    ActionChains(driver).move_to_element(btn).perform()
    random_delay(0.2, 0.6)
    try:
        btn.click()
    except Exception:
        driver.execute_script("arguments[0].click();", btn)
    random_delay(1.5, 3.5)


def search_contact(driver, number):
    """Type the phone number into the search bar."""
    print(f"[*] Search input located, typing contact number: {number}...")
    selectors = (
        "input[aria-label='Search name or number'], "
        "input[placeholder='Search name or number'], "
        "input[aria-label='Search or start a new chat'], "
        "div[contenteditable='true'][data-tab='3'], "
        "div.lexical-rich-text-input div[contenteditable='true']"
    )
    search_bar = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, selectors))
    )
    # Focus + clear
    try:
        search_bar.click()
    except Exception:
        driver.execute_script("arguments[0].click();", search_bar)
    random_delay(0.2, 0.5)
    search_bar.send_keys(Keys.CONTROL + "a")
    random_delay(0.1, 0.3)
    search_bar.send_keys(Keys.DELETE)
    random_delay(0.3, 0.7)

    # Type the number with human-like pauses
    for i, ch in enumerate(number):
        search_bar.send_keys(ch)
        # Pause longer at the 3rd and 7th digit (simulates reading the number)
        if i in (2, 6):
            time.sleep(random.uniform(0.3, 0.8))
        else:
            time.sleep(random.uniform(0.06, 0.18))

    print(f"[*] Number {number} typed. Waiting for search results to load...")
    # Wait for results to load
    smart_wait(driver, 3.0, 6.0)


def click_first_contact_result(driver):
    """Click the top contact search result with robust overlay handling."""
    # First dismiss any overlays that might be blocking
    dismiss_overlays(driver)

    # Wait for result to be present
    selectors = (
        "div[data-testid^='list-item-'], "
        "div[data-testid='cell-frame-container'], "
        "div[role='listitem']"
    )
    result = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, selectors))
    )

    # Scroll the result into view within the scrollable panel
    try:
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', behavior: 'instant'});",
            result
        )
        random_delay(0.3, 0.7)
    except Exception:
        pass

    # Check if anything is still overlaying the target
    try:
        overlay_check = driver.find_element(By.CSS_SELECTOR, "div.x1n2onr6.xupqr0c")
        if overlay_check.is_displayed():
            print("[*] Overlay still present after scroll, pressing Escape...")
            ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            random_delay(0.5, 1.0)
    except Exception:
        pass

    # Multiple click strategies
    strategies = [
        ("ActionChains move + click", lambda: ActionChains(driver)
            .move_to_element(result)
            .pause(random.uniform(0.1, 0.3))
            .click()
            .perform()),
        ("Direct click", lambda: result.click()),
        ("JS click", lambda: driver.execute_script("arguments[0].click();", result)),
        ("JS mouse event dispatch", lambda: driver.execute_script("""
            var el = arguments[0];
            var rect = el.getBoundingClientRect();
            var event = new MouseEvent('click', {
                bubbles: true,
                cancelable: true,
                clientX: rect.left + rect.width/2,
                clientY: rect.top + rect.height/2
            });
            el.dispatchEvent(event);
        """, result)),
    ]

    last_exception = None
    for name, click_fn in strategies:
        try:
            click_fn()
            print(f"[+] Click successful via: {name}")
            random_delay(1.0, 2.0)

            # Wait for chat to fully load
            if wait_for_chat_to_load(driver):
                print("[+] Chat opened and ready")
                return

            # If chat didn't load, try next strategy
            print("[*] Chat not ready after this strategy, trying next...")
            continue

        except Exception as e:
            last_exception = e
            print(f"[-] {name} failed: {e}")
            random_delay(0.5, 1.0)
            continue

    if last_exception:
        raise last_exception


def find_message_input(driver):
    """Locate the message compose box with retry logic."""
    # First try to dismiss anything blocking the view
    dismiss_overlays(driver)

    max_attempts = 3
    for attempt in range(max_attempts):
        xpaths = [
            "//div[@data-testid='conversation-compose-box-input']",
            "//div[@contenteditable='true' and @data-tab='1']",
            "//div[contains(@class, 'copyable-text') and @contenteditable='true']",
            "//div[contains(@class, 'lexical-rich-text-input')]//div[@contenteditable='true']",
            "//footer//div[@contenteditable='true']"
        ]
        for xp in xpaths:
            try:
                el = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, xp))
                )
                return el
            except Exception:
                continue

        print(f"[*] Attempt {attempt+1}/{max_attempts}: input not found, retrying...")

        # Wait for chat to load properly
        wait_for_chat_to_load(driver, timeout=5)

        try:
            ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        except Exception:
            pass
        random_delay(1.0, 2.0)

    raise Exception("Could not locate message input box after multiple attempts")


def send_message(driver, message):
    """
    Type and send the message using one of several methods,
    chosen randomly to avoid behavioural fingerprinting.
    """
    print("[*] Locating message input area...")
    input_box = find_message_input(driver)
    try:
        input_box.click()
    except Exception:
        driver.execute_script("arguments[0].click();", input_box)
    random_delay(0.3, 0.8)

    # Choose a sending method
    method_weights = {
        'type':   0.50,   # character-by-character with typos
        'paste':  0.25,   # clipboard paste
        'typo':   0.15,   # deliberate typo + correction
        'split':  0.10,   # type first line, paste second line
    }
    methods = list(method_weights.keys())
    weights = list(method_weights.values())
    method = random.choices(methods, weights=weights, k=1)[0]
    print(f"[*] Chosen delivery style: {method}")

    if method == 'paste':
        # --- Paste via clipboard ---
        print("[*] 📋 Sending via paste...")
        pyperclip.copy(message)
        random_delay(0.5, 1.5)
        mod = Keys.COMMAND if sys.platform == "darwin" else Keys.CONTROL
        input_box.send_keys(mod + 'v')
        random_delay(0.3, 0.8)

    elif method == 'typo':
        # --- Simulate typo then complete ---
        print("[*] ⌨️ Sending with simulated typo...")
        maybe_simulate_typo_in_message(driver, input_box, message)

    elif method == 'split':
        # --- Type first line manually, paste the rest ---
        print("[*] ✂️ Split send...")
        lines = message.split('\n', 1)
        first = lines[0]
        rest = lines[1] if len(lines) > 1 else ""
        # Type first line
        for ch in first:
            input_box.send_keys(ch)
            time.sleep(random.uniform(0.06, 0.18))
        random_delay(0.3, 0.8)
        if rest:
            input_box.send_keys(Keys.SHIFT + Keys.RETURN)
            random_delay(0.2, 0.5)
            pyperclip.copy(rest)
            mod = Keys.COMMAND if sys.platform == "darwin" else Keys.CONTROL
            input_box.send_keys(mod + 'v')
            random_delay(0.3, 0.8)

    else:
        # --- Default: character-by-character ---
        print("[*] ⌨️ Sending character-by-character...")
        type_like_human(input_box, message)

    # --- Press Send ---
    print("[*] Sending message...")
    try:
        send_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH,
                "//button[@data-testid='send'] | "
                "//span[@data-icon='send']/.. | "
                "//button[@aria-label='Send']"
            ))
        )
        ActionChains(driver).move_to_element(send_btn).pause(0.1).perform()
        random_delay(0.1, 0.4)
        send_btn.click()
    except Exception:
        # Fallback: press Enter
        input_box.send_keys(Keys.RETURN)

    print("[+] ✅ Message sent")
    random_delay(2.0, 5.0)


# =============================================================================
# FILE MANAGEMENT
# =============================================================================

def validate_number(number):
    """Strip formatting from a phone number."""
    return number.strip().replace("+", "").replace(" ", "").replace("-", "")


def move_number_to_delivered(number):
    """Move a processed number from numbers.txt to delivered.txt."""
    try:
        with open("delivered.txt", "a", encoding="utf-8") as f:
            f.write(number + "\n")
        if os.path.exists("numbers.txt"):
            with open("numbers.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
            with open("numbers.txt", "w", encoding="utf-8") as f:
                for line in lines:
                    cleaned = validate_number(line)
                    if cleaned and cleaned != number:
                        f.write(line)
    except Exception as e:
        print(f"⚠️ File update error: {e}")


# =============================================================================
# SESSION & DRIVER MANAGEMENT
# =============================================================================

def get_driver(session_num=1):
    """
    Create a fresh undetected Chrome driver with full stealth configuration.
    Uses persistent profiles (one per session) to maintain login state.
    """
    options = get_fingerprint_options()

    # Proxy (optional)
    proxy = get_proxy()
    if proxy:
        options.add_argument(f"--proxy-server={proxy}")
        print(f"🌐 Proxy: {proxy}")

    # Persistent user-data directory (rotated per session)
    profile_base = os.path.join(os.path.dirname(__file__), "profiles")
    os.makedirs(profile_base, exist_ok=True)
    profile_dir = os.path.join(profile_base, f"profile_{session_num}")
    os.makedirs(profile_dir, exist_ok=True)
    options.add_argument(f"--user-data-dir={profile_dir}")

    # Launch driver
    driver = uc.Chrome(options=options, version_main=150)

    # Apply COMPLETE stealth from one consistent profile
    profile_data = apply_complete_stealth(driver)
    print(f"[*] Using fingerprint profile: {profile_data['name']}")

    # Network conditions
    apply_network_conditions(driver)
    driver.implicitly_wait(10)

    return driver, profile_dir


# =============================================================================
# CORE LOGIC — PROCESS A SINGLE NUMBER
# =============================================================================

def process_number(driver, number, message, idx, total, sent_in_batch):
    """
    Execute the full flow for one recipient:
        1. Optional distraction
        2. Optional wrong-click
        3. Search for contact
        4. Click result
        5. Send message
    """
    print(f'\n{"="*55}')
    print(f'[{idx+1}/{total}] → {number}')
    print(f'{"="*55}')

    # --- Step 0: Pre-action distraction (random) ---
    maybe_perform_distraction(driver)

    # --- Step 1: Click new chat / search ---
    click_new_chat(driver)

    # --- Step 2: Type number ---
    search_contact(driver, number)

    # --- Step 3: Optional wrong-click diversion ---
    if maybe_click_wrong_contact(driver, number):
        print("[*] Re-searching contact after wrong click diversion...")
        click_new_chat(driver)
        search_contact(driver, number)

    # --- Step 4: Click the correct result ---
    try:
        click_first_contact_result(driver)
    except Exception as e:
        print(f"⚠️  Contact not found or click failed: {e}")
        click_back_button(driver)
        return False  # failure

    # --- Step 5: Parse spintax and send ---
    final_msg = parse_spintax(message)
    try:
        send_message(driver, final_msg)
    except Exception as e:
        print(f"⚠️  Send failed: {e}")
        click_back_button(driver)
        return False

    return True  # success


# =============================================================================
# BATCH PROCESSOR
# =============================================================================

def process_batch(driver, numbers, message, start_idx):
    """Process a batch of numbers in one browser session."""
    total = len(numbers)
    sent = 0
    failures = 0

    for offset, number in enumerate(numbers):
        number = validate_number(number)
        if not number:
            continue

        idx = start_idx + offset
        success = process_number(driver, number, message, idx, total, sent)

        if success:
            sent += 1
            failures = 0
        else:
            failures += 1

        move_number_to_delivered(number)

        # Cooldown between messages (unless it's the last one)
        if offset < total - 1:
            anti_detection_delay(driver, start_idx + sent, sent)

        # Abort if too many consecutive failures
        if failures >= 5:
            print("[!] Too many consecutive failures. Ending session.")
            break

    return sent


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    print("\n" + "="*55)
    print("  WHATSAPP BULK SENDER — STEALTH MODE")
    print("  Authorized pentesting use only")
    print("="*55)

    # --- Validate input files ---
    if not os.path.exists("numbers.txt"):
        print("❌ numbers.txt not found!")
        sys.exit(1)
    if not os.path.exists("message.txt"):
        print("❌ message.txt not found!")
        sys.exit(1)

    # --- Read numbers ---
    with open("numbers.txt", "r", encoding="utf-8") as f:
        raw = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    numbers = [validate_number(n) for n in raw if validate_number(n)]

    # --- Read message ---
    with open("message.txt", "r", encoding="utf-8") as f:
        message = f.read().strip()

    if not numbers:
        print("❌ No valid numbers found.")
        sys.exit(1)

    print(f"\n📱 Numbers loaded : {len(numbers)}")
    print(f"💬 Message preview: {message[:60]}..." if len(message) > 60
          else f"💬 Message: {message}")
    print(f"📦 Batch per session: {MIN_BATCH_PER_SESSION}–{MAX_BATCH_PER_SESSION}")
    print(f"⏱  Between messages: 45s–5m")
    print(f"🔁 Between sessions:  {MIN_SESSION_COOLDOWN//60}–{MAX_SESSION_COOLDOWN//60} min")
    print("-" * 55)

    # --- Main loop: sessions ---
    total_sent = 0
    session_num = 1
    remaining = numbers[:]   # copy

    while remaining:
        batch_size = random.randint(MIN_BATCH_PER_SESSION, MAX_BATCH_PER_SESSION)
        batch = remaining[:batch_size]
        remaining = remaining[batch_size:]

        print(f"\n{'#'*55}")
        print(f"  SESSION #{session_num} — {len(batch)} contacts")
        print(f"{'#'*55}")

        # Get a fresh browser
        driver, profile = get_driver(session_num)
        print(f"📁 Profile: {profile}")

        driver.get("https://web.whatsapp.com")

        # Check if already logged in
        logged_in = False
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR,
                    "[data-testid='chat-list'], [aria-label='Chat list']"
                ))
            )
            print("[+] Session restored from persistent profile")
            logged_in = True
        except Exception:
            pass

        if not logged_in:
            input("🔐 Scan QR code, then press ENTER when chats are visible...")

        # Wait for WhatsApp Web interface to finish loading/syncing
        print("[*] Waiting for WhatsApp Web interface to fully stabilize...")
        try:
            WebDriverWait(driver, 30).until_not(
                EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'spinner') or contains(@class, 'loading') or @role='progressbar']"))
            )
        except Exception:
            pass
        # Dismiss any initial overlays
        dismiss_overlays(driver)
        # Short random delay for rendering stabilization
        random_delay(3.0, 5.0)

        # Process the batch
        sent_this_session = process_batch(driver, batch, message, total_sent)
        total_sent += sent_this_session

        print(f"\n[+] Session #{session_num}: {sent_this_session}/{len(batch)} sent")

        driver.quit()
        session_num += 1

        # --- Between-session cooldown ---
        if remaining:
            cooldown = random.randint(MIN_SESSION_COOLDOWN, MAX_SESSION_COOLDOWN)
            print(f"\n⏳ Cooldown: {cooldown//60} min {cooldown%60}s  (sent {total_sent}/{len(numbers)} total)")
            print(f"   Remaining: {len(remaining)} contacts")
            # Sleep in chunks so we could interrupt with Ctrl+C
            end = time.time() + cooldown
            while time.time() < end:
                time.sleep(min(30, end - time.time()))

    # --- Final report ---
    print("\n" + "="*55)
    print(f"  ✅ COMPLETE — {total_sent}/{len(numbers)} messages sent")
    print(f"     across {session_num - 1} sessions")
    print("="*55)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user.")
        sys.exit(0)