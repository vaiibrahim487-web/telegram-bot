import os
import telebot
import google.generativeai as genai
import requests
from groq import Groq
from openai import OpenAI
import threading
import time
from datetime import datetime
import pytz

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-2.5-flash")
groq_client = Groq(api_key=GROQ_API_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

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
- কেউ কোনো account কিনতে চাইলে বা জিজ্ঞেস করলে বলো:
  আসসালামু আলাইকুম! আমি Ibrahim ভাইয়ের AI Assistant।
  আপনি যে account সম্পর্কে জানতে চাইছেন সেটা আমাদের কাছে পাওয়া যায়।
  তবে দাম ও বিস্তারিত তথ্য শুধু Ibrahim ভাই জানেন।
  সরাসরি মেসেজ করুন: @ibrahimbinshiraj786
  অথবা WhatsApp: 01811893375

উত্তর দেওয়ার নিয়ম:
- সব প্রশ্নের সুন্দর ও সঠিক বাংলায় উত্তর দাও
- কেউ Hi, হ্যালো, হাই বললে বলো: হ্যালো! আসসালামু আলাইকুম, কিভাবে সাহায্য করতে পারি?
- কেউ সাহায্য চাইলে বলো: হুম, বলুন! আমি আছি
- কেউ আসসালামু আলাইকুম বললে বলো: ওয়ালাইকুম আসসালাম! কিভাবে সাহায্য করতে পারি?
- সবসময় বিনয়ী, সহায়ক ও আন্তরিক থাকো
- যেকোনো বিষয়ে প্রশ্ন করলে সঠিক উত্তর দাও
- কেউ prompt চাইলে বলো: আমাদের Prompt চ্যানেল ভিজিট করুন: https://t.me/FreeAllPrompt
- এই গ্রুপের সবাই YouTuber, তাই YouTube সম্পর্কিত যেকোনো প্রশ্নের বিস্তারিত উত্তর দাও
- YouTube SEO, thumbnail, title, description, monetization, views বাড়ানো ইত্যাদি বিষয়ে expert পরামর্শ দাও
- সবাইকে YouTube এ সফল হতে উৎসাহিত করো, ইসলামিক দৃষ্টিভঙ্গিতে
"""

# ============================================================
# AI RESPONSE — Gemini → Groq → OpenAI Fallback
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

    try:
        now = datetime.now(BD_TZ)
        time_context = f"\n\n[বর্তমান সময়: {now.strftime('%Y-%m-%d %H:%M')} বাংলাদেশ সময়, সাল: {now.year}]"
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": OWNER_INFO + time_context},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Groq Error: {e}")

    try:
        now = datetime.now(BD_TZ)
        time_context = f"\n\n[বর্তমান সময়: {now.strftime('%Y-%m-%d %H:%M')} বাংলাদেশ সময়, সাল: {now.year}]"
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": OWNER_INFO + time_context},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI Error: {e}")

    return "দুঃখিত, এই মুহূর্তে উত্তর দিতে পারছি না। একটু পরে চেষ্টা করুন।"

# ============================================================
# নামাজের সময় API থেকে নেওয়া
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
    day_name = days[now.weekday()]
    month_name = months[now.month - 1]
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
        "day": day_name,
        "date": now.day,
        "month": month_name,
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
    period = dt["period"]
    hour = dt["hour"]
    day = dt["day"]
    date = dt["date"]
    month = dt["month"]
    year = dt["year"]

    header = f"🕐 {period} {hour}:00 | {day}, {date} {month} {year}\n➖➖➖➖➖➖➖➖➖➖\n\n"

    messages = {
        4:  "🌙 ভোর ৪টা!\n\nফজরের ওয়াক্ত হয়ে আসছে। উঠুন, অজু করুন! 💧\nআল্লাহর দরবারে হাজির হন। 🤲\n\n📹 সফল YouTuber রা ভোরে উঠে কাজ শুরু করেন। আপনিও পারবেন! 💪",
        5:  "🌅 ভোর ৫টা!\n\nফজর পড়েছেন? আলহামদুলিল্লাহ! 🤲\n\n📹 আজকের ভিডিওর আইডিয়া ভাবুন। সকালের মাথা সবচেয়ে creative! 💡",
        6:  "☀️ সকাল ৬টা!\n\nনতুন দিন, নতুন সুযোগ! আলহামদুলিল্লাহ 🌸\n\n📹 আজ কি নতুন ভিডিও আপলোড করবেন? Consistency-ই সাফল্যের চাবিকাঠি! 🔑",
        7:  "🍳 সকাল ৭টা!\n\nসকালের নাস্তা খেয়েছেন? বিসমিল্লাহ বলে খান! 😊\n\n📹 YouTube Studio খুলুন, analytics চেক করুন! 📊",
        8:  "💼 সকাল ৮টা!\n\nবিসমিল্লাহ বলে দিনের কাজ শুরু করুন! 💪\n\n📹 আজকের script লেখা শুরু করুন! ✍️",
        9:  "☕ সকাল ৯টা!\n\nআল্লাহকে স্মরণ করুন। সুবহানাল্লাহ! 🌸\n\n📹 Thumbnail নিয়ে কাজ করুন। ভালো thumbnail = বেশি views! 🎨",
        10: "🌞 সকাল ১০টা!\n\nআলহামদুলিল্লাহ! 😊\n\n📹 SEO করেছেন? Title, description, tags ঠিকমতো দিন! 🔍",
        11: "⏰ সকাল ১১টা!\n\nযোহরের নামাজের প্রস্তুতি নিন। 🕌\n\n📹 Video editing শেষ হলে একবার পুরোটা দেখুন! ✅",
        12: "🕛 দুপুর ১২টা!\n\nযোহরের ওয়াক্ত! নামাজ পড়ুন। 🕌🤲\n\n📹 নামাজের পর ভিডিও আপলোড দিন! 📈",
        13: "🍽️ দুপুর ১টা!\n\nদুপুরের খাবার খেয়েছেন? বিসমিল্লাহ! 😊\n\n📹 YouTube trends দেখুন। কোন topic hot? 🔥",
        14: "😴 দুপুর ২টা!\n\nকায়লুলা সুন্নত! একটু বিশ্রাম নিন। 🌙\n\n📹 ১৫-২০ মিনিট ঘুমান, তারপর energetic কাজ করুন! ⚡",
        15: "🌤️ বিকাল ৩টা!\n\nআসরের নামাজের সময়! 🕌🤲\n\n📹 Community post করুন! Algorithm ভালোবাসে! 💬",
        16: "☕ বিকাল ৪টা!\n\nবিকালের চা খেয়েছেন? 😊\n\n📹 Comment reply করুন! Subscribers loyal হয়। ❤️",
        17: "🌅 বিকাল ৫টা!\n\nমাগরিবের প্রস্তুতি নিন! 🕌\n\n📹 আজকের কাজের সারসংক্ষেপ করুন। 📝",
        18: "🌆 সন্ধ্যা ৬টা!\n\nমাগরিবের ওয়াক্ত! নামাজ পড়েছেন? 🕌🤲\n\n📹 নতুন ভিডিওর আইডিয়া note করুন! 💡",
        19: "🌙 রাত ৭টা!\n\nরাতের খাবার খান। পরিবারের সাথে থাকুন! 🏠\n\n📹 YouTube এর নতুন features দেখুন! 🔄",
        20: "⭐ রাত ৮টা!\n\nইশার নামাজের সময় হয়ে আসছে! 🕌🤲\n\n📹 রাতের কাজের plan করুন! 📋",
        21: "🌟 রাত ৯টা!\n\nইশার নামাজ পড়েছেন? আলহামদুলিল্লাহ! 🤲\n\n📹 শান্ত রাতে focused editing করুন! 🎬",
        22: "😴 রাত ১০টা!\n\nআয়াতুল কুরসি পড়ুন। ভালো ঘুম হোক! 🌙\n\n📹 আগামীকালের plan করুন! 📅",
        23: "🌙 রাত ১১টা!\n\nঘুমিয়ে পড়ুন! সুস্থ শরীর = ভালো content! 😊\n\n📹 Early to bed, early to rise! 🌅",
        0:  "🌃 রাত ১২টা!\n\nবিশ্রাম নিন। আল্লাহ হেফাজত করুন! 🤲\n\n📹 Fresh mind = Better content! 💪",
        1:  "🌌 রাত ১টা!\n\nতাহাজ্জুদের সময়! নামাজ পড়ুন। 🕌\n\n📹 আল্লাহর কাছে channel এর জন্য দোয়া করুন! 🤲",
        2:  "🌌 রাত ২টা!\n\nঘুমান, ফজরের alarm দিন! ⏰\n\n📹 Overwork করবেন না। 😊",
        3:  "🌙 রাত ৩টা!\n\nতাহাজ্জুদ পড়ুন! 🤲\n\n📹 Channel এর সাফল্যের দোয়া করুন! 🌙",
    }

    msg = messages.get(h, f"আল্লাহর রহমতে {period} {hour}টা। আল্লাহকে স্মরণ করুন! 🌸\n\n📹 কাজ চালিয়ে যান, সাফল্য আসবেই ইনশাআল্লাহ! 💪")
    return header + msg

# ============================================================
# নামাজের reminder
# ============================================================
def get_prayer_reminder(prayer_name):
    dt = get_bangla_datetime()
    header = f"📅 {dt['day']}, {dt['date']} {dt['month']} {dt['year']}\n➖➖➖➖➖➖➖➖➖➖\n\n"

    reminders = {
        "ফজর": "🌙 মাত্র ১০ মিনিট পরে ফজরের আজান!\n\n🛏️ উঠুন\n💧 অজু করুন\n🕌 নামাজ পড়ুন\n\nফজরের নামাজ জান্নাতের চাবিকাঠি! 🤲\n\n📹 ফজরের পর আজকের ভিডিওর আইডিয়া ভাবুন! 💡",
        "যোহর": "☀️ মাত্র ১০ মিনিট পরে যোহরের আজান!\n\n⏸️ কাজ থামান\n💧 অজু করুন\n🕌 নামাজ পড়ুন\n\nযোহর মিস করবেন না! 🤲\n\n📹 নামাজের পর fresh হয়ে editing করুন! ✂️",
        "আসর": "🌤️ মাত্র ১০ মিনিট পরে আসরের আজান!\n\n🕌 প্রস্তুত হন\n💧 অজু করুন\n🙏 নামাজ পড়ুন\n\nআসর অত্যন্ত গুরুত্বপূর্ণ! 🤲\n\n📹 আসরের পর community post করুন! 💬",
        "মাগরিব": "🌅 মাত্র ১০ মিনিট পরে মাগরিবের আজান!\n\n📵 কাজ রাখুন\n💧 অজু করুন\n🕌 নামাজ পড়ুন\n\nদেরি করবেন না! 🤲\n\n📹 মাগরিবের পর আজকের হিসাব করুন! 📊",
        "ইশা": "🌙 মাত্র ১০ মিনিট পরে ইশার আজান!\n\n🌟 রাতের শেষ ফরজ\n💧 অজু করুন\n🕌 নামাজ পড়ুন\n\nইশা = অর্ধেক রাত ইবাদতের সওয়াব! 🤲\n\n📹 ইশার পর focused editing করুন! 🎬"
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
                    msg = get_hourly_message()
                    bot.send_message(GROUP_CHAT_ID, msg)
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
                            msg = get_prayer_reminder(prayer)
                            bot.send_message(GROUP_CHAT_ID, msg)
                            last_prayer_reminded = reminder_key
                        except Exception as e:
                            print(f"Prayer error: {e}")

        time.sleep(30)

# ============================================================
# /setgroup
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
            f"এখন থেকে:\n"
            f"🕌 প্রতি নামাজের ১০ মিনিট আগে reminder\n"
            f"⏰ প্রতি ঘন্টায় message\n"
            f"📹 YouTube tips ও উৎসাহ\n\n"
            f"আল্লাহ সবার channel সফল করুন! 🤲"
        )
    else:
        bot.reply_to(msg, "⚠️ এই command শুধু গ্রুপে কাজ করবে!")

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
    response = get_ai_response(user_text)
    bot.reply_to(msg, response)

# ============================================================
# Welcome
# ============================================================
@bot.message_handler(content_types=['new_chat_members'])
def welcome(message):
    for user in message.new_chat_members:
        name = user.first_name
        bot.send_message(message.chat.id,
            f"আসসালামু আলাইকুম! 👋\n"
            f"স্বাগতম {name} ভাই/আপু! 🎉\n\n"
            f"আমরা সবাই YouTuber, ইসলামিক মূল্যবোধ নিয়ে চলি! 🌸\n\n"
            f"📢 https://t.me/FreeHelpNow786\n"
            f"🛒 @ibrahimbinshiraj786\n\n"
            f"আল্লাহ আপনার channel সফল করুন! 🤲"
        )

# ============================================================
# Blocked word check
# ============================================================
def contains_blocked_word(text):
    for word in BLOCKED_WORDS:
        if word in text:
            return True
    return False

# ============================================================
# Commands
# ============================================================
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
        response = requests.get(image_url, timeout=30)
        if response.status_code == 200:
            bot.send_photo(msg.chat.id, image_url, caption=f"🎨 {prompt}")
        else:
            bot.reply_to(msg, "দুঃখিত, ছবি তৈরি হয়নি।")
    except Exception as e:
        print(f"Image Error: {e}")
        bot.reply_to(msg, "দুঃখিত, ছবি তৈরি হয়নি।")

# ============================================================
# ✅ General message handler — ফিক্সড time keywords
# ============================================================
def is_time_question(text):
    """
    শুধুমাত্র সত্যিকারের সময়/তারিখ সংক্রান্ত প্রশ্ন detect করে।
    "বার" এর মতো common শব্দ বাদ দেওয়া হয়েছে।
    """
    text_lower = text.lower().strip()

    # সরাসরি সময় জিজ্ঞাসার প্যাটার্ন
    direct_patterns = [
        "এখন কয়টা", "এখন কটা", "এখন কত",
        "কয়টা বাজে", "কটা বাজে", "কত বাজে",
        "এখন সময়", "বর্তমান সময়", "সময় কত",
        "কত তারিখ", "আজ তারিখ", "আজকে তারিখ",
        "আজ কি বার", "আজকে কি বার", "কি বার আজ",
        "আজ কত", "আজকে কত", "কত সাল",
        "এখন কি সময়", "টাইম কত", "টাইম বলো",
        "সময় বলো", "তারিখ বলো", "ঘড়িতে কত",
        "what time", "current time", "what date",
    ]

    for pattern in direct_patterns:
        if pattern in text_lower:
            return True

    # শুধু একটি শব্দ হলে এবং সেটা সময়-সংক্রান্ত হলে
    single_word_triggers = ["টাইম", "ঘড়ি"]
    words = text_lower.split()
    if len(words) <= 3:
        for word in single_word_triggers:
            if word in text_lower:
                return True

    return False


@bot.message_handler(func=lambda msg: True)
def handle(msg):
    user_text = msg.text
    if not user_text:
        return

    if contains_blocked_word(user_text):
        bot.reply_to(msg, "⚠️ অনুগ্রহ করে ভদ্র ভাষা ব্যবহার করুন।")
        return

    # ✅ সময় জিজ্ঞেস করলে real time দেখাও
    if is_time_question(user_text):
        dt = get_bangla_datetime()
        bot.reply_to(msg,
            f"🕐 এখন {dt['period']} {dt['hour']}:{str(dt['minute']).zfill(2)}\n"
            f"📅 {dt['day']}, {dt['date']} {dt['month']} {dt['year']}\n"
            f"🌍 বাংলাদেশ সময় (ঢাকা)"
        )
        return

    # বাকি সব প্রশ্ন AI তে পাঠাও
    response = get_ai_response(user_text)
    bot.reply_to(msg, response)

# ============================================================
# Scheduler thread
# ============================================================
scheduler_thread = threading.Thread(target=scheduler, daemon=True)
scheduler_thread.start()

# ============================================================
# Bot polling
# ============================================================
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
