from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration


# Secret app TOKEN
# TODO: Place it somewhere else
TOKEN = "4f5c605073e7e741-801386ee70f8470d-dd779006e2e4d2b8"

bot_configuration = BotConfiguration(
    name="Test_Bot",
    avatar="",
    auth_token=TOKEN
)
viber = Api(bot_configuration)

