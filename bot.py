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


# ---------------------------------------
# НАСТРОЙКИ ЗАЩИЩЁННЫХ ЧАТОВ / ТЕМ
# ---------------------------------------

TEST_GROUP_ID = -1002910465621
TEST_TOPIC_ID = 1722

STUDENT_GROUP_ID = -1004328947804


def is_protected(chat_id: int, thread_id):
    """
    Возвращает True только для тех мест,
    где студентам запрещено писать.
    """

    # Тестовая группа — только тема 1722
    if chat_id == TEST_GROUP_ID and thread_id == TEST_TOPIC_ID:
        return True

    # Группа 17-116 — только главный чат / General
    # Там Telegram передаёт thread_id = None
    if chat_id == STUDENT_GROUP_ID and thread_id is None:
        return True

    return False


async def moderate(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if not message or not chat:
        return

    chat_id = chat.id
    thread_id = message.message_thread_id

    # Если это не защищённая тема — вообще ничего не делаем
    if not is_protected(chat_id, thread_id):
        return

    # Служебные сообщения без пользователя не трогаем
    if not user:
        return

    try:
        member = await context.bot.get_chat_member(
            chat_id=chat_id,
            user_id=user.id
        )

        # Администраторам и владельцу разрешаем писать
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
            f"Пользователь: {user.full_name} | "
            f"{error}"
        )


app = Application.builder().token(TOKEN).build()

app.add_handler(
    MessageHandler(
        filters.ALL,
        moderate
    )
)


if __name__ == "__main__":
    print("Topic Guard запускается...")

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"{RENDER_EXTERNAL_URL}/{TOKEN}",
    )