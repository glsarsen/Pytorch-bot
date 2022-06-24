import random
import json
import torch
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

from flask import Flask, request, Response
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage
import logging

from viberbot.api.viber_requests import (
    ViberConversationStartedRequest, 
    ViberFailedRequest,
    ViberMessageRequest, 
    ViberSubscribedRequest, 
    ViberUnsubscribedRequest
    )

TOKEN = "4f5c605073e7e741-801386ee70f8470d-dd779006e2e4d2b8"

app = Flask(__name__)

bot_configuration = BotConfiguration(
    name="Test_Bot",
    avatar="",
    auth_token=TOKEN
)
viber = Api(bot_configuration)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r') as f:
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

bot_name = 'Sam'

@app.route("/", methods=["POST"])
def incoming():
    logger.debug(f"recieved request. post data: {request.get_data()}")
    if not viber.verify_signature(request.get_data(), request.headers.get("X-Viber-Content-Signature")):
        return Response(status=403)

    viber_request = viber.parse_request(request.get_data())
    
    if isinstance(viber_request, ViberMessageRequest):
        message = viber_request.message
         
        sentence = message.text
        # if sentence == 'quit':
        #     break
        # else:
        sentence = tokenize(sentence)
        x = bag_of_words(sentence, all_words)
        x = x.reshape(1, x.shape[0])
        x = torch.from_numpy(x)

        output = model(x)
        _, predicted = torch.max(output, dim=1) # 0
        tag = tags[predicted.item()]

        probs = torch.softmax(output, dim=1)
        prob = probs[0][predicted.item()]

        if prob.item() > 0.75:
            for intent in intents['intents']:
                if tag == intent['tag']:
                    viber.send_messages(viber_request.sender.id, [TextMessage(text=f"{bot_name}: {random.choice(intent['responses'])}")])
        else:
            viber.send_messages(viber_request.sender.id, [TextMessage(text=f"{bot_name}: I do not understand...")])

    if isinstance(viber_request, ViberSubscribedRequest):
        viber.send_messages(viber_request.get_user.id, [TextMessage(text="Thanks for subscribing!")])

    if isinstance(viber_request, ViberFailedRequest):
        logger.warn(f"Client failed receiving message. failure: {viber_request}")

    if isinstance(viber_request, ViberConversationStartedRequest):
        viber.send_messages(viber_request.sender.id, [TextMessage(text="Let's chat! type 'quit' to exit")])
       
    return Response(status=200)

if __name__ == "__main__":
    app.run(host="localhost", port=8087, debug=True)
