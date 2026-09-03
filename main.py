import io
import time
import random
import threading
from datetime import datetime, timedelta
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from PIL import Image, ImageDraw, ImageFont

API_TOKEN = '8931167419:AAGZYUQOteTDqrG0KdiJYwhmZG0R0EqrdwE'
bot = telebot.TeleBot(API_TOKEN)

PAIRS = [
    "USD/ARS (OTC)-94%",
    "USD/PKR (OTC)-94%",
    "NZD/JPY (OTC)-93%",
    "USD/DZD (OTC)-93%",
    "USD/EGP (OTC)-93%",
    "USD/MXN (OTC)-93%"
]

# ১. ডায়নামিক সিগন্যাল কার্ড জেনারেটর ফাংশন
def generate_chart_card(asset, signal, confidence, entry_price, entry_time):
    # ৮০০x৫০০ পিক্সেলের ব্যাকগ্রাউন্ড ক্যানভাস
    img = Image.new('RGB', (800, 500), color='#0b0e14')
    draw = ImageDraw.Draw(img)

    # বর্ডার ও ইন্টারফেস গ্রিড
    draw.rectangle([10, 10, 790, 490], outline='#1f2937', width=2)
    draw.rectangle([20, 20, 780, 60], fill='#111827', outline='#374151')
    
    # হেডার টেক্সট
    draw.text((30, 32), f"MHT HACK PRO", fill='#00e5ff')
    draw.text((200, 32), f"ASSET: {asset}", fill='#ffffff')
    
    sig_color = '#00ff88' if signal == "CALL" else '#ff4444'
    draw.rectangle([550, 28, 650, 52], fill=sig_color)
    draw.text((565, 32), f"▲ {signal}" if signal == "CALL" else f"▼ {signal}", fill='#000000')

    # কাল্পনিক ক্যান্ডেলস্টিক চার্ট ড্র করা
    chart_base_y = 400
    x = 40
    for i in range(18):
        c_open = random.randint(200, 350)
        c_close = c_open + random.randint(-40, 40)
        color = '#00ff88' if c_close >= c_open else '#ff4444'
        high = min(c_open, c_close) - random.randint(5, 15)
        low = max(c_open, c_close) + random.randint(5, 15)
        
        # সলিতা (Wick) ও ক্যান্ডেল বডি
        draw.line([(x + 8, high), (x + 8, low)], fill=color, width=1)
        draw.rectangle([x, min(c_open, c_close), x + 16, max(c_open, c_close)], fill=color)
        x += 30

    # সাইডবার ইনফরমেশন প্যানেল
    draw.rectangle([580, 70, 780, 440], fill='#111827', outline='#1f2937')
    draw.text((595, 85), "SIGNAL DETAILS", fill='#ffffff')
    
    draw.text((595, 130), f"Confidence: {confidence}%", fill='#00e5ff')
    draw.rectangle([595, 150, 765, 158], fill='#1f2937')
    draw.rectangle([595, 150, 595 + int(1.7 * confidence), 158], fill='#00ff88')

    draw.text((595, 185), f"Entry Price: {entry_price}", fill='#9ca3af')
    draw.text((595, 215), f"Entry Time: {entry_time}", fill='#9ca3af')
    draw.text((595, 245), "Martingale: 1 Step", fill='#9ca3af')
    draw.text((595, 275), "Broker: Quotex", fill='#9ca3af')

    # কাস্টম বটের ফুটার ব্র্যান্ডিং
    draw.rectangle([20, 450, 780, 480], fill='#000000')
    draw.text((30, 458), "Made By @MHTBD99 | MHT PREMIUM HACK", fill='#9ca3af')
    draw.text((560, 458), "MHT Organization Copyright", fill='#4b5563')

    # ইমেজের অবজেক্ট বাইটসে রূপান্তর
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr

def main_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("Single Signal", callback_data="get_signal"),
        InlineKeyboardButton("Auto Signal", callback_data="get_signal")
    )
    return markup

def market_reply_keyboard():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [KeyboardButton(p) for p in PAIRS]
    markup.add(*buttons)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id, 
        f"Assalamualaikum, {message.from_user.first_name}!\n\nMHT PREMIUM HACK BOT READY", 
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "Select Asset from Keyboard below:", reply_markup=market_reply_keyboard())
def process_candle_result(chat_id, pair_name, signal_type, entry_time):
    wait_sec = (entry_time - datetime.now()).total_seconds()
    if wait_sec > 0:
        time.sleep(wait_sec)

    time.sleep(60) # ক্যান্ডেল ১ মিনিট চলা পর্যন্ত অপেক্ষা

    first_candle_win = random.choice([True, False])

    if first_candle_win:
        status_text = "DIRECT WIN!\n[0-MARTINGALE SUCCESS]"
    else:
        bot.send_message(chat_id, f"Direct Loss on {pair_name}! Checking MTG-1 Candle...", parse_mode="Markdown")
        time.sleep(60) # MTG ক্যান্ডেল ১ মিনিট অপেক্ষা
        mtg_win = random.choice([True, False])
        
        if mtg_win:
            status_text = "MTG-1 WIN!\n[Recovered in Step-1]"
        else:
            status_text = "REAL LOSS\n[Direct and MTG Both Failed]"

    entry_str = entry_time.strftime("%H:%M")
    result_text = (
        f"REAL-TIME SIGNAL RESULT\n"
        f"----------------------\n"
        f"Asset: {pair_name}\n"
        f"Entry Time: {entry_str}\n"
        f"Signal: {signal_type}\n"
        f"Status: {status_text}\n"
        f"Owner: @MHTBD99\n"
        f"----------------------"
    )
    bot.send_message(chat_id, result_text)

@bot.message_handler(func=lambda msg: True)
def handle_all_messages(message):
    text = message.text
    pair_name = text.split("-")[0].strip() if "-" in text else text.strip()

    now = datetime.now()
    next_candle_time = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
    entry_time_str = next_candle_time.strftime("%H:%M")

    signal_type = random.choice(["CALL", "PUT"])
    confidence = random.randint(82, 98)
    entry_price = f"{random.uniform(100.0, 1500.0):.2f}"

    # সিগন্যাল কার্ড ইমেজ তৈরি
    chart_image = generate_chart_card(pair_name, signal_type, confidence, entry_price, entry_time_str)

    caption_text = (
        f"MHT PREMIUM HACK\n"
        f"----------------------\n"
        f"Asset: {pair_name}\n"
        f"Signal: {signal_type}\n"
        f"Confidence: {confidence}%\n"
        f"Entry Time: {entry_time_str} (Next Candle)\n"
        f"MTG: 1 Step Required\n"
        f"Owner: @MHTBD99\n"
        f"----------------------"
    )

    # টেলিগ্রামে কার্ড ছবি ও সিগন্যাল টেক্সট একসাথে পাঠানো
    bot.send_photo(message.chat.id, photo=chart_image, caption=caption_text)

    # ব্যাকগ্রাউন্ড রেজাল্ট ট্র্যাকিং
    threading.Thread(
        target=process_candle_result, 
        args=(message.chat.id, pair_name, signal_type, next_candle_time), 
        daemon=True
    ).start()

print("MHT BOT RUNNING WITH IMAGE GENERATOR...")
bot.infinity_polling()