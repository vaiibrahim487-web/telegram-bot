import os
import telebot
import google.generativeai as genai

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
            f"🛒 account কিনতে: @ibrahimbinshiraj786\n"
            f"❓ যেকোনো প্রশ্ন করুন, আমি সাহায্য করব!"
        )
        bot.send_message(message.chat.id, welcome_text)

def contains_blocked_word(text):
    for word in BLOCKED_WORDS:
        if word in text:
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

    try:
        full_prompt = OWNER_INFO + "\n\nUser: " + user_text + "\n\nAssistant:"
        response = model.generate_content(full_prompt)
        bot.reply_to(msg, response.text)
    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(msg, "দুঃখিত, এই মুহূর্তে উত্তর দিতে পারছি না। একটু পরে চেষ্টা করুন।")

bot.polling(none_stop=True, interval=0, timeout=20)
