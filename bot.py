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


# =========================================
# НАСТРОЙКИ ЗАЩИЩЁННЫХ ГРУПП / ТЕМ
# =========================================

# Формат:
# chat_id: set(thread_id)
# None = главный чат / General

PROTECTED_TOPICS = {
    -1002910465621: {1722},        # тестовая группа
    -1004328947804: {61, None},    # группа 17-116: два подчата
}


def is_protected(chat_id: int, thread_id):
    """
    Проверяем, является ли текущее сообщение сообщением
    из защищённой темы / подчата.
    """
    if chat_id not in PROTECTED_TOPICS:
        return False

    return thread_id in PROTECTED_TOPICS[chat_id]


async def moderate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if not message or not chat:
        return

    chat_id = chat.id
    thread_id = message.message_thread_id

    # Если это не защищённый подчат — ничего не делаем
    if not is_protected(chat_id, thread_id):
        return

    # Если это служебное сообщение без пользователя — пропускаем
    if not user:
        return

    try:
        member = await context.bot.get_chat_member(
            chat_id=chat_id,
            user_id=user.id
        )

        # Админов и владельца группы не трогаем
        if member.status in ("administrator", "creator"):
            print(
                f"РАЗРЕШЕНО | "
                f"Группа: {chat.title} | "
                f"Пользователь: {user.full_name} | "
                f"thread_id: {thread_id}"
            )
            return

        # Остальных удаляем
        await message.delete()

        print(
            f"УДАЛЕНО | "
            f"Группа: {chat.title} | "
            f"Пользователь: {user.full_name} | "
            f"thread_id: {thread_id}"
        )

    except Exception as error:
        print(
            f"ОШИБКА | "
            f"Группа: {chat.title} | "
            f"Пользователь: {user.full_name if user else 'Unknown'} | "
            f"thread_id: {thread_id} | "
            f"{error}"
        )


app = Application.builder().token(TOKEN).build()

app.add_handler(
    MessageHandler(filters.ALL, moderate)
)

if __name__ == "__main__":
    print("Topic Guard запускается...")

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"{RENDER_EXTERNAL_URL}/{TOKEN}",
    )