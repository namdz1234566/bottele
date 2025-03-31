import telebot
from telebot import types
import requests
import os

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Hoặc thay bằng chuỗi token của bạn
bot = telebot.TeleBot(TOKEN)

# Headers để check UID Facebook
FB_HEADERS = {
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': 'https://id.traodoisub.com',
    'referer': 'https://id.traodoisub.com/',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, như Gecko) Chrome/134.0.0.0 Mobile Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
}

# Lệnh /start - Hiển thị hướng dẫn
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "🤖 Chào mừng bạn! Nhập /menu để xem các chức năng.")

# Lệnh /menu - Hiển thị danh sách chức năng
@bot.message_handler(commands=['menu'])
def menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🔎 Check UID Facebook")
    btn2 = types.KeyboardButton("✅ Check Follow TikTok")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "📋 Chọn chức năng:", reply_markup=markup)

# Xử lý khi người dùng chọn chức năng từ menu
@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    if message.text == "🔎 Check UID Facebook":
        msg = bot.send_message(message.chat.id, "📌 Nhập link Facebook:")
        bot.register_next_step_handler(msg, check_facebook_uid)
    elif message.text == "✅ Check Follow TikTok":
        msg = bot.send_message(message.chat.id, "📌 Nhập username TikTok:")
        bot.register_next_step_handler(msg, check_follow_tiktok)

# Chức năng check UID Facebook
def check_facebook_uid(message):
    fb_link = message.text
    data = {'link': fb_link}
    response = requests.post('https://id.traodoisub.com/api.php', headers=FB_HEADERS, data=data)
    
    if response.status_code == 200:
        try:
            result = response.json()
            if 'id' in result:
                bot.send_message(message.chat.id, f"✅ Facebook ID: {result['id']}")
            else:
                bot.send_message(message.chat.id, "❌ Không tìm thấy ID.")
        except Exception as e:
            bot.send_message(message.chat.id, f"⚠️ Lỗi khi phân tích JSON: {e}")
    else:
        bot.send_message(message.chat.id, f"❌ Lỗi kết nối API: {response.status_code}")

# Chức năng check follow TikTok (dùng code bạn đã nhận trước đó)
def check_follow_tiktok(message):
    username = message.text
    tiktok_url = f"https://www.tiktok.com/@{username}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    response = requests.get(tiktok_url, headers=headers)

    if response.status_code == 200:
        if "followerCount" in response.text:
            follower_count = response.text.split('"followerCount":')[1].split(",")[0]
            bot.send_message(message.chat.id, f"✅ Người dùng **{username}** có **{follower_count}** followers trên TikTok.")
        else:
            bot.send_message(message.chat.id, "❌ Không tìm thấy thông tin follow.")
    else:
        bot.send_message(message.chat.id, f"❌ Lỗi kết nối TikTok: {response.status_code}")

# Chạy bot
bot.polling(none_stop=True)
