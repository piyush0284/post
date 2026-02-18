import os
import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

conn = sqlite3.connect("data.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS workers (
    name TEXT PRIMARY KEY,
    balance INTEGER DEFAULT 0
)
""")
conn.commit()

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.args[0]
    posts = int(context.args[1])
    amount = posts * 60

    cursor.execute("INSERT OR IGNORE INTO workers (name, balance) VALUES (?, 0)", (name,))
    cursor.execute("UPDATE workers SET balance = balance + ? WHERE name = ?", (amount, name))
    conn.commit()

    await update.message.reply_text(f"{name} added ₹{amount}. Total updated.")

async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.args[0]
    amount = int(context.args[1])

    cursor.execute("UPDATE workers SET balance = balance - ? WHERE name = ?", (amount, name))
    conn.commit()

    await update.message.reply_text(f"{name} paid ₹{amount}. Balance updated.")

async def due(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.args[0]

    cursor.execute("SELECT balance FROM workers WHERE name = ?", (name,))
    result = cursor.fetchone()

    if result:
        await update.message.reply_text(f"{name} total due: ₹{result[0]}")
    else:
        await update.message.reply_text("Worker not found.")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("add", add))
app.add_handler(CommandHandler("paid", paid))
app.add_handler(CommandHandler("due", due))

app.run_polling()
