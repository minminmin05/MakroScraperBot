from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

def scrape_product(url):
    chrome_options = Options()
    #chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 15)
    driver.maximize_window()

    product_info = {}
    try:
        driver.get(url)
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # ชื่อสินค้า
        name_tag = soup.find("div", class_="MuiBox-root css-13u9jxe")
        product_info["name"] = name_tag.get_text(strip=True) if name_tag else "ไม่ระบุชื่อ"

        # ราคา
        price_tag = soup.find("div", class_="MuiBox-root css-irt67i")
        product_info["price"] = price_tag.get_text(strip=True) if price_tag else "ไม่ระบุราคา"

        divs = driver.find_elements(By.CSS_SELECTOR, "div.MuiBox-root.css-0")
        for i, div in enumerate(divs):
            if div.text.strip() == "น้ำหนักรวมสุทธิ":
                if i + 1 < len(divs):
                    product_info["size_quantity"] = divs[i + 1].text.strip()
                else:
                    product_info["size_quantity"] = "-"
                break

        product_info["url"] = url

    except Exception as e:
        product_info = {"error": f"❌ ไม่สามารถดึงข้อมูลสินค้าได้: {str(e)}"}
    finally:
        driver.quit()

    return product_info

# ------------------- Test -------------------
if __name__ == "__main__":
    test_url = "https://www.makro.pro/p/123456"  # ตัวอย่าง
    print(scrape_product(test_url))
