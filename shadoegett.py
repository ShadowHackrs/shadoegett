import os
import telebot
import subprocess
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# Bot configuration
API_TOKEN = "7774560400:AAGwdc2hXa78GQsSKpbnmfktQaBaEugN2A0"
CHANNEL_USERNAME = "@ShadowHackr"  # Channel username
OWNER_ID = 972326806  # Your User ID as the bot owner

bot = telebot.TeleBot(API_TOKEN)

# Directory for downloads
DOWNLOAD_DIR = "downloads/"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def check_subscription(user_id):
    """Check if the user is subscribed to the channel or is the owner."""
    if user_id == OWNER_ID:
        return True  # Allow the owner to use the bot without restrictions
    try:
        status = bot.get_chat_member(CHANNEL_USERNAME, user_id).status
        return status in ["member", "administrator", "creator"]
    except Exception:
        return False

def download_content(url):
    """Download video or image in high quality using yt-dlp."""
    try:
        output_template = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
        command = [
            "yt-dlp", 
            "-o", output_template, 
            "--cookies", "cookies.txt",  # Use cookies if needed
            "-f", "best"  # Always download the best quality available
        ]
        command.append(url)
        subprocess.run(command, check=True)

        downloaded_files = [
            os.path.join(DOWNLOAD_DIR, f) for f in os.listdir(DOWNLOAD_DIR)
            if not f.endswith('.part')
        ]
        latest_file = max(downloaded_files, key=os.path.getctime)
        return latest_file
    except Exception as e:
        return f"Error: {e}"

@bot.message_handler(commands=["start", "help"])
def send_welcome(message: Message):
    """Send a welcome message and instructions."""
    if not check_subscription(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "⚠️ You must subscribe to our channel to use this bot.\n"
            f"Please subscribe here: {CHANNEL_USERNAME}",
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton("Subscribe", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}"),
                InlineKeyboardButton("Check Subscription", callback_data="check_sub")
            )
        )
        return

    bot.reply_to(
        message,
        "👋 Welcome to the bot!\n"
        "💡 Just send me a link to download videos or images in high quality.\n"
        f"© Powered by [ShadowHackr](https://www.shadowhackr.com)."
    )

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def handle_subscription_check(call):
    """Handle subscription check."""
    if check_subscription(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ You are subscribed!")
        bot.send_message(call.message.chat.id, "🎉 Thank you for subscribing! You can now use the bot.")
    else:
        bot.answer_callback_query(call.id, "❌ You are not subscribed.")
        bot.send_message(call.message.chat.id, "⚠️ Please subscribe to the channel to use this bot.")

@bot.message_handler(func=lambda message: True)
def handle_message(message: Message):
    """Handle incoming messages."""
    user_id = message.from_user.id

    if not check_subscription(user_id):
        bot.send_message(
            message.chat.id,
            "⚠️ You must subscribe to our channel to use this bot.\n"
            f"Please subscribe here: {CHANNEL_USERNAME}",
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton("Subscribe", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}"),
                InlineKeyboardButton("Check Subscription", callback_data="check_sub")
            )
        )
        return

    url = message.text.strip()
    if not url.startswith("http"):
        bot.reply_to(message, "❌ Please send a valid URL.")
        return

    bot.reply_to(message, "⏳ Downloading... Please wait.")
    downloaded_file = download_content(url)

    if downloaded_file.startswith("Error"):
        bot.send_message(message.chat.id, f"❌ Failed to download: {downloaded_file}")
    else:
        try:
            with open(downloaded_file, "rb") as file:
                bot.send_document(message.chat.id, file)
            bot.send_message(message.chat.id, "✅ Download complete!")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Error sending file: {e}")
        finally:
            if os.path.exists(downloaded_file):
                os.remove(downloaded_file)

if __name__ == "__main__":
    print("🤖 Bot is running...")
    bot.polling()
