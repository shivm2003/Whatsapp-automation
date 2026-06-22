# complete_stealth.py
# Drop this in your project and import it

import json
import random
import os

# =============================================================================
# REAL FINGERPRINT PROFILES — These are consistent, real-user profiles
# =============================================================================

FINGERPRINT_PROFILES = [
    {
        "name": "Windows 10 / Chrome 124 / Intel Laptop",
        "platform": "Win32",
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "screen": {"width": 1920, "height": 1080, "availWidth": 1920, "availHeight": 1040, "colorDepth": 24},
        "hardwareConcurrency": 8,
        "deviceMemory": 8,
        "webglVendor": "Intel Inc.",
        "webglRenderer": "Intel(R) UHD Graphics 620",
        "timezone": "Asia/Kolkata",
        "languages": ["en-US", "en", "hi"],
        "touchSupport": False,
        "fonts": [
            "Arial", "Calibri", "Cambria", "Cambria Math", "Candara", 
            "Comic Sans MS", "Consolas", "Constantia", "Corbel", 
            "Courier New", "Ebrima", "Franklin Gothic Medium", 
            "Gabriola", "Gadugi", "Georgia", "Impact", "Ink Free",
            "Javanese Text", "Leelawadee UI", "Lucida Console",
            "Lucida Sans Unicode", "Malgun Gothic", "Microsoft Himalaya",
            "Microsoft JhengHei", "Microsoft New Tai Lue", "Microsoft PhagsPa",
            "Microsoft Sans Serif", "Microsoft Tai Le", "Microsoft YaHei",
            "Microsoft Yi Baiti", "MingLiU-ExtB", "Mongolian Baiti",
            "MS Gothic", "MV Boli", "Myanmar Text", "Nirmala UI",
            "Palatino Linotype", "Segoe MDL2 Assets", "Segoe Print",
            "Segoe Script", "Segoe UI", "Segoe UI Emoji", "Segoe UI Historic",
            "Segoe UI Symbol", "SimSun", "Sitka Banner", "Sitka Display",
            "Sitka Heading", "Sitka Small", "Sitka Subheading", "Sitka Text",
            "Sylfaen", "Symbol", "Tahoma", "Times New Roman", "Trebuchet MS",
            "Verdana", "Webdings", "Wingdings", "Yu Gothic"
        ],
        "canvasNoiseSeed": 12345,
    },
    {
        "name": "Windows 11 / Chrome 125 / Gaming PC",
        "platform": "Win32",
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "screen": {"width": 2560, "height": 1440, "availWidth": 2560, "availHeight": 1400, "colorDepth": 24},
        "hardwareConcurrency": 16,
        "deviceMemory": 16,
        "webglVendor": "NVIDIA Corporation",
        "webglRenderer": "NVIDIA GeForce RTX 3070",
        "timezone": "America/New_York",
        "languages": ["en-US", "en"],
        "touchSupport": False,
        "fonts": [  # Same as above + additional gaming fonts
            "Arial", "Calibri",
            "OCR A Extended", "OCR-B 10 BT", "Fira Code", "Cascadia Code"
        ],
        "canvasNoiseSeed": 67890,
    },
    {
        "name": "macOS Ventura / Chrome 124 / MacBook Pro",
        "platform": "MacIntel",
        "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "screen": {"width": 1440, "height": 900, "availWidth": 1440, "availHeight": 877, "colorDepth": 24},
        "hardwareConcurrency": 10,
        "deviceMemory": 8,
        "webglVendor": "Apple Inc.",
        "webglRenderer": "Apple M1 Pro",
        "timezone": "Europe/London",
        "languages": ["en-GB", "en"],
        "touchSupport": True,  # MacBook trackpad reports touch
        "fonts": [
            "American Typewriter", "Andale Mono", "Apple Braille",
            "Apple Color Emoji", "Apple SD Gothic Neo", "Arial",
            "Arial Hebrew", "Arial Narrow", "Arial Rounded MT Bold",
            "Arial Unicode MS", "Avenir", "Avenir Next", "Avenir Next Condensed",
            "Baskerville", "Big Caslon", "Bodoni 72", "Bodoni 72 Oldstyle",
            "Bodoni 72 Smallcaps", "Bradley Hand", "Brush Script MT",
            "Chalkboard", "Chalkboard SE", "Chalkduster", "Charter",
            "Cochin", "Comic Sans MS", "Copperplate", "Courier New",
            "Didot", "DIN Alternate", "DIN Condensed", "Futura",
            "Geneva", "Georgia", "Gill Sans", "Helvetica", "Helvetica Neue",
            "Herculanum", "Hoefler Text", "Impact", "Kai", "Lao MN",
            "Lucida Grande", "Luminari", "Marker Felt", "Menlo",
            "Microsoft Sans Serif", "Monaco", "Noteworthy", "Optima",
            "Palatino", "Papyrus", "Phosphate", "PingFang HK",
            "PingFang SC", "PingFang TC", "Plantagenet Cherokee",
            "Raanana", "Savoye LET", "Sinhala MN", "Skia",
            "Snell Roundhand", "Symbol", "Tahoma", "Thonburi",
            "Times New Roman", "Trebuchet MS", "Verdana", "Zapf Dingbats",
            "Zapfino"
        ],
        "canvasNoiseSeed": 34567,
    }
]


def get_random_profile():
    """Return a randomly selected, consistent fingerprint profile."""
    return random.choice(FINGERPRINT_PROFILES)


def apply_complete_stealth(driver, profile=None):
    """
    Apply ALL fingerprint patches from a single consistent profile.
    
    This is the only stealth function you need. Call it once per session.
    """
    if profile is None:
        profile = get_random_profile()
    
    # Build the complete stealth script
    script = f"""
    // ================================================================
    // COMPLETE FINGERPRINT SPOOF — Profile: {profile['name']}
    // ================================================================
    
    // 1. HIDE WEBDRIVER
    Object.defineProperty(navigator, 'webdriver', {{ get: () => undefined }});
    
    // 2. CHROME RUNTIME
    if (!window.chrome) {{ window.chrome = {{ runtime: {{}} }}; }}
    
    // 3. PERMISSIONS
    const origQuery = navigator.permissions.query;
    navigator.permissions.query = (params) => {{
        if (params.name === 'notifications') {{
            return Promise.resolve({{ state: 'prompt' }});
        }}
        return origQuery(params);
    }};
    
    // 4. LANGUAGES
    Object.defineProperty(navigator, 'languages', {{
        get: () => {json.dumps(profile['languages'])}
    }});
    Object.defineProperty(navigator, 'language', {{
        get: () => '{profile['languages'][0]}'
    }});
    
    // 5. PLATFORM
    Object.defineProperty(navigator, 'platform', {{
        get: () => '{profile['platform']}'
    }});
    
    // 6. HARDWARE CONCURRENCY
    Object.defineProperty(navigator, 'hardwareConcurrency', {{
        get: () => {profile['hardwareConcurrency']}
    }});
    
    // 7. DEVICE MEMORY
    Object.defineProperty(navigator, 'deviceMemory', {{
        get: () => {profile['deviceMemory']}
    }});
    
    // 8. PLUGINS
    Object.defineProperty(navigator, 'plugins', {{
        get: () => {{
            const p = [
                {{ name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer' }},
                {{ name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' }},
                {{ name: 'Native Client', filename: 'internal-nacl-plugin' }}
            ];
            p.item = (i) => p[i];
            p.length = p.length;
            return p;
        }}
    }});
    
    // 9. SCREEN GEOMETRY
    Object.defineProperty(screen, 'width', {{ get: () => {profile['screen']['width']} }});
    Object.defineProperty(screen, 'height', {{ get: () => {profile['screen']['height']} }});
    Object.defineProperty(screen, 'availWidth', {{ get: () => {profile['screen']['availWidth']} }});
    Object.defineProperty(screen, 'availHeight', {{ get: () => {profile['screen']['availHeight']} }});
    Object.defineProperty(screen, 'colorDepth', {{ get: () => {profile['screen']['colorDepth']} }});
    Object.defineProperty(screen, 'pixelDepth', {{ get: () => {profile['screen']['colorDepth']} }});
    
    // 10. TOUCH SUPPORT
    Object.defineProperty(navigator, 'maxTouchPoints', {{
        get: () => {1 if profile['touchSupport'] else 0}
    }});
    
    // 11. WEBGL VENDOR/RENDERER
    const getParam = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {{
        // UNMASKED_VENDOR_WEBGL
        if (parameter === 37445) return '{profile['webglVendor']}';
        // UNMASKED_RENDERER_WEBGL  
        if (parameter === 37446) return '{profile['webglRenderer']}';
        return getParam(parameter);
    }};
    
    // Also patch the WebGL2 context
    if (WebGL2RenderingContext) {{
        WebGL2RenderingContext.prototype.getParameter = WebGLRenderingContext.prototype.getParameter;
    }}
    
    // 12. CANVAS FINGERPRINT NOISE
    const origToDataURL = HTMLCanvasElement.prototype.toDataURL;
    const origGetContext = HTMLCanvasElement.prototype.getContext;
    const canvasNoiseSeed = {profile['canvasNoiseSeed']};
    
    // Add deterministic noise based on the seed
    HTMLCanvasElement.prototype.toDataURL = function(type, ...args) {{
        const ctx = this.getContext('2d');
        if (ctx) {{
            const imageData = ctx.getImageData(0, 0, this.width, this.height);
            // Add deterministic noise (based on seed) to 2% of pixels
            for (let i = 0; i < imageData.data.length; i += 4) {{
                if ((i + canvasNoiseSeed) % 50 === 0) {{
                    imageData.data[i] = imageData.data[i] ^ 1;     // R
                    imageData.data[i+1] = imageData.data[i+1] ^ 1; // G
                    imageData.data[i+2] = imageData.data[i+2] ^ 1; // B
                }}
            }}
            ctx.putImageData(imageData, 0, 0);
        }}
        return origToDataURL.call(this, type, ...args);
    }};
    
    // 13. AUDIO CONTEXT FINGERPRINT
    if (AudioContext || webkitAudioContext) {{
        const AudioCtx = AudioContext || webkitAudioContext;
        const origGetChannelData = AudioBuffer.prototype.getChannelData;
        AudioBuffer.prototype.getChannelData = function(channel) {{
            const data = origGetChannelData.call(this, channel);
            for (let i = 0; i < data.length; i += 100) {{
                data[i] += (Math.random() - 0.5) * 0.00001;
            }}
            return data;
        }};
    }}
    
    // 14. TIMEZONE (spoof via Intl.DateTimeFormat)
    // Note: This only works for JS-level timezone detection
    // The --timezone browser arg handles the OS level
    
    // 15. BATTERY API
    if (navigator.getBattery) {{
        navigator.getBattery = () => Promise.resolve({{
            charging: {str(random.random() > 0.5).lower()},
            chargingTime: 0,
            dischargingTime: {random.randint(1800, 7200)},
            level: {round(random.uniform(0.3, 0.95), 2)},
        }});
    }}
    
    // 16. MEDIA DEVICES (hide VM virtual cameras/microphones)
    if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {{
        const origEnumerate = navigator.mediaDevices.enumerateDevices;
        navigator.mediaDevices.enumerateDevices = async function() {{
            const devices = await origEnumerate();
            // Filter out virtual devices
            return devices.filter(d => {{
                const label = d.label.toLowerCase();
                return !label.includes('virtual') && 
                       !label.includes('vmware') && 
                       !label.includes('remote') &&
                       !label.includes('vdmag');
            }});
        }};
    }}
    
    // 17. FONT ENUMERATION SPOOFING
    // (The actual font list is spoofed via the CDP approach below)
    """
    
    # Execute the script
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": script
    })
    
    # 18. SPOOF FONTS via CDP (more reliable than JS)
    font_css = ")".join(profile['fonts'])
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": f"""
        // Override font enumeration
        if (document.fonts) {{
            const origFonts = document.fonts;
            document.fonts = new Set();
            document.fonts.add = function(font) {{}};
            document.fonts.has = function(font) {{
                // Return true for fonts in our profile
                const fontFamily = font.family || font;
                return {font_css}.includes(fontFamily);
            }};
            document.fonts.ready = Promise.resolve(document.fonts);
        }}
        """
    })
    
    # 19. SPOOF TIMEZONE via Intl.DateTimeFormat
    tz = profile['timezone']
    try:
        # Get the actual offset for this timezone
        import pytz
        from datetime import datetime
        tz_obj = pytz.timezone(tz)
        offset = tz_obj.utcoffset(datetime.now()).total_seconds() / 60
        tz_offset = -int(offset)  # JS uses opposite sign
    except:
        tz_offset = -330  # Default to IST if pytz unavailable
    
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": f"""
        // Spoof timezone via Intl.DateTimeFormat
        const origDateTimeFormat = Intl.DateTimeFormat;
        Intl.DateTimeFormat = function(locales, options) {{
            if (options && options.timeZone) {{
                options.timeZone = '{tz}';
            }}
            return new origDateTimeFormat(locales, options);
        }};
        
        // Date.prototype.getTimezoneOffset spoof
        const origGetTZOffset = Date.prototype.getTimezoneOffset;
        Date.prototype.getTimezoneOffset = function() {{
            return {tz_offset};
        }};
        """
    })
    
    return profile  # Return the profile used for logging