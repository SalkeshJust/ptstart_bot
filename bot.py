import logging
import re

import paramiko
import os

import psycopg2
from psycopg2 import Error

from dotenv import load_dotenv

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

load_dotenv()

TOKEN = os.getenv('TOKEN')
global write_to_db



# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO
)
logging.info("Начало программы")

logger = logging.getLogger(__name__)

def connectSSH():
    logging.info('Подключение по SSH')

    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    return client

clientSSH = connectSSH()

def selectDB(update: Update, cursor, command):
    cursor.execute(command)
    data = cursor.fetchall()
    message = ''
    for row in data:
        message += ('. '.join([str(i) for i in row])) + '\n'
    update.message.reply_text(message)
    logging.info("Команда успешно выполнена")

def insertDB(cursor, command):
    cursor.execute(command)
    logging.info("Команда успешно выполнена")


def connectDB(dbuser, dbpass, dbhost, dbport, dbname):
    connection = psycopg2.connect(user=dbuser,
                            password=dbpass,
                            host=dbhost,
                            port=dbport, 
                            database=dbname)
    return connection
def workDB(update: Update, command):
    connection = None
    dbuser = os.getenv('DB_USER')
    dbpass = os.getenv('DB_PASSWORD')
    dbhost = os.getenv('DB_HOST')
    dbport = os.getenv('DB_PORT')
    dbname = os.getenv('DB_DATABASE')
    try:
        connection = connectDB(dbuser,
                                dbpass,
                                dbhost,
                                dbport,
                                dbname)

    except (Exception, Error):
        dbuser = os.getenv('DB_REPL_USER')
        dbpass = os.getenv('DB_REPL_PASSWORD')
        dbhost = os.getenv('DB_REPL_HOST')
        dbport = os.getenv('DB_REPL_PORT')
        connection = connectDB(dbuser,
                                dbpass,
                                dbhost,
                                dbport,
                                dbname)
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS Emails(Email_id SERIAL, Email VARCHAR(225));")
        connection.commit()
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS PhoneNumbers(PhoneNumber_id SERIAL, PhoneNumber VARCHAR(20));")
        connection.commit()
        cursor = connection.cursor()
        if ("SELECT" in command):
            selectDB(update, cursor, command)
        else:
            insertDB(cursor, command)
            connection.commit()
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
        update.message.reply_text(f"Ошибка при работе с PostgreSQL: {error}")
    finally:
        if connection is not None:
            cursor.close()
            connection.close()
            logging.info("Соединение с PostgreSQL закрыто")

def start(update: Update, context):
    logging.info('Приветствие пользователя')
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')


def helpCommand(update: Update, context):
    logging.info('Команда /help')
    update.message.reply_text('В данном боте вы можете воспользоваться следующими командами: \n/find_email - поиск почт в сообщении\n/find_phone_number - поиск мобильных номеров в сообщении\n/verify_password - проверка сложности пароля\n/get_release - О релизе подключенной к боту по SSH ОС\n/get_uname - Об архитектуре процессора подключенной к боту по SSH ОС\n/get_uptime - Время запуска подключенной к боту по SSH ОС\n/get_df - Состояние файловой системы подключенной к боту по SSH ОС\n/get_free - Состояние оперативной памяти подключенной к боту по SSH ОС\n/get_mpstat - Информация о производительности подключенной к боту по SSH ОС\n/get_w - Работающие пользователи в подключенной к боту по SSH ОС\n/get_auths - 10 последних вошедших пользователей подключенной к боту по SSH ОС\n/get_critical - 5 последних критических событий подключенной к боту по SSH ОС\n/get_ps - Запущенные процессы подключенной к боту по SSH ОС\n/get_ss - Работающие порты подключенной к боту по SSH ОС\n/get_apt_list - Информация о загруженных пакетах  и поиск пакетов на подключенной к боту по SSH ОС\n/get_services - Работающие сервисы на подключенной к боту по SSH ОС\n/get_repl_logs - Возвращает логи репликации\n/get_emails - Выводит таблицу номеров\n/get_phone_numbers - Выводит таблицу номеров')


def findPhoneNumbersCommand(update: Update, context):
    logging.info('Начало find_phone_numbers')
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')

    return 'find_phone_number'

def findEmailsCommand(update: Update, context):
    logging.info('Начало find_email')
    update.message.reply_text('Введите текст для поиска emailов: ')

    return 'find_email'

def checkPassCommand(update: Update, context):
    logging.info('Начало verify_password')
    update.message.reply_text('Введите пароль для проверки его сложности: ')

    return 'verify_password'

def getAptListCommand(update: Update, context):
    logging.info('Начало get_apt_list')
    update.message.reply_text('Введите --all если хотите получить данные обо всех установленных пакетах и --find [имя пакета] если хотите узнать данные о конкретном пакете')
        
    return 'get_apt_list' 


def findPhoneNumbers (update: Update, context):
    global write_to_db
    user_input = update.message.text # Получаем текст, содержащий(или нет) номера телефонов
    logging.info('Получено сообщение для поиска номеров')

    phoneNumRegex = re.compile(r'(?:\+7|8)\s?(?:\(|-)?\d{3}(?:\)|-)?\s?\d{3}(?:(?:-|\s)?\d{2}){2}')

    phoneNumberList = phoneNumRegex.findall(user_input) # Ищем номера телефонов

    if not phoneNumberList: # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END# Завершаем выполнение функции
    write_to_db = phoneNumberList
    logging.info(f'Найдено {len(phoneNumberList)} номеров')
    phoneNumbers = '' # Создаем строку, в которую будем записывать номера телефонов
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{i+1}. {phoneNumberList[i]}\n' # Записываем очередной номер
    
    logging.info('Номера записаны в список')
    update.message.reply_text(phoneNumbers) # Отправляем сообщение пользователю
    update.message.reply_text("Введите --write если хотите записать данные в таблицу, иначе любой другой текст")
    logging.info('Список номеров отправлен. Конец поиска номеров.')
    return 'write_phone_number'

def findEmails (update: Update, context):
    global write_to_db
    user_input = update.message.text # Получаем текст, содержащий(или нет) имейлы
    logging.info('Получено сообщение для поиска почт')
    emailRegex = re.compile(r"\b [a-zA-Z0-9._%+-]+(?<!\.\.)@[a-zA-Z0-9.-]+(?<!]+(?<!\.)\.[a-zA-Z]{2,}\b")

    emailList = emailRegex.findall(user_input) # Ищем имейлы

    if not emailList: # Обрабатываем случай, когда имейлов нет
        update.message.reply_text('Почты не найдены')
        return ConversationHandler.END# Завершаем выполнение функции
    logging.info(f'Найдено {len(emailList)} почт')
    write_to_db = emailList
    emails = '' # Создаем строку, в которую будем записывать имейлы
    for i in range(len(emailList)):
        emails += f'{i+1}. {emailList[i]}\n' # Записываем очередной имейл
    logging.info('Почты записаны в список')
    update.message.reply_text(emails) # Отправляем сообщение пользователю
    update.message.reply_text("Введите --write если хотите записать данные в таблицу, иначе любой другой текст")
    logging.info('Список почт отправлен. Конец поиска почт.')
    return 'write_email' # Завершаем работу обработчика диалога

def checkPass (update: Update, context):
    user_input = update.message.text # Получаем пароль от пользователя
    logging.info('Получен пароль от пользователя')
    strongPass = re.compile(r'(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*()])[0-9a-zA-Z!@#$%^&*()]{8,}')
    logging.info('Начало проверки пароля')
    if strongPass.match(user_input): # Сравниваем пароль пользователя с регулярным выражением
        update.message.reply_text("Пароль сложный")
    else: # Обрабатываем случай, когда пароль не соответствует шаблону
        update.message.reply_text("Пароль простой")
    logging.info('Конец проверки пароля')
    return ConversationHandler.END # Завершаем работу обработчика диалога

def execCommand(command):
    logging.info(f'Исполение команды {command} на kali')
    stdin, stdout, stderr = clientSSH.exec_command(command) # Получаем информацию о системе от сервера
    data = stdout.read() + stderr.read()
    data = data.decode('utf-8')
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    return data

def getRelease (update: Update, context):
    logging.info('Начало работы get_release')
    data = execCommand('lsb_release -a')
    update.message.reply_text(data) # Отправляем отформатированные данные пользователю
    logging.info('Конец работы get_release')
    return ConversationHandler.END

def getUname (update: Update, context):
    logging.info('Начало работы get_uname')
    data = execCommand('uname -a')
    update.message.reply_text(data) # Отправляем отформатированные данные пользователю
    logging.info('Конец работы get_uname')
    return ConversationHandler.END

def getUptime (update: Update, context):
    logging.info('Начало работы get_uptime')
    data = execCommand('uptime')
    update.message.reply_text(data) # Отправляем отформатированные данные пользователю
    logging.info('Конец работы get_uptime')
    return ConversationHandler.END

def getDf (update: Update, context):
    logging.info('Начало работы get_df')
    data = execCommand('df')
    update.message.reply_text(data) # Отправляем отформатированные данные пользователю
    logging.info('Конец работы get_df')
    return ConversationHandler.END

def getFree (update: Update, context):
    logging.info('Начало работы get_free')
    data = execCommand('free')
    update.message.reply_text(data) # Отправляем отформатированные данные пользователю
    logging.info('Конец работы get_free')
    return ConversationHandler.END

def getMpstat (update: Update, context):
    logging.info('Начало работы get_mpstat')
    data = execCommand('mpstat')
    update.message.reply_text(data) # Отправляем отформатированные данные пользователю
    logging.info('Конец работы get_mpstat')
    return ConversationHandler.END

def getW (update: Update, context):
    logging.info('Начало работы get_w')
    data = execCommand('w')
    update.message.reply_text(data) # Отправляем отформатированные данные пользователю
    logging.info('Конец работы get_w')
    return ConversationHandler.END

def getAuths (update: Update, context):
    logging.info('Начало работы get_auths')
    data = execCommand('last -10')
    update.message.reply_text(data) # Отправляем отформатированные данные пользователю
    logging.info('Конец работы get_auths')
    return ConversationHandler.END

def getCritical (update: Update, context):
    logging.info('Начало работы get_critical')
    data = execCommand('journalctl -n 5')
    update.message.reply_text(data) # Отправляем отформатированные данные пользователю
    logging.info('Конец работы get_critical')
    return ConversationHandler.END

def getPs (update: Update, context):
    logging.info('Начало работы get_ps')
    data = execCommand('ps')
    update.message.reply_text(data) # Отправляем отформатированные данные пользователю
    logging.info('Конец работы get_ps')
    return ConversationHandler.END

def getSs (update: Update, context):
    logging.info('Начало работы get_ss')
    data = execCommand('ss -lntu')
    update.message.reply_text(data) # Отправляем отформатированные данные пользователю
    logging.info('Конец работы get_ss')
    return ConversationHandler.END

def getAptList (update: Update, context):
    logging.info('Начало работы get_app_list')
    user_input = update.message.text
    logging.info('Получение режима работы от пользователя')
    if (user_input[:5] == "--all"):
        logging.info('Режим --all')
        data = execCommand('dpkg -l | head -n 10')
        update.message.reply_text(data)
    elif(user_input[:6] == "--find"):
        logging.info('Режим --find')
        exec_command = 'dpkg -s ' + user_input[7:] + ' | head -n 10'
        data = execCommand(exec_command)
        update.message.reply_text(data) # Отправляем отформатированные данные пользователю
    logging.info('Конец работы get_app_list')
    return ConversationHandler.END

def getServices (update: Update, context):
    logging.info('Начало работы get_services')
    data = execCommand('systemctl list-units --type=service --state=running')
    update.message.reply_text(data) # Отправляем отформатированные данные пользователю
    logging.info('Конец работы get_services')
    return ConversationHandler.END

def getReplLogs (update: Update, context):
    logging.info('Начало работы get_repl_logs')
    data = execCommand('docker logs db_repl_image_ --tail 10')
    update.message.reply_text(data) # Отправляем отформатированные данные пользователю
    logging.info('Конец работы get_repl_logs')
    return ConversationHandler.END

def getEmails (update: Update, context):
    logging.info('Начало работы get_emails')
    workDB(update, "SELECT * FROM Emails;")
    logging.info('Конец работы get_emails')
    return ConversationHandler.END

def getPhoneNumbers (update: Update, context):
    logging.info('Начало работы get_emails')
    workDB(update, "SELECT * FROM PhoneNumbers;")
    logging.info('Конец работы get_emails')
    return ConversationHandler.END

def writePhoneNumbers(update: Update, context):
    global write_to_db
    if (update.message.text == "--write"):
        command = "INSERT INTO PhoneNumbers(PhoneNumber) VALUES"
        for i in range (len(write_to_db)):
            if (i + 1 == len(write_to_db)):
                command += '(\''+str(write_to_db[i])+'\');'
                break
            command += '(\''+str(write_to_db[i])+'\'), '
        
        workDB(update, command)
        update.message.reply_text("Данные успешно загружены")
    return ConversationHandler.END

def writeEmails(update: Update, context):
    global write_to_db
    if (update.message.text == "--write"):
        command = "INSERT INTO Emails(Email) VALUES"
        for i in range (len(write_to_db)):
            if (i + 1 == len(write_to_db)):
                command += '(\''+str(write_to_db[i])+'\');'
                break
            command += '(\''+str(write_to_db[i])+'\'), '
        
        workDB(update, command)
        update.message.reply_text("Данные успешно загружены")
    return ConversationHandler.END


def echo(update: Update, context):
    logging.info('Команда эхо')
    update.message.reply_text(update.message.text)


def main():

    logging.info('Начало программы')

    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчик диалога
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'find_phone_number': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
            'write_phone_number': [MessageHandler(Filters.text & ~Filters.command, writePhoneNumbers)],
        },
        fallbacks=[]
    )

    convHandlerFindEmails = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailsCommand)],
        states={
            'find_email': [MessageHandler(Filters.text & ~Filters.command, findEmails)],
            'write_email': [MessageHandler(Filters.text & ~Filters.command, writeEmails)],
        },
        fallbacks=[]
    )

    convHandlerCheckPass = ConversationHandler(
        entry_points=[CommandHandler('verify_password', checkPassCommand)],
        states={
            'verify_password': [MessageHandler(Filters.text & ~Filters.command, checkPass)],
        },
        fallbacks=[]
    )

    convHandlerGetAptList = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', getAptListCommand)],
        states={
            'get_apt_list': [MessageHandler(Filters.text & ~Filters.command, getAptList)],
        },
        fallbacks=[]
    )

    convHandlerGetRelease = CommandHandler('get_release', getRelease)
    convHandlerGetUname = CommandHandler('get_uname', getUname)
    convHandlerGetUptime = CommandHandler('get_uptime', getUptime)
    convHandlerGetDf = CommandHandler('get_df', getDf)
    convHandlerGetFree = CommandHandler('get_free', getFree)
    convHandlerGetMpstat = CommandHandler('get_mpstat', getMpstat)
    convHandlerGetW = CommandHandler('get_w', getW)
    convHandlerGetAuths = CommandHandler('get_auths', getAuths)
    convHandlerGetCritical = CommandHandler('get_critical', getCritical)
    convHandlerGetPs = CommandHandler('get_ps', getPs)
    convHandlerGetSs = CommandHandler('get_ss', getSs)
    convHandlerGetServices = CommandHandler('get_services', getServices)
    convHandlerGetReplLogs = CommandHandler('get_repl_logs', getReplLogs)
    convHandlerGetEmails = CommandHandler('get_emails', getEmails)
    convHandlerGetPhoneNumbers = CommandHandler('get_phone_numbers', getPhoneNumbers)

		
	# Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmails)
    dp.add_handler(convHandlerCheckPass)
    dp.add_handler(convHandlerGetRelease)
    dp.add_handler(convHandlerGetUname)
    dp.add_handler(convHandlerGetUptime)
    dp.add_handler(convHandlerGetDf)
    dp.add_handler(convHandlerGetFree)
    dp.add_handler(convHandlerGetMpstat)
    dp.add_handler(convHandlerGetW)
    dp.add_handler(convHandlerGetAuths)
    dp.add_handler(convHandlerGetCritical)
    dp.add_handler(convHandlerGetPs)
    dp.add_handler(convHandlerGetSs)
    dp.add_handler(convHandlerGetAptList)
    dp.add_handler(convHandlerGetServices)
    dp.add_handler(convHandlerGetReplLogs)
    dp.add_handler(convHandlerGetEmails)
    dp.add_handler(convHandlerGetPhoneNumbers)
		
	# Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    logging.info('Запуск бота')	
	# Запускаем бота
    updater.start_polling()

	# Останавливаем бота при нажатии Ctrl+C
    updater.idle()
    logging.info('Бот остановлен')

if __name__ == '__main__':
    main()
