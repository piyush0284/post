import os
import sqlite3
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Flask app (needed for Render to keep service alive)
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

TOKEN = os.getenv("BOT_TOKEN")

# Database setup
conn = sqlite3.connect("data.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS workers (
    name TEXT PRIMARY KEY,
    balance INTEGER DEFAULT 0
)
""")
conn.commit()

# Add valid posts
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.args[0]
    posts = int(context.args[1])
    amount = posts * 60

    cursor.execute("INSERT OR IGNORE INTO workers (name, balance) VALUES (?, 0)", (name,))
    cursor.execute("UPDATE workers SET balance = balance + ? WHERE name = ?", (amount, name))
    conn.commit()

    await update.message.reply_text(f"{name} added ₹{amount}. Total updated.")

# Record payment
async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.args[0]
    amount = int(context.args[1])

    cursor.execute("UPDATE workers SET balance = balance - ? WHERE name = ?", (amount, name))
    conn.commit()

    await update.message.reply_text(f"{name} paid ₹{amount}. Balance updated.")

# Check due
async def due(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.args[0]

    cursor.execute("SELECT balance FROM workers WHERE name = ?", (name,))
    result = cursor.fetchone()

    if result:
        await update.message.reply_text(f"{name} total due: ₹{result[0]}")
    else:
        await update.message.reply_text("Worker not found.")

# Telegram bot setup
telegram_app = ApplicationBuilder().token(TOKEN).build()

telegram_app.add_handler(CommandHandler("add", add))
telegram_app.add_handler(CommandHandler("paid", paid))
telegram_app.add_handler(CommandHandler("due", due))

if __name__ == "__main__":
    telegram_app.run_polling()
