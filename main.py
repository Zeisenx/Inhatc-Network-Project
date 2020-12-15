import logging

import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

from content import token_id as telegramtoken

import pyzbar.pyzbar as pyzbar
import cv2

from pymongo import MongoClient
# import picamera

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def decode_image(image):
    decoded_image = pyzbar.decode(image)
    return decoded_image

def test_sample_image():
    image = cv2.imread('./content/sample_image.jpg')
    decoded_image = decode_image(image)
    for obj in decoded_image:
        print(obj.type, obj.data)
        print(getInfo(obj.data.decode('utf-8')))


def takeShot(_time):
    pass
    # stream = io.BytesIO()
    # with picamera.PiCamera() as camera:
    #     camera.start_preview()
    #     time.sleep(_time)
    #     camera.capture(stream, format='jpeg')
    # stream.seek(0)
    # return stream


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hi! Use /set <seconds> to set a timer')


def alarm(context):
    """Send the alarm message."""
    job = context.job
    context.bot.send_message(job.context, text='Beep!')


def remove_job_if_exists(name, context):
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def set_timer(update: Update, context: CallbackContext) -> None:
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(context.args[0])
        if due < 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return

        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_once(alarm, due, context=chat_id, name=str(chat_id))

        text = 'Timer successfully set!'
        if job_removed:
            text += ' Old one was removed.'
        update.message.reply_text(text)

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <seconds>')


def getInfo(barcode_id):
    try:
        url = 'http://www.gs1kr.org/Service/Service/appl/01.asp'

        payload = {'MEMB_DIV': 1, 'CODE': barcode_id, 'CODE1': ''}
        a = requests.post(url, data=payload)

        result_soup = BeautifulSoup(a.text, 'html.parser')
        data = result_soup.find('table', {'class': ['odd', 'nofirst', 'tc']})

        return data.select('tr > td')[1].get_text(), data.select('tr > td')[3].get_text()
    except:
        return None


def main():
    COLA_ID = '8801094082604'
    print(getInfo(COLA_ID))

    test_sample_image()


    """Run bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(telegramtoken.id, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", start))
    dispatcher.add_handler(CommandHandler("set", set_timer))

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
