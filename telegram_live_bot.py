import os
import json
import requests
import telebot
from telebot import types

BOT_TOKEN = "8643569059:AAGtNPhQRSt6_mGImHmazlL0zhrjpQ9q6nA"
MERCHANT_WALLET = "TL3BavN5gnMFqw2XjdnQDJRhc2n6spEFhK"
USDT_TRC20_CONTRACT = "TR7NHqjekqxGxTW8Pbm78528U7v282KmtV"
PROCESSED_TX_FILE = "processed_txids.json"

bot = telebot.TeleBot(BOT_TOKEN)

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
                except Exception:
                    pass
    return products

def is_tx_processed(txid):
    if not os.path.exists(PROCESSED_TX_FILE):
        return False
    with open(PROCESSED_TX_FILE, "r", encoding="utf-8") as f:
        try:
            records = json.load(f)
            return txid in records
        except Exception:
            return False

def mark_tx_processed(txid, pid, amount):
    records = {}
    if os.path.exists(PROCESSED_TX_FILE):
        with open(PROCESSED_TX_FILE, "r", encoding="utf-8") as f:
            try:
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

        verified = False
        paid_amount = 0.0
        for transfer in trc20_transfers:
            to_addr = transfer.get("to_address", "")
            symbol = transfer.get("symbol", "")
            contract = transfer.get("contract_address", "")
            
            if to_addr.lower() == MERCHANT_WALLET.lower() and (symbol == "USDT" or contract == USDT_TRC20_CONTRACT):
                raw_amt = float(transfer.get("amount_str", 0))
                paid_amount = raw_amt / (10 ** int(transfer.get("decimals", 6)))
                if paid_amount >= (expected_usd - 0.5):
                    verified = True
                    break

        if verified:
            return True, paid_amount
        else:
            return False, f"Payment mismatch. Expected: {expected_usd} USDT, Detected: {paid_amount} USDT to merchant wallet."
    except Exception as e:
        return False, f"Verification error: {str(e)}"

user_sessions = {}

@bot.message_handler(commands=["start"])
def handle_start(message):
    args = message.text.split()
    products = get_products()
    pid = args[1].strip() if len(args) > 1 else None

    if pid and pid in products:
        prod = products[pid]
        user_sessions[message.chat.id] = pid
        price = prod.get("price_usd", "0")
        title = prod.get("title", "Product")
        msg = (
            f"🛍️ *Order Confirmation: {title}*\n\n"
            f"💵 *Amount Due:* `{price} USDT` (TRC20)\n"
            f"📥 *Official TRC20 Wallet:*\n`{MERCHANT_WALLET}`\n\n"
            f"📌 *Instructions:*\n"
            f"1. Transfer the exact amount above.\n"
            f"2. Copy your transaction hash (**TXID**).\n"
            f"3. Send the TXID here for instant automated delivery!"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Verify Transaction / إرسال الـ TXID", callback_data=f"verify_{pid}"))
        bot.send_message(message.chat.id, msg, parse_mode="Markdown", reply_markup=markup)
    else:
        bot.send_message(
            message.chat.id,
            "👋 Welcome to the Digital Products Automated Delivery Bot!\n\nPlease select a product from our live storefront to proceed with purchase.",
            parse_mode="Markdown"
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith("verify_"))
def prompt_txid(call):
    pid = call.data.replace("verify_", "")
    user_sessions[call.message.chat.id] = pid
    bot.send_message(call.message.chat.id, "✍️ Please paste your TRC20 **TXID / Hash** here:", parse_mode="Markdown")

@bot.message_handler(func=lambda msg: len(msg.text.strip()) == 64)
def handle_txid(message):
    txid = message.text.strip()
    chat_id = message.chat.id
    pid = user_sessions.get(chat_id)

    products = get_products()
    if not pid or pid not in products:
        bot.send_message(chat_id, "⚠️ Please initiate an order by clicking 'Buy / Instant Access' from the storefront first.")
        return

    if is_tx_processed(txid):
        bot.send_message(chat_id, "❌ This transaction ID has already been redeemed.")
        return

    prod = products[pid]
    price = float(prod.get("price_usd", 19.99))
    bot.send_message(chat_id, "🔍 Verifying transaction on TRON blockchain, please hold on...")

    ok, res = verify_tron_tx(txid, price)
    if ok:
        mark_tx_processed(txid, pid, res)
        template_url = prod.get("template_url", "#")
        success_msg = (
            f"🎉 *Payment Confirmed Successfully!*\n\n"
            f"📦 *Product:* {prod.get('title')}\n"
            f"💰 *Received:* {res} USDT\n\n"
            f"🔗 *Instant Access Link:*\n[Click Here to Open & Duplicate Notion OS]({template_url})\n\n"
            f"Thank you for your purchase!"
        )
        bot.send_message(chat_id, success_msg, parse_mode="Markdown", disable_web_page_preview=False)
    else:
        bot.send_message(chat_id, f"❌ Verification Failed:\n{res}")

print("🟢 Starting Automated Payment Verification Telegram Bot...")
bot.infinity_polling(skip_pending=True)
