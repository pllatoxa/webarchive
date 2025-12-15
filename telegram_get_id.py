import asyncio

from telethon import TelegramClient

api_id = 29724408
api_hash = "d3dd6dc57205144410539b2abab89fc2"

session = "getid_session"
target = "@devs_storage"   # твой канал


async def main():
    client = TelegramClient(session, api_id, api_hash)
    await client.start()

    entity = await client.get_entity(target)

    print("Название:", entity.title)
    print("ID:", entity.id)


if __name__ == "__main__":
    asyncio.run(main())
