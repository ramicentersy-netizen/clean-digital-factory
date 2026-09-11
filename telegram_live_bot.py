import os
import json
import requests
import telebot
from telebot import types

# توكن البوت والمحفظة
BOT_TOKEN = "8643569059:AAGtNPhQRSt6_mGImHmazlL0zhrjpQ9q6nA"
MERCHANT_WALLET = "TL3BavN5gnMFqw2XjdnQDJRhc2n6spEFhK"
USDT_TRC20_CONTRACT = "TR7NHqjekqxGxTW8Pbm78528U7v282KmtV"
PROCESSED_TX_FILE = "processed_txids.json"

bot = telebot.TeleBot(BOT_TOKEN)

PRODUCTS = {
    "prod_finance_tracker_os": {
        "title": "Finance & Wealth Tracker OS (Notion Template)",
        "price_usd": "19.99",
        "template_url": "https://notion.so"  # ضع رابط القالب الفعلي هنا
    },
    "prod_mobile_repair_os_1788691000": {
        "title": "Mobile Repair & Store Management OS",
        "price_usd": "14.99",
        "template_url": "https://notion.so"
    }
}

user_sessions = {}

def is_tx_processed(txid):
    if not os.path.exists(PROCESSED_TX_FILE):
        return False
    try:
        with open(PROCESSED_TX_FILE, "r", encoding="utf-8") as f:
            records = json.load(f)
            return txid in records
    except Exception:
        return False

def mark_tx_processed(txid, pid, amount):
    records = {}
    if os.path.exists(PROCESSED_TX_FILE):
        try:
            with open(PROCESSED_TX_FILE, "r", encoding="utf-8") as f:
                records = json.load(f)
        except Exception:
            records = {}
    records[txid] = {"product_id": pid, "amount": amount}
    with open(PROCESSED_TX_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

def verify_tron_tx(txid, expected_usd):
    try:
        url = f"https://apilist.tronscanapi.com/api/transaction-info?hash={txid.strip()}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=12)
        if res.status_code != 200:
            return False, "Unable to query TRON network. Please try again shortly."
        
        data = res.json()
        if not data.get("confirmed", False):
            return False, "Transaction is not confirmed on blockchain yet. Please wait 1-2 minutes."

        trc20_transfers = data.get("trc20TransferInfo", [])
        if not trc20_transfers:
            return False, "No TRC20 transfer detected in this transaction hash."

        for transfer in trc20_transfers:
            to_addr = transfer.get("to_address", "")
            symbol = transfer.get("symbol", "")
            contract = transfer.get("contract_address", "")
            
            if to_addr.lower() == MERCHANT_WALLET.lower() and (symbol == "USDT" or contract == USDT_TRC20_CONTRACT):
                raw_amt = float(transfer.get("amount_str", 0))
                paid_amount = raw_amt / (10 ** int(transfer.get("decimals", 6)))
                if paid_amount >= (expected_usd - 0.5):
                    return True, paid_amount

        return False, "Payment mismatch or not sent to merchant wallet."
    except Exception as e:
        return False, f"Verification error: {str(e)}"

def send_invoice(chat_id, pid):
    prod = PRODUCTS.get(pid)
    if not prod:
        return
    user_sessions[chat_id] = pid
    price = prod["price_usd"]
    title = prod["title"]
    
    msg = (
        f"🛍️ Order Confirmation: {title}\n\n"
        f"💵 Amount Due: {price} USDT (TRC20)\n"
        f"📥 Official TRC20 Wallet:\n{MERCHANT_WALLET}\n\n"
        f"📌 Instructions:\n"
        f"1. Transfer the exact amount above.\n"
        f"2. Copy your transaction hash (TXID).\n"
        f"3. Send the TXID here for instant automated delivery!"
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Verify Transaction / إرسال الـ TXID", callback_data=f"verify_{pid}"))
    bot.send_message(chat_id, msg, reply_markup=markup)

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
            "👋 أهلاً بك في متجر المنتجات الرقمية!\nالرجاء اختيار القالب لإتمام الشراء والتسليم الفوري:",
            reply_markup=markup
        )
    except Exception as e:
        print(f"Error in handle_start: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def handle_buy_click(call):
    pid = call.data.replace("buy_", "")
    send_invoice(call.message.chat.id, pid)

@bot.callback_query_handler(func=lambda call: call.data.startswith("verify_"))
def prompt_txid(call):
    pid = call.data.replace("verify_", "")
    user_sessions[call.message.chat.id] = pid
    bot.send_message(call.message.chat.id, "✍️ أرسل الآن رمز المعاملة (TXID / Hash) الخاص بالتحويل:")

@bot.message_handler(func=lambda msg: len(msg.text.strip()) == 64)
def handle_txid(message):
    try:
        txid = message.text.strip()
        chat_id = message.chat.id
        pid = user_sessions.get(chat_id)

        if not pid or pid not in PRODUCTS:
            bot.send_message(chat_id, "⚠️ الرجاء اختيار المنتج أولاً قبل إرسال الـ TXID.")
            return

        if is_tx_processed(txid):
            bot.send_message(chat_id, "❌ تم استخدام رمز هذه المعاملة مسبقاً.")
            return

        prod = PRODUCTS[pid]
        price = float(prod["price_usd"])
        bot.send_message(chat_id, "🔍 جاري التحقق من شبكة البلوكشين (TRON)، يرجى الانتظار ثوانٍ...")

        ok, res = verify_tron_tx(txid, price)
        if ok:
            mark_tx_processed(txid, pid, res)
            template_url = prod["template_url"]
            success_msg = (
                f"🎉 تم تأكيد الدفع بنجاح!\n\n"
                f"📦 المنتج: {prod['title']}\n"
                f"💰 المبلغ المستلم: {res} USDT\n\n"
                f"🔗 رابط استلام القالب فوراً:\n{template_url}\n\n"
                f"شكراً لشرائك!"
            )
            bot.send_message(chat_id, success_msg)
        else:
            bot.send_message(chat_id, f"❌ فشل التحقق:\n{res}")
    except Exception as e:
        print(f"Error in handle_txid: {e}")

if __name__ == "__main__":
    print("🟢 Bot is starting polling loop...")
    bot.infinity_polling(skip_pending=True)
