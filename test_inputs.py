import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

def dump_inputs():
    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir=profiles/profile_1")
    driver = uc.Chrome(options=options, version_main=149)
    driver.get("https://web.whatsapp.com")
    
    print("[!] Waiting 15s for chats to load...")
    time.sleep(15)
    
    try:
        # Click a chat
        chats = driver.find_elements(By.CSS_SELECTOR, "div[data-testid^='list-item-']")
        if chats:
            chats[0].click()
            time.sleep(2)
            
            # Click attach button
            attach = driver.find_element(By.CSS_SELECTOR, "[data-icon='plus-rounded'], [data-testid='clip']")
            attach.click()
            time.sleep(2)
            
            inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
            print(f"Found {len(inputs)} file inputs.")
            for idx, fi in enumerate(inputs):
                accept = fi.get_attribute('accept')
                parent_text = "N/A"
                try:
                    parent_text = fi.find_element(By.XPATH, "./ancestor::li").text
                except:
                    pass
                print(f"Input {idx}: accept={accept}, parent_text={parent_text.strip()}")
                
    except Exception as e:
        print("Error:", e)
    finally:
        driver.quit()

if __name__ == '__main__':
    dump_inputs()
