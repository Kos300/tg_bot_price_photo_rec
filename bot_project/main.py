import requests
from datetime import datetime
import telebot
import easyocr

from auth_token import token
# token записать в отдельном файле в формате: token = "5967...."


def get_data():
    """
    Получаем данные о курсе валюты. Сайт биржи https://www.yobit.net/en/api
    Используем метод ticker.
    Method provides statistic data for the last 24 hours.
    Example of request: https://yobit.net/api/3/ticker/ltc_btc
    Example of response:
    {
        "ltc_btc":{
            "high":105.41,
            "low":104.67,
            "avg":105.04,
            "vol":43398.22251455,
            "vol_cur":4546.26962359,
            "last":105.11,
            "buy":104.2,
            "sell":105.11,
            "updated":1418654531
        }
        ...
    }
    high: maximal price
    low: minimal price
    avg: average price
    vol: traded volume
    vol_cur: traded volume in currency
    last: last transaction price
    buy: buying price
    sell: selling price
    updated: last cache upgrade
    """

    url = f'https://yobit.net/api/3/ticker/btc_usd'
    req = requests.request("GET", url)
    response = req.json()
    sell_price = response['btc_usd']['sell']
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M')}\nSell BTC price: {sell_price} USD")

def telegram_bot(token):
    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=["start"])
    def start_message(message):
        bot.send_message(message.chat.id, "Hello there! Write the 'price' to find out the cost of BTC! or send a photo to the bot - to recognize English text on the image!")

    @bot.message_handler(content_types=["text"])
    def send_text(message):
        if message.text.lower() == "price":
            try:
                url = f'https://yobit.net/api/3/ticker/btc_usd'
                req = requests.request("GET", url)
                response = req.json()
                sell_price = response['btc_usd']['sell']
                bot.send_message(
                    message.chat.id,
                    f"{datetime.now().strftime('%Y-%m-%d %H:%M')}\nSell BTC price: {sell_price} USD"
                )
            except Exception as ex:
                print(ex)
                bot.send_message(
                    message.chat.id,
                    "Something was wrong...\nbot features:\n1) write 'price' - to get the current BTC selling price in USD.\n2) send a photo to the bot - to recognize English text on the image."
                )
        else:
            bot.send_message(message.chat.id, "Check the command. \nbot features:\n1) write 'price' - to get the current BTC selling price in USD.\n2) send a photo to the bot - to recognize English text on the image." )

    @bot.message_handler(content_types=['photo'])
    def photo(message):
        """
        Получение и обработка фото по одному.
        Перед запуском указать правильный file_path, где будет изображение.
        """
        fileID = message.photo[-1].file_id
        file_info = bot.get_file(fileID)
        downloaded_file = bot.download_file(file_info.file_path)

        with open("image.jpg", 'wb') as new_file:
            new_file.write(downloaded_file)

        try:
            bot.send_message(
                message.chat.id,
                f"Text recognition in progress...(lang.:{','.join(lang)})"
            )
            # file_path = '/home/telegram_bot/image.jpg' # для сервера
            file_path = 'image.jpg' # для localhost

            # языков может быть несколько в списке,
            # кол-во языков может снизить качество распознавания текста
            lang = ["en"]
            reader = easyocr.Reader(lang, gpu=False)
            result = reader.readtext(file_path, detail=0, paragraph=False, width_ths=300, slope_ths=0.1)
            result = '\n'.join(result)

            bot.send_message(
                message.chat.id,
                f"{datetime.now().strftime('%Y-%m-%d %H:%M')}\nText recognition result:\n\n{result}"
            )

            bot.send_message(
                message.chat.id,
                f"Text recognition completed! See result above."
            )

        except Exception as ex:
            print(ex)
            bot.send_message(
                message.chat.id,
                "You send a photo. Something was wrong..."
            )

    bot.polling()


if __name__ == '__main__':
    telegram_bot(token)