import telebot
import Classes

lake = Classes.Lake()

bot = telebot.TeleBot('1458109890:AAFXfwEAZLm0UCO_kWOAz9kNCE9GVW_Nqvk')
state_of_user = {}  # здесь словать глобальный, а нужен в рамках сессии.
states = {'знает правила': 'Выбери метод производства на этот ход: грязный/чистый',
          'chosen_way': '''Желаете ли вы что-то купить?
        Покупки на выбор: Лобстер/яхта/тренинг/почистить озеро''',
          'buy_boat': 'Выберите имя для яхты',
          'buy_something': 'Вы закончили с выбором покупок'}


def state(start_state, finish_state):
    def decorator(func):
        @bot.message_handler(func=lambda message: check_user_state(message, start_state))
        def wrapped(message):
            res = func(message)
            if res and type(res) == bool:
                set_user_state(message, finish_state)
                bot.send_message(message.chat.id, states[finish_state])
            elif type(res) == str:
                set_user_state(message, res)
                bot.send_message(message.chat.id, states[res])
            elif res == False and start_state in states:
                bot.send_message(message.chat.id, states[start_state])

        return wrapped

    return decorator


def set_user_state(message, stat):
    state_of_user[message.chat.id] = stat


def check_user_state(message, stat):
    return message.chat.id in state_of_user and state_of_user[message.chat.id] == stat


@bot.message_handler(func=lambda message: message.text, commands=['start', 'help', 'statistics'])
def reactions(message):
    if message.text == '/start':
        lake.add_player(message.chat.id, message.chat.id)
        state_of_user[message.chat.id] = 'start'
        bot.send_message(message.chat.id,
                         '''Добро пожаловать в озеро!
        Есть 3 минуты на правила?''')


@state(start_state='start', finish_state='знает правила')
def send_text_rules(message):
    if message.text.lower() == 'да':
        bot.send_message(message.chat.id, '''Правила''')
    elif message.text.lower() == 'нет':
        bot.send_message(message.chat.id, '''Окей''')
    else:
        bot.send_message(message.chat.id, 'Я не знаю таких команд, выбери из предложенных.')
        return False
    return True
# Тут бот перестал отправлять новые сообщения


@state(start_state='знает правила', finish_state='chosen_way')
def send_text_producing(message):
    if message.text.lower() == 'грязный':  # Запоминаем выбор пользователя
        lake.players[message.chat.id].make_choice('pollute')
        bot.send_message(message.chat.id, 'пользователь использует дедовский грязный способ')

    elif message.text.lower() == 'чистый':  # Запоминаем выбор пользователя
        lake.players[message.chat.id].make_choice('clean')
        bot.send_message(message.chat.id, 'пользователь использует eco-friendly способ производства')
    else:
        bot.send_message(message.chat.id, 'Я не знаю таких команд, выбери из предложенных.')
        return False
    return True


@state(start_state='chosen_way', finish_state='buy_something')  # На будущее - НЕ ВОЗВРАЩАТЬ РАЗНЫЕ ТИПЫ переменных
def send_text_purchase(message):
    player = lake.players[message.chat.id]
    if message.text.lower() == 'лобстер':  # вычитаем из бюджета затраты на лобстера и добавляем его в инвентарь
        if player.buy_lobster():
            bot.send_message(message.chat.id, 'пользователь выбрал лобстера')
        else:
            bot.send_message(message.chat.id, 'Недостаточно средств')
            return False
    elif message.text.lower() == 'яхта':  # вычитаем из бюджета затраты на яхту и добавляем ее в инвентарь

        return 'buy_boat'
    elif message.text.lower() == 'тренинг':  # вычитаем затраты на улучшение, увеличиваем уровень сотрудников на один,
        if player.upgrade_prod_level():
            bot.send_message(message.chat.id, 'пользователь выбрал тренинг')
        else:
            bot.send_message(message.chat.id, 'Недостаточно средств')
            return False
    elif message.text.lower() == 'почистить озеро':  # увеличиваем параметр чистоты озера на 3, вычитаем из бюджета
        if player.clean_lake():
            bot.send_message(message.chat.id, 'пользователь чистит озеро')
        else:
            bot.send_message(message.chat.id, 'Недостаточно средств')
            return False
    elif message.text.lower() == 'нет':
        player.ready = True
        if lake.is_ready():
            lake.proceed_round()
            for i in lake.players:
                bot.send_message(i, f'Все игроки готовы, оцените результат: '
                                    f'{lake.get_stat()}'
                                    f'{lake.players[i].get_stat()}')
                state_of_user[i] = 'знает правила'
                bot.send_message(i, states['знает правила'])
                if lake.water_level < 0:
                    bot.send_message(i, 'Ваши злодейства повлияли на маленькое озеро и вы погубили его. Живите с этим')
            if lake.water_level < 0:
                Classes.error()
            return 'знает правила'
        else:
            bot.send_message(message.chat.id, 'Вы готовы. Дождитесь всех игроков')

        return True
    else:
        bot.send_message(message.chat.id, 'Я не знаю таких команд, выбери из предложенных.')
        return False
    bot.send_message(message.chat.id, player.get_stat())
    return False


@state(start_state='buy_boat', finish_state='chosen_way')
def send_text_boat(message):
    if lake.players[message.chat.id].buy_yacht(message.text):
        pass
    else:
        bot.send_message(message.chat.id, 'Недостаточно средств')
    return True


print(help(bot.message_handler))

bot.polling()
