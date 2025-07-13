import os
import json
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

API_ID = int(os.getenv('TELEGRAM_API_ID', 0))
API_HASH = os.getenv('TELEGRAM_API_HASH')
PHONE = os.getenv('TELEGRAM_PHONE_NUMBER')  # Optional

DATA_LAKE_PATH = "data/raw/telegram_messages"
IMAGE_PATH = "data/raw/telegram_images"

def sanitize_data(obj):
    """Recursively sanitize data to make it JSON serializable."""
    if isinstance(obj, dict):
        return {k: sanitize_data(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_data(i) for i in obj]
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, bytes):
        return obj.hex()
    else:
        return obj

async def scrape_channel(client, channel_entity, limit=100, image_dir=None, relative_image_path_prefix="", max_images=200):
    """Scrapes messages and downloads photos from a given Telegram channel with a max images limit."""
    print(f"Scraping channel: {getattr(channel_entity, 'title', channel_entity.username)}")
    all_messages = []
    offset_id = 0
    downloaded_images_count = 0

    if image_dir:
        os.makedirs(image_dir, exist_ok=True)

    while True:
        history = await client(GetHistoryRequest(
            peer=channel_entity,
            offset_id=offset_id,
            offset_date=None,
            add_offset=0,
            limit=limit,
            max_id=0,
            min_id=0,
            hash=0
        ))

        if not history.messages:
            break

        for message in history.messages:
            downloaded_image = None

            # Download image only if media is photo AND max_images not reached
            if (message.media and message.media.__class__.__name__ == 'MessageMediaPhoto' 
                and downloaded_images_count < max_images):
                try:
                    filename = f"{message.id}.jpg"
                    full_path = os.path.join(image_dir, filename)
                    await client.download_media(message, file=full_path)
                    downloaded_image = os.path.join(relative_image_path_prefix, filename)
                    print(f"Downloaded image: {full_path}")
                    downloaded_images_count += 1
                except Exception as e:
                    print(f"Error downloading image for message {message.id}: {e}")

            msg_dict = message.to_dict()
            msg_clean = sanitize_data(msg_dict)
            if downloaded_image:
                msg_clean["downloaded_image_path"] = downloaded_image
            all_messages.append(msg_clean)

        offset_id = history.messages[-1].id

        if len(history.messages) < limit:
            break

    print(f"Total images downloaded: {downloaded_images_count}")
    return all_messages

async def main():
    if not API_ID or not API_HASH:
        print("Please set TELEGRAM_API_ID and TELEGRAM_API_HASH in your .env file.")
        return

    client = TelegramClient('telegram_scraper_session', API_ID, API_HASH)
    await client.start(phone=PHONE if PHONE else None)

    channels = [
        'https://t.me/lobelia4cosmetics',
        'https://t.me/tikvahpharma',
        # Add more channels here
    ]

    today_str = datetime.now().strftime('%Y-%m-%d')

    for channel_url in channels:
        try:
            channel_entity = await client.get_entity(channel_url)
            channel_name = getattr(channel_entity, 'username', None) or channel_entity.title.replace(" ", "_")

            output_dir = os.path.join(DATA_LAKE_PATH, today_str, channel_name)
            image_dir = os.path.join(IMAGE_PATH, today_str, channel_name)
            relative_image_prefix = os.path.relpath(image_dir, os.path.dirname(output_dir))

            os.makedirs(output_dir, exist_ok=True)

            # Scrape with max_images limit
            messages = await scrape_channel(
                client, 
                channel_entity, 
                image_dir=image_dir,
                relative_image_path_prefix=relative_image_prefix,
                max_images=200
            )

            output_file = os.path.join(output_dir, f"{channel_name}_{today_str}.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(messages, f, ensure_ascii=False, indent=4)

            print(f"✅ Saved {len(messages)} messages from {channel_name} to {output_file}")
        except Exception as e:
            print(f"❌ Error scraping {channel_url}: {e}")

    await client.disconnect()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
