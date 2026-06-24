import time
import random
import sys
import os
import json
import undetected_chromedriver as uc
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import pyperclip
import re

# =============================================================================
# CONFIGURATION — Tune these based on your threat model
# =============================================================================

# Absolute minimum and maximum idle between messages (in seconds)
MIN_IDLE_BETWEEN_MSGS = 45       # 45 seconds minimum
MAX_IDLE_BETWEEN_MSGS = 300      # 5 minutes maximum

# Per-session message limits (very low to avoid pattern detection)
MIN_BATCH_PER_SESSION = 40
MAX_BATCH_PER_SESSION = 50

# Between-session cooldown (in seconds)
MIN_SESSION_COOLDOWN = 3600      # 1 hour
MAX_SESSION_COOLDOWN = 9800     # 2.7 hours

# Chance of performing a "distraction" action between messages (0.0 – 1.0)
DISTRACTION_PROBABILITY = 0.18   # ~18%

# Chance of clicking a wrong contact before the correct one
WRONG_CLICK_PROBABILITY = 0.12   # ~12%

# Chance of making a typing mistake and correcting it
TYPO_PROBABILITY_PER_MSG = 0.15  # ~15% of messages have a typo

# Typing speed ranges (seconds per character)
TYPING_SPEED_MIN = 0.08
TYPING_SPEED_MAX = 0.35

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def random_delay(min_s=2.0, max_s=5.0):
    """Sleep for a random duration between min_s and max_s (float seconds)."""
    delay = random.uniform(min_s, max_s)
    time.sleep(delay)
    return delay


def smart_wait(driver, min_s, max_s):
    """Wait while performing occasional human-like micro-actions."""
    end_time = time.time() + random.uniform(min_s, max_s)
    last_action = 0.0

    while time.time() < end_time:
        remaining = end_time - time.time()
        if remaining <= 0:
            break
        # Sleep in small chunks so we can re-evaluate
        chunk = min(2.0, remaining)
        time.sleep(chunk)

        # Every 5–12 seconds, do something human-like
        if time.time() - last_action > random.uniform(5.0, 12.0):
            action = random.choice([
                lambda: _safe_scroll(driver),
                lambda: _safe_mouse_wiggle(driver),
                lambda: None   # sometimes do nothing
            ])
            try:
                action()
            except Exception:
                pass
            last_action = time.time()


def _safe_scroll(driver):
    """Small random scroll up or down."""
    delta = random.randint(-150, 150)
    driver.execute_script(f"window.scrollBy(0, {delta});")


def _safe_mouse_wiggle(driver):
    """Slight mouse movement to a random element."""
    try:
        elements = driver.find_elements(By.CSS_SELECTOR,
            "[data-testid='conversation-header'], "
            "[data-testid='chat-list-search'], "
            "header, footer, div[role='button']"
        )
        if elements:
            target = random.choice(elements)
            ActionChains(driver).move_to_element(target).perform()
    except Exception:
        pass


def simulate_mouse_movement(driver):
    """Simulate a series of realistic mouse wiggles."""
    try:
        actions = ActionChains(driver)
        steps = random.randint(3, 6)
        for _ in range(steps):
            actions.move_by_offset(
                random.randint(-60, 60),
                random.randint(-50, 50)
            )
        actions.perform()
        random_delay(0.15, 0.45)
    except Exception:
        pass


def parse_spintax(text):
    """Parse {option1|option2|...} spintax and return a random variation."""
    pattern = re.compile(r'\{([^{}]*)\}')
    match = pattern.search(text)
    while match:
        options = match.group(1).split('|')
        choice = random.choice(options)
        text = text[:match.start()] + choice + text[match.end():]
        match = pattern.search(text)
    return text


# =============================================================================
# FINGERPRINTING & STEALTH
# =============================================================================

def get_fingerprint_options():
    """Return uc.ChromeOptions with randomized, realistic fingerprints."""
    options = uc.ChromeOptions()

    # --- Window size (common real-world resolutions) ---
    resolutions = [
        (1920, 1080), (1366, 768), (1536, 864),
        (1280, 720), (1440, 900), (1600, 900), (1920, 1200)
    ]
    w, h = random.choice(resolutions)
    options.add_argument(f"--window-size={w},{h}")

    # --- Timezone (weighted toward realistic geographies) ---
    timezones = [
        "Asia/Kolkata", "Asia/Kolkata", "Asia/Kolkata",
        "Asia/Dubai",      "Asia/Singapore",
        "America/New_York","Europe/London", "Asia/Bangkok"
    ]
    options.add_argument(f"--timezone={random.choice(timezones)}")

    # --- Spoofed User-Agent (rotating Chrome versions, real platform strings) ---
    chrome_ver = random.choice(["120","121","122","123","124","125","126","127"])
    platforms = [
        "Windows NT 10.0; Win64; x64",
        "Windows NT 10.0; Win64; x64",
        "Macintosh; Intel Mac OS X 10_15_7",
        "X11; Linux x86_64"
    ]
    plat = random.choice(platforms)
    ua = (f"Mozilla/5.0 ({plat}) AppleWebKit/537.36 "
          f"(KHTML, like Gecko) Chrome/{chrome_ver}.0.0.0 Safari/537.36")
    options.add_argument(f"user-agent={ua}")

    # --- Locale (randomize accept-language) ---
    locales = ["en-US,en;q=0.9", "en-IN,en;q=0.9,hi;q=0.8",
               "en-GB,en;q=0.9", "en-US,en;q=0.8,es;q=0.7"]
    options.add_experimental_option("prefs", {
        "intl.accept_languages": random.choice(locales)
    })

    # --- Disable automation flags ---
    options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # options.add_experimental_option("useAutomationExtension", False)

    # --- Performance & sandbox (safe for headless or headed) ---
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-infobars")

    return options


def apply_stealth(driver):
    """
    Apply a single, minimal, robust CDP stealth script.
    Avoids heavy prototype-patching that can itself be detected.
    """
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        // 1) Hide webdriver
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });

        // 2) Chrome runtime
        if (!window.chrome) { window.chrome = { runtime: {} }; }

        // 3) Override permissions query to never reveal automation
        const origPermQuery = navigator.permissions.query;
        navigator.permissions.query = (params) => (
            params.name === 'notifications'
                ? Promise.resolve({ state: 'prompt' })
                : origPermQuery(params)
        );

        // 4) Languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en', 'hi']
        });

        // 5) Plugins list (realistic)
        Object.defineProperty(navigator, 'plugins', {
            get: () => {
                const p = [
                    { name: 'Chrome PDF Plugin',   filename: 'internal-pdf-viewer' },
                    { name: 'Chrome PDF Viewer',   filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
                    { name: 'Native Client',       filename: 'internal-nacl-plugin' }
                ];
                p.item = (i) => p[i];
                p.length = p.length;
                return p;
            }
        });

        // 6) Hardware concurrency & device memory
        Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
        Object.defineProperty(navigator, 'deviceMemory',       { get: () => 8 });

        // 7) Screen geometry normalisation
        Object.defineProperty(screen, 'availTop',  { get: () => 0 });
        Object.defineProperty(screen, 'availLeft', { get: () => 0 });
        """
    })


def apply_network_conditions(driver):
    """Emulate realistic network latency + throughput with jitter."""
    base_latency = random.gauss(60, 30)   # mean 60ms, stddev 30ms
    base_latency = max(15, min(250, base_latency))

    # Occasionally simulate a slow connection
    if random.random() < 0.08:   # 8% chance
        dl = random.randint(300, 800) * 1024       # 300–800 Kbps
        ul = random.randint(100, 300) * 1024       # 100–300 Kbps
        lat = random.randint(200, 600)
    else:
        dl = random.randint(5 * 1024 * 1024, 80 * 1024 * 1024)   # 5–80 Mbps
        ul = random.randint(1 * 1024 * 1024, 20 * 1024 * 1024)   # 1–20 Mbps
        lat = base_latency

    driver.execute_cdp_cmd("Network.emulateNetworkConditions", {
        "offline": False,
        "latency": lat,
        "downloadThroughput": dl,
        "uploadThroughput": ul,
        "connectionType": random.choice(["wifi","wifi","wifi","cellular4g","cellular3g"])
    })


def get_proxy():
    """Return a random proxy from a list (populate with your actual proxies)."""
    proxies = [
        # "http://user:pass@proxy1:port",
        # "http://user:pass@proxy2:port",
    ]
    if not proxies:
        return None
    return random.choice(proxies)


# =============================================================================
# HUMAN-LIKE TYPING
# =============================================================================

def type_like_human(element, text):
    """
    Advanced human-like typing with:
    - Variable speed per character
    - Occasional typos (backspace + correct)
    - Pauses at punctuation
    """
    try:
        element.click()
    except Exception:
        try:
            element.parent.execute_script("arguments[0].click();", element)
        except Exception:
            pass
    random_delay(0.4, 1.2)

    text_len = len(text)

    # For very long messages, paste instead of typing char-by-char
    if text_len > 200:
        _paste_via_clipboard(element, text)
        return

    for i, char in enumerate(text):
        # --- Make a typo ~3% of the time (only on alphabetic chars) ---
        if char.isalpha() and random.random() < 0.03:
            wrong = random.choice('asdfghjklzxcvbnmqwertyuiop')
            element.send_keys(wrong)
            time.sleep(random.uniform(0.08, 0.20))
            element.send_keys(Keys.BACKSPACE)
            time.sleep(random.uniform(0.12, 0.30))

        # --- Type the correct character ---
        element.send_keys(char)

        # --- Inter-key delay, with natural pauses ---
        if char in '.!?':
            delay = random.uniform(0.35, 0.80)
        elif char == ',':
            delay = random.uniform(0.20, 0.45)
        elif char == ' ':
            delay = random.uniform(0.08, 0.22)
        else:
            delay = random.uniform(TYPING_SPEED_MIN, TYPING_SPEED_MAX)
        time.sleep(delay)


def _paste_via_clipboard(element, text):
    """Paste long text via clipboard with a human-like preparation delay."""
    print("[*] Pasting long text (simulated copy-paste)...")
    pyperclip.copy(text)
    random_delay(0.6, 1.8)   # Simulates: select all → copy → switch window
    modifier = Keys.COMMAND if sys.platform == "darwin" else Keys.CONTROL
    element.send_keys(modifier + 'v')
    random_delay(0.5, 1.2)


# =============================================================================
# ANTI-DETECTION DELAYS & SESSION MANAGEMENT
# =============================================================================

def anti_detection_delay(driver, total_sent, batch_count):
    """
    Human-like variable cooldown between messages with exponential back-off.
    """
    # Base delay: 45s – 5min
    base = random.uniform(MIN_IDLE_BETWEEN_MSGS, MAX_IDLE_BETWEEN_MSGS)

    # Extended break every 3–5 messages
    if batch_count > 0 and batch_count % random.randint(3, 5) == 0:
        base += random.uniform(90, 240)
        print(f"[*] Taking extended break: ~{base:.0f}s ...")

    # Random deep-pause (~18% chance) — simulates user putting phone down
    if random.random() < 0.18:
        base += random.uniform(120, 360)
        print(f"[*] Long pause: ~{base:.0f}s ...")

    # Exponential back-off as total messages increase
    if total_sent > 20:
        base *= 1.5
    if total_sent > 50:
        base *= 2.0
    if total_sent > 100:
        base *= 3.0

    # Never exceed 20 minutes
    base = min(base, 1200)

    print(f"[*] Cooldown: ~{base:.0f}s ...")
    smart_wait(driver, base, base + random.uniform(5, 20))


def should_rotate_session(total_sent, consecutive_failures):
    """Decide whether to start a new browser session."""
    if total_sent >= random.randint(MIN_BATCH_PER_SESSION, MAX_BATCH_PER_SESSION):
        return True
    if consecutive_failures >= 3:
        return True
    return False


# =============================================================================
# DISTRACTION & MISTAKE SIMULATION
# =============================================================================

def maybe_perform_distraction(driver):
    """Random chance of doing something unrelated (scrolling, clicking elsewhere)."""
    if random.random() > DISTRACTION_PROBABILITY:
        return

    print("[*] 🔀 Distraction: browsing around...")
    try:
        actions = ActionChains(driver)
        # Scroll a bit
        driver.execute_script(f"window.scrollBy(0, {random.randint(-200, 200)});")
        random_delay(1.0, 3.0)

        # Click a safe element (e.g., the header, or the sidebar pane background)
        targets = driver.find_elements(By.CSS_SELECTOR,
            "[data-testid='conversation-header'], "
            "header, "
            "#pane-side"
        )
        if targets and random.random() < 0.35:
            t = random.choice(targets)
            ActionChains(driver).move_to_element(t).pause(0.2).click().perform()
            random_delay(1.5, 4.0)
    except Exception:
        pass


def maybe_click_wrong_contact(driver, correct_number):
    """
    ~12% chance: click a different contact, then 'realise' and go back.
    Returns True if a wrong-click diversion happened.
    """
    if random.random() > WRONG_CLICK_PROBABILITY:
        return False

    print("[*] 🎯 Wrong click diversion...")
    try:
        # Find all visible chat items
        items = driver.find_elements(By.CSS_SELECTOR,
            "div[role='listitem'], div[data-testid^='list-item-']"
        )
        if len(items) < 2:
            return False

        # Pick one that is NOT our target (hard to know which is target in search results,
        # so just pick any random one)
        wrong = random.choice(items)
        wrong.click()
        random_delay(2.0, 5.0)

        # "Realise" mistake → go back
        from main import click_back_button  # lazy import to avoid circular
        click_back_button(driver)
        random_delay(1.5, 4.0)
        print("[*] ✅ Back from wrong contact")
        return True
    except Exception:
        return False


def maybe_simulate_typo_in_message(driver, input_box, message):
    """
    15% chance: type the message with a deliberate typo, correct it,
    then continue. Returns True if a typo was simulated.
    """
    if random.random() > TYPO_PROBABILITY_PER_MSG or len(message) < 10:
        return False

    # Insert a typo somewhere in the first half of the message
    pos = random.randint(3, min(len(message)//2, 20))
    typo_char = random.choice('abcdefghijklmnopqrstuvwxyz')
    # Type up to the typo position, then wrong char, backspace, continue
    prefix = message[:pos]
    rest = message[pos:]

    # Type prefix
    for ch in prefix:
        input_box.send_keys(ch)
        time.sleep(random.uniform(0.06, 0.15))

    # Type wrong char
    input_box.send_keys(typo_char)
    random_delay(0.15, 0.35)

    # Backspace
    input_box.send_keys(Keys.BACKSPACE)
    random_delay(0.15, 0.35)

    # Continue typing
    for ch in rest:
        input_box.send_keys(ch)
        time.sleep(random.uniform(0.06, 0.15))

    print("[*] ⌨️ Simulated typo + correction")
    return True