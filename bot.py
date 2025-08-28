import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلًا 👋 أرسل صور ورقتك وحدة وحدة.\nمن تكمل اكتب /finish")

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count = context.user_data.get("count", 0) + 1
    context.user_data["count"] = count
    await update.message.reply_text(f"✅ تم استلام الصورة رقم {count}")

async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count = context.user_data.get("count", 0)
    await update.message.reply_text(f"📚 تم تسليم ورقتك.\nعدد الصور: {count}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("finish", finish))
    app.add_handler(MessageHandler(filters.PHOTO, photo))
    print("🤖 Bot is running on Render ...")
    app.run_polling()

if __name__ == "__main__":
    main()
