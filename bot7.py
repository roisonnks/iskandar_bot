import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters
import pandas as pd
import os
from datetime import datetime

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Token
TOKEN = '7392721590:AAEF_tvf1kp3sXyqIr8xUThXnGsSh5PC_SY'

# Department passwords
PASSWORDS = {
    '02': '1985',
    '16': '1979',
    '15': '1974',
    '07': '1986',
    '05': '1980',
    '06': '1985',
    '03': '1976',
    '10': '1988',
    '19': '1984',
    '09': '1986',
    '13': '1973',
    '11': '1968',
    '08': '1985',
    '04': '1989',
    '12': '1973',
    '01': '1979',
    '14': '1987',
    '18': '1988',
    '20': '1979',
    '17': '1992'
}

# Steps
ENTER_DEPARTMENT, ENTER_PASSWORD, SELECT_PERSON, SELECT_ORGANIZATION = range(4)

# Data list
data = []

# File path for current_number
NUMBER_FILE = 'current_number.txt'

# Load current_number from file
def load_current_number():
    if os.path.exists(NUMBER_FILE):
        with open(NUMBER_FILE, 'r') as file:
            return int(file.read().strip())
    return 650  # Default start value

# Save current_number to file
def save_current_number(number):
    with open(NUMBER_FILE, 'w') as file:
        file.write(str(number))

current_number = load_current_number()

department_state = {
    '02': 7,
    '01': 12,
    '16': 6,
    '15': 6,
    '07': 6,
    '05': 6,
    '06': 6,
    '03': 6,
    '10': 6,
    '19': 6,
    '09': 6,
    '13': 6,
    '11': 6,
    '08': 6,
    '04': 6,
    '12': 6,
    '14': 6,
    '18': 6,
    '20': 6,
    '17': 6
}

# Define functions
def start(update, context):
    keyboard = [
        [InlineKeyboardButton("1-Svodniy", callback_data='02')],
        [InlineKeyboardButton("2-Buxugalteriya", callback_data='16')],
        [InlineKeyboardButton("3-O kadr", callback_data='15')],
        [InlineKeyboardButton("4-Cena", callback_data='07')],
        [InlineKeyboardButton("5-MB", callback_data='05')],
        [InlineKeyboardButton("6-Torg", callback_data='06')],
        [InlineKeyboardButton("7-Prom", callback_data='03')],
        [InlineKeyboardButton("8-Budjet", callback_data='10')],
        [InlineKeyboardButton("9-Akt", callback_data='19')],
        [InlineKeyboardButton("10-Trud", callback_data='09')],
        [InlineKeyboardButton("11-Selxoz", callback_data='13')],
        [InlineKeyboardButton("12-Uslug", callback_data='11')],
        [InlineKeyboardButton("13-Registr", callback_data='08')],
        [InlineKeyboardButton("14-Kapstroy", callback_data='04')],
        [InlineKeyboardButton("15-Socialniy", callback_data='12')],
        [InlineKeyboardButton("16-Obshiy Odel", callback_data='01')],
        [InlineKeyboardButton("17-Perepis", callback_data='14')],
        [InlineKeyboardButton("18-Yurist", callback_data='18')],
        [InlineKeyboardButton("19-Profkom", callback_data='20')],
        [InlineKeyboardButton("20-Press slujba", callback_data='17')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Bo'limni tanlang:", reply_markup=reply_markup)
    return ENTER_DEPARTMENT

def enter_department(update, context):
    query = update.callback_query
    context.user_data['department'] = query.data
    query.message.reply_text(f"{query.data.capitalize()} bo'limi uchun parolni kiriting:")
    return ENTER_PASSWORD

def enter_password(update, context):
    department = context.user_data['department']
    if update.message.text == PASSWORDS[department]:
        keyboard = [
            [InlineKeyboardButton("1-T.Ganiev", callback_data='1')],
            [InlineKeyboardButton("2-S.Bekmuratov", callback_data='2')],
            [InlineKeyboardButton("3-K.Omarov", callback_data='3')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Imzolovchini tanlang:', reply_markup=reply_markup)
        return SELECT_PERSON
    else:
        update.message.reply_text('Noto\'g\'ri parol. Qayta urinib ko\'ring:')
        return ENTER_PASSWORD

def select_person(update, context):
    query = update.callback_query
    context.user_data['person'] = query.data
    department = context.user_data['department']
    current_state = department_state.get(department, 7)
    keyboard = [
        [InlineKeyboardButton("1-Yuqari turivch", callback_data=str(current_state))],
        [InlineKeyboardButton("2-tashkilotlarga", callback_data=str(current_state + 1))],
        [InlineKeyboardButton("3-Tumanga", callback_data=str(current_state + 2))],
        [InlineKeyboardButton("4-Murojaat", callback_data=str(current_state + 3))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Tashkilotni tanlang:", reply_markup=reply_markup)
    return SELECT_ORGANIZATION

def select_organization(update, context):
    global current_number
    query = update.callback_query
    context.user_data['organization'] = query.data
    department = context.user_data['department']
    person = context.user_data['person']
    organization = context.user_data['organization']
    record_number = f"01/{person}-{department}-{organization}-{current_number:03}"
    data.append({
        'Department': department,
        'Person': person,
        'Organization': organization,
        'Record Number': record_number
    })
    current_number += 1
    save_current_number(current_number)
    query.edit_message_text(text=f"Yaratilgan raqam: {record_number}")
    return ConversationHandler.END

def export_to_excel(update, context):
    df = pd.DataFrame(data)

    # Map department codes to names for export
    department_names = {
        '02': 'Svodniy',
        '16': 'Buxugalteriya',
        '15': 'O kadr',
        '07': 'Cena',
        '05': 'MB',
        '06': 'Torg',
        '03': 'Prom',
        '10': 'Budjet',
        '19': 'Akt',
        '09': 'Trud',
        '13': 'Selxoz',
        '11': 'Uslug',
        '08': 'Registr',
        '04': 'Kapstroy',
        '12': 'Socialniy',
        '01': 'Obshiy Odel',
        '14': 'Perepis',
        '18': 'Yurist',
        '20': 'Profkom',
        '17': 'Press slujba'
    }

    # Replace department codes with names
    df['Department'] = df['Department'].map(department_names)

    # Add timestamp to the filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filepath = os.path.join(os.getcwd(), f'records_{timestamp}.xlsx')
    df.to_excel(filepath, index=False)
    update.message.reply_text(f"Ma'lumotlar Excel fayliga yuklandi: {filepath}")

def cancel(update, context):
    update.message.reply_text('Bekor qilindi.')
    return ConversationHandler.END

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Define the conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ENTER_DEPARTMENT: [CallbackQueryHandler(enter_department)],
            ENTER_PASSWORD: [MessageHandler(Filters.text & ~Filters.command, enter_password)],
            SELECT_PERSON: [CallbackQueryHandler(select_person)],
            SELECT_ORGANIZATION: [CallbackQueryHandler(select_organization)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler('export', export_to_excel))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()