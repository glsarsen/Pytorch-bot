import json
import torch
import logging
import bot_messages as bm
from time import sleep
from model import NeuralNet
from torch_utils import get_intents

from viber_config import viber
from request_handler import ViberHandler, ElementTree

from flask import Flask, request, Response, url_for, redirect
from viberbot.api.messages.typed_message import TypedMessage
from viberbot.api.messages import TextMessage
from viberbot.api.messages import KeyboardMessage
from viberbot.api.messages import URLMessage
from viberbot.api.messages import RichMediaMessage
from viberbot.api.messages import ContactMessage
from viberbot.api.messages import PictureMessage
from viberbot.api.messages import VideoMessage
from viberbot.api.messages import LocationMessage
from viberbot.api.messages import StickerMessage
from viberbot.api.messages import FileMessage

from viberbot.api.viber_requests import ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest
from viberbot.api.viber_requests import ViberUnsubscribedRequest
from viberbot.api.viber_requests import ViberDeliveredRequest
from viberbot.api.viber_requests import ViberSeenRequest

app = Flask(__name__)
# app.config['SERVER_NAME'] = "d3a1-92-253-236-40.eu.ngrok.io"

# Set up the logger for the bot
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s\n')
# formatter = logging.Formatter()
handler.setFormatter(formatter)
logger.addHandler(handler)

# Start up the torch module, load intents and set up the neural net
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r', encoding="utf-8") as f:
    intents = json.load(f)

FILE = 'data.pth'
data = torch.load(FILE)


input_size = data['input_size']
hidden_size = data['hidden_size']
output_size = data['output_size']
all_words = data['all_words']
tags = data['tags']
model_state = data['model_state']


model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

command = None
# TODO: do I still need it?


my_handler = ViberHandler()
rhandler = ElementTree(my_handler)
# TODO: check in_contact_list tag
rhandler.add_branch("_start")
rhandler.add_message("Добро пожаловать в компанию!")
rhandler.add_message("Как тебя зовут?")
rhandler.add_input("user_name")
rhandler.add_message("И введи свой номер телефона пожалуйста:")
rhandler.add_input("user_phone")
rhandler.add_message("Выбери нужный вариант в меню ниже:")
# TODO: google sheets integration
# TODO: add new_user_menu tag
# TODO: remove questions_menu tag
rhandler.set_keyboard(bm.NEW_USER_MENU)
rhandler.add_branch("_new_user")
rhandler.add_message("Ты подписал *договор и заполнил карту сотрудника*?")
rhandler.add_buttons({"Сделано! Что дальше?":"_contract_done", "Еще нет.":"_contract_not_done"})
rhandler.add_branch("_contract_not_done")
rhandler.add_message("Пожалуйста, напиши рекрутеру, который с тобой общался.")
rhandler.add_buttons({"Далее":"_contract_done", "Обратная связь":"_feedback"})
rhandler.add_branch("_contract_done")
rhandler.add_message("Ты уже создал *Гугл-почту*?")
rhandler.add_buttons({"Сделано! Что дальше?":"_google_mail_done", "Еще нет, покажи как.":"_google_mail_not_done"})
rhandler.add_branch("_google_mail_not_done")
rhandler.add_message('Окей. Я помогу тебе это сделать.\n*Зайди на Gmail и нажми "Создать аккаунт"*')
rhandler.add_url("https://www.google.com/intl/uk/gmail/about/")
rhandler.add_timer(2)
rhandler.add_message('Далее следуй инструкции Gmail...')
rhandler.add_buttons({"И вот еще подсказки":"_google_mail_not_done_2"})
rhandler.add_branch("_google_mail_not_done_2")
rhandler.add_message('Запрос на закрепление номера телефона к аккаунту - нажми "Пропустить"')
rhandler.add_timer(2)
rhandler.add_message('*Номер телефона не указывай!*\nКак резервную почту, можешь указать - niko@rh-s.com\nУкажи свою дату рождения и свой пол.')
rhandler.add_timer(2)
rhandler.add_message('*Принимай правила Google*, пролистывай их до конца.\nhttps://youtu.be/7rVH13AHp5o')
rhandler.add_timer(2)
rhandler.add_message('Вуаля! Почта готова!')
rhandler.add_buttons({"Круто! Что дальше?":"_google_mail_done", "Обратная связь":"_feedback"})
rhandler.add_branch("_google_mail_done")
rhandler.add_message("Ты уже настроил Хром-пользователя?")
rhandler.add_buttons({"Сделано! Что дальше?":"_chrome_user_done", "Нет, покажи как.":"_chrome_user_not_done"})
rhandler.add_branch("_chrome_user_not_done")
rhandler.add_message("Окей. Я помогу тебе это сделать.\nОткрой браузер Гугл Хром. Нажми на окошко пользователя в верхнем правом углу. Кликай *Управлять пользователями*")
rhandler.add_timer(3)
rhandler.add_picture("хромпользователь1.png")
rhandler.add_timer(3)
rhandler.add_message("Выбери *Добавить пользователя* в нижнем правом углу.\nНазови своего пользователя так *ИМЯ_LinkedIn*.\nДобавь аватарку.\nПоставь галочку *Создать ярлык этого профиля на рабочем столе*.\nНажми *Добавить*.")
rhandler.add_timer(3)
rhandler.add_picture("хромпользователь3.png")
rhandler.add_timer(3)
rhandler.add_message("Подключи рабочую почту, которую ты создал, к Хром-пользователю.\nhttps://youtu.be/7rVH13AHp5o")
rhandler.add_timer(10)
rhandler.add_message("Вуаля! Новый пользователь ГуглХром готов.\n_Автоматически откроется новая вкладка Хрома под новым пользователем_.\n_На рабочем столе появился ярлык для входа именно в этого пользователя_.")
rhandler.add_buttons({"Круто! Что дальше?":"_chrome_user_done", "Обратная связь":"_feedback"})
rhandler.add_branch("_chrome_user_done")
rhandler.add_message("Молодец!\nА *Линкедин-аккаунт* уже сделал?")
rhandler.add_buttons({"Сделано! Что дальше?":"_linkedin_account_done", "Еще нет, покажи, как.":"_linkedin_account_not_done"})
rhandler.add_branch("_linkedin_account_not_done")
rhandler.add_message("Окей, я помогу тебе создать аккаунт на Линкедин\n_Нажми на кнопку_")
rhandler.add_buttons({"Шаг первый":"_linkedin_account_not_done_1"})
rhandler.add_branch("_linkedin_account_not_done_1")
rhandler.add_message("1) Зайди на LinkedIn.\n2) Начни регистрацию.\n3) *Зарегистрируй профиль Линкедин на Гугл-почту, которую ты создал ранее*.\nВАЖНО: *вся информация в твоем профиле должна быть на английском* так, как вся переписка с лидами ведется именно на этом языке.\nhttps://youtu.be/SlvxQQTFFxg")
rhandler.add_url("https://www.linkedin.com/")
rhandler.add_timer(3)
rhandler.add_message("Готов?\nПереходи ко второму шагу")
rhandler.add_buttons({"Шаг второй":"_linkedin_account_not_done_2"})
rhandler.add_branch("_linkedin_account_not_done_2")
rhandler.add_message('*Укажи свои настоящие имя и фамилию на английском языке*.\nЗапрещено: указывать никнеймы или сокрашения имени.\n*Загрузи свое фото* \nПараметры фото: портрет, без лишнего фона, желательно более официальное.\n*Переведи профиль на английский язык*\nКак это сделать:\n- в правом верхнем углу ты видишь свое фото\n- нажми на стрелочку под фото\n- откроется меню\n- выбери "Язык/Language"\nЕсли готов, переходи к третьему шагу')
rhandler.add_buttons({"Шаг третий":"_linkedin_account_not_done_3"})
rhandler.add_branch("_linkedin_account_not_done_3")
rhandler.add_message('Поле *Образование/Education*\nУкажи актуальные данные о своем высшем образовании на английском языке.\nЕсли ты еще студент, в поле "Дата окончания" укажи 2020 год или более ранний, а в поле "Дата начала" - год на 4-5 лет раньше.\nГотов? Жми кнопку')
rhandler.add_buttons({"Шаг четвертый":"_linkedin_account_not_done_4"})
rhandler.add_branch("_linkedin_account_not_done_4")
rhandler.add_message('Поле *Опыт работы/Edit experience*\n*Заполни в точности по инструкции*\n- должность: Account manager\n- график работы: Full-time\n- компания: Remote Helpers\n- локация: твое текущее местоположение (Город, Украина)\n- время работы в компании: любой месяц/год до настоящего времени + поставь галочку to present.\nГотово? Жми кнопку')
rhandler.add_buttons({"Шаг пятый":"_linkedin_account_not_done_5"})
rhandler.add_branch("_linkedin_account_not_done_5")
rhandler.add_message('Поле *Навыки/Skills*\n*Указывай скиллы на английском языке*.\nСписок твоих возможных скиллов:\n- Email marketing\n- Lead Generation\n- Social media marketing\n- Online Advertising\n- Data Analysis\n- Searching skills\n- Targeting\n- WordPress\n- English language\n- Design\n- и другие навыки из выпадающего списка.\n*Используй штук 5-8*\nГотово? Жми кнопку')
rhandler.add_buttons({"Шаг шестой":"_linkedin_account_not_done_6"})
rhandler.add_branch("_linkedin_account_not_done_6")
rhandler.add_message('Замени *статус профиля*.\nКак это сделать:\n- открой свой профиль\n- нажми на карандашик справа от фото профиля\n- замени поле *Headline/Статус*\nВарианты замены:\n_Hire online full-time remote employees| Marketing| Content Managers| SMM| Designers| Devs_\n_Dedicated virtual assistants in Ukraine: Lead Generation| SMM| Media| Design| Developers_\n_Build your online team in few clicks| Lead Generation| Marketing| Media| Design| Devs_\nТебе не обязательно копировать слово в слово. Основной посыл: мы предлагаем клиентам расширить их команду, наняв удаленных сотрудников из Украины, специальности видите выше.\nГотово? Жми кнопку')
rhandler.add_buttons({"Шаг седьмой":"_linkedin_account_not_done_7"})
rhandler.add_branch("_linkedin_account_not_done_7")
rhandler.add_message('*Красивая ссылка на твой профиль*\nКак это сделать:\n- зайди на свою страницу\n- _в правом верхнем углу наведи мышку на свое фото, откроется выпадающий список_\n- выбери на нем _View profile_\n- на открывшейся странице в правом верхнем углу нажимаем _Edit public profile & URL_\n- снова в правом верхнем углу нажми на _Edit your custom URL_, внизу будет твоя ссылка и значок карандаша\n- нажми на карандашик и удали все ненужные цифры и символы. Оставь только свое имя и фамилию.\n- нажми _Save_.\nURL обновится в течении нескольких минут.\nГотово? Жми кнопку')
rhandler.add_buttons({"Шаг восьмой":"_linkedin_account_not_done_8"})
rhandler.add_branch("_linkedin_account_not_done_8")
rhandler.add_message('Расширь сеть своих контактов. Добавь в друзья своих коллег.\n*Вариант 1 - зайди на страницу компании Remote Helpers в Линкедин, в раздел сотрудники*\n*Вариант 2 - используй поиск в Гугл*\nsite:linkedin.com remote helpers')
rhandler.add_url("https://www.linkedin.com/mynetwork/")
rhandler.add_url("https://www.google.com/search?q=site%3Alinkedin.com+remote+helpers&oq=site%3Alinkedin.com+remote+helpers&aqs=chrome.0.69i59j69i58j69i60.1079j0j7&sourceid=chrome&ie=UTF-8")
rhandler.add_timer(10)
rhandler.add_message('Вуаля! Профиль в Линкедин готов!')
rhandler.add_buttons({"Далее":"_linkedin_account_done", "Обратная связь":"_feedback"})
# TODO: check access transferred tag
rhandler.add_branch("_linkedin_account_done")
rhandler.add_message('*Отправь логин к Гугл-почте*\n*Пиши прямо в чат*')
rhandler.add_input("google_login")
rhandler.add_message('*Отправь пароль к Гугл-почте*\n*Пиши прямо в чат*')
rhandler.add_input("google_password")
rhandler.add_message('*Отправь логин к Линкедин*\n*Пиши прямо в чат*')
rhandler.add_input("linkedin_login")
rhandler.add_message('*Отправь пароль к Линкедин*\n*Пиши прямо в чат*')
rhandler.add_input("linkedin_password")
rhandler.add_message('Спасибо!\nДля продолжения нажми _Далее_')
rhandler.add_buttons({"Далее":"_academy_registration", "Обратная связь":"_feedback"})
# TODO: google sheets integration
# TODO: add tag access_transferred
rhandler.add_branch("_academy_registration")
rhandler.add_message('Теперь *нажми на кнопку и зарегистрируйся в нашей Академии*. \nДля регистрации можешь использовать данные гугл-почты, которую ты создал сегодня.\nЧтобы легче и быстрее начать работу в отделе Лидогенерации, мы создали целый курс.')
rhandler.add_url("https://oa-y.com/courses/lead-generation/")
rhandler.add_buttons({"Далее":"_last_message", "Обратная связь":"_feedback"})
rhandler.add_branch("_last_message")
rhandler.add_picture("any_questions.jpg")
rhandler.add_message('Я помогу найти ответы.\nНажми на кнопку.')
rhandler.add_buttons({"Ответы":"_questions"})



# All request processing is done here
@app.route("/", methods=["POST"])
def incoming():
    logger.debug(f"recieved request. post data: {request.get_data()}")

    #checking the signature of the request
    if not viber.verify_signature(request.get_data(), request.headers.get("X-Viber-Content-Signature")):
        return Response(status=403)

    viber_request = viber.parse_request(request.get_data())

    # Processing bot subscription request, to start conversation with a bot
    if isinstance(viber_request, ViberConversationStartedRequest):
        viber.send_messages(viber_request.user.id, [RichMediaMessage(rich_media=bm.START_MESSAGE, min_api_version=7)])
    
    # Processing requests during a conversation with a bot
    if isinstance(viber_request, ViberMessageRequest):
        rhandler.handle(request=viber_request)

        # if command == "_question":
        #     # Processing requests with a neural net
        #     message = viber_request.message
            
        #     answers = get_intents(sentence=message.text, 
        #                         all_words=all_words, 
        #                         model=model, 
        #                         tags=tags, 
        #                         intents=intents)
        #     for message in answers:
        #         viber.send_messages(viber_request.sender.id, 
        #                             [TextMessage(text=f"{message}")])
        #     funnel_state = "message"
                

    if isinstance(viber_request, ViberFailedRequest):
        logger.warn(f"Client failed receiving message. failure: {viber_request}")
       
    return Response(status=200)

if __name__ == "__main__":
    app.run(host="localhost", port=8087, debug=True)
