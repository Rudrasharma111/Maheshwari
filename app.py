from flask import Flask, render_template, request, redirect, url_for, flash
import os
import threading
import time
import random
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)
app.secret_key = "super_secret_key"

# --- CONFIG ---
UPLOAD_FOLDER = 'uploads'
RESIZED_FOLDER = 'resized_temp'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESIZED_FOLDER, exist_ok=True)

# --- GLOBAL VARIABLES ---
automation_running = False

def resize_images(image_paths):
    resized_paths = []
    for img_path in image_paths:
        try:
            filename = os.path.basename(img_path)
            save_path = os.path.join(RESIZED_FOLDER, f"small_{filename}")
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1280, 1280))
                img.save(save_path, optimize=True, quality=85)
                resized_paths.append(os.path.abspath(save_path))
        except Exception as e:
            print(f"Error resizing {img_path}: {e}")
    return resized_paths

def find_chat_box(driver):
    selectors = [
        "//div[@aria-placeholder='Type a message']",
        "//div[@title='Type a message']",
        "//div[@contenteditable='true' and @data-tab='10']"
    ]
    for xpath in selectors:
        try:
            return driver.find_element(By.XPATH, xpath)
        except:
            continue
    return None

def run_whatsapp_bot(numbers_path, image_paths, message_text, my_number):
    global automation_running
    automation_running = True
    
    try:
        # 1. Read Numbers
        with open(numbers_path, "r") as f:
            numbers = [line.strip() for line in f if line.strip()]

        # 2. Resize Images
        optimized_images = resize_images(image_paths)

        # 3. Start Browser
        options = webdriver.ChromeOptions()
        options.add_argument(r"--user-data-dir=C:\whatsapp_profile")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        driver = webdriver.Chrome(service=Service(), options=options)
        wait = WebDriverWait(driver, 60)

        driver.get("https://web.whatsapp.com")
        time.sleep(20) # Time to scan QR

        success = 0
        failed = 0

        for num in numbers:
            try:
                driver.get(f"https://web.whatsapp.com/send/?phone=91{num}")
                wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='main']")))
                time.sleep(3)

                # Send Images
                for img in optimized_images:
                    file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
                    file_input.send_keys(img)
                    time.sleep(1)
                    webdriver.ActionChains(driver).send_keys(Keys.ENTER).perform()
                    time.sleep(1)

                # Send Message
                box = find_chat_box(driver)
                if box:
                    box.click()
                    for line in message_text.split('\n'):
                        box.send_keys(line)
                        box.send_keys(Keys.SHIFT + Keys.ENTER)
                    box.send_keys(Keys.ENTER)
                    success += 1
                    time.sleep(random.uniform(5, 10))
                
            except Exception as e:
                print(f"Failed {num}: {e}")
                failed += 1

        # Final Report
        try:
            driver.get(f"https://web.whatsapp.com/send/?phone=91{my_number}")
            wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='main']")))
            time.sleep(5)
            box = find_chat_box(driver)
            if box:
                report = f"*Hello Ashutosh This is Today Report!*\nSuccess: {success}\nFailed: {failed}"
                for line in report.split('\n'):
                    box.send_keys(line)
                    box.send_keys(Keys.SHIFT + Keys.ENTER)
                box.send_keys(Keys.ENTER)
                time.sleep(5)
        except:
            pass

    except Exception as e:
        print(f"Bot Crashed: {e}")
    finally:
        automation_running = False
        # driver.quit() # Optional: Close browser when done

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if automation_running:
            flash("Bot is already running! Please wait.", "error")
            return redirect(url_for('index'))

        # Get Form Data
        numbers_file = request.files['numbers_file']
        uploaded_photos = request.files.getlist('photos')
        message = request.form['message']
        my_number = request.form['my_number']

        # Save Numbers File
        if numbers_file.filename == '':
            flash("No numbers file selected!", "error")
            return redirect(url_for('index'))
            
        num_path = os.path.join(UPLOAD_FOLDER, "numbers.txt")
        numbers_file.save(num_path)

        # Save Photos
        saved_img_paths = []
        for photo in uploaded_photos:
            if photo.filename != '':
                p_path = os.path.join(UPLOAD_FOLDER, photo.filename)
                photo.save(p_path)
                saved_img_paths.append(p_path)

        # Run Bot in Background Thread
        thread = threading.Thread(target=run_whatsapp_bot, args=(num_path, saved_img_paths, message, my_number))
        thread.start()

        flash("🚀 Automation Started! Check the Chrome window.", "success")
        return redirect(url_for('index'))

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)