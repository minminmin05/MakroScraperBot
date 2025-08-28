from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import time
import os

# ------------------- ตั้งค่า Chrome -------------------
chrome_options = Options()
# chrome_options.add_argument("--headless")  # รันแบบไม่มี UI ถ้าต้องการ
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

service = Service()
driver = webdriver.Chrome(service=service, options=chrome_options)
wait = WebDriverWait(driver, 15)

# ------------------- รายการหมวดหมู่ -------------------
categories = {
    "fish-seafood": "/c/fish-seafood",
    "meat": "/c/meat",
    "fruit-vegetables": "/c/fruit-vegetables",
}

base_url = "https://www.makro.pro"

# ------------------- เข้าเว็บ Makro -------------------
driver.get(base_url)
driver.maximize_window()

# ------------------- ปิด Banner ถ้ามี -------------------
time.sleep(3)
try:
    banner = driver.find_element(By.ID, "c-bns")
    driver.execute_script("arguments[0].style.display = 'none';", banner)
    print("✅ Banner hidden")
except:
    print("ℹ️ No banner found")

# ------------------- คลิกเมนูหมวดหมู่ -------------------
menu_category = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='หมวดหมู่สินค้า']")))
driver.execute_script("arguments[0].click();", menu_category)
time.sleep(2)

# ------------------- ดึงข้อมูลแต่ละหมวดหมู่ -------------------
for cat_name, cat_path in categories.items():
    print(f"🔍 กำลังดึงข้อมูลหมวดหมู่: {cat_name}")

    # คลิกที่ลิงก์หมวดหมู่
    menu_item = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[contains(@href, '{cat_path}')]")))
    driver.execute_script("arguments[0].click();", menu_item)
    time.sleep(5)

    # คลิก "โปรโมชั่น ลดราคา" ถ้ามี
    try:
        promo_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//p[text()='ลดราคา']")))
        driver.execute_script("arguments[0].click();", promo_button)
        print("✅ คลิกที่โปรโมชั่น: ลดราคา สำเร็จ")
        time.sleep(3)
    except:
        print("⚠️ ไม่พบปุ่ม 'ลดราคา'")

    # ดึง HTML
    soup = BeautifulSoup(driver.page_source, "html.parser")
    products = []

    # Loop ดึงสินค้า
    for item in soup.find_all("div", class_="MuiBox-root css-1p137hx"):
        price_div = item.find("div", class_="MuiBox-root css-irt67i")
        if not price_div:
            continue

        # ชื่อสินค้า
        name_tag = item.find("span", class_="css-1n8x1y2")
        name = name_tag.get_text(strip=True) if name_tag else "No name"

        # รูป
        img_tag = item.find("img")
        img = img_tag["src"] if img_tag else ""

        # ✅ ลิงก์สินค้า จาก div ที่มี class MuiBox-root css-1jnkcok
        link_tag = item.find("div", class_="MuiBox-root css-1jnkcok")
        link_html = link_tag.get("href") if link_tag else ""  # ดึงค่า href โดยตรง

        # ราคา
        price = price_div.get_text(strip=True)

        products.append({
            "name": name,
            "image": img,
            "link": "https://www.makro.pro/" + link_html,
            "price": price
        })

        if len(products) >= 20:
            break



    # บันทึก JSON
    file_name = f"makro_{cat_name}.json"
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print(f"✅ บันทึก {len(products)} รายการที่ {file_name}")

    # กลับไปหน้าหมวดหมู่หลัก
    driver.get(base_url)
    time.sleep(3)
    try:
        menu_category = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='หมวดหมู่สินค้า']")))
        driver.execute_script("arguments[0].click();", menu_category)
        time.sleep(2)
    except:
        print("⚠️ ไม่พบเมนูหมวดหมู่")

driver.quit()
print("🎉 ดึงข้อมูลครบทุกหมวดหมู่เรียบร้อย")
