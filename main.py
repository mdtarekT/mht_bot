import time
import random
import threading
from datetime import datetime, timedelta
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from PIL import Image, ImageDraw

API_TOKEN = '8931167419:AAGYI3lt_5psV-fGRWfA5DiAjyGUViXMr3Y'
bot = telebot.TeleBot(API_TOKEN)

ADMIN_ID = 8057979160
bot_active = True

# স্ক্রিনশটের সব রিয়েল মার্কেট (Real Markets)
REAL_PAIRS = [
    "EUR/JPY", "GBP/USD", "USD/JPY", "AUD/CAD", 
    "EUR/USD", "CAD/JPY", "EUR/GBP", "AUD/JPY", 
    "AUD/USD", "EUR/CHF", "CHF/JPY", "GBP/CHF", 
    "GBP/JPY", "EUR/AUD", "EUR/CAD", "USD/CAD"
]

# স্ক্রিনশটের সব ওটিসি মার্কেট (OTC Markets: Currencies, Crypto, Commodities)
OTC_PAIRS = [
    # Currencies (OTC)
    "USD/EGP (OTC)", "GBP/NZD (OTC)", "USD/BDT (OTC)", "USD/NGN (OTC)", 
    "USD/BRL (OTC)", "USD/ARS (OTC)", "EUR/NZD (OTC)", "USD/INR (OTC)", 
    "USD/COP (OTC)", "USD/IDR (OTC)", "USD/ZAR (OTC)", "NZD/CHF (OTC)", 
    "USD/PKR (OTC)", "CAD/CHF (OTC)", "AUD/NZD (OTC)", "USD/MXN (OTC)", 
    "USD/PHP (OTC)", "NZD/CAD (OTC)", "NZD/JPY (OTC)", "USD/DZD (OTC)", 
    "NZD/USD (OTC)",

    # Crypto (OTC)
    "Litecoin (OTC)", "Avalanche (OTC)", "Solana (OTC)", "Trump (OTC)", 
    "Bitcoin (OTC)", "Zcash (OTC)", "Cosmos (OTC)", "Dash (OTC)", 
    "Toncoin (OTC)", "Axie Infinity (OTC)", "Bitcoin Cash (OTC)", "Chainlink (OTC)", 
    "Ethereum Classic (OTC)", "Ripple (OTC)", "Ethereum (OTC)", "Binance Coin (OTC)", 
    "Polkadot (OTC)",

    # Commodities (OTC)
    "USCrude (OTC)", "UKBrent (OTC)", "Silver (OTC)", "Gold (OTC)"
]

# ডায়নামিক সিগন্যাল কার্ড জেনারেটর
def generate_chart_card(asset, signal, confidence, entry_price, entry_time):
    img = Image.new('RGB', (800, 500), color='#0b0e14')
    draw = ImageDraw.Draw(img)

    draw.rectangle([10, 10, 790, 490], outline='#1f2937', width=2)
    draw.rectangle([20, 20, 780, 480], fill='#111827', outline='#374151')

    draw.text((30, 32), "MHT HACK PRO", fill='#00e5ff')
    draw.text((200, 32), f"ASSET: {asset}", fill='#ffffff')

    sig_color = '#00e676' if signal == "CALL" else '#ff1744'
    draw.rectangle([30, 80, 250, 150], fill=sig_color)
    draw.text((50, 95), f"SIGNAL: {signal}", fill='#ffffff')

    draw.text((300, 95), f"ACCURACY: {confidence}%", fill='#ffea00')

    draw.rectangle([30, 180, 770, 380], fill='#0b0e14', outline='#1f2937')
    draw.text((50, 200), f"Entry Price : {entry_price}", fill='#ffffff')
    draw.text((50, 250), f"Entry Time  : {entry_time} (Next Candle)", fill='#00e5ff')
    draw.text((50, 300), f"Strategy    : MHT VIP ALGO v4.2", fill='#9ca3af')

    draw.text((30, 420), "STATUS: LIVE SIGNAL GENERATED", fill='#00e676')
    draw.text((30, 445), "❖ MHT PREMIUM CHANNEL ❖", fill='#ffea00')

    import io
    bio = io.BytesIO()
    bio.name = 'signal.png'
    img.save(bio, 'PNG')
    bio.seek(0)
    return bio

# /start কমান্ড হ্যান্ডলার
@bot.message_handler(commands=['start'])
def start_cmd(message):
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_real = KeyboardButton("📈 Real Market")
    btn_otc = KeyboardButton("🌀 OTC Market")
    markup.add(btn_real, btn_otc)
    bot.send_message(message.chat.id, "👋 MHT VIP Bot-এ স্বাগতম!\n\nমার্কেট টাইপ বেছে নিন:", reply_markup=markup, parse_mode="Markdown")

# অ্যাডমিন কন্ট্রোল কমান্ড (/on এবং /off)
@bot.message_handler(commands=['on', 'off'])
def toggle_bot(message):
    global bot_active
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ এই কমান্ড ব্যবহারের অনুমতি আপনার নেই।")
        return

    if message.text == '/off':
        bot_active = False
        bot.reply_to(message, "🔴 বট অফ করা হয়েছে। এখন মেম্বাররা সিগন্যাল পাবে না।")
    elif message.text == '/on':
        bot_active = True
        bot.reply_to(message, "🟢 বট অন করা হয়েছে। মেম্বাররা সিগন্যাল পাবে।")
  # রেজাল্ট আপডেট ফাংশন
def process_candle_result(chat_id, pair_name, signal_type, next_candle_time):
    time.sleep(60)
    result = random.choice(["WIN ✅", "WIN ✅", "REFUND 🔄", "LOSE ❌"])
    bot.send_message(chat_id, f"📊 RESULT UPDATE\nPair: {pair_name}\nSignal: {signal_type}\nResult: {result}")

# মেম্বারদের মেসেজ হ্যান্ডলার
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    global bot_active

    if not bot_active and message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⚠️ বর্তমানে সিগন্যাল সার্ভিস বন্ধ আছে। দয়া করে পরবর্তী সেশনের জন্য অপেক্ষা করুন।")
        return

    text = message.text

    # রিয়েল মার্কেট লিস্ট দেখানো
    if text == "📈 Real Market":
        markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        buttons = [KeyboardButton(pair) for pair in REAL_PAIRS]
        buttons.append(KeyboardButton("⬅️ Back to Menu"))
        markup.add(*buttons)
        bot.send_message(message.chat.id, "📈 Real Markets: আপনার পছন্দের পেয়ার বেছে নিন:", reply_markup=markup)
        return

    # ওটিসি মার্কেট লিস্ট দেখানো
    elif text == "🌀 OTC Market":
        markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        buttons = [KeyboardButton(pair) for pair in OTC_PAIRS]
        buttons.append(KeyboardButton("⬅️ Back to Menu"))
        markup.add(*buttons)
        bot.send_message(message.chat.id, "🌀 OTC Markets: আপনার পছন্দের পেয়ার বেছে নিন:", reply_markup=markup)
        return

    # ব্যাক বাটন
    elif text == "⬅️ Back to Menu":
        start_cmd(message)
        return

    # পেয়ার সিলেক্ট করলে সিগন্যাল ও ফটো পাঠানো
    pair_name = text.strip()

    now = datetime.now()
    next_candle_time = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
    entry_time_str = next_candle_time.strftime("%H:%M")

    signal_type = random.choice(["CALL", "PUT"])
    confidence = random.randint(82, 98)
    entry_price = f"{random.uniform(100.0, 1500.0):.2f}"

    chart_image = generate_chart_card(pair_name, signal_type, confidence, entry_price, entry_time_str)

    caption_text = (
        f"❖MHT PREMIUM HACK❖\n\n"
        f"📌Asset: {pair_name}\n"
        f"📌Signal: {signal_type}\n"
        f"📌Confidence: {confidence}%\n"
        f"📌Entry Time: {entry_time_str} (Next Candle)\n"
        f"📌MTG: 1 Step Required\n"
        f"📌Owner: @MHT8099VIP\n"
    )

    bot.send_photo(message.chat.id, photo=chart_image, caption=caption_text)

    threading.Thread(
        target=process_candle_result,
        args=(message.chat.id, pair_name, signal_type, next_candle_time),
        daemon=True
    ).start()

print("MHT BOT RUNNING WITH ALL SCREENSHOT MARKETS...")
bot.infinity_polling()      
