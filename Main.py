from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import time
import random
import os

# --- SETTINGS ---
COUNTRY_CODE = "91"
MY_NUMBER = "8982138233"
IMAGE_FOLDER_PATH = r"C:\Users\windows11\Desktop\Masheshwari-F Whatapps Automation bulk Message sender\Photos"
RESIZED_FOLDER_PATH = r"C:\Users\windows11\Desktop\Masheshwari-F Whatapps Automation bulk Message sender\Resized_Temp"
BREAK_EVERY_N_PEOPLE = 100
BREAK_DURATION_SECONDS = 900

def jittery_sleep(min_s, max_s):
    time.sleep(random.uniform(min_s, max_s))

def log_failed_number(number, reason):
    with open("failed_numbers.txt", "a") as f:
        f.write(f"{number} | Reason: {reason}\n")

def auto_resize_photos():
    if not os.path.exists(RESIZED_FOLDER_PATH):
        os.makedirs(RESIZED_FOLDER_PATH)
    print("📸 Optimizing photos...")
    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp')
    resized_list = []
    for filename in os.listdir(IMAGE_FOLDER_PATH):
        if filename.lower().endswith(valid_extensions):
            img_path = os.path.join(IMAGE_FOLDER_PATH, filename)
            save_path = os.path.join(RESIZED_FOLDER_PATH, f"small_{filename}")
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1280, 1280))
                img.save(save_path, optimize=True, quality=85)
                resized_list.append(os.path.abspath(save_path))
    return resized_list

options = webdriver.ChromeOptions()
options.add_argument(r"--user-data-dir=C:\whatsapp_profile")
options.add_experimental_option("excludeSwitches", ["enable-automation"])

driver = webdriver.Chrome(service=Service(), options=options)
wait = WebDriverWait(driver, 60)

# --- 🛠️ FIND BOX ACCURATELY ---
def find_chat_box(driver):
    selectors = [
        "//div[@aria-placeholder='Type a message']",
        "//div[@title='Type a message']",
        "//div[@contenteditable='true' and @data-tab='10']"
    ]
    
    for xpath in selectors:
        try:
            box = driver.find_element(By.XPATH, xpath)
            return box
        except:
            continue
    return None

def start_broadcast():
    if os.path.exists("failed_numbers.txt"):
        os.remove("failed_numbers.txt")

    try:
        images = auto_resize_photos()
        with open("numbers.txt", "r") as f:
            all_numbers = [n.strip() for n in f if n.strip()]
        with open("message.txt", "r", encoding="utf-8") as f:
            msg_content = f.read()
    except Exception as e:
        print(f"File Error: {e}")
        return

    driver.get("https://web.whatsapp.com")
    print("Waiting for sync...")
    time.sleep(30)

    success_count = 0
    fail_count = 0

    for i, num in enumerate(all_numbers):
        if (success_count + fail_count) > 0 and (success_count + fail_count) % BREAK_EVERY_N_PEOPLE == 0:
            print(f"☕ Break Time... waiting 15 mins.")
            time.sleep(BREAK_DURATION_SECONDS)

        print(f"[{i + 1}/{len(all_numbers)}] Processing: {num}")

        try:
            link = f"https://web.whatsapp.com/send/?phone={COUNTRY_CODE}{num}"
            driver.execute_script(f'window.location.href="{link}";')
            
            # Wait for the chat to be ready
            wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='main']")))
            jittery_sleep(3, 5)

            # --- SEND IMAGES ---
            for img_path in images:
                file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
                file_input.send_keys(img_path)
                time.sleep(2)
                webdriver.ActionChains(driver).send_keys(Keys.ENTER).perform()
                time.sleep(1.5)

            # --- SEND MESSAGE ---
            chat_box = find_chat_box(driver)
            
            if chat_box:
                chat_box.click()
                time.sleep(0.5)
                for line in msg_content.split("\n"):
                    chat_box.send_keys(line)
                    chat_box.send_keys(Keys.SHIFT + Keys.ENTER)
                chat_box.send_keys(Keys.ENTER)
                
                success_count += 1
                print(f"✅ Success: {num}")
                jittery_sleep(10, 15)
            else:
                raise Exception("Could not find text box")

        except Exception as e:
            fail_count += 1
            print(f"❌ Failed: {num} ({e})")
            log_failed_number(num, "Error")
            continue

    # --- FINAL REPORT SECTION (UPDATED) ---
    print("\n--- Sending Final Report ---")
    try:
        driver.get(f"https://web.whatsapp.com/send/?phone={COUNTRY_CODE}{MY_NUMBER}")
        wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='main']")))
        time.sleep(5)
        
        report_box = find_chat_box(driver)
        if report_box:
            report_box.click()
            time.sleep(0.5)
            
            # * denotes BOLD in WhatsApp
            report_text = f"*Hello Ashutosh This is Today Report!*\nSuccess: {success_count}\nFailed: {fail_count}"
            
            # Use SHIFT + ENTER to keep it in one box
            for line in report_text.split("\n"):
                report_box.send_keys(line)
                report_box.send_keys(Keys.SHIFT + Keys.ENTER)
                
            report_box.send_keys(Keys.ENTER)
            print("✅ Report sent.")
            time.sleep(10)
    except Exception as e:
        print(f"Report error: {e}")

    driver.quit()

if __name__ == "__main__":
    start_broadcast()