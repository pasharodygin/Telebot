import telebot
import requests
from telebot import types
from bs4 import BeautifulSoup as BS
import config
import pymorphy2
import openpyxl

bot = telebot.TeleBot(config.TOKEN)
excel_file = openpyxl.load_workbook('calendar.xlsx')
olymps = excel_file['Уровни']


def print_olymp(message: types.Message):
    mess1 = str()
    for x in range(3, 22):
        mess1 += f'\U0001F538 {olymps.cell(row=x, column=2).value}\n'
    bot.send_message(message.chat.id, mess1, parse_mode='html')


def print_day(n):
    morph = pymorphy2.MorphAnalyzer()
    day = morph.parse('день')[0]
    print(n, day.make_agree_with_number(n).word)


def parser(url):
    r = requests.get(url)
    soup = BS(r.text, 'html.parser')
    olymps = soup.find_all('ul', class_="events")
    only_text = [c for c in olymps]
    ans = []
    for olymp in only_text:
        date = olymp.find('div', class_="ecwd-date").text
        time = olymp.find('div', class_="ecwd-time").text
        name = olymp.find('div', class_="event-details-title").text
        if '-' in time:
            time = time[:8] + ' ' + time[8:]
        else:
            time = ' ' + time
        ans.append(date + name + time)
    return ans


def wrong_request(message: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    mess = 'Наш бот не может распознать ваше сообщение, убедитесь, что вы его правильно написали или вернитесь в главное меню'
    btn1 = types.KeyboardButton(text='Вернуться в главное меню')
    kb.add(btn1)
    bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=kb)


list_of_olymps = parser(config.URL1)


@bot.message_handler(commands=['start'])
def start(message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton(text='Олимпиады РСОШ 22-23')
    btn2 = types.KeyboardButton(text='Узнать уровень ОЛИМПИАДЫ')
    btn3 = types.KeyboardButton(text='Получить ссылку на сайт олимпиады')
    kb.add(btn1, btn2, btn3)
    mess = f'Привет, <b>{message.from_user.first_name}!</b>'
    mess1 = f'Используй <b>меню кнопок</b> для дальнейшей работы'
    bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=kb)
    bot.send_message(message.chat.id, mess1, parse_mode='html')


@bot.message_handler(commands=['website'])
def website(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Перейти на сайт ИТМО", url="https://itmo.ru"))
    bot.send_message(message.chat.id, "Перейдите на сайт", parse_mode='html', reply_markup=markup)


@bot.message_handler(func=lambda x: x.text == 'Вернуться в главное меню')
def return_(message: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton(text='Олимпиады РСОШ 22-23')
    btn2 = types.KeyboardButton(text='Узнать уровень ОЛИМПИАДЫ')
    btn3 = types.KeyboardButton(text='Получить ссылку на сайт олимпиады')
    kb.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, "Теперь вы находитесь в главном меню, продолжайте работу", reply_markup=kb)


@bot.message_handler(func=lambda msg: msg.text == "Узнать уровень ОЛИМПИАДЫ")
def if_sp(message: types.Message):
    mess1 = 'Чтобы узнать уровень олимпиады, введите: \n<i>узнать уровень <b>название олимпиады</b></i>\nНапример: узнать уровень Высшая проба'
    bot.send_message(message.chat.id, mess1, parse_mode='html')


@bot.message_handler(func=lambda msg: msg.text == "Узнать подробнее об этой олимпиаде")
def if_sp(message: types.Message):
    mess1 = 'Чтобы узнать уровень олимпиады, введите: \n<i>узнать уровень <b>название олимпиады</b></i>\nНапример: узнать уровень Высшая проба'
    bot.send_message(message.chat.id, mess1, parse_mode='html')


@bot.message_handler(func=lambda msg: msg.text == "Вывести все олимпиады")
def if_sp(message: types.Message):
    print_olymp(message)


@bot.message_handler(content_types=['text'])
def olympiadas(message):
    text = message.text
    ans = []
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    if message.text.isdigit():
        for s in list_of_olymps:
            ans.append(s)
        if len(ans) == 0:
            print('\uE333УВЫ! В это месяце нет олимпиад по информатике')
        else:
            bot.send_message(message.chat.id, '\n'.join(ans))
    elif len(text) > 15 and text[:15].lower() == 'узнать уровень ':
        text = str(text[15:]).lower()
        line = 0
        for x in range(3, 22):
            if text in str(olymps.cell(row=x, column=2).value).lower():
                line = x
                break
        if line == 0:
            kb.row('Вернуться в главное меню', 'Вывести все олимпиады')
            error = '\u274CОлимпиада находится не в списке РСОШ или вы ошиблись в названии'
            btn = "Вернуться"
            mess = f'Нажми на кнопку {btn} или ознакомься со списком всех олимпиад'
            bot.send_message(message.chat.id, error, reply_markup=kb)
            bot.send_message(message.chat.id, mess)
        else:
            kb.row('Вернуться в главное меню', 'Получить ссылку на сайт олимпиады')
            k = olymps.cell(row=line, column=4).value
            bot.send_message(message.chat.id, f'УРОВЕНЬ: {k}\n', reply_markup=kb)
    else:
        wrong_request(message)


bot.polling()
