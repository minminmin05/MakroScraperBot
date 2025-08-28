from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    TemplateSendMessage, CarouselTemplate, CarouselColumn,
    PostbackAction, PostbackEvent
)
import json
import os
from scrap_menudetail import scrape_product

app = Flask(__name__)

CHANNEL_SECRET = 'XXXXXX'#enter yours
CHANNEL_ACCESS_TOKEN = 'XXXX'#enter yours

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

current_menu_data = []

# ------------------- Flask Callback -------------------
@app.route("/", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

# ------------------- MessageEvent Handler -------------------
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global current_menu_data
    user_message = event.message.text.strip().lower()

    greetings = ["hi", "hello", "hey", "สวัสดี", "หวัดดี", "เมนู", "menu"]
    categories = ["fish-seafood", "meat", "fruit-vegetables"]

    # ------------------- Greeting → Show Category Carousel -------------------
    if user_message in greetings:
        category_list = [
            {"name": "fish-seafood 🐟", "image": "https://via.placeholder.com/1024x1024.png?text=Fish+Seafood", "data": "fish-seafood", "title":"ปลาเเละอาหารทะเล"},#img remove
            {"name": "meat 🍖", "image": "https://via.placeholder.com/1024x1024.png?text=Meat", "data": "meat", "title":"เนื้อสัตว์"},
            {"name": "fruit-vegetables 🍎", "image": "https://via.placeholder.com/1024x1024.png?text=Fruit+Vegetables", "data": "fruit-vegetables", "title":"ผลไม้เเละผัก"}
        ]


        carousel_columns = []
        for cat in category_list:
            carousel_columns.append(
                CarouselColumn(
                    thumbnail_image_url=cat["image"],
                    title=cat["name"][:40],
                    text=f"สิ้นค้าประเภท{cat['title']}",
                    actions=[PostbackAction(label="เลือกหมวดนี้", data=cat["data"])]
                )
            )

        template_message = TemplateSendMessage(
            alt_text="เลือกหมวดหมู่สินค้า",
            template=CarouselTemplate(columns=carousel_columns)
        )
        line_bot_api.reply_message(event.reply_token, template_message)
        return

    # ------------------- Keyword Search -------------------
    if current_menu_data:
        matched_items = [item for item in current_menu_data if user_message in item.get("name", "").lower()]
        if matched_items:
            carousel_columns = []
            for idx, item in enumerate(matched_items[:10]):
                name = item.get("name", "ไม่ระบุชื่อ")
                image_url = item.get("image") or "https://via.placeholder.com/1024x1024.png?text=No+Image"
                carousel_columns.append(
                    CarouselColumn(
                        thumbnail_image_url=image_url,
                        title=name[:40],
                        text=name[:60],
                        actions=[PostbackAction(label="รายละเอียดเพิ่มเติม", data=str(idx))]
                    )
                )
            template_message = TemplateSendMessage(
                alt_text="สินค้าที่คุณค้นหา",
                template=CarouselTemplate(columns=carousel_columns)
            )
            line_bot_api.reply_message(event.reply_token, template_message)
            return
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="⚠️ ไม่พบสินค้าที่ตรงกับชื่อที่คุณพิมพ์"))
            return

    # ------------------- Fallback -------------------
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"คุณพิมพ์: {user_message}"))

# ------------------- PostbackEvent Handler -------------------
@handler.add(PostbackEvent)
def handle_postback(event):
    global current_menu_data
    data = event.postback.data

    categories = ["fish-seafood", "meat", "fruit-vegetables"]

    # ------------------- User selects a category -------------------
    if data in categories:
        file_name = f"makro_{data}.json"
        if not os.path.exists(file_name):
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"⚠️ ไม่พบข้อมูลสำหรับหมวดหมู่ {data}"))
            return

        with open(file_name, encoding="utf-8") as f:
            current_menu_data = json.load(f)

        if not current_menu_data:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="⚠️ ไม่มีสินค้าที่จะแสดง"))
            return

        carousel_columns = []
        for idx, item in enumerate(current_menu_data[:10]):
            name = item.get("name", "ไม่ระบุชื่อ")
            image_url = item.get("image") or "https://via.placeholder.com/1024x1024.png?text=No+Image"
            carousel_columns.append(
                CarouselColumn(
                    thumbnail_image_url=image_url,
                    title=name[:40],
                    text=name[:60],
                    actions=[PostbackAction(label="รายละเอียดเพิ่มเติม", data=str(idx))]
                )
            )

        template_message = TemplateSendMessage(
            alt_text=f"สินค้าหมวด {data}",
            template=CarouselTemplate(columns=carousel_columns)
        )
        line_bot_api.reply_message(event.reply_token, template_message)
        return

    # ------------------- User selects a product -------------------
    if data.isdigit():
        idx = int(data)
        if idx >= len(current_menu_data):
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ ไม่พบข้อมูลสินค้า"))
            return

        product_url = current_menu_data[idx].get("link", "")
        product_info = scrape_product(product_url)

        if "error" in product_info:
            reply_text = product_info["error"]
        else:
            reply_text = (
                f"📦 ชื่อสินค้า: {product_info.get('name', '-')}\n"
                f"💰 ราคา: {product_info.get('price', '-')}\n"
                f"📏 น้ำหนักรวมสุทธิ:{product_info.get('size_quantity', '-')}\n"
                f"🔗 ลิงก์สินค้า: {product_info.get('url', '-')}"
            )

        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
        return

# ------------------- Run Flask -------------------
if __name__ == "__main__":
    app.run(port=5000, debug=True)
