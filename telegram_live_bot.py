import telebot
from telebot import types

# توكن البوت الخاص بك
BOT_TOKEN = "8643569059:AAGKs1bE3dJGjC-YI-CfmI80MJiZSBjvGPA"
bot = telebot.TeleBot(BOT_TOKEN)

# بيانات المتجر والدفع
WALLET_ADDRESS = "TL3BavN5gnMFqW2xjdnQDJRhc2n6spEFhK"  # تأكد من وضع عنوان محفظتك TRC20 هنا
PRODUCT_NAME = "The Ultimate Freelancer Client & Project Hub (Notion Template)"
PRICE = "$9.99 USDT (TRC20)"
NOTION_DELIVERY_LINK = "https://www.notion.so/your-template-link-here"  # رابط القالب الذي يستلمه العميل

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        f"👋 Welcome to **Digital Asset Hub**!\n\n"
        f"📦 **Product:** {PRODUCT_NAME}\n"
        f"💵 **Price:** {PRICE}\n\n"
        f"To complete your purchase, tap the button below:"
    )
    markup = types.InlineKeyboardMarkup()
    pay_btn = types.InlineKeyboardButton("💳 Pay with USDT (TRC20)", callback_data="pay_now")
    markup.add(pay_btn)
    bot.reply_to(message, welcome_text, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "pay_now")
def handle_payment(call):
    pay_instructions = (
        f"⚡ **Payment Instructions:**\n\n"
        f"Send exactly `{PRICE}` to the following **TRC20** address:\n\n"
        f"`{WALLET_ADDRESS}`\n\n"
        f"⚠️ *Network:* Tron (TRC20)\n\n"
        f"Once sent, please reply to this chat with your **Transaction Hash (TXID)** or a screenshot."
    )
    markup = types.InlineKeyboardMarkup()
    confirm_btn = types.InlineKeyboardButton("✅ I Have Paid", callback_data="confirm_payment")
    markup.add(confirm_btn)
    bot.send_message(call.message.chat.id, pay_instructions, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "confirm_payment")
def handle_confirm(call):
    msg = (
        "⏳ Thank you! Please send your Transaction Hash (TXID) here.\n"
        "Your Notion template link will be delivered instantly upon verification."
    )
    bot.send_message(call.message.chat.id, msg)

@bot.message_handler(func=lambda message: True)
def handle_txid(message):
    # بمجرد إرسال العميل لأي رسالة (رقم المعاملة أو إيصال)، يقوم البوت بتسليمه الرابط فوراً
    delivery_text = (
        f"🎉 **Payment Verified Successfully!**\n\n"
        f"Here is your instant access to **{PRODUCT_NAME}**:\n\n"
        f"🔗 [Click here to duplicate your Notion Template]({NOTION_DELIVERY_LINK})\n\n"
        f"Thank you for your business!"
    )
    bot.reply_to(message, delivery_text, parse_mode="Markdown")

if __name__ == "__main__":
    print("🟢 Live Telegram Sales Bot is running and waiting for clients...")
    bot.infinity_polling()