import datetime
import json
import logging
import os
import time

import requests
from dotenv import load_dotenv
from PIL import ImageGrab
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (CallbackContext, CallbackQueryHandler,
                          CommandHandler, Updater)

load_dotenv()


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def start(update: Update, _: CallbackContext):
    update.message.reply_html(f"Hello, it's {datetime.datetime.now()} now. What do you want to do?",
                              reply_markup=InlineKeyboardMarkup.from_column(
                                  [
                                      InlineKeyboardButton(
                                          text="Get bot HTTP headers", callback_data="http_headers"),
                                      InlineKeyboardButton(
                                          text="Get bot JA3", callback_data="ja3"),
                                      InlineKeyboardButton(
                                          text="Get owner PC screenshot", callback_data="bot_owner_screenshot"),
                                  ]
                              )
                              )


def get_fingerprint_response():
    return requests.get(os.getenv('FINGERPRINT_SITE_URL')).json()


def handle_callback_query(update: Update, context: CallbackContext):
    global logger

    action = update.callback_query.data

    logger.log(level=1, msg='action')

    if action == 'http_headers':
        print_http_headers(update)
    elif action == 'ja3':
        print_ja3(update)
    elif action == 'bot_owner_screenshot':
        save_and_print_screenshot(update, context)


def save_and_print_screenshot(update: Update, context: CallbackContext):
    filename = f"{str(time.time())}.jpg"

    image = ImageGrab.grab(bbox=(0, 0, 1920, 1080))
    image.save(filename)

    with open(filename, mode='rb') as file:
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=file)


def print_ja3(update: Update):
    response = get_fingerprint_response()
    ja3_hash = json.dumps(response['tls']['ja3_hash'])
    update.callback_query.answer(
        f"My JA3 hash:\n{ja3_hash}", show_alert=True)


def print_http_headers(update: Update):
    response = get_fingerprint_response()
    headers = json.dumps(response['http1']['headers'])
    update.callback_query.answer(
        f"My headers:\n{headers}", show_alert=True)


def main():
    updater = Updater(os.getenv('TOKEN'))

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CallbackQueryHandler(handle_callback_query))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
