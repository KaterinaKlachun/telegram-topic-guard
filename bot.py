import os

from telegram import Update
from telegram.ext import (
    Application,
    ContextTypes,
    MessageHandler,
    filters,
)

TOKEN = os.environ["BOT_TOKEN"]

PORT = int(os.environ.get("PORT", "10000"))
RENDER_EXTERNAL_URL = os.environ["RENDER_EXTERNAL_URL"]

PROTECTED_TOPIC_ID = 1722


async def moderate(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    message = update.effective_message

    if not message:
        return

    # Игнорируем все остальные темы
    if message.message_thread_id != PROTECTED_TOPIC_ID:
        return

    user = update.effective_user

    if not user:
        return

    member = await context.bot.get_chat_member(
        chat_id=update.effective_chat.id,
        user_id=user.id
    )

    # Админов и владельца группы не трогаем
    if member.status in ("administrator", "creator"):
        print(f"Админ: {user.full_name}")
        return

    try:
        await message.delete()
        print(f"Удалено сообщение: {user.full_name}")
    except Exception as error:
        print("Ошибка удаления:", error)


app = Application.builder().token(TOKEN).build()

app.add_handler(
    MessageHandler(
        filters.ALL,
        moderate
    )
)

if __name__ == "__main__":
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"{RENDER_EXTERNAL_URL}/{TOKEN}",
    )