
import telegram
import secret_settings

class TelegramSend():
    def __init__(self):
        self.bot = telegram.Bot(secret_settings.token)


    #
    # def send(self, image, text):
    #     self.bot.send_photo(chat_id)

