from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, User, CallbackQuery
from aiogram_dialog import Dialog, DialogManager, StartMode, Window, setup_dialogs
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.kbd import Group, Column, Radio, Select, Button, SwitchTo, Next, Back, Start, Cancel
from aiogram_dialog.api.entities import MediaAttachment
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput, MessageInput
from aiogram.enums import ContentType
from environs import Env
import operator
import requests, os
from typing import Any
from other import check_way


env = Env()
env.read_env()


bot = Bot(token=env('BOT_TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()

class StartSG(StatesGroup):
    start = State()
    second = State()


class SecondSG(StatesGroup):
    start = State()
    second = State()

class InpitSG(StatesGroup):
    first = State()
    second = State()

async def get_city(dialog_manager: DialogManager, **kwargs):
    list_city = [
        'Москва',
        'Лондон',
        'Варшава',
        'Лестер',
        'Монако',
        'Стамбул',
        'Дубай',
        'q',
    ]
    dialog_manager.dialog_data.update(list_city = list_city)
    return {'result': [(str(i), city) for i, city in enumerate(list_city)]}


async def weather_show(callback: CallbackQuery, widget: Select,
                            dialog_manager: DialogManager, item_id: str):
    list_city = dialog_manager.dialog_data.get('list_city')
    url = 'https://api.openweathermap.org/data/2.5/weather'
    weather_items = {
    'q': list_city[int(item_id)], #город
    'appid': 'bbb83a07f5323c28aab81812b9d816bc',
    'units': 'metric',
    'lang': 'ru',
}
    response = requests.get(url, params=weather_items)
    if response.status_code == 200:
        data = response.json()
        await dialog_manager.start(state=SecondSG.start, data={'weather': data, 'city': list_city[int(item_id)]})
    else:
        print(f"Ошибка: {response.status_code} = {response.text}")
        await dialog_manager.switch_to(state=StartSG.second)

async def weatheer_getter(dialog_manager: DialogManager, **kwargs):
    city = dialog_manager.start_data.get('city')
    path  = check_way(city)
    if os.path.exists(path):
        picture_path = MediaAttachment(type=ContentType.PHOTO, path=path)
    else:
        picture_path = MediaAttachment(type=ContentType.PHOTO, path='C:/Users/Home/Desktop/CITY/macan.jpg')
    weather = dialog_manager.start_data['weather']
    weather_1 = weather['weather'][0]['description']
    weather_2 = weather['main']['temp']
    weather_3 = weather['wind']['speed']
    return {'weather_1' : weather_1,
            'weather_2': weather_2,
            'weather_3': weather_3,
            'picture': picture_path}

def check_text(city: str):
    if not city.isdigit(): return city
    raise ValueError


async def correct_handler(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    url = 'https://api.openweathermap.org/data/2.5/weather'
    weather_items = {
    'q': text, #город
    'appid': 'bbb83a07f5323c28aab81812b9d816bc',
    'units': 'metric',
    'lang': 'ru',
}
    response = requests.get(url, params=weather_items)
    if response.status_code == 200:
        data = response.json()
        await dialog_manager.start(state=InpitSG.first, data={'data': data, 'city': text})
    else:
        await dialog_manager.start(state=InpitSG.second)

async def error_handler(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, error: ValueError):
    await dialog_manager.start(state=InpitSG.second)

async def input_getter(dialog_manager: DialogManager, **kwargs):
    weather = dialog_manager.start_data.get('data')
    weather_1 = weather['weather'][0]['description']
    weather_2 = weather['main']['temp']
    weather_3 = weather['wind']['speed']
    city = dialog_manager.start_data.get('city')
    path = check_way(city)
    if path:
        picture = MediaAttachment(type=ContentType.PHOTO, path=path)
    else: 
        picture = MediaAttachment(type=ContentType.PHOTO, path='C:/Users/Home/Desktop/CITY/macan_1.webp')
    return {'weather_1' : weather_1,
            'weather_2': weather_2,
            'weather_3': weather_3,
            'picture': picture}    
    
async def macan_getter(dialog_manager: DialogManager, **kwargs):
    picture_path = MediaAttachment(type=ContentType.PHOTO, path='C:/Users/Home/Desktop/CITY/macan.jpg')
    return {'picture': picture_path}

async def no_text(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    await dialog_manager.start(state=InpitSG.second)


start_dialog = Dialog(
    Window(
        Const('Выберете город в котором хотите узнать погоду'),
        Column(
            Radio(
                checked_text=Format('🔘 {item[1]}'),
                unchecked_text=Format('⚪️ {item[1]}'),
                id='city',
                item_id_getter=operator.itemgetter(0),
                items='result',
                on_click=weather_show,
            ),
        ),
        TextInput(
            id='city',
            type_factory=check_text,
            on_success=correct_handler,
            on_error=error_handler,
        ),
        MessageInput(
            func=no_text,
            content_types=ContentType.ANY,
        ),
        state=StartSG.start,
        getter=get_city,
    ),
    Window(
        Const(text='БАлбес такого города нет, баран'),
        Back(text=Const('◀️ Назад'), id='back'),
        state=StartSG.second,
    ),
)


second_dialog = Dialog(
    Window(
        Format('Погода в общем и целом: {weather_1}\nТемепература воздуха: {weather_2}\nСкорость ветра: {weather_3}'),
        Cancel(text=Const('◀️ Назад'), id='back'),
        DynamicMedia('picture'),
        state=SecondSG.start,
        getter=weatheer_getter,
    ),
)

input_user = Dialog(
    Window(
        Format('Погода в общем и целом: {weather_1}\nТемепература воздуха: {weather_2}\nСкорость ветра: {weather_3}'),
        Cancel(text=Const('◀️ Назад'), id='back'),
        DynamicMedia('picture'),
        state= InpitSG.first,
        getter=input_getter,
    ),
    Window(
        Const(text='МАКАНЫЧ'),
        Cancel(text=Const('◀️ Назад'), id='back'),
        DynamicMedia('picture'),
        state=InpitSG.second,
        getter=macan_getter,
    )
)





@router.message(CommandStart())
async def start_command(msg: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=StartSG.start, mode=StartMode.RESET_STACK)


dp.include_router(router)
dp.include_routers(start_dialog, second_dialog, input_user)
setup_dialogs(dp)
dp.run_polling(bot)
