import telebot
import requests
from telebot import types
from bs4 import BeautifulSoup as BS
import config
import pymorphy2
import openpyxl

bot = telebot.TeleBot(config.TOKEN)


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


list_of_olymps = parser(config.URL1)


@bot.message_handler(commands=['start'])
def start(message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton(text='Олимпиады РСОШ 22-23')
    btn2 = types.KeyboardButton(text='Узнать уровень ОЛИМПИАДЫ')
    kb.add(btn1, btn2)
    mess = f'Привет, <b>{message.from_user.first_name}!</b>'
    mess1 = f'Чтобы увидеть весь список олимпиад на ТЕКУЩИЙ МЕСЯЦ введите любое число: '
    bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=kb)
    bot.send_message(message.chat.id, mess1, parse_mode='html')


@bot.message_handler(commands=['website'])
def website(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Перейти на сайт ИТМО", url="https://itmo.ru"))
    bot.send_message(message.chat.id, "Перейдите на сайт", parse_mode='html', reply_markup=markup)


@bot.message_handler(commands=['get_update'])
def upd(message):
    bot.send_message(message.chat.id, 'я тебе не скажу новостей, ты маленький ещё!!', parse_mode='html')


@bot.message_handler(func=lambda x: x.text == 'Вернуться в главное меню')
def return_(message: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton(text='Олимпиады РСОШ 22-23')
    btn2 = types.KeyboardButton(text='Узнать уровень ОЛИМПИАДЫ')
    kb.add(btn1, btn2)
    bot.send_message(message.chat.id, "Теперь вы находитесь в главном меню, продолжайте работу", reply_markup=kb)


@bot.message_handler(func=lambda msg: msg.text == "Узнать уровень ОЛИМПИАДЫ")
def if_sp(message: types.Message):
    mess1 = 'Чтобы узнать уровень олимпиады, введите: \n<i>узнать уровень <b>название олимпиады</b></i>\nНапример: узнать уровень Высшая проба'
    bot.send_message(message.chat.id, mess1, parse_mode='html')


@bot.message_handler(content_types=['text'])
def olympiadas(message):
    text = message.text
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    ans = []
    if message.text.isdigit():
        for s in list_of_olymps:
            ans.append(s)
        if len(ans) == 0:
            print('УВЫ! В это месяце нет олимпиад по информатике')
        else:
            bot.send_message(message.chat.id, '\n'.join(ans))
    elif text[:15] == 'узнать уровень ':
        text = str(text[:15]).lower()
        text.replace('олимпиада', '')
        text.replace('открытая', '')
        excel_file = openpyxl.load_workbook('calendar.xlsx')
        olymps = excel_file['Уровни']
        line = 0
        for x in range(3, 22):
            if text in str(olymps.cell(row=x, column=2).value).lower():
                line = x
        if line == 0:
            kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
            kb.row('Вернуться в главное меню')
            error = 'Олимпиада находится не в списке РСОШ или вы ошиблись в названии'
            btn = "Вернуться"
            mess = f'Нажмите на кнопку {btn} и попробуйте ещё раз'
            bot.send_message(message.chat.id, error, reply_markup=kb)
            bot.send_message(message.chat.id, mess)
        else:
            kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
            kb.row('Вернуться в главное меню', 'Узнать подробнее об этой олимпиаде')
            data = []
            for x in range(1, 6):
                data.append(olymps.cell(row=line, column=x).value)
            bot.send_message(message.chat.id, f'УРОВЕНЬ: {data[3]}\n')



bot.infinity_polling(skip_pending=True)
