import asyncio
import logging
import qrcode
import json
import sys
from os import getenv
from io import BytesIO
from PIL import ImageColor

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, BufferedInputFile

dp = Dispatcher()

def load_phrases(filepath: str) -> dict:
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)

phrases = load_phrases('phrases.json')

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(phrases['command_start'])
    await message.answer(phrases['hex_codes'])


@dp.message()
async def qrcode_generator(message: Message) -> None:
    parts = message.text.split()
    link = parts[0]

    if not link:
        await message.reply(phrases['error_link_missing'])
        return

    back_color = '#fff'
    fill_color = '#000'
    caption = None

    if len(parts) == 2:
        caption = phrases['insufficient_args']
    elif len(parts) >= 3:
        try:
            _, back_color, fill_color = parts[:3]
            ImageColor.getrgb(back_color)
            ImageColor.getrgb(fill_color)
        except ValueError:
            caption = phrases['invalid_hex']
            back_color, fill_color = '#fff', '#000'

    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(link)
    qr.make(fit=True)

    img = qr.make_image(fill_color=fill_color, back_color=back_color)
    bio = BytesIO()
    img.save(bio, format="PNG")
    bio.seek(0)

    await message.reply_photo(photo=BufferedInputFile(bio.getvalue(), filename='qr.png'), caption=caption)



async def main() -> None:
    from config.config import token
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())