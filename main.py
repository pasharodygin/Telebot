import telebot
import requests
from telebot import types
from bs4 import BeautifulSoup as BS
import config
import pymorphy2

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
    mess = f'Привет, <b>{message.from_user.first_name}\U0001F92E!</b>'
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


@bot.message_handler(content_types=['text'])
def olympiadas(message):
    text = message.text
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if message.text.isdigit():
        ans = []
        for s in list_of_olymps:
            ans.append(s)
        if len(ans) == 0:
            print('УВЫ! В это месяце нет олимпиад')

        bot.send_message(message.chat.id, '\n'.join(ans))
    #elif text == 'Узнать уровень ОЛИМПИАДЫ':


bot.infinity_polling(skip_pending=True)
