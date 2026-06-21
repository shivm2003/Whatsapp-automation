import time
import random
import sys
import undetected_chromedriver as uc
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
        print("[*] Typing message character-by-character...")
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
        print("[*] Pasting message with natural preparation delay...")
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
        print(f"[*] Simulating {steps} random mouse movements...")
        
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
        print(f"[!] Mouse movement simulation skipped: {e}")

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

def apply_advanced_stealth_cdp(driver):
    """More comprehensive CDP stealth overrides"""
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            // Overwrite navigator properties
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            
            // Chrome runtime
            if (!window.chrome) {
                window.chrome = { runtime: {} };
            }
            
            // Permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // Languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en', 'hi', 'mr']
            });
            
            // Plugins - more realistic
            Object.defineProperty(navigator, 'plugins', {
                get: () => {
                    const plugins = [
                        { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer' },
                        { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
                        { name: 'Native Client', filename: 'internal-nacl-plugin' }
                    ];
                    plugins.item = (i) => plugins[i];
                    plugins.length = plugins.length;
                    return plugins;
                }
            });
            
            // WebGL vendor/renderer spoofing (hide real GPU)
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) return 'Intel Inc.';  // UNMASKED_VENDOR_WEBGL
                if (parameter === 37446) return 'Intel Iris OpenGL Engine';  // UNMASKED_RENDERER_WEBGL
                return getParameter(parameter);
            };
            
            // Screen dimensions (normalize)
            Object.defineProperty(screen, 'availTop', { get: () => 0 });
            Object.defineProperty(screen, 'availLeft', { get: () => 0 });
            
            // Hardware concurrency (spoof)
            Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
            
            // Device memory
            Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
        """
    })

def parse_spintax(text):
    """
    Parses spintax formatted text (e.g., '{Hi|Hello|Hey} there!') and 
    returns a randomly generated variation.
    """
    import re
    
    # Regular expression to find {option1|option2}
    pattern = re.compile(r'\{([^{}]*)\}')
    
    match = pattern.search(text)
    while match:
        options = match.group(1).split('|')
        choice = random.choice(options)
        text = text[:match.start()] + choice + text[match.end():]
        match = pattern.search(text)
        
    return text

def get_fingerprint_options():
    """Randomize browser fingerprint to avoid profiling"""
    options = uc.ChromeOptions()
    
    # Random window size (common resolutions only)
    resolutions = [
        (1920, 1080), (1366, 768), (1536, 864), 
        (1280, 720), (1440, 900), (1600, 900)
    ]
    width, height = random.choice(resolutions)
    options.add_argument(f"--window-size={width},{height}")
    
    # Random timezone
    timezones = [
        "Asia/Kolkata", "Asia/Kolkata", "Asia/Kolkata",  # Weight India
        "Asia/Dubai", "Asia/Singapore", "America/New_York",
        "Europe/London", "Asia/Bangkok"
    ]
    tz = random.choice(timezones)
    options.add_argument(f"--timezone={tz}")
    
    # Random user agent (rotate between recent Chrome versions)
    chrome_versions = ["120", "121", "122", "123", "124", "125"]
    platform = random.choice(["Windows NT 10.0; Win64; x64", 
                               "Windows NT 10.0; Win64; x64"])
    ua = f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.choice(chrome_versions)}.0.0.0 Safari/537.36"
    options.add_argument(f"user-agent={ua}")
    
    return options

def type_like_human_advanced(element, text, typo_probability=0.03):
    """
    Types text with realistic typos and corrections.
    typo_probability: chance (0-1) of making a typo per character
    """
    element.click()
    random_delay(0.3, 0.8)
    
    for i, char in enumerate(text):
        # Simulate occasional typo
        if random.random() < typo_probability and char.isalpha():
            # Type wrong character
            wrong_char = random.choice('asdfghjkl')
            element.send_keys(wrong_char)
            random_delay(0.1, 0.25)
            # Backspace
            element.send_keys(Keys.BACKSPACE)
            random_delay(0.15, 0.3)
            # Type correct character
            element.send_keys(char)
        else:
            element.send_keys(char)
        
        # Variable inter-key delay
        delay = random.uniform(0.03, 0.12)
        # Pause longer at punctuation and spaces
        if char in '.!?':
            delay = random.uniform(0.3, 0.7)
        elif char == ',':
            delay = random.uniform(0.2, 0.4)
        elif char == ' ':
            delay = random.uniform(0.08, 0.2)
        
        time.sleep(delay)

def anti_detection_delay(driver, sent_count, batch_count):
    """
    Variable delays with patterns that look human.
    """
    base_delay = random.uniform(30, 45)
    
    # Longer delay after every 5-8 messages
    if batch_count > 0 and batch_count % random.randint(5, 8) == 0:
        base_delay += random.uniform(60, 120)
        print(f"[*] Taking extended break ({base_delay:.0f}s)...")
    
    # Random longer pauses (mimics checking phone)
    if random.random() < 0.15:  # 15% chance
        base_delay += random.uniform(45, 90)
        print(f"[*] Long pause ({base_delay:.0f}s)...")
    
    # Exponential backoff as total messages increase
    if sent_count > 50:
        base_delay *= 1.5
    if sent_count > 100:
        base_delay *= 2.0
    
    print(f"[*] Waiting {base_delay:.0f}s...")
    smart_wait(driver, base_delay, base_delay + 5.0)

def should_rotate_session(sent_count, failures):
    """Decide whether to restart browser to get fresh fingerprint"""
    if sent_count >= random.randint(80, 120):
        return True
    if failures >= 3:
        return True
    return False

def apply_network_conditions(driver):
    """Simulate realistic network latency"""
    driver.execute_cdp_cmd("Network.emulateNetworkConditions", {
        "offline": False,
        "latency": random.randint(20, 80),      # ms
        "downloadThroughput": random.randint(5 * 1024 * 1024, 50 * 1024 * 1024),
        "uploadThroughput": random.randint(1 * 1024 * 1024, 10 * 1024 * 1024),
        "connectionType": random.choice(["wifi", "wifi", "wifi", "cellular4g"])
    })

def apply_canvas_stealth(driver):
    """Spoof canvas fingerprint to avoid browser profiling"""
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            // Canvas fingerprint spoofing
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            const originalGetContext = HTMLCanvasElement.prototype.getContext;
            
            HTMLCanvasElement.prototype.getContext = function(type, ...args) {
                const ctx = originalGetContext.apply(this, [type, ...args]);
                if (type === '2d') {
                    const originalFillText = ctx.fillText;
                    ctx.fillText = function(...args) {
                        // Add subtle noise to text rendering
                        const shift = Math.random() * 0.00001;
                        args[1] += shift;
                        return originalFillText.apply(this, args);
                    };
                }
                return ctx;
            };
            
            // Noise to toDataURL
            HTMLCanvasElement.prototype.toDataURL = function(type) {
                const canvas = this;
                const ctx = canvas.getContext('2d');
                const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                // Add imperceptible noise to 1% of pixels
                for (let i = 0; i < imageData.data.length; i += 4) {
                    if (Math.random() < 0.01) {
                        imageData.data[i] = imageData.data[i] ^ 1;        // R
                        imageData.data[i+1] = imageData.data[i+1] ^ 1;  // G
                        imageData.data[i+2] = imageData.data[i+2] ^ 1;  // B
                    }
                }
                ctx.putImageData(imageData, 0, 0);
                return originalToDataURL.call(this, type);
            };
        """
    })

def apply_audio_stealth(driver):
    """Spoof AudioContext fingerprint"""
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            const originalGetChannelData = AudioBuffer.prototype.getChannelData;
            AudioBuffer.prototype.getChannelData = function(channel) {
                const data = originalGetChannelData.call(this, channel);
                // Add tiny noise to audio data
                for (let i = 0; i < data.length; i += 100) {
                    data[i] += (Math.random() - 0.5) * 0.00001;
                }
                return data;
            };
        """
    })

def apply_font_stealth(driver):
    """Return a consistent, realistic font list"""
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            // Block font enumeration used for fingerprinting
            const originalQuery = document.fonts.query;
            if (document.fonts) {
                Object.defineProperty(document.fonts, 'ready', {
                    get: () => Promise.resolve(new Set())
                });
            }
        """
    })

def apply_visibility_stealth(driver):
    """Prevent WhatsApp from detecting the tab is in background"""
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            // Never report the tab as hidden
            Object.defineProperty(document, 'hidden', {
                get: () => false
            });
            Object.defineProperty(document, 'visibilityState', {
                get: () => 'visible'
            });
            // Override the visibilitychange event
            const originalAddEventListener = document.addEventListener;
            document.addEventListener = function(type, listener, options) {
                if (type === 'visibilitychange') {
                    // Don't register visibility change listeners
                    return;
                }
                return originalAddEventListener.call(this, type, listener, options);
            };
        """
    })

def apply_media_stealth(driver):
    """Spoof CSS media features that can be used for fingerprinting"""
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            // MatchMedia override
            const originalMatchMedia = window.matchMedia;
            window.matchMedia = function(query) {
                const mediaList = originalMatchMedia.call(this, query);
                // Always report as not preferring reduced motion (bots often have this on)
                if (query.includes('prefers-reduced-motion')) {
                    mediaList.matches = false;
                }
                return mediaList;
            };
        """
    })

def apply_webrtc_stealth(driver):
    """Disable WebRTC IP leaks that could reveal VPN/proxy"""
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            // Disable WebRTC
            if (window.RTCPeerConnection) {
                window.RTCPeerConnection = undefined;
            }
            if (window.webkitRTCPeerConnection) {
                window.webkitRTCPeerConnection = undefined;
            }
        """
    })

def get_proxy():
    """Get a random proxy from a rotation list (Populate with your real proxies)"""
    # Replace these with your actual proxy service details if scaling to thousands of messages
    proxies = [
        # "http://user:pass@proxy1:port",
        # "http://user:pass@proxy2:port",
    ]
    if not proxies:
        return None
    return random.choice(proxies)

def smart_wait(driver, min_s, max_s):
    """Wait with occasional human-like interactions"""
    end_time = time.time() + random.uniform(min_s, max_s)
    last_action = time.time()
    
    while time.time() < end_time:
        time.sleep(min(2.0, end_time - time.time() + 0.1)) # Don't oversleep
        if time.time() >= end_time:
            break
        
        # Every 5-10 seconds, do something human-like
        if time.time() - last_action > random.uniform(5.0, 10.0):
            action = random.choice([
                lambda: simulate_mouse_movement(driver),
                lambda: driver.execute_script(f"window.scrollBy(0, {random.randint(-100, 100)});"),
                lambda: None  # do nothing sometimes
            ])
            try:
                action()
            except:
                pass
            last_action = time.time()
