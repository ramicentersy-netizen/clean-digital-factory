import telebot
from telebot import types
import requests
import time

BOT_TOKEN = "8643569059:AAGKs1bE3dJGjC-YI-CfmI80MJiZSBjvGPA"
ADMIN_CHAT_ID = "658340386"  # حسابك الشخصي لاستلام الإشعارات
bot = telebot.TeleBot(BOT_TOKEN)

# إعدادات المحفظة والمنتج
WALLET_ADDRESS = "TL3BavN5gnMFqW2xjdnQDJRhc2n6spEFhK"
PRODUCT_NAME = "The Ultimate Freelancer Client & Project Hub (Notion Template)"
EXPECTED_AMOUNT = 9.99  # السعر بالـ USDT
NOTION_DELIVERY_LINK = "https://www.notion.so/your-template-link-here"

def send_admin_alert(text):
    """إرسال إشعار فوري لحساب الأدمن"""
    try:
        bot.send_message(ADMIN_CHAT_ID, text, parse_mode="Markdown")
    except Exception as e:
        print(f"⚠️ Admin alert error: {e}")

def verify_tron_tx(txid, target_wallet, expected_amount):
    """التحقق من صحة معاملة USDT TRC20 عبر TronScan API"""
    url = f"https://apilist.tronscanapi.com/api/transaction-info?hash={txid.strip()}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return False, "تعذر الاتصال بشبكة ترون حالياً، حاول مجدداً بعد لحظات."
        
        data = response.json()
        
        if not data.get("confirmed") or data.get("contractRet") != "SUCCESS":
            return False, "المعاملة غير مؤكدة أو فشلت على الشبكة."
        
        trc20_transfers = data.get("trc20TransferInfo", [])
        for transfer in trc20_transfers:
            recipient = transfer.get("to_address")
            symbol = transfer.get("symbol")
            amount_str = transfer.get("amount_str", "0")
            decimals = int(transfer.get("decimals", 6))
            actual_amount = float(amount_str) / (10 ** decimals)
            
            if recipient == target_wallet and symbol == "USDT":
                if actual_amount >= (expected_amount - 0.1):
                    return True, "تم التحقق بنجاح!"
                else:
                    return False, f"المبلغ المستلم ({actual_amount} USDT) أقل من المطلوب ({expected_amount} USDT)."
                    
        return False, "لم يتم العثور على تحويل USDT موجه إلى محفظة المتجر في هذه المعاملة."
    except Exception as e:
        return False, f"خطأ أثناء فحص المعاملة: {str(e)}"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user = message.from_user
    username = f"@{user.username}" if user.username else user.first_name
    
    # إشعار المدير بدخول عميل جديد
    send_admin_alert(f"👤 *عميل جديد دخل البوت!*\nالاسم: {user.first_name}\nاليوزر: {username}\nالآيدي: `{user.id}`")

    welcome_text = (
        f"👋 Welcome to **Digital Asset Hub**!\n\n"
        f"📦 **Product:** {PRODUCT_NAME}\n"
        f"💵 **Price:** ${EXPECTED_AMOUNT} USDT (TRC20)\n\n"
        f"To complete your purchase, click below:"
    )
    markup = types.InlineKeyboardMarkup()
    pay_btn = types.InlineKeyboardButton("💳 Pay with USDT (TRC20)", callback_data="pay_now")
    markup.add(pay_btn)
    bot.reply_to(message, welcome_text, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "pay_now")
def handle_payment(call):
    pay_instructions = (
        f"⚡ **Payment Instructions:**\n\n"
        f"Send exactly `{EXPECTED_AMOUNT} USDT` to this **TRC20** address:\n\n"
        f"`{WALLET_ADDRESS}`\n\n"
        f"⚠️ *Network:* Tron (TRC20)\n\n"
        f"Once sent, reply here with your **Transaction Hash (TXID)** to verify automatically."
    )
    markup = types.InlineKeyboardMarkup()
    confirm_btn = types.InlineKeyboardButton("✅ I Have Sent the Payment", callback_data="confirm_payment")
    markup.add(confirm_btn)
    bot.send_message(call.message.chat.id, pay_instructions, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "confirm_payment")
def handle_confirm(call):
    msg = (
        "🔍 Please paste your **Transaction Hash (TXID)** below.\n"
        "Our system will verify it on the Tron blockchain and send your Notion template link instantly."
    )
    bot.send_message(call.message.chat.id, msg)

@bot.message_handler(func=lambda message: True)
def handle_verification(message):
    txid = message.text.strip()
    user = message.from_user
    username = f"@{user.username}" if user.username else user.first_name

    if len(txid) < 50:
        bot.reply_to(message, "⚠️ This doesn't look like a valid Tron Transaction Hash (TXID). Please check and paste the full hash.")
        return

    verifying_msg = bot.reply_to(message, "⏳ Verifying transaction on the blockchain... Please wait 5 seconds.")
    
    is_valid, reason = verify_tron_tx(txid, WALLET_ADDRESS, EXPECTED_AMOUNT)
    
    if is_valid:
        delivery_text = (
            f"🎉 **Payment Verified Successfully!**\n\n"
            f"Here is your instant access to **{PRODUCT_NAME}**:\n\n"
            f"🔗 [Click here to duplicate your Notion Template]({NOTION_DELIVERY_LINK})\n\n"
            f"Thank you for your purchase!"
        )
        bot.edit_message_text(delivery_text, chat_id=message.chat.id, message_id=verifying_msg.message_id, parse_mode="Markdown")
        
        # إشعار المدير بإتمام عملية الشراء بنجاح واستلام المبلغ
        admin_sale_msg = (
            f"💰 *مبروك! عملية بيع جديدة ناجحة!*\n\n"
            f"👤 العميل: {username}\n"
            f"📦 المنتج: {PRODUCT_NAME}\n"
            f"💵 القيمة: ${EXPECTED_AMOUNT} USDT\n"
            f"🔗 الـ TXID:\n`{txid}`"
        )
        send_admin_alert(admin_sale_msg)
    else:
        failure_text = (
            f"❌ **Verification Failed:**\n"
            f"{reason}\n\n"
            f"Please ensure you entered the exact TXID and that the transaction is fully confirmed on TronScan."
        )
        bot.edit_message_text(failure_text, chat_id=message.chat.id, message_id=verifying_msg.message_id)

if __name__ == "__main__":
    print("🟢 Live Auto-Verifying Bot with Admin Alerts is running...")
    bot.infinity_polling()