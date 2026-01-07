import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import threading
import os
import time
import random
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURATION ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
RESIZED_FOLDER = os.path.join(BASE_DIR, 'resized_temp')
PROFILE_FOLDER = os.path.join(BASE_DIR, 'whatsapp_profile_data')

if not os.path.exists(RESIZED_FOLDER):
    os.makedirs(RESIZED_FOLDER)

class WhatsAppBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("WhatsApp Bulk Sender (Pro Version)")
        self.root.geometry("600x750")
        self.root.configure(bg="#f0f2f5")

        self.numbers_file = None
        self.image_files = []
        self.is_running = False

        # --- UI ELEMENTS ---
        
        # Title
        tk.Label(root, text="WhatsApp Automation Tool 🚀", font=("Arial", 16, "bold"), bg="#f0f2f5", fg="#075e54").pack(pady=10)

        # 1. Select Numbers
        self.btn_nums = tk.Button(root, text="📂 Select Numbers File (.txt)", command=self.select_numbers, bg="white", width=40)
        self.btn_nums.pack(pady=5)
        self.lbl_nums = tk.Label(root, text="No file selected", bg="#f0f2f5", fg="gray", font=("Arial", 8))
        self.lbl_nums.pack()

        # 2. Select Images
        self.btn_imgs = tk.Button(root, text="📸 Select Photos (Optional)", command=self.select_images, bg="white", width=40)
        self.btn_imgs.pack(pady=5)
        self.lbl_imgs = tk.Label(root, text="No photos selected", bg="#f0f2f5", fg="gray", font=("Arial", 8))
        self.lbl_imgs.pack()

        # 3. Message Input
        tk.Label(root, text="Message:", bg="#f0f2f5", font=("Arial", 10, "bold")).pack(pady=(10, 0))
        self.txt_msg = tk.Text(root, height=5, width=50)
        self.txt_msg.pack(pady=5)

        # 4. Your Number
        tk.Label(root, text="Your Number (For Report):", bg="#f0f2f5").pack()
        self.ent_my_num = tk.Entry(root, width=30)
        self.ent_my_num.insert(0, "8982138233")
        self.ent_my_num.pack(pady=5)

        # 5. Buttons
        btn_frame = tk.Frame(root, bg="#f0f2f5")
        btn_frame.pack(pady=15)
        
        self.btn_start = tk.Button(btn_frame, text="▶ START", command=self.start_thread, bg="#25D366", fg="white", font=("Arial", 12, "bold"), width=15)
        self.btn_start.pack(side=tk.LEFT, padx=10)

        # 6. Log Window
        tk.Label(root, text="Live Logs:", bg="#f0f2f5", font=("Arial", 9, "bold")).pack(anchor="w", padx=20)
        self.log_box = scrolledtext.ScrolledText(root, height=12, width=65, bg="black", fg="#00ff00", font=("Consolas", 9))
        self.log_box.pack(pady=5)

    def log(self, message):
        """Adds a message to the black log box"""
        self.log_box.insert(tk.END, f">> {message}\n")
        self.log_box.see(tk.END)

    def select_numbers(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            self.numbers_file = file_path
            self.lbl_nums.config(text=os.path.basename(file_path), fg="black")

    def select_images(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("Images", "*.jpg *.jpeg *.png *.webp")])
        if file_paths:
            self.image_files = list(file_paths)
            self.lbl_imgs.config(text=f"{len(file_paths)} photos selected", fg="black")

    def resize_images(self, image_paths):
        resized_paths = []
        self.log("📸 Optimizing images to JPG...")
        for img_path in image_paths:
            try:
                filename = os.path.basename(img_path)
                filename_no_ext = os.path.splitext(filename)[0]
                save_path = os.path.join(RESIZED_FOLDER, f"small_{filename_no_ext}.jpg")
                
                with Image.open(img_path) as img:
                    img = img.convert("RGB")
                    img.thumbnail((1280, 1280))
                    img.save(save_path, "JPEG", optimize=True, quality=85)
                    resized_paths.append(save_path)
            except Exception as e:
                self.log(f"⚠️ Error resizing {filename}: {e}")
        return resized_paths

    def start_thread(self):
        if not self.numbers_file:
            messagebox.showerror("Error", "Please select a Numbers file first!")
            return
        
        if self.is_running:
            return

        self.is_running = True
        self.btn_start.config(state=tk.DISABLED, text="Running...")
        
        # Run logic in background thread
        t = threading.Thread(target=self.run_bot)
        t.start()

    def run_bot(self):
        try:
            # Get inputs
            with open(self.numbers_file, "r") as f:
                numbers = [line.strip() for line in f if line.strip()]
            
            message_text = self.txt_msg.get("1.0", tk.END).strip()
            my_number = self.ent_my_num.get().strip()
            optimized_images = self.resize_images(self.image_files)

            # Start Chrome
            self.log("🚀 Launching Browser...")
            options = webdriver.ChromeOptions()
            options.add_argument(f"--user-data-dir={PROFILE_FOLDER}")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_argument("--no-sandbox")
            
            driver = webdriver.Chrome(service=Service(), options=options)
            wait = WebDriverWait(driver, 30)
            
            driver.get("https://web.whatsapp.com")
            self.log("⏳ Please SCAN the QR Code now.")
            self.log("Waiting indefinitely for login...")

            # Wait for Login
            while True:
                try:
                    driver.find_element(By.ID, "side")
                    self.log("✅ Login Detected! Starting in 5s...")
                    time.sleep(5)
                    break
                except:
                    time.sleep(2)
                    try:
                        _ = driver.window_handles
                    except:
                        self.log("❌ Browser closed.")
                        return

            success = 0
            failed = 0

            for i, num in enumerate(numbers):
                self.log(f"[{i+1}/{len(numbers)}] Processing: {num}")

                try:
                    link = f"https://web.whatsapp.com/send/?phone=91{num}"
                    driver.execute_script(f'window.location.href="{link}";')

                    # Wait for Chat or Invalid
                    try:
                        WebDriverWait(driver, 45).until(EC.any_of(
                            EC.presence_of_element_located((By.ID, "main")),
                            EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Phone number shared via url is invalid')]")),
                            EC.presence_of_element_located((By.XPATH, "//div[@data-testid='popup-controls']"))
                        ))
                    except:
                        self.log(f"❌ Timeout loading chat: {num}")
                        failed += 1
                        continue

                    # Check Invalid
                    if driver.find_elements(By.XPATH, "//div[contains(text(), 'Phone number shared via url is invalid')]"):
                        self.log(f"🚫 Invalid Number: {num}")
                        failed += 1
                        continue
                    
                    time.sleep(random.uniform(2, 4))

                    # Upload Images
                    if optimized_images:
                        image_sent = False
                        # Try standard click
                        try:
                            driver.find_element(By.XPATH, "//div[@title='Attach'] | //span[@data-icon='plus']").click()
                            time.sleep(1)
                            inp = driver.find_element(By.XPATH, "//input[@accept='image/*,video/mp4,video/3gpp,video/quicktime']")
                            for img in optimized_images:
                                inp.send_keys(img)
                            image_sent = True
                        except:
                            # Try brute force
                            try:
                                inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
                                for inp in inputs:
                                    try:
                                        for img in optimized_images:
                                            inp.send_keys(img)
                                        image_sent = True
                                        break
                                    except:
                                        continue
                            except:
                                self.log("⚠️ Image upload failed.")

                        if image_sent:
                            time.sleep(2)
                            try:
                                wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@data-icon='send'] | //div[@aria-label='Send']"))).click()
                                time.sleep(2)
                            except:
                                pass

                    # Send Text
                    if message_text:
                        # Find box (Standard + Fallback)
                        box = None
                        selectors = [
                            "//div[@contenteditable='true'][@data-tab='10']",
                            "//div[@id='main']//footer//div[@contenteditable='true']",
                            "//div[@title='Type a message']"
                        ]
                        for xpath in selectors:
                            try:
                                box = driver.find_element(By.XPATH, xpath)
                                break
                            except:
                                continue
                        
                        if box:
                            box.click()
                            for line in message_text.split('\n'):
                                box.send_keys(line)
                                box.send_keys(Keys.SHIFT + Keys.ENTER)
                            box.send_keys(Keys.ENTER)
                            success += 1
                            self.log(f"✅ Sent to {num}")
                            time.sleep(random.uniform(4, 8))
                        else:
                            self.log(f"❌ Text box not found: {num}")
                            failed += 1
                    else:
                        # Even if no text, count as success if image sent
                        success += 1
                        self.log(f"✅ Sent (Image Only) to {num}")
                        time.sleep(random.uniform(4, 8))

                except Exception as e:
                    self.log(f"❌ Critical Error {num}: {e}")
                    failed += 1

            # Report
            self.log("📝 Sending Final Report...")
            try:
                driver.get(f"https://web.whatsapp.com/send/?phone=91{my_number}")
                WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//div[@id='main']")))
                time.sleep(3)
                
                # Find box again for report
                box = driver.find_element(By.XPATH, "//div[@contenteditable='true'][@data-tab='10']")
                box.click()
                report = f"*Run Complete*\n✅ Sent: {success}\n❌ Failed: {failed}"
                box.send_keys(report)
                box.send_keys(Keys.ENTER)
                time.sleep(5)
            except Exception as e:
                self.log(f"⚠️ Report failed: {e}")

            self.log("🏁 Automation Finished.")
            messagebox.showinfo("Done", "Broadcast Complete!")

        except Exception as e:
            self.log(f"🔥 Crash: {e}")
        finally:
            self.is_running = False
            self.btn_start.config(state=tk.NORMAL, text="▶ START")


if __name__ == "__main__":
    root = tk.Tk()
    app = WhatsAppBotGUI(root)
    root.mainloop()