import os
import telebot
import google.generativeai as genai
import requests
import threading
import time
from datetime import datetime
import pytz

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-2.5-flash")

bot = telebot.TeleBot(BOT_TOKEN)

BLOCKED_WORDS = ["গালি", "অশ্লীল", "ফালতু", "খারাপ"]
BD_TZ = pytz.timezone("Asia/Dhaka")
GROUP_CHAT_ID = None

OWNER_INFO = """
তুমি Ibrahim ভাইয়ের AI Assistant Bot। তুমি সবসময় বাংলায় উত্তর দেবে।

👤 মালিকের তথ্য:
- নাম: Ibrahim Bin Shiraj
- Telegram: @ibrahimbinshiraj786
- WhatsApp ও বিকাশ: 01811893375

📺 YouTube চ্যানেল:
- Free Help Now: https://youtube.com/@freehelpnow786
- FHN Technology: https://youtube.com/@fhntechnology-786

📢 Telegram লিংক:
- চ্যানেল: https://t.me/FreeHelpNow786
- সাপোর্ট গ্রুপ: https://t.me/FreeHelpNowSupport
- প্রাইভেট গ্রুপ: https://t.me/+nTwI-7PBKBg0Zjg1
- সেলার গ্রুপ: https://t.me/Ytseller78
- Prompt চ্যানেল: https://t.me/FreeAllPrompt

🛒 একাউন্ট সার্ভিস:
- আমাদের কাছে যেসব premium account পাওয়া যায়:
  Alta, Grok, ChatGPT, CapCut, ElevenLabs, HeyGen সহ আরো অনেক কিছু
- কেউ কোনো account কিনতে চাইলে বলো:
  সরাসরি মেসেজ করুন: @ibrahimbinshiraj786
  অথবা WhatsApp: 01811893375

উত্তর দেওয়ার নিয়ম:
- সব প্রশ্নের সুন্দর ও সঠিক বাংলায় উত্তর দাও
- কেউ Hi বা হ্যালো বললে: হ্যালো! আসসালামু আলাইকুম, কিভাবে সাহায্য করতে পারি?
- কেউ আসসালামু আলাইকুম বললে: ওয়ালাইকুম আসসালাম! কিভাবে সাহায্য করতে পারি?
- সবসময় বিনয়ী, সহায়ক ও আন্তরিক থাকো
- কেউ prompt চাইলে: https://t.me/FreeAllPrompt
- YouTube SEO, thumbnail, monetization বিষয়ে expert পরামর্শ দাও
- সবাইকে YouTube এ সফল হতে উৎসাহিত করো, ইসলামিক দৃষ্টিভঙ্গিতে
"""

# ============================================================
# AI RESPONSE — শুধু Gemini
# ============================================================
def get_ai_response(prompt):
    try:
        now = datetime.now(BD_TZ)
        time_context = f"\n\n[বর্তমান সময়: {now.strftime('%Y-%m-%d %H:%M')} বাংলাদেশ সময়, সাল: {now.year}]"
        full_prompt = OWNER_INFO + time_context + "\n\nUser: " + prompt + "\n\nAssistant:"
        response = gemini_model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        print(f"Gemini Error: {e}")
        return "দুঃখিত, এই মুহূর্তে উত্তর দিতে পারছি না। একটু পরে চেষ্টা করুন।"

# ============================================================
# নামাজের সময় API
# ============================================================
def get_prayer_times():
    try:
        today = datetime.now(BD_TZ)
        url = f"https://api.aladhan.com/v1/timingsByCity?city=Dhaka&country=Bangladesh&method=1&date={today.strftime('%d-%m-%Y')}"
        response = requests.get(url, timeout=10)
        data = response.json()
        timings = data["data"]["timings"]
        return {
            "ফজর": timings["Fajr"],
            "যোহর": timings["Dhuhr"],
            "আসর": timings["Asr"],
            "মাগরিব": timings["Maghrib"],
            "ইশা": timings["Isha"]
        }
    except Exception as e:
        print(f"Prayer Time Error: {e}")
        return None

# ============================================================
# বাংলায় তারিখ ও সময়
# ============================================================
def get_bangla_datetime():
    now = datetime.now(BD_TZ)
    days = ["সোমবার", "মঙ্গলবার", "বুধবার", "বৃহস্পতিবার", "শুক্রবার", "শনিবার", "রবিবার"]
    months = ["জানুয়ারি", "ফেব্রুয়ারি", "মার্চ", "এপ্রিল", "মে", "জুন",
              "জুলাই", "আগস্ট", "সেপ্টেম্বর", "অক্টোবর", "নভেম্বর", "ডিসেম্বর"]
    hour = now.hour
    minute = now.minute
    if hour < 12:
        period = "সকাল"
    elif hour < 15:
        period = "দুপুর"
    elif hour < 18:
        period = "বিকাল"
    elif hour < 20:
        period = "সন্ধ্যা"
    else:
        period = "রাত"
    display_hour = hour if hour <= 12 else hour - 12
    if display_hour == 0:
        display_hour = 12
    return {
        "day": days[now.weekday()],
        "date": now.day,
        "month": months[now.month - 1],
        "year": now.year,
        "period": period,
        "hour": display_hour,
        "minute": minute,
        "hour24": hour
    }

# ============================================================
# প্রতি ঘন্টার message
# ============================================================
def get_hourly_message():
    dt = get_bangla_datetime()
    h = dt["hour24"]
    header = f"🕐 {dt['period']} {dt['hour']}:00 | {dt['day']}, {dt['date']} {dt['month']} {dt['year']}\n➖➖➖➖➖➖➖➖➖➖\n\n"
    messages = {
        4:  "🌙 ভোর ৪টা!\n\nফজরের ওয়াক্ত হয়ে আসছে। উঠুন, অজু করুন! 💧\n\n📹 সফল YouTuber রা ভোরে উঠে কাজ শুরু করেন। আপনিও পারবেন! 💪",
        5:  "🌅 ভোর ৫টা!\n\nফজর পড়েছেন? আলহামদুলিল্লাহ! 🤲\n\n📹 আজকের ভিডিওর আইডিয়া ভাবুন! 💡",
        6:  "☀️ সকাল ৬টা!\n\nনতুন দিন, নতুন সুযোগ! আলহামদুলিল্লাহ 🌸\n\n📹 Consistency-ই সাফল্যের চাবিকাঠি! 🔑",
        7:  "🍳 সকাল ৭টা!\n\nবিসমিল্লাহ বলে নাস্তা করুন! 😊\n\n📹 YouTube Studio খুলুন, analytics চেক করুন! 📊",
        8:  "💼 সকাল ৮টা!\n\nবিসমিল্লাহ বলে কাজ শুরু করুন! 💪\n\n📹 আজকের script লেখা শুরু করুন! ✍️",
        9:  "☕ সকাল ৯টা!\n\nসুবহানাল্লাহ! 🌸\n\n📹 ভালো thumbnail = বেশি views! 🎨",
        10: "🌞 সকাল ১০টা!\n\nআলহামদুলিল্লাহ! 😊\n\n📹 SEO করেছেন? Title, description, tags ঠিকমতো দিন! 🔍",
        11: "⏰ সকাল ১১টা!\n\nযোহরের প্রস্তুতি নিন। 🕌\n\n📹 Editing শেষে একবার পুরোটা দেখুন! ✅",
        12: "🕛 দুপুর ১২টা!\n\nযোহরের ওয়াক্ত! নামাজ পড়ুন। 🕌🤲\n\n📹 নামাজের পর ভিডিও আপলোড দিন! 📈",
        13: "🍽️ দুপুর ১টা!\n\nবিসমিল্লাহ বলে খাবার খান! 😊\n\n📹 YouTube trends দেখুন। কোন topic hot? 🔥",
        14: "😴 দুপুর ২টা!\n\nকায়লুলা সুন্নত! একটু বিশ্রাম নিন। 🌙\n\n📹 Fresh mind = Better content! ⚡",
        15: "🌤️ বিকাল ৩টা!\n\nআসরের নামাজের সময়! 🕌🤲\n\n📹 Community post করুন! 💬",
        16: "☕ বিকাল ৪টা!\n\n😊\n\n📹 Comment reply করুন! Subscribers loyal হয়। ❤️",
        17: "🌅 বিকাল ৫টা!\n\nমাগরিবের প্রস্তুতি নিন! 🕌\n\n📹 আজকের কাজের সারসংক্ষেপ করুন। 📝",
        18: "🌆 সন্ধ্যা ৬টা!\n\nমাগরিবের ওয়াক্ত! নামাজ পড়েছেন? 🕌🤲\n\n📹 নতুন ভিডিওর আইডিয়া note করুন! 💡",
        19: "🌙 রাত ৭টা!\n\nপরিবারের সাথে থাকুন! 🏠\n\n📹 YouTube এর নতুন features দেখুন! 🔄",
        20: "⭐ রাত ৮টা!\n\nইশার নামাজের সময় হয়ে আসছে! 🕌🤲\n\n📹 রাতের plan করুন! 📋",
        21: "🌟 রাত ৯টা!\n\nইশার নামাজ পড়েছেন? আলহামদুলিল্লাহ! 🤲\n\n📹 Focused editing করুন! 🎬",
        22: "😴 রাত ১০টা!\n\nআয়াতুল কুরসি পড়ুন। ভালো ঘুম হোক! 🌙\n\n📹 আগামীকালের plan করুন! 📅",
        23: "🌙 রাত ১১টা!\n\nঘুমিয়ে পড়ুন! 😊\n\n📹 Early to bed, early to rise! 🌅",
        0:  "🌃 রাত ১২টা!\n\nআল্লাহ হেফাজত করুন! 🤲\n\n📹 Fresh mind = Better content! 💪",
        1:  "🌌 রাত ১টা!\n\nতাহাজ্জুদের সময়! 🕌🤲",
        2:  "🌌 রাত ২টা!\n\nঘুমান, ফজরের alarm দিন! ⏰",
        3:  "🌙 রাত ৩টা!\n\nতাহাজ্জুদ পড়ুন! 🤲",
    }
    msg = messages.get(h, f"আল্লাহর রহমতে {dt['period']} {dt['hour']}টা। 🌸\n\n📹 কাজ চালিয়ে যান! 💪")
    return header + msg

# ============================================================
# নামাজের reminder
# ============================================================
def get_prayer_reminder(prayer_name):
    dt = get_bangla_datetime()
    header = f"📅 {dt['day']}, {dt['date']} {dt['month']} {dt['year']}\n➖➖➖➖➖➖➖➖➖➖\n\n"
    reminders = {
        "ফজর": "🌙 মাত্র ১০ মিনিট পরে ফজরের আজান!\n\n🛏️ উঠুন → 💧 অজু → 🕌 নামাজ\n\nফজরের নামাজ জান্নাতের চাবিকাঠি! 🤲",
        "যোহর": "☀️ মাত্র ১০ মিনিট পরে যোহরের আজান!\n\n⏸️ কাজ থামান → 💧 অজু → 🕌 নামাজ\n\nযোহর মিস করবেন না! 🤲",
        "আসর": "🌤️ মাত্র ১০ মিনিট পরে আসরের আজান!\n\n🕌 প্রস্তুত হন → 💧 অজু → 🙏 নামাজ\n\nআসর অত্যন্ত গুরুত্বপূর্ণ! 🤲",
        "মাগরিব": "🌅 মাত্র ১০ মিনিট পরে মাগরিবের আজান!\n\n📵 কাজ রাখুন → 💧 অজু → 🕌 নামাজ\n\nদেরি করবেন না! 🤲",
        "ইশা": "🌙 মাত্র ১০ মিনিট পরে ইশার আজান!\n\n🌟 রাতের শেষ ফরজ → 💧 অজু → 🕌 নামাজ\n\nইশা = অর্ধেক রাত ইবাদতের সওয়াব! 🤲"
    }
    return header + reminders.get(prayer_name, "")

# ============================================================
# Scheduler
# ============================================================
def scheduler():
    global GROUP_CHAT_ID
    last_hour_sent = -1
    last_prayer_reminded = ""
    while True:
        if GROUP_CHAT_ID:
            now = datetime.now(BD_TZ)
            current_hour = now.hour
            current_minute = now.minute
            if current_minute == 0 and current_hour != last_hour_sent:
                try:
                    bot.send_message(GROUP_CHAT_ID, get_hourly_message())
                    last_hour_sent = current_hour
                except Exception as e:
                    print(f"Hourly error: {e}")
            prayer_times = get_prayer_times()
            if prayer_times:
                for prayer, prayer_time in prayer_times.items():
                    p_hour, p_minute = map(int, prayer_time.split(":"))
                    reminder_minute = p_minute - 10
                    reminder_hour = p_hour
                    if reminder_minute < 0:
                        reminder_minute += 60
                        reminder_hour -= 1
                    reminder_key = f"{prayer}_{now.strftime('%Y-%m-%d')}"
                    if (current_hour == reminder_hour and
                            current_minute == reminder_minute and
                            last_prayer_reminded != reminder_key):
                        try:
                            bot.send_message(GROUP_CHAT_ID, get_prayer_reminder(prayer))
                            last_prayer_reminded = reminder_key
                        except Exception as e:
                            print(f"Prayer error: {e}")
        time.sleep(30)

# ============================================================
# Commands
# ============================================================
@bot.message_handler(commands=['setgroup'])
def set_group(msg):
    global GROUP_CHAT_ID
    if msg.chat.type in ['group', 'supergroup']:
        GROUP_CHAT_ID = msg.chat.id
        dt = get_bangla_datetime()
        bot.reply_to(msg,
            f"✅ গ্রুপ সেট হয়ে গেছে! আলহামদুলিল্লাহ!\n\n"
            f"📅 {dt['day']}, {dt['date']} {dt['month']} {dt['year']}\n"
            f"🕐 {dt['period']} {dt['hour']}:{str(dt['minute']).zfill(2)}\n\n"
            f"🕌 নামাজের ১০ মিনিট আগে reminder\n"
            f"⏰ প্রতি ঘন্টায় message চালু!\n\n"
            f"আল্লাহ সবার channel সফল করুন! 🤲"
        )
    else:
        bot.reply_to(msg, "⚠️ এই command শুধু গ্রুপে কাজ করবে!")

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg,
        "আসসালামু আলাইকুম! 👋\n\n"
        "আমি Free Help Now AI Assistant! 🤖\n\n"
        "✅ যেকোনো প্রশ্নের উত্তর\n"
        "🎨 /image — ছবি বানানো\n"
        "🕌 /setgroup — নামাজ reminder চালু\n"
        "📹 YouTube tips ও পরামর্শ\n"
        "🛒 Premium Account তথ্য\n\n"
        "আল্লাহ আপনার channel সফল করুন! 🤲"
    )

@bot.message_handler(commands=['help'])
def help_cmd(msg):
    bot.reply_to(msg,
        "🆘 সাহায্য মেনু:\n\n"
        "/start - বট শুরু\n"
        "/image - ছবি বানান\n"
        "/setgroup - গ্রুপ সেট করুন\n"
        "/account - একাউন্ট কিনুন\n"
        "/contact - যোগাযোগ\n"
        "/channel - আমাদের চ্যানেল\n\n"
        "সরাসরি যেকোনো প্রশ্ন করুন! 😊"
    )

@bot.message_handler(commands=['account'])
def account(msg):
    bot.reply_to(msg,
        "🛒 Premium Account:\n\n"
        "✅ Alta ✅ Grok ✅ ChatGPT\n"
        "✅ CapCut ✅ ElevenLabs ✅ HeyGen\n\n"
        "অর্ডার: @ibrahimbinshiraj786\n"
        "WhatsApp: 01811893375"
    )

@bot.message_handler(commands=['contact'])
def contact(msg):
    bot.reply_to(msg,
        "📞 যোগাযোগ:\n\n"
        "Telegram: @ibrahimbinshiraj786\n"
        "WhatsApp: 01811893375"
    )

@bot.message_handler(commands=['channel'])
def channel(msg):
    bot.reply_to(msg,
        "📢 চ্যানেল ও গ্রুপ:\n\n"
        "📺 https://youtube.com/@freehelpnow786\n"
        "📢 https://t.me/FreeHelpNow786\n"
        "📝 https://t.me/FreeAllPrompt\n"
        "🛒 https://t.me/+nTwI-7PBKBg0Zjg1"
    )

@bot.message_handler(commands=['image'])
def generate_image(msg):
    prompt = msg.text.replace('/image', '').strip()
    if not prompt:
        bot.reply_to(msg, "লিখুন: /image আপনার বিষয়\nযেমন: /image একটি সুন্দর মসজিদ")
        return
    bot.reply_to(msg, "⏳ ছবি তৈরি হচ্ছে...")
    try:
        image_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}"
        resp = requests.get(image_url, timeout=30)
        if resp.status_code == 200:
            bot.send_photo(msg.chat.id, image_url, caption=f"🎨 {prompt}")
        else:
            bot.reply_to(msg, "দুঃখিত, ছবি তৈরি হয়নি।")
    except Exception as e:
        print(f"Image Error: {e}")
        bot.reply_to(msg, "দুঃখিত, ছবি তৈরি হয়নি।")

# ============================================================
# Business handlers
# ============================================================
@bot.business_connection_handler(func=lambda connected: True)
def handle_business_connection(connected):
    print(f"Business connection: {connected}")

@bot.business_message_handler(func=lambda msg: True)
def handle_business_message(msg):
    user_text = msg.text
    if not user_text:
        return
    if contains_blocked_word(user_text):
        bot.reply_to(msg, "⚠️ অনুগ্রহ করে ভদ্র ভাষা ব্যবহার করুন।")
        return
    bot.reply_to(msg, get_ai_response(user_text))

# ============================================================
# Welcome
# ============================================================
@bot.message_handler(content_types=['new_chat_members'])
def welcome(message):
    for user in message.new_chat_members:
        bot.send_message(message.chat.id,
            f"আসসালামু আলাইকুম! 👋\n"
            f"স্বাগতম {user.first_name} ভাই/আপু! 🎉\n\n"
            f"আমরা সবাই YouTuber, ইসলামিক মূল্যবোধ নিয়ে চলি! 🌸\n\n"
            f"📢 https://t.me/FreeHelpNow786\n"
            f"🛒 @ibrahimbinshiraj786\n\n"
            f"আল্লাহ আপনার channel সফল করুন! 🤲"
        )

# ============================================================
# Blocked word check
# ============================================================
def contains_blocked_word(text):
    return any(word in text for word in BLOCKED_WORDS)

# ============================================================
# সময় প্রশ্ন detect — শুধু সরাসরি জিজ্ঞেসায়
# ============================================================
def is_time_question(text):
    text_lower = text.lower().strip()
    # exact phrase match — "তারিখে" বা "তারিখের" এ match হবে না
    direct_patterns = [
        "এখন কয়টা", "এখন কটা", "এখন কত বাজে",
        "কয়টা বাজে", "কটা বাজে", "কত বাজে",
        "এখন সময় কত", "বর্তমান সময়", "সময় কত",
        "আজ কত তারিখ", "আজকে কত তারিখ",
        "আজ কি বার", "আজকে কি বার",
        "কত সাল চলছে", "এখন কত সাল",
        "টাইম কত", "টাইম বলো", "সময় বলো",
        "what time", "current time",
    ]
    for pattern in direct_patterns:
        if pattern in text_lower:
            return True
    # ১-২ শব্দের ছোট মেসেজ, শুধু "টাইম" বা "ঘড়ি" থাকলে
    words = text.split()
    if len(words) <= 2 and any(w in text for w in ["টাইম", "ঘড়ি"]):
        return True
    return False

# ============================================================
# General message handler
# ============================================================
@bot.message_handler(func=lambda msg: True)
def handle(msg):
    user_text = msg.text
    if not user_text:
        return
    if contains_blocked_word(user_text):
        bot.reply_to(msg, "⚠️ অনুগ্রহ করে ভদ্র ভাষা ব্যবহার করুন।")
        return
    if is_time_question(user_text):
        dt = get_bangla_datetime()
        bot.reply_to(msg,
            f"🕐 এখন {dt['period']} {dt['hour']}:{str(dt['minute']).zfill(2)}\n"
            f"📅 {dt['day']}, {dt['date']} {dt['month']} {dt['year']}\n"
            f"🌍 বাংলাদেশ সময় (ঢাকা)"
        )
        return
    bot.reply_to(msg, get_ai_response(user_text))

# ============================================================
# Start scheduler & polling
# ============================================================
threading.Thread(target=scheduler, daemon=True).start()

bot.polling(
    none_stop=True,
    interval=0,
    timeout=20,
    allowed_updates=[
        "message",
        "business_message",
        "business_connection",
        "deleted_business_messages"
    ]
)
