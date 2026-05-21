import os
import telebot
import google.generativeai as genai
import requests

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

bot = telebot.TeleBot(BOT_TOKEN)

BLOCKED_WORDS = ["গালি", "অশ্লীল", "বাজে", "ফালতু", "খারাপ"]

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
"""

@bot.message_handler(content_types=['new_chat_members'])
def welcome(message):
    for user in message.new_chat_members:
        name = user.first_name
        welcome_text = (
            f"আসসালামু আলাইকুম! 👋\n"
            f"স্বাগতম {name} ভাই/আপু! 🎉\n\n"
            f"আমাদের গ্রুপে আপনাকে স্বাগতম!\n\n"
            f"📢 চ্যানেল: https://t.me/FreeHelpNow786\n"
            f"📝 Prompt চ্যানেল: https://t.me/FreeAllPrompt\n"
            f"🛒 Account কিনতে: @ibrahimbinshiraj786\n"
            f"❓ যেকোনো প্রশ্ন করুন, আমি সাহায্য করব!"
        )
        bot.send_message(message.chat.id, welcome_text)

def contains_blocked_word(text):
    for word in BLOCKED_WORDS:
        if word in text:
            return True
    return False

@bot.message_handler(commands=['image'])
def generate_image(msg):
    prompt = msg.text.replace('/image', '').strip()
    if not prompt:
        bot.reply_to(msg, "ছবি বানাতে লিখুন: /image আপনার বিষয়\nযেমন: /image একটি সুন্দর মসজিদ")
        return
    bot.reply_to(msg, "⏳ ছবি তৈরি হচ্ছে, একটু অপেক্ষা করুন...")
    try:
        image_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}"
        response = requests.get(image_url, timeout=30)
        if response.status_code == 200:
            bot.send_photo(msg.chat.id, image_url, caption=f"🎨 {prompt}")
        else:
            bot.reply_to(msg, "দুঃখিত, ছবি তৈরি করা যায়নি। আবার চেষ্টা করুন।")
    except Exception as e:
        print(f"Image Error: {e}")
        bot.reply_to(msg, "দুঃখিত, ছবি তৈরি করা যায়নি। আবার চেষ্টা করুন।")

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, 
        "আসসালামু আলাইকুম! 👋\n\n"
        "আমি Free Help Now এর AI Assistant! 🤖\n\n"
        "আমি যা করতে পারি:\n"
        "✅ যেকোনো প্রশ্নের উত্তর দিতে পারি\n"
        "🎨 /image দিয়ে ছবি বানাতে পারি\n"
        "🛒 Premium Account সম্পর্কে তথ্য দিতে পারি\n\n"
        "📢 চ্যানেল: https://t.me/FreeHelpNow786\n"
        "📝 Prompt: https://t.me/FreeAllPrompt"
    )

@bot.message_handler(commands=['help'])
def help(msg):
    bot.reply_to(msg,
        "🆘 সাহায্য মেনু:\n\n"
        "/start - বট শুরু করুন\n"
        "/image - ছবি বানান\n"
        "/account - একাউন্ট কিনুন\n"
        "/contact - যোগাযোগ করুন\n"
        "/channel - আমাদের চ্যানেল\n\n"
        "অথবা সরাসরি যেকোনো প্রশ্ন করুন! 😊"
    )

@bot.message_handler(commands=['account'])
def account(msg):
    bot.reply_to(msg,
        "🛒 আমাদের Premium Account সমূহ:\n\n"
        "✅ Alta\n✅ Grok\n✅ ChatGPT\n✅ CapCut\n"
        "✅ ElevenLabs\n✅ HeyGen\n✅ আরো অনেক কিছু!\n\n"
        "অর্ডার করতে: @ibrahimbinshiraj786\n"
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
        "📢 আমাদের চ্যানেল ও গ্রুপ:\n\n"
        "📺 YouTube: https://youtube.com/@freehelpnow786\n"
        "📢 Telegram: https://t.me/FreeHelpNow786\n"
        "📝 Prompt: https://t.me/FreeAllPrompt\n"
        "🛒 Group: https://t.me/+nTwI-7PBKBg0Zjg1"
    )

@bot.message_handler(func=lambda msg: True)
def handle(msg):
    user_text = msg.text
    if not user_text:
        return

    if contains_blocked_word(user_text):
        bot.reply_to(msg, "⚠️ অনুগ্রহ করে ভদ্র ভাষা ব্যবহার করুন।")
        return

    try:
        full_prompt = OWNER_INFO + "\n\nUser: " + user_text + "\n\nAssistant:"
        response = model.generate_content(full_prompt)
        bot.reply_to(msg, response.text)
    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(msg, "দুঃখিত, এই মুহূর্তে উত্তর দিতে পারছি না। একটু পরে চেষ্টা করুন।")

bot.polling(none_stop=True, interval=0, timeout=20)
