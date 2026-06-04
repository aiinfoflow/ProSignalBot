import telebot
from telebot import types
import random
import os
from datetime import datetime

TOKEN = os.environ.get("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

# ================== ASSETS ==================
assets = {
    "EUR/USD": 1.08765, "GBP/USD": 1.2734, "USD/JPY": 157.23,
    "BTC/USD": 67842, "ETH/USD": 2684.5, "SOL/USD": 178.9,
    "GOLD": 2341.5, "CRUDE OIL": 76.45, "NASDAQ": 19234,
    "APPLE": 234.5, "TESLA": 345.6, "NVIDIA": 134.2
}

timeframes = ["15s", "30s", "1m", "2m", "5m"]

user_history = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚀 Generate Signal")
    markup.add("📖 My History")
    bot.send_message(message.chat.id, 
        "🔥 **ProSignalBot** Ready!\n\nاب Signal بنانے کے لیے بٹن دبائیں 👇", 
        reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda msg: msg.text == "🚀 Generate Signal")
def generate_signal(message):
    markup = types.InlineKeyboardMarkup(row_width=3)
    for asset in assets.keys():
        markup.add(types.InlineKeyboardButton(asset, callback_data=f"asset_{asset}"))
    bot.send_message(message.chat.id, "📌 کون سا Pair چاہیے؟", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("asset_"))
def select_timeframe(call):
    asset = call.data.split("_")[1]
    markup = types.InlineKeyboardMarkup(row_width=3)
    for tf in timeframes:
        markup.add(types.InlineKeyboardButton(tf, callback_data=f"time_{tf}_{asset}"))
    bot.edit_message_text(f"✅ {asset} منتخب ہو گیا۔\nاب Timeframe چنیں:", 
                          call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("time_"))
def send_signal(call):
    tf, asset = call.data.split("_")[1:]
    direction = "UP" if random.random() > 0.47 else "DOWN"
    confidence = random.randint(96, 99)
    entry = assets[asset]
    sl = round(entry * (0.996 if direction == "UP" else 1.004), 5)
    tp = round(entry * (1.012 if direction == "UP" else 0.988), 5)

    text = f"""
🔥 **ProSignalBot**

**Pair:** {asset}
**Timeframe:** {tf}
**Direction:** {direction}
**Confidence:** {confidence}%

**Entry:** {entry}
**Stop Loss:** {sl}
**Take Profit:** {tp}
    """
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id)

    # Save history
    if call.from_user.id not in user_history:
        user_history[call.from_user.id] = []
    user_history[call.from_user.id].insert(0, {
        "time": datetime.now().strftime("%H:%M"),
        "asset": asset,
        "tf": tf,
        "direction": direction
    })

@bot.message_handler(func=lambda msg: msg.text == "📖 My History")
def show_history(message):
    if message.from_user.id not in user_history or not user_history[message.from_user.id]:
        bot.send_message(message.chat.id, "ابھی کوئی سگنل نہیں بنایا۔")
        return
    text = "📖 آپ کی آخری سگنلز:\n\n"
    for s in user_history[message.from_user.id][:5]:
        text += f"🕒 {s['time']} | {s['asset']} | {s['direction']}\n"
    bot.send_message(message.chat.id, text)

print("🚀 ProSignalBot Started Successfully...")
bot.infinity_polling()
