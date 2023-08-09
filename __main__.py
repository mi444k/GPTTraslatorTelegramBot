import asyncio
import json
import logging
import textwrap

import config as cfg
import openai
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types.error_event import ErrorEvent
from aiogram.utils.chat_action import ChatActionSender
from l10n import Locales
from termcolor import cprint

if cfg.DEBUG:
    cprint('   WebOFF GPT Translate Bot starting in development mode...   ', "white", "on_red", attrs=["blink"])
    logging.basicConfig(level=logging.DEBUG)

locales = Locales()
loc = locales['en']
with open('./languages.json', 'r') as f:
    languages = json.loads(f.read())

openai.api_key = cfg.OPENAPI_KEY


router = Router()
bot = Bot(cfg.BOT_TOKEN, parse_mode=ParseMode.MARKDOWN)


def get_locales(lang):
    try:
        return locales[lang]
    except:
        return locales['en']


async def get_translate(text: str, lang: str) -> str:
    lang = text.split(' ')[0]
    form = 'formal'
    language = languages['de']
    if lang and lang.split(':')[0].lower() in languages:
        text = text[len(lang):].strip().rstrip()
        _ = lang.split(':')
        try:
            language = languages[_[0].lower()]
        except:
            pass
        if len(_) > 1 and _[1].lower() in ['i', 'u']:
            form = 'informal'
    messages = [f"Translate next texts to {language} in {form} form:"]
    if len(text) > 1500:
        messages += textwrap.wrap(text, width=1500)
    else:
        messages += [text]
    messages = [
        {"role": "user", "content": s} for s in messages
    ]

    # try:
    result = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=messages
    )
    result = result.choices[0].message.content
    # except Exception as err:
    #     result = f'*{err}*'
    return result


@router.error()
async def error_handler(event: ErrorEvent):
    if cfg.DEBUG:
        logging.error(cprint(f"ERROR: {event.exception}", "white", "on_red"), exc_info=cfg.SHOW_ERROR_INFO)


@router.message(Command(commands=["start", 'help']))
async def command_start_handler(message: Message) -> None:
    loc = get_locales(message.from_user.language_code)
    await message.answer(loc.get("welcome_message").format(full_name=message.from_user.full_name))


@router.message()
async def translate_handler(message: types.Message) -> None:
    loc = get_locales(message.from_user.language_code)
    if message.text and message.text[0] == '/':
        await message.delete()
        return
    answer = await message.reply(loc.get('translate'))
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        translation = await get_translate(message.text, loc.language)
    try:
        await answer.edit_text(translation)
    except TypeError:
        await message.reply("Nice try!")


async def main() -> None:
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
