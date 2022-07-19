BG_COLOR = "#FFFFFF"
BUTTON_BG_COLOR = "#69C48A"

START_MESSAGE = {
    "Type":"rich_media",
    "BgColor": BG_COLOR,
    "ButtonsGroupRows": 3,
    "Text": "Testing richmedia text",
    "Buttons": [
        {
            "Columns": 6,
            "Rows": 2,
            "Silent": "true",
            "ActionType": "none",
            "TextVAlign": "middle",
            "TextHAlign": "center",
            "Text": "Добро пожаловать в компанию!\nЧтобы подписаться на бота нажми кнопку 'Начать'"
        },
        {
            "Columns": 6,
            "Rows": 1,
            "BgColor": BUTTON_BG_COLOR,
            "Silent": "true",
            "ActionType": "reply",
            "ActionBody": "_start",
            "TextVAlign": "middle",
            "TextHAlign": "center",
            "TextOpacity": 99,
            "Text": "Начать"
        }
    ]
}

NEW_USER_MENU = {
        "Type": "keyboard",
        "BgColor": BG_COLOR,
        "Buttons": [
            {
            "Columns": 2,
            "Rows": 1,
            "BgColor": BUTTON_BG_COLOR,
            "Silent": "true",
            "ActionType": "reply",
            "ActionBody": "_new_user",
            "TextVAlign": "middle",
            "TextHAlign": "center",
            "TextOpacity": 99,
            "Text": "Новый сотрудник"
            },
            {
            "Columns": 2,
            "Rows": 1,
            "BgColor": BUTTON_BG_COLOR,
            "Silent": "true",
            "ActionType": "reply",
            "ActionBody": "_employed_user",
            "TextVAlign": "middle",
            "TextHAlign": "center",
            "TextOpacity": 1,
            "Text": "Уже работаешь с нами"
            },
            {
            "Columns": 2,
            "Rows": 1,
            "BgColor": BUTTON_BG_COLOR,
            "Silent": "true",
            "ActionType": "reply",
            "ActionBody": "_restart",
            "TextVAlign": "middle",
            "TextHAlign": "center",
            "TextOpacity": 1,
            "Text": "Вернуться на старт"
            }
        ]
}

# TODO: check if needed, if not - remove
SAMPLE_RICH_MEDIA = {
    "Type": "rich_media",
    "BgColor": BG_COLOR,
    "ButtonsGroupRows": 2,
    "Buttons": [
        {
        "Columns": 6,
        "Rows": 1,
        "BgColor": BUTTON_BG_COLOR,
        "Silent": "true",
        "ActionType": "reply",
        "ActionBody": "test1",
        "TextVAlign": "middle",
        "TextHAlign": "center",
        "TextOpacity": 99,
        "Text": "<b>example</b> button"
        },
        {
        "Columns": 6,
        "Rows": 1,
        "BgColor": BUTTON_BG_COLOR,
        "Silent": "true",
        "ActionType": "reply",
        "ActionBody": "test2",
        "TextVAlign": "middle",
        "TextHAlign": "center",
        "TextOpacity": 1,
        "Text": "<b>example</b> button"
        }
    ]
    }

def buttons(buttons_dict:dict):
    buttons_count = len(buttons_dict) if 0 < len(buttons_dict) <= 7 else 7
    RICH_MEDIA = {
        "Type":"rich_media",
        "BgColor": BG_COLOR,
        "ButtonsGroupRows": buttons_count,
        "Buttons": []
        }
    for key, value in buttons_dict.items():
        RICH_MEDIA["Buttons"].append(
            {
            "Columns": 6,
            "Rows": 1,
            "BgColor": BUTTON_BG_COLOR,
            "Silent": "true",
            "ActionType": "reply",
            "ActionBody": value,
            "TextVAlign": "middle",
            "TextHAlign": "center",
            "TextOpacity": 99,
            "Text": key
            }
            )
    return RICH_MEDIA