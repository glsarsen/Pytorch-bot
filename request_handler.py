from abc import abstractmethod
from time import sleep

from flask import url_for
from viber_config import viber
import bot_messages as bm

from viberbot.api.viber_requests import ViberMessageRequest

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


class ElementType():
    TEXT = 'text'
    BRANCH = 'branch'
    PICTURE = 'picture'
    URL = 'url'
    BUTTON = 'button'
    TIMER = 'timer'
    INPUT = 'input'


user_input = dict()
# TODO: make it a class


class Element:
    def __init__(self, type:str, data):
        self._type = type
        self._data = data
    
    @property
    def type(self):
        return self._type
    
    @property
    def data(self):
        return self._data
    
    def __repr__(self):
        return f"Element({self._type}, {self._data})"


class Handler():    
    @abstractmethod
    def handle(self, element: Element, request: ViberMessageRequest):
        return
    
    @abstractmethod
    def set_keyboard(self, keyboard):
        return


class ViberHandler(Handler):
    def __init__(self):
        self._keyboard = None
    
    def handle(self, element: Element, request: ViberMessageRequest):
        global user_input
        if element.type == ElementType.TEXT:
            viber.send_messages(request.sender.id, TextMessage(text=element.data, keyboard=self._keyboard))
        if element.type == ElementType.PICTURE:
            viber.send_messages(request.sender.id, PictureMessage(media=url_for("static", filename=f"pictures/{element.data}", _external=True), keyboard=self._keyboard))
        if element.type == ElementType.BRANCH:
            return
            # it does nothing but indicates the start of a branch
        if element.type == ElementType.URL:
            viber.send_messages(request.sender.id, URLMessage(media=element.data, keyboard=self._keyboard))
        if element.type == ElementType.BUTTON:
            viber.send_messages(request.sender.id, RichMediaMessage(rich_media=bm.buttons(element.data), keyboard=self._keyboard, min_api_version=7))
        if element.type == ElementType.TIMER:
            sleep(element.data)
            # TODO: make it async
        if element.type == ElementType.INPUT:
            user_input[element.data] = request.message.text
            for key, value in user_input.items():
                print(key, value, "\n")
    
    def set_keyboard(self, keyboard):
        self._keyboard = keyboard


class ElementTree():
    def __init__(self, handler):
        self._element_list: list[Element] = []
        self._current_index: int = None
        self._handler: Handler = handler

    def set_handler(self, handler):
        self._handler = handler
        return self
    
    def set_keyboard(self, keyboard):
        self._handler.set_keyboard(keyboard)
        return self
    
    def add_branch(self, branch):
        self.add_element(Element(ElementType.BRANCH, branch))
        return self
    
    def add_message(self, message):
        self.add_element(Element(ElementType.TEXT, message))
        return self
    
    def add_input(self, input):
        self.add_element(Element(ElementType.INPUT, input))
        return self
    
    def add_timer(self, timer):
        self.add_element(Element(ElementType.TIMER, timer))
        return self
    
    def add_picture(self, picture):
        self.add_element(Element(ElementType.PICTURE, picture))
        return self
    
    def add_url(self, url):
        self.add_element(Element(ElementType.URL, url))
        return self

    def add_buttons(self, buttons):
        self.add_element(Element(ElementType.BUTTON, buttons))
        return self

    def add_element(self, element: Element):
        self._element_list.append(element)
        return self
    
    def handle(self, request: ViberMessageRequest):
        if self._current_index is None:
            for index, element in enumerate(self._element_list):
                if element.type == ElementType.BRANCH and element.data == request.message.text:
                    self._current_index = index + 1
                    break
        if self._current_index is not None:
            while self._element_list[self._current_index].type != ElementType.BRANCH:
                self._handler.handle(self._element_list[self._current_index], request)
                self._current_index += 1
                if self._element_list[self._current_index].type == ElementType.INPUT:
                    break
            else:
                self._current_index = None
        return self



# class Element:
#     def __init__(self, type, data):
#         self.type = type    # message | timer | input | branch
#         self.data = data
#         self.next = None
    

# class RequestHandler:
#     def __init__(self):
#         self.first_element: Element = None
#         self.last_element: Element = None
#         self.current_element: Element = None
#         self.keyboard = None
#         self.vars = dict() # user input data

#     def add_branch(self, branch):
#         self.add_element("branch", branch)
#         return self
    
#     def add_message(self, message):
#         self.add_element("message", message)
#         return self
    
#     def add_timer(self, time):
#         self.add_element("timer", time)
#         return self

#     def add_input(self, name):
#         self.add_element("input", name)
#         return self
    
#     def add_element(self, type, data:TypedMessage):
#         new_element = Element(type, data)
#         if self.first_element is None:
#             self.first_element = new_element
#             self.last_element = new_element
#         else:
#             self.last_element.next = new_element
#             self.last_element = new_element
#         return self
    
#     def set_keyboard(self, keyboard):
#         self.keyboard = keyboard
#         return self
    
#     def handle(self, request:ViberMessageRequest):
#         element = self.current_element # starting from last unhandled element in chain (if available)
#         if element is None:
#             element = self.first_element.next # otherwise starting from the start of a chain
#             while True:
#                 if element is None: # when there is no more elements in chain
#                     return
#                 if element.type == "branch" and element.data == request.message.text: # found the correct chain branch
#                     element = element.next
#                     break
#                 element = element.next
#         if element.type == "input": # handle the input and continue
#             self.vars[element.data] = request.message.text
#             self.current_element = self.current_element.next
#         while element.type != "branch": # handle messages in chain until the next chain branch
#             if element.type == "message":
#                 if self.keyboard:
#                     viber.send_messages(request.message.id, element.data.from_dict(self.keyboard))
#                 else:
#                     viber.send_messages(request.message.id, element.data)
#             if element.type == "timer":
#                 sleep(element.data)
#             if element.type == "input":
#                 self.current_element = element # remember the current element to handle the next request with
#                 break