from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

TOKEN = "8716891485:AAFG_5F-jqSGqgR9Q0vEY8ODC-ikf7c5CUk"

async def show_ids(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message

    if not message:
        return

    print("\n-------------------------")
    print("Группа:", update.effective_chat.title)
    print("chat_id:", update.effective_chat.id)
    print("thread_id:", message.message_thread_id)
    print("message_id:", message.message_id)
    print("Текст:", message.text)
    print("-------------------------")

app = Application.builder().token(TOKEN).build()

app.add_handler(
    MessageHandler(filters.ALL, show_ids)
)

print("Диагностический бот запущен...")
app.run_polling()