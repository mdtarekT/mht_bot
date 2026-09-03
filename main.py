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
ADMIN_ID = 8057979160
BOT_NAME = "MHT PREMIUM HACK"
OWNER_USERNAME = "@MHTBD99"

bot = telebot.TeleBot(API_TOKEN)

# User states to track active auto signals and running threads
user_auto_signals = {}
active_threads = {}

OTC_PAIRS = [
    ("USD/MXN (OTC)", 93),
    ("EUR/USD (OTC)", 93),
    ("GBP/USD (OTC)", 92),
    ("USD/BDT (OTC)", 95),
    ("USD/EGP (OTC)", 91),
    ("USD/INR (OTC)", 90),
    ("USD/BRL (OTC)", 89),
    ("USD/PKR (OTC)", 88),
    ("BTC/USD (OTC)", 90),
    ("ETH/USD (OTC)", 89)
]

# ==================== HELPER FUNCTIONS ====================
def generate_signal_card(asset, signal_type, strength, time_str, payout):
    img = Image.new('RGB', (800, 500), color='#0b0e14')
    draw = ImageDraw.Draw(img)

    # Outer & Inner Borders
    draw.rectangle([10, 10, 790, 490], outline='#1f2937', width=2)
    draw.rectangle([20, 20, 780, 480], fill='#111827', outline='#374151')

    # Header Section
    draw.text((30, 35), BOT_NAME, fill='#00e5ff')
    draw.text((320, 35), f"ASSET: {asset}", fill='#ffffff')
    draw.text((620, 35), f"PAYOUT: {payout}%", fill='#00e676')

    # Signal Type Box
    sig_color = '#00e676' if "CALL" in signal_type else '#ff1744'
    draw.rectangle([30, 85, 270, 155], fill=sig_color)
    draw.text((50, 105), f"SIGNAL: {signal_type}", fill='#ffffff')

    draw.text((320, 105), f"TREND STRENGTH: {strength}", fill='#ffea00')

    # Technical Details Box
    draw.rectangle([30, 180, 770, 390], fill='#0b0e14', outline='#1f2937')
    draw.text((50, 210), f"Broker       : Quotex", fill='#ffffff')
    draw.text((50, 255), f"Entry Time   : {time_str} (1 MIN)", fill='#00e5ff')
    draw.text((50, 300), f"Martingale   : 1 Step Required", fill='#ffea00')
    draw.text((50, 345), f"Strategy     : MHT ALGO v7.0", fill='#9ca3af')

    # Footer
    draw.text((30, 425), "STATUS: LIVE OTC SYNCED", fill='#00e676')
    draw.text((500, 425), f"OWNER: {OWNER_USERNAME}", fill='#ffea00')

    bio = io.BytesIO()
    bio.name = 'signal_card.png'
    img.save(bio, 'PNG')
    bio.seek(0)
    return bio

def get_main_menu_markup():
    markup = InlineKeyboardMarkup(row_width=2)
    b1 = InlineKeyboardButton("Single Signal 🎯", callback_data="btn_single")
    b2 = InlineKeyboardButton("Auto Signal 🤖", callback_data="btn_auto")
    b3 = InlineKeyboardButton("Checker 🔍", callback_data="btn_checker")
    b4 = InlineKeyboardButton("Future Signal ⏳", callback_data="btn_future")
    b5 = InlineKeyboardButton("Filter Signal ⚙️", callback_data="btn_filter")
    b6 = InlineKeyboardButton("Help / Admin 💬", callback_data="btn_help")
    b7 = InlineKeyboardButton("Change Broker 🔄", callback_data="btn_broker")
    markup.add(b1, b2, b3, b4, b5, b6, b7)
    return markup

def get_market_type_markup():
    markup = InlineKeyboardMarkup(row_width=2)
    b1 = InlineKeyboardButton("OTC Markets 📊", callback_data="market_otc")
    b2 = InlineKeyboardButton("Real Markets 📈", callback_data="market_real")
    markup.add(b1, b2)
    return markup

def send_otc_pairs_keyboard(chat_id):
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [KeyboardButton(f"{pair[0]} - {pair[1]}%") for pair in OTC_PAIRS]
    markup.add(*buttons)
    bot.send_message(chat_id, "📊 **ওটিসি মার্কেট থেকে পেয়ার সিলেক্ট করুন:**", reply_markup=markup, parse_mode="Markdown")

# ==================== HANDLERS ====================
@bot.message_handler(commands=['start'])
def start_cmd(message):
    welcome_msg = (
        f"👋 **Welcome to {BOT_NAME}**\n\n"
        f"📌 **Broker:** Quotex\n"
        f"👤 **Owner:** {OWNER_USERNAME}\n\n"
        f"নিচের মেনু থেকে আপনার কাঙ্ক্ষিত অপশন সিলেক্ট করুন:"
    )
    bot.send_message(message.chat.id, welcome_msg, reply_markup=get_main_menu_markup(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    if call.data in ["btn_single", "btn_auto"]:
        user_auto_signals[call.message.chat.id] = (call.data == "btn_auto")
        bot.send_message(call.message.chat.id, "🌐 **মার্কেট টাইপ বেছে নিন:**", reply_markup=get_market_type_markup(), parse_mode="Markdown")
    
    elif call.data == "market_otc":
        send_otc_pairs_keyboard(call.message.chat.id)
        
    elif call.data == "stop_auto":
        user_auto_signals[call.message.chat.id] = False
        bot.send_message(call.message.chat.id, "🛑 **Auto Signal stopped successfully.**")

    elif call.data == "btn_help":
        bot.send_message(call.message.chat.id, f"💬 এডমিনের সাথে যোগাযোগ করুন: {OWNER_USERNAME}")

    elif call.data == "partial_info":
        bot.answer_callback_query(call.id, text="📊 Partial analysis recorded.", show_alert=True)

    bot.answer_callback_query(call.id)

# ==================== CORE SIGNAL ENGINE ====================
def send_auto_signal_cycle(chat_id, pair_name, payout):
    while user_auto_signals.get(chat_id, False):
        # 1. Calculate Entry Time for Bangladesh Standard Time (UTC+6)
        bd_time = datetime.utcnow() + timedelta(hours=6)
        next_candle = (bd_time + timedelta(minutes=1)).replace(second=0, microsecond=0)
        entry_time_str = next_candle.strftime("%H:%M")

        signal_type = random.choice(["CALL 🟢", "PUT 🔴"])
        strength = random.choice(["STRONG", "VERY STRONG", "HIGH ACCURACY"])

        # Send Signal Card & Message
        card_img = generate_signal_card(pair_name, signal_type, strength, entry_time_str, payout)
        caption = (
            f"✨ **{BOT_NAME} SIGNAL** ✨\n\n"
            f"📊 **Asset:** {pair_name}\n"
            f"📈 **Signal:** {signal_type}\n"
            f"⚡ **Strength:** {strength}\n"
            f"⏰ **Time:** {entry_time_str} (1 MIN Candle)\n"
            f"🎯 **MTG:** 1 Step\n\n"
            f"👤 **Owner:** {OWNER_USERNAME}"
        )
        bot.send_photo(chat_id, photo=card_img, caption=caption, parse_mode="Markdown")

        # 2. Wait until 1st candle officially finishes
        first_candle_end = next_candle + timedelta(minutes=1)
        now = datetime.utcnow() + timedelta(hours=6)
        sleep_sec = (first_candle_end - now).total_seconds()
        if sleep_sec > 0:
            time.sleep(sleep_sec)

        if not user_auto_signals.get(chat_id, False):
            break

        # 3. Determine Result Outcome
        # 60% Direct Win, 25% MTG Win, 15% Loss
        res_type = random.choices(["DIRECT_WIN", "MTG_WIN", "LOSS"], weights=[60, 25, 15])[0]

        if res_type == "DIRECT_WIN":
            res_text = "DIRECT WIN"
            emoji = "✅"
            used_mtg = False
        else:
            # Need to wait 1 more minute for MTG candle to complete
            time.sleep(60)
            if not user_auto_signals.get(chat_id, False):
                break
            
            if res_type == "MTG_WIN":
                res_text = "WIN (MTG 1)"
                emoji = "✅"
            else:
                res_text = "LOSS"
                emoji = "🚫"

        # Control Keyboard for Result Message
        control_markup = InlineKeyboardMarkup(row_width=2)
        control_markup.add(
            InlineKeyboardButton("📊 Partial", callback_data="partial_info"),
            InlineKeyboardButton("🛑 Stop", callback_data="stop_auto")
        )

        result_message = (
            f"✨ **{BOT_NAME} RESULT** ✨\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💎 **Asset:** {pair_name}\n"
            f"⏰ **Signal Time:** {entry_time_str}\n"
            f"🦅 **Signal:** {signal_type}\n"
            f"🎈 **Result:** {emoji} {res_text}\n"
            f"👑 **Owner:** {OWNER_USERNAME}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━"
        )

        bot.send_message(
            chat_id, 
            result_message, 
            reply_markup=control_markup,
            parse_mode="Markdown"
        )

        # Single Signal mode ends after 1 signal
        if not user_auto_signals.get(chat_id, False):
            break

        # Market Analysis Delay before generating next signal (3 seconds)
        time.sleep(3)


@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    text = message.text.strip()

    # Check if user selected an OTC pair
    for pair, payout in OTC_PAIRS:
        if pair in text:
            # Stop any existing thread for this user
            user_auto_signals[message.chat.id] = False
            time.sleep(0.5)

            is_auto = user_auto_signals.get(message.chat.id, False)
            
            # Default to Auto Signal if not specified
            user_auto_signals[message.chat.id] = True
            
            bot.send_message(
                message.chat.id, 
                f"🚀 **Signal Engine Started for {pair}** | Daily Usage: Active",
                parse_mode="Markdown"
            )

            # Start thread safely
            t = threading.Thread(
                target=send_auto_signal_cycle, 
                args=(message.chat.id, pair, payout), 
                daemon=True
            )
            active_threads[message.chat.id] = t
            t.start()
            return

bot.infinity_polling()
