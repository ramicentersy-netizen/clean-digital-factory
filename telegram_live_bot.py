import os
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
import telebot
from telebot import types

# 1. خادم فحص الصحة لمنصة Render (يعمل على بورت 10000)
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b"SystemFlow OS Bot is Healthy and Running 24/7!")

    def log_message(self, format, *args):
        return

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

BOT_TOKEN = "8643569059:AAGtNPhQRSt6_mGImHmazlL0zhrjpQ9q6nA"
MERCHANT_WALLET = "TL3BavN5gnMFqw2XjdnQDJRhc2n6spEFhK"
USDT_TRC20_CONTRACT = "TR7NHqjekqxGxTW8Pbm78528U7v282KmtV"
PROCESSED_TX_FILE = "processed_txids.json"

# إيقاف التعدد الملتبس في الخيوط لتثبيت الاستجابة محلياً
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

# 2. قراءة كتالوج المنتجات
def get_products():
    products = {}
    catalog_path = "products/generated_outputs"
    if os.path.exists(catalog_path):
        for f in os.listdir(catalog_path):
            if f.endswith(".json"):
                try:
                    with open(os.path.join(catalog_path, f), "r", encoding="utf-8-sig") as jf:
                        data = json.load(jf)
                        pid = data.get("product_id")
                        if pid:
                            products[pid] = data
                except Exception as e:
                    print(f"Error loading {f}: {e}")
    return products

# 3. المطابقة الذكية للمنتجات (Smart Matching)
def match_product(query_pid, products):
    if not query_pid:
        return None, None
    if query_pid in products:
        return query_pid, products[query_pid]
    
    q = str(query_pid).lower()
    for pid, data in products.items():
        p_str = (pid + " " + data.get("title", "")).lower()
        if "repair" in q and "repair" in p_str:
            return pid, data
        if "second_brain" in q and ("second_brain" in p_str or "second brain" in p_str):
            return pid, data
        if "finance" in q and "finance" in p_str:
            return pid, data
            
    for pid, data in products.items():
        if q in pid.lower():
            return pid, data
    return None, None

user_sessions = {}

# 4. إرسال بطاقة الفاتورة الرسمية باللغة الإنجليزية
def send_invoice(chat_id, actual_pid, prod):
    user_sessions[chat_id] = actual_pid
    price = prod.get("price_usd", "0")
    title = prod.get("title", "Product")
    
    msg = (
        f"🛍️ Order Confirmation: {title}\n\n"
        f"💵 Amount Due: {price} USDT (TRC20)\n"
        f"📥 Official TRC20 Wallet:\n"
        f"`{MERCHANT_WALLET}`\n\n"
        f"📌 Instructions:\n"
        f"1. Transfer the exact amount above.\n"
        f"2. Copy your transaction hash (TXID).\n"
        f"3. Send the TXID here for instant automated delivery!"
    )
    # Inline button
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("⚡ Verify Transaction / Submit TXID", callback_data="btn_verify"))
    bot.send_message(chat_id, msg, parse_mode="Markdown", reply_markup=markup)
    print(f"--> [OK] Invoice delivered to {chat_id} for: {title}")

# 5. معالجة أمر /start وإرسال أزرار Inline وأزرار الكيبورد المباشرة
@bot.message_handler(commands=["start"])
def handle_start(message):
    try:
        chat_id = message.chat.id
        args = message.text.split()
        products = get_products()
        query_pid = args[1].strip() if len(args) > 1 else None

        actual_pid, prod = match_product(query_pid, products)
        if prod:
            send_invoice(chat_id, actual_pid, prod)
        else:
            # Inline Keyboard
            inline_kb = types.InlineKeyboardMarkup(row_width=1)
            inline_kb.add(
                types.InlineKeyboardButton("🛒 Finance & Wealth Tracker OS ($19.99)", callback_data="buy_finance"),
                types.InlineKeyboardButton("🛒 Mobile Repair & Store Management OS ($14.99)", callback_data="buy_repair"),
                types.InlineKeyboardButton("🛒 Ultimate Second Brain OS ($19.99)", callback_data="buy_second_brain")
            )
            
            # Reply Keyboard (كيبورد شات مضمون بنسبة 100% ولا يعلق أبداً)
            reply_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
            reply_kb.add(types.KeyboardButton("🛠️ Mobile Repair OS ($14.99)"))
            reply_kb.add(types.KeyboardButton("💰 Finance & Wealth Tracker ($19.99)"))
            reply_kb.add(types.KeyboardButton("🧠 Ultimate Second Brain ($19.99)"))

            welcome_text = (
                "👋 Welcome to the Digital Products Store!\n\n"
                "Please select a template below to view the invoice and proceed with instant delivery:"
            )
            bot.send_message(chat_id, welcome_text, reply_markup=inline_kb)
            bot.send_message(chat_id, "👇 Or tap any item from the menu below:", reply_markup=reply_kb)
            print(f"--> [OK] Storefront menu sent to {chat_id}")
    except Exception as e:
        print(f"Error in /start: {e}")

# 6. معالج أزرار الكيبورد العادية (Reply Buttons) - مضمون وفوري
@bot.message_handler(func=lambda msg: any(k in msg.text for k in ["Mobile Repair", "Finance", "Second Brain"]))
def handle_menu_text_selection(message):
    chat_id = message.chat.id
    text = message.text.lower()
    products = get_products()

    if "repair" in text:
        actual_pid, prod = match_product("repair", products)
    elif "finance" in text:
        actual_pid, prod = match_product("finance", products)
    elif "second" in text or "brain" in text:
        actual_pid, prod = match_product("second_brain", products)
    else:
        actual_pid, prod = None, None

    if prod:
        send_invoice(chat_id, actual_pid, prod)
    else:
        bot.send_message(chat_id, "⚠️ Product spec not found.")

# 7. معالج أحداث الـ Inline Callbacks المباشر
@bot.callback_query_handler(func=lambda call: True)
def handle_inline_clicks(call):
    chat_id = call.message.chat.id
    data = str(call.data)
    print(f"--> [CLICK] Received callback data: {data} from user {chat_id}")

    try:
        bot.answer_callback_query(call.id, text="Loading...")
    except Exception as e:
        print(f"Callback answer warning: {e}")

    products = get_products()

    if data == "btn_verify":
        bot.send_message(chat_id, "✍️ Please paste your 64-character TRC20 transaction hash (TXID) below:")
    elif data == "buy_finance":
        actual_pid, prod = match_product("finance", products)
        if prod:
            send_invoice(chat_id, actual_pid, prod)
    elif data == "buy_repair":
        actual_pid, prod = match_product("repair", products)
        if prod:
            send_invoice(chat_id, actual_pid, prod)
    elif data == "buy_second_brain":
        actual_pid, prod = match_product("second_brain", products)
        if prod:
            send_invoice(chat_id, actual_pid, prod)

# 8. منع الإنفاق المزدوج والتحقق من المعاملات
def is_tx_processed(txid):
    if not os.path.exists(PROCESSED_TX_FILE):
        return False
    try:
        with open(PROCESSED_TX_FILE, "r", encoding="utf-8") as f:
            return txid in json.load(f)
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
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=12)
        if res.status_code != 200:
            return False, "Unable to reach TRON blockchain. Please try again in a few moments."
        
        data = res.json()
        if not data.get("confirmed", False):
            return False, "Transaction is still confirming on the blockchain. Please wait 1 minute and re-send."

        for transfer in data.get("trc20TransferInfo", []):
            to_addr = transfer.get("to_address", "")
            symbol = transfer.get("symbol", "")
            contract = transfer.get("contract_address", "")
            
            if to_addr.lower() == MERCHANT_WALLET.lower() and (symbol == "USDT" or contract == USDT_TRC20_CONTRACT):
                paid_amount = float(transfer.get("amount_str", 0)) / (10 ** int(transfer.get("decimals", 6)))
                if paid_amount >= (expected_usd - 0.5):
                    return True, paid_amount

        return False, f"Payment mismatch. Expected: {expected_usd} USDT to merchant wallet."
    except Exception as e:
        return False, f"Blockchain verification error: {str(e)}"

# 9. استقبال وفحص الـ TXID
@bot.message_handler(func=lambda msg: len(msg.text.strip()) == 64)
def handle_txid_input(message):
    try:
        chat_id = message.chat.id
        txid = message.text.strip()
        pid = user_sessions.get(chat_id)
        products = get_products()

        if not pid or pid not in products:
            for p in products:
                if "repair" in p.lower():
                    pid = p
                    break

        if is_tx_processed(txid):
            bot.send_message(chat_id, "❌ This transaction hash has already been redeemed.")
            return

        prod = products.get(pid, {})
        price = float(prod.get("price_usd", 14.99))

        bot.send_message(chat_id, "🔍 Verifying transaction on TRON blockchain, please hold on...")
        ok, res = verify_tron_tx(txid, price)

        if ok:
            mark_tx_processed(txid, pid, res)
            template_url = prod.get("template_url", "https://notion.so")
            success_msg = (
                f"🎉 **Payment Confirmed Successfully!**\n\n"
                f"📦 **Product:** {prod.get('title')}\n"
                f"💰 **Amount Received:** {res} USDT\n\n"
                f"🔗 **Instant Access Link (Notion):**\n{template_url}\n\n"
                f"Thank you for your purchase!"
            )
            bot.send_message(chat_id, success_msg, parse_mode="Markdown")
        else:
            bot.send_message(chat_id, f"❌ **Verification Failed:**\n{res}")
    except Exception as e:
        print(f"Error in handle_txid: {e}")

if __name__ == "__main__":
    # تشغيل خادم الصحة لمنصة Render
    threading.Thread(target=run_health_server, daemon=True).start()
    print("🟢 Render Health server active on port 10000...")
    print("🟢 Bot engine is LIVE with Dual-Keyboard mode (Inline + Reply)...")
    bot.infinity_polling(skip_pending=True, timeout=20)