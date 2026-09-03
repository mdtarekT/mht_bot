@bot.message_handler(commands=['start'])
def start_cmd(message):
    welcome_msg = (
        f"👋 Welcome to {BOT_NAME}\n\n"
        f"📌 Broker: Quotex\n"
        f"👤 Owner: {OWNER_USERNAME}\n\n"
        f"নিচের মেনু থেকে আপনার কাঙ্ক্ষিত অপশন সিলেক্ট করুন:"
    )
    bot.send_message(message.chat.id, welcome_msg, reply_markup=get_main_menu_markup(), parse_mode="Markdown")
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    if call.data in ["btn_single", "btn_auto"]:
        user_auto_signals[call.message.chat.id] = (call.data == "btn_auto")
        bot.send_message(call.message.chat.id, "🌐 মার্কেট টাইপ বেছে নিন:", reply_markup=get_market_type_markup(), parse_mode="Markdown")
    
    elif call.data == "market_otc":
        send_otc_pairs_keyboard(call.message.chat.id)
        
    elif call.data == "stop_auto":
        user_auto_signals[call.message.chat.id] = False
        bot.send_message(call.message.chat.id, "🛑 Auto Signal stopped. The already-sent signal result will still be delivered.")

    elif call.data == "btn_help":
        bot.send_message(call.message.chat.id, f"💬 এডমিনের সাথে যোগাযোগ করুন: {OWNER_USERNAME}")

    elif call.data == "partial_info":
        bot.answer_callback_query(call.id, text="📊 Partial analysis recorded.", show_alert=True)

    bot.answer_callback_query(call.id)

def send_auto_signal_cycle(chat_id, pair_name, payout):
    if not user_auto_signals.get(chat_id, False):
        return

    now = datetime.now()
    next_candle = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
    time_str = next_candle.strftime("%H:%M")

    signal_type = random.choice(["CALL 🟢", "PUT 🔴"])
    strength = random.choice(["STRONG", "VERY STRONG", "HIGH ACCURACY"])

    card_img = generate_signal_card(pair_name, signal_type, strength, time_str, payout)

    caption = (
        f"✨ {BOT_NAME} SIGNAL ✨\n\n"
        f"📊 Asset: {pair_name}\n"
        f"📈 Signal: {signal_type}\n"
        f"⚡ Strength: {strength}\n"
        f"⏰ Time: {time_str} (1 MIN Candle)\n"
        f"🎯 MTG: 1 Step\n\n"
        f"👤 Owner: {OWNER_USERNAME}"
    )

    bot.send_photo(chat_id, photo=card_img, caption=caption, parse_mode="Markdown")

    # Waiting 60 seconds for candle finish
    time.sleep(60)

    if user_auto_signals.get(chat_id, False):
        # Win / Loss Simulation
        res_type = random.choice(["DIRECT_WIN", "DIRECT_WIN", "LOSS", "MTG_WIN"])
        
        if res_type == "DIRECT_WIN":
            res_text = "DIRECT WIN"
            emoji = "✅"
        elif res_type == "MTG_WIN":
            res_text = "WIN (MTG 1)"
            emoji = "✅"
        else:
            res_text = "LOSS"
            emoji = "🚫"

        control_markup = InlineKeyboardMarkup(row_width=2)
        control_markup.add(
            InlineKeyboardButton("📊 Partial", callback_data="partial_info"),
            InlineKeyboardButton("🛑 Stop", callback_data="stop_auto")
        )

        result_message = (
            f"✨ {BOT_NAME} RESULT ✨\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💎 Asset: {pair_name}\n"
            f"🦅 Signal: {signal_type}\n"
            f"🎈 Result: {emoji} {res_text}\n"
            f"👑 Owner: {OWNER_USERNAME}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━"
        )

        bot.send_message(
            chat_id, 
            result_message, 
            reply_markup=control_markup,
            parse_mode="Markdown"
        )

        # Loop for next signal if auto signal is active
        threading.Thread(target=send_auto_signal_cycle, args=(chat_id, pair_name, payout), daemon=True).start()

@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    text = message.text.strip()

    # Check if user selected an OTC pair
    for pair, payout in OTC_PAIRS:
        if pair in text:
            is_auto = user_auto_signals.get(message.chat.id, False)
            mode_label = "Auto Signal" if is_auto else "Single Signal"
            
            bot.send_message(
                message.chat.id, 
                f"🚀 {mode_label} Started for {pair} | Daily Usage: Active",
                parse_mode="Markdown"
            )

            threading.Thread(
                target=send_auto_signal_cycle, 
                args=(message.chat.id, pair, payout), 
                daemon=True
            ).start()
            return

bot.infinity_polling()
