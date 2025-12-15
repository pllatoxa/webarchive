import asyncio
import json
import re
from datetime import datetime

from telethon import TelegramClient, events

# ========= НАСТРОЙКИ =========
api_id = 29724408   # твой api_id
api_hash = "d3dd6dc57205144410539b2abab89fc2"  # не забудь потом сменить на новый
session_name = "one_channel_session"
output_file = "devs_storage_messages.jsonl"

# канал можно указать так:
target_channel = -1001427475948   # ИЛИ так: "@devs_storage"
# =============================


# Регулярка для поиска всех http/https ссылок в тексте
URL_REGEX = re.compile(r"(https?://[^\\s]+)")


def extract_links(text: str):
    """Вернёт список всех ссылок из текста."""
    if not text:
        return []

    links = URL_REGEX.findall(text)

    # чуть подчистим хвосты типа ")", ".", "," и т.п.
    cleaned = []
    for url in links:
        url = url.rstrip("),.;]")
        cleaned.append(url)

    return cleaned


def write(data: dict):
    """Записываем одну строку JSON в файл."""
    with open(output_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")


async def export_history(client: TelegramClient, channel):
    print("Начинаю выгрузку ВСЕХ сообщений канала...")

    async for msg in client.iter_messages(channel, reverse=True):
        text = msg.message or msg.raw_text or ""
        links = extract_links(text)

        data = {
            "type": "history",
            "msg_id": msg.id,
            "date": msg.date.isoformat() if msg.date else None,
            "from_id": getattr(msg.from_id, "user_id", None) if msg.from_id else None,
            "text": text,
            "reply_to": msg.reply_to_msg_id if msg.reply_to_msg_id else None,
            "links": links,   # <--- вот здесь список ссылок из текста
        }
        write(data)

    print("История канала выгружена.")


async def main():
    client = TelegramClient(session_name, api_id, api_hash)
    await client.start()

    # получаем entity канала
    channel = await client.get_entity(target_channel)

    # 1) выгружаем старые сообщения
    await export_history(client, channel)

    # 2) слушаем новые сообщения
    @client.on(events.NewMessage(chats=channel))
    async def handler(event: events.NewMessage.Event):
        msg = event.message
        text = msg.message or msg.raw_text or ""
        links = extract_links(text)

        data = {
            "type": "new",
            "msg_id": msg.id,
            "date": datetime.utcnow().isoformat(),
            "from_id": getattr(msg.from_id, "user_id", None) if msg.from_id else None,
            "text": text,
            "links": links,
        }
        write(data)
        print("Новое сообщение:", data["text"][:80], "| links:", links)

    print("История выгружена. Слушаю новые сообщения канала...")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
