import os
import time
import json
import requests
import telebot
from telebot import types

BOT_TOKEN = "8643569059:AAGtNPhQRSt6_mGImHmazlL0zhrjpQ9q6nA"
MERCHANT_WALLET = "TL3BavN5gnMFqw2XjdnQDJRhc2n6spEFhK"
USDT_TRC20_CONTRACT = "TR7NHqjekqxGxTW8Pbm78528U7v282KmtV"
PROCESSED_TX_FILE = "processed_txids.json"

bot = telebot.TeleBot(BOT_TOKEN)

PRODUCTS = {
    "prod_finance_tracker_os": {
        "title": "Finance & Wealth Tracker OS (Notion Template)",
        "price_usd": 19.99,
        "template_url": "https://meadow-cork-ca9.notion.site/Finance-Wealth-Tracker-OS-3d75f716ea9d8030b2d4c89a06d96d60?source=copy_link"
    },
    "prod_mobile_repair_os_1788691000": {
        "title": "Mobile Repair & Store Management OS",
        "price_usd": 14.99,
        "template_url": "https://notion.so"
    }
}

def load_processed_txids():
    if not os.path.exists(PROCESSED_TX_FILE):
        return {}
    try:
        with open(PROCESSED_TX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_processed_txid(txid, pid, amount):
    records = load_processed_txids()
    records[txid] = {"product_id": pid, "amount": amount, "timestamp": time.time()}
    with open(PROCESSED_TX_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

def check_wallet_for_payment(expected_amount):
    """البحث في محفظة المتجر عن أي تحويل حديث بالمبلغ المطلوب"""
    try:
        url = f"https://apilist.tronscanapi.com/api/transfer/trc20?address={MERCHANT_WALLET}&trc20Id={USDT_TRC20_CONTRACT}&limit=10&direction=1"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        
        if res.status_code != 200:
            return False, "تعذر فحص الشبكة حالياً، يرجى المحاولة بعد قليل."
            
        data = res.json()
        transfers = data.get("data", [])
        processed = load_processed_txids()
        current_time_ms = int(time.time() * 1000)

        for tx in transfers:
            tx_hash = tx.get("transaction_id", "")
            confirmed = tx.get("confirmed", False)
            timestamp = tx.get("block_timestamp", 0)
            
            # فحص التحويلات في آخر 45 دقيقة
            is_recent = (current_time_ms - timestamp) <= (45 * 60 * 1000)
            
            if tx_hash in processed:
                continue
                
            raw_amt = float(tx.get("amount", 0))
            decimals = int(tx.get("decimals", 6))
            paid_amount = raw_amt / (10 ** decimals)

            # مطابقة المبلغ وعنوان الاستلام
            if abs(paid_amount - expected_amount) <= 0.5 and is_recent and confirmed:
                return True, {"txid": tx_hash, "amount": paid_amount}

        return False, "لم يتم العثور على تحويل جديد مطابق للمبلغ بعد. يرجى الانتظار دقيقة حتى تؤكد الشبكة العملية ثم الضغط مرة أخرى."
    except Exception as e:
        return False, f"خطأ أثناء الفحص: {str(e)}"

def send_invoice(chat_id, pid):
    prod = PRODUCTS.get(pid)
    if not prod:
        return
    price = prod["price_usd"]
    title = prod["title"]
    
    msg = (
        f"🛍️ **طلب شراء:** {title}\n\n"
        f"💵 **المبلغ المطلوب:** `{price} USDT` (شبكة TRC20)\n"
        f"📥 **عنوان المحفظة:**\n`{MERCHANT_WALLET}`\n\n"
        f"⚡ **طريقة الاستلام:**\n"
        f"1. حوّل المبلغ إلى العنوان أعلاه.\n"
        f"2. اضغط على الزر أدناه فور إتمام التحويل لتسليم القالب تلقائياً!"
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ تم التحويل، تحقق وسلّمني القالب", callback_data=f"check_{pid}"))
    bot.send_message(chat_id, msg, reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(commands=["start"])
def handle_start(message):
    try:
        parts = message.text.split()
        if len(parts) > 1:
            pid = parts[1].strip()
            if pid in PRODUCTS:
                send_invoice(message.chat.id, pid)
                return

        markup = types.InlineKeyboardMarkup()
        for pid, data in PRODUCTS.items():
            markup.add(types.InlineKeyboardButton(f"🛒 {data['title']} (${data['price_usd']})", callback_data=f"buy_{pid}"))
        
        bot.send_message(
            message.chat.id,
            "👋 أهلاً بك! اختر القالب للمتابعة واستلام رابط التحميل فوراً:",
            reply_markup=markup
        )
    except Exception as e:
        print(f"Error: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def handle_buy_click(call):
    pid = call.data.replace("buy_", "")
    send_invoice(call.message.chat.id, pid)

@bot.callback_query_handler(func=lambda call: call.data.startswith("check_"))
def handle_auto_check(call):
    pid = call.data.replace("check_", "")
    prod = PRODUCTS.get(pid)
    if not prod:
        return

    bot.answer_callback_query(call.id, text="🔍 جاري فحص المحفظة على البلوكشين...")
    bot.send_message(call.message.chat.id, "⏳ جاري التأكد من وصول الحوالة إلى المحفظة، يرجى الانتظار بضع ثوانٍ...")

    ok, res = check_wallet_for_payment(prod["price_usd"])
    if ok:
        save_processed_txid(res["txid"], pid, res["amount"])
        success_msg = (
            f"🎉 **تم استلام الدفعة بنجاح!**\n\n"
            f"📦 **المنتج:** {prod['title']}\n"
            f"💰 **المبلغ المستلم:** {res['amount']} USDT\n\n"
            f"🔗 **رابط القالب الخاص بك:**\n{prod['template_url']}\n\n"
            f"نتمنى لك تجربة ممتعة ومفيدة!"
        )
        bot.send_message(call.message.chat.id, success_msg, parse_mode="Markdown")
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔄 إعادة المحاولة الآن", callback_data=f"check_{pid}"))
        bot.send_message(call.message.chat.id, f"⚠️ {res}", reply_markup=markup)

if __name__ == "__main__":
    print("🟢 Bot is running with one-click verification...")
    bot.infinity_polling(skip_pending=True)
