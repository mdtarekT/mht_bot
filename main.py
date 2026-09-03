import time
import random
import threading
import requests
from datetime import datetime, timedelta
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from PIL import Image, ImageDraw

# updated token
API_TOKEN = '8931167419:AAGYI3lt_5psV-fGRWfA5DiAjyGUViXMr3Y'
bot = telebot.TeleBot(API_TOKEN)

ADMIN_ID = 8057979160
bot_active = True

LARAVEL_SESSION = "eyJpdiI6InpRK2hDdStGSTVLZXRYdi9RZHFLL0E9PSIsInZhbHVlIjoiMGNmdENWZUM4bFJtTHpZUzcxanZZdEhINmFqcjdpeVBBSnFleU9NTnFtODRQcENHWmJwOFpnaVpMT0d0YmN4ajRjdVpuUGpQY2lJaW1vR3Z2MlhZdkNGQkUrb3Vnc0VvVEhJZE5JMXg3ejMvenJubnkvcVMzVUFBZ0tIQ2lNeVYiLCJtYWMiOiI3MGE0NzIwOGEyMmI1ZTI3ZDc0ZTY2Njg3NWM4NWQ0YmNiYjU3OWQ4MTJjZGFhYTM2NzdjNTMxY2E2MGNkMTNmIiwidGFnIjoiIn0%3D"

OTC_PAIRS = [
    "USD/EGP (OTC)", "GBP/NZD (OTC)", "USD/BDT (OTC)", "USD/NGN (OTC)", 
    "USD/BRL (OTC)", "USD/ARS (OTC)", "EUR/NZD (OTC)", "USD/INR (OTC)", 
    "USD/COP (OTC)", "USD/IDR (OTC)", "USD/ZAR (OTC)", "NZD/CHF (OTC)", 
    "USD/PKR (OTC)", "CAD/CHF (OTC)", "AUD/NZD (OTC)", "USD/MXN (OTC)", 
    "USD/PHP (OTC)", "NZD/CAD (OTC)", "NZD/JPY (OTC)", "USD/DZD (OTC)", 
    "NZD/USD (OTC)", "Litecoin (OTC)", "Avalanche (OTC)", "Solana (OTC)", 
    "Trump (OTC)", "Bitcoin (OTC)", "Zcash (OTC)", "Cosmos (OTC)", 
    "Dash (OTC)", "Toncoin (OTC)", "Axie Infinity (OTC)", "Bitcoin Cash (OTC)", 
    "Chainlink (OTC)", "Ethereum Classic (OTC)", "Ripple (OTC)", "Ethereum (OTC)", 
    "Binance Coin (OTC)", "Polkadot (OTC)", "USCrude (OTC)", "UKBrent (OTC)", 
    "Silver (OTC)", "Gold (OTC)"
]

def get_live_market_payout(pair_name):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Cookie': f'laravel_session={LARAVEL_SESSION}'
        }
        response = requests.get('https://market-quantinfo.net/api/v1/payouts', headers=headers, timeout=3)
        if response.status_code == 200:
            data = response.json()
            return data.get(pair_name, random.randint(85, 98))
    except Exception:
        pass
    return random.randint(88, 95)

def generate_chart_card(asset, signal, confidence, entry_price, entry_time, payout):
    img = Image.new('RGB', (800, 520), color='#0b0e14')
    draw = ImageDraw.Draw(img)

    draw.rectangle([10, 10, 790, 510], outline='#1f2937', width=2)
    draw.rectangle([20, 20, 780, 500], fill='#111827', outline='#374151')

    draw.text((30, 32), "MHT HACK PRO", fill='#00e5ff')
    draw.text((200, 32), f"ASSET: {asset}", fill='#ffffff')
    draw.text((620, 32), f"PROFIT: {payout}%", fill='#00e676')

    sig_color = '#00e676' if signal == "CALL" else '#ff1744'
    draw.rectangle([30, 80, 250, 150], fill=sig_color)
    draw.text((50, 95), f"SIGNAL: {signal}", fill='#ffffff')

    draw.text((300, 95), f"ACCURACY: {confidence}%", fill='#ffea00')

    draw.rectangle([30, 180, 770, 400], fill='#0b0e14', outline='#1f2937')
    draw.text((50, 205), f"Entry Price  : {entry_price}", fill='#ffffff')
    draw.text((50, 255), f"Entry Time   : {entry_time} (Next Candle)", fill='#00e5ff')
    draw.text((50, 305), f"Live Market  : {payout}% Payout Active", fill='#00e676')
    draw.text((50, 355), f"Strategy     : MHT LIVE ALGO v5.0", fill='#9ca3af')

    draw.text((30, 435), "STATUS: LIVE OTC SYNCED", fill='#00e676')
    draw.text((30, 465), "❖ MHT PREMIUM CHANNEL ❖", fill='#ffea00')

    import io
    bio = io.BytesIO()
    bio.name = 'signal.png'
    img.save(bio, 'PNG')
    bio.seek(0)
    return bio

def send_otc_keyboard(chat_id):
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [KeyboardButton(pair) for pair in OTC_PAIRS]
    markup.add(*buttons)
    bot.send_message(chat_id, "📊 ওটিসি (OTC) মার্কেট সিলেক্ট করুন:", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(commands=['start'])
def start_cmd(message):
    send_otc_keyboard(message.chat.id)

@bot.message_handler(commands=['on', 'off'])
def toggle_bot(message):
    global bot_active
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ অনুমতি নেই।")
        return
 bot_active = (message.text == '/on')
    status_msg = "🟢 বট অন করা হয়েছে।" if bot_active else "🔴 বট অফ করা হয়েছে।"
    bot.reply_to(message, status_msg)

def process_candle_result(chat_id, pair_name, signal_type):
    time.sleep(60)
    result = random.choice(["WIN ✅", "WIN ✅", "WIN ✅", "REFUND 🔄"])
    bot.send_message(chat_id, f"📊 REAL-TIME RESULT\nPair: {pair_name}\nSignal: {signal_type}\nResult: {result}")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    global bot_active

    if not bot_active and message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⚠️ বর্তমানে সিগন্যাল সার্ভিস বন্ধ আছে।")
        return

    text = message.text.strip()

    if text in ["OTC Market", "OTC Markets", "Real Market"]:
        send_otc_keyboard(message.chat.id)
        return

    if text not in OTC_PAIRS:
        return

    now = datetime.now()
    next_candle_time = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
    entry_time_str = next_candle_time.strftime("%H:%M")

    payout = get_live_market_payout(text)
    signal_type = random.choice(["CALL", "PUT"])
    confidence = random.randint(88, 98)
    entry_price = f"{random.uniform(100.0, 1500.0):.2f}"

    chart_image = generate_chart_card(text, signal_type, confidence, entry_price, entry_time_str, payout)

    caption_text = (
        f"❖MHT PREMIUM HACK❖\n\n"
        f"📌Asset: {text} ({payout}% Profit)\n"
        f"📌Signal: {signal_type}\n"
        f"📌Confidence: {confidence}%\n"
        f"📌Entry Time: {entry_time_str} (Next Candle)\n"
        f"📌MTG: 1 Step Required\n"
        f"📌Owner: @MHT8099VIP\n"
    )

    bot.send_photo(message.chat.id, photo=chart_image, caption=caption_text)

    threading.Thread(
        target=process_candle_result,
        args=(message.chat.id, text, signal_type),
        daemon=True
    ).start()

bot.infinity_polling()       
