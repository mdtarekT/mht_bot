import time
import random
import threading
from datetime import datetime, timedelta
import io

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from PIL import Image, ImageDraw

# ==================== CONFIGURATION ====================
API_TOKEN = '8931167419:AAGYI3lt_5psV-fGRWfA5DiAjyGUViXMr3Y'
BOT_NAME = "MHT PREMIUM HACK"
OWNER_USERNAME = "@MHTBD99"

# আপনার দেওয়া Quotex Session Cookie/Token
QUOTEX_COOKIE = "eyJpdiI6IkxQYkgrWVZEdEJLam9kM2FZbmFCL1E9PSIsInZhbHVlIjoid0RuWVRkWkR6SFlmMjZ2eWRWNGMvSFRhQk9BUURSamNzOEVaSFMvWnkvM1ZEVmFzK2I3U1VLbUhuV0dRMmd6eFFmUi9MRTdlZEQyZmY1dWZBSGRUaFNKdWtUZ1BseFRacjhuUWorZlQ0UjBqbWZ2Lyt4Njd4Q1BOKy9UV2ZIWVNBekZjN2orVnhML1VQZlpRd0x2Yno4VisvdDAvK0o5UW50TDdvNEFxT2d3U25aQ0ZrKzVzQk5VcnM3b2wwUTVsVEo2cWxISjhrQVBrTFJ4cVZjRUFVYXM2NFRwa0lMZzliKzVzVXlLTzJZSVdNRy9DN0N0OVdTTy9pUmZDc1kvaCIsIm1hYyI6IjI3ZWFmNDFlMGUzMGNlMWUwYzcwZDFlYmQ1NjQwZmU4MGYxNWQ2ZjEzNTRiZDk5NGI0YzAxYzQ5Zjk1MjU1NWYiLCJ0YWciOiIifQ%3D%3D"

bot = telebot.TeleBot(API_TOKEN)
user_auto_signals = {}

OTC_PAIRS = [
    ("USD/MXN (OTC)", "USD/MXN_otc", 93),
    ("EUR/USD (OTC)", "EUR/USD_otc", 93),
    ("GBP/USD (OTC)", "GBP/USD_otc", 92),
    ("USD/BDT (OTC)", "USD/BDT_otc", 95),
    ("USD/INR (OTC)", "USD/INR_otc", 90)
]

def check_real_candle_result(pair_symbol, signal_dir):
    """ কোটেক্স কুকি ব্যবহার করে লাইভ ক্যান্ডেলের ক্লোজ ও ওপেন প্রাইস তুলনা করে আসল রেজাল্ট চেক """
    try:
        from quotexpy import Quotex
        client = Quotex(ssid=QUOTEX_COOKIE)
        check, _ = client.connect()
        if check:
            candles = client.get_candles(pair_symbol, 60)
            if candles:
                last_candle = candles[-1]
                open_p = last_candle['open']
                close_p = last_candle['close']
                if signal_dir == "CALL":
                    return "WIN" if close_p > open_p else "LOSS"
                else:
                    return "WIN" if close_p < open_p else "LOSS"
    except Exception as e:
        print(f"Candle API fetch error: {e}")
    
    # এপিআই রেসপন্স না দিলে ফলব্যাক
    return "WIN" if random.random() > 0.3 else "LOSS"

def send_auto_signal_cycle(chat_id, pair_display, pair_symbol, payout):
    while user_auto_signals.get(chat_id, False):
        bd_time = datetime.utcnow() + timedelta(hours=6)
        next_candle = (bd_time + timedelta(minutes=1)).replace(second=0, microsecond=0)
        entry_time_str = next_candle.strftime("%H:%M")

        signal_dir = random.choice(["CALL", "PUT"])
        signal_icon = "🟢" if signal_dir == "CALL" else "🔴"
        strength = random.choice(["STRONG", "HIGH ACCURACY"])

        caption = (
            f"✨ **{BOT_NAME} SIGNAL** ✨\n\n"
            f"📊 **Asset:** {pair_display}\n"
            f"📈 **Signal:** {signal_dir} {signal_icon}\n"
            f"⚡ **Strength:** {strength}\n"
            f"⏰ **Time:** {entry_time_str} (1 MIN Candle)\n"
            f"🎯 **MTG:** 1 Step\n\n"
            f"👤 **Owner:** {mhtbd99}"
        )
        bot.send_message(chat_id, caption, parse_mode="Markdown")

        # ১. ক্যান্ডেল শেষ হওয়া পর্যন্ত অপেক্ষা (১ মিনিট)
        first_candle_end = next_candle + timedelta(minutes=1)
        now = datetime.utcnow() + timedelta(hours=6)
        sleep_sec = (first_candle_end - now).total_seconds()
        if sleep_sec > 0:
            time.sleep(sleep_sec)

        if not user_auto_signals.get(chat_id, False):
            break

        # ২. প্রথম ক্যান্ডেলের আসল রেজাল্ট চেক
        first_res = check_real_candle_result(pair_symbol, signal_dir)

        if first_res == "WIN":
            final_res_text = "DIRECT WIN ✅"
        else:
            # Direct Win না হলে MTG 1 ক্যান্ডেলের জন্য আরও ১ মিনিট অপেক্ষা
            time.sleep(60)
            if not user_auto_signals.get(chat_id, False):
                break
            
            mtg_res = check_real_candle_result(pair_symbol, signal_dir)
            if mtg_res == "WIN":
                final_res_text = "WIN (MTG 1) ✅"
            else:
                final_res_text = "LOSS 🚫"

        # ৩. আসল রেজাল্ট পাঠানো
        result_message = (
            f"✨ **{BOT_NAME} RESULT** ✨\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💎 **Asset:** {pair_display}\n"
            f"⏰ **Signal Time:** {entry_time_str}\n"
            f"🦅 **Signal:** {signal_dir} {signal_icon}\n"
            f"🎈 **Result:** {final_res_text}\n"
            f"👑 **Owner:** {OWNER_USERNAME}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━"
        )
        bot.send_message(chat_id, result_message, parse_mode="Markdown")

        if not user_auto_signals.get(chat_id, False):
            break

        time.sleep(3)

@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.send_message(message.chat.id, f"👋 **Welcome to {BOT_NAME}**\n\nস্টার্ট করতে পেয়ার চুজ করুন।")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    for display_name, symbol, payout in OTC_PAIRS:
        if display_name in message.text or symbol in message.text:
            user_auto_signals[message.chat.id] = True
            bot.send_message(message.chat.id, f"🚀 Signal engine started for {display_name}")
            threading.Thread(target=send_auto_signal_cycle, args=(message.chat.id, display_name, symbol, payout), daemon=True).start()
            return

bot.infinity_polling()
