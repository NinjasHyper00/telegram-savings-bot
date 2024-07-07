import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Connect to the SQLite database
conn = sqlite3.connect('savings.db', check_same_thread=False)
cursor = conn.cursor()

# Function to start the bot and display the main menu
def start(update: Update, context: CallbackContext) -> None:
    main_menu(update)

# Function to display the main menu
def main_menu(update: Update) -> None:
    keyboard = [
        ["🏦 Joint Savings"],
        ["👤 Personal Savings"],
        ["💰 Deposit"],
        ["🏧 Withdraw"],
        ["📜 History"],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text('Welcome! Please choose an option:', reply_markup=reply_markup)

# Function to handle text messages
def handle_message(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    if text == '🏦 Joint Savings':
        total_savings = get_total_savings()
        update.message.reply_text(f"🏦 Joint Savings: ₱{total_savings}")
    elif text == '👤 Personal Savings':
        personal_savings_menu(update)
    elif text in ['Richard', 'Jericha']:
        person = text
        if context.user_data.get('awaiting_deposit_selection'):
            context.user_data['deposit_person'] = text
            context.user_data['awaiting_deposit_selection'] = False
            context.user_data['awaiting_deposit_amount'] = True
            update.message.reply_text(f"Enter the amount to deposit to {person}:")
        elif context.user_data.get('awaiting_withdraw_selection'):
            context.user_data['withdraw_person'] = text
            context.user_data['awaiting_withdraw_selection'] = False
            context.user_data['awaiting_withdraw_amount'] = True
            update.message.reply_text(f"Enter the amount to withdraw from {person}:")
        else:
            savings = get_personal_savings(person)
            update.message.reply_text(f"👤 {person}'s Savings: ₱{savings}")
    elif text == '💰 Deposit':
        deposit_menu(update, context)
    elif text == '🏧 Withdraw':
        withdraw_menu(update, context)
    elif text == '📜 History':
        history_text = get_transaction_history()
        update.message.reply_text(text=history_text)
    elif text == '↩️ Go Back':
        main_menu(update)
    elif context.user_data.get('awaiting_deposit_amount'):
        amount = int(update.message.text)
        person = context.user_data['deposit_person']
        deposit_savings(person, amount)
        context.user_data['awaiting_deposit_amount'] = False
        update.message.reply_text(f"💰 Deposited ₱{amount} to {person}'s savings.")
        main_menu(update)
    elif context.user_data.get('awaiting_withdraw_amount'):
        amount = int(update.message.text)
        person = context.user_data['withdraw_person']
        if withdraw_savings(person, amount):
            update.message.reply_text(f"🏧 Withdrawn ₱{amount} from {person}'s savings.")
        else:
            update.message.reply_text(f"⚠️ Insufficient funds in {person}'s savings.")
        context.user_data['awaiting_withdraw_amount'] = False
        main_menu(update)

# Function to display the personal savings menu
def personal_savings_menu(update: Update) -> None:
    keyboard = [
        ["Richard", "Jericha"],
        ["↩️ Go Back"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text("Select a person:", reply_markup=reply_markup)

# Function to display the deposit menu
def deposit_menu(update: Update, context: CallbackContext) -> None:
    keyboard = [
        ["Richard", "Jericha"],
        ["↩️ Go Back"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text("Select a person to deposit:", reply_markup=reply_markup)
    context.user_data['awaiting_deposit_selection'] = True

# Function to display the withdraw menu
def withdraw_menu(update: Update, context: CallbackContext) -> None:
    keyboard = [
        ["Richard", "Jericha"],
        ["↩️ Go Back"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text("Select a person to withdraw:", reply_markup=reply_markup)
    context.user_data['awaiting_withdraw_selection'] = True

# Function to get total savings
def get_total_savings() -> int:
    cursor.execute("SELECT SUM(amount) FROM savings")
    result = cursor.fetchone()
    return result[0] if result[0] else 0

# Function to get personal savings
def get_personal_savings(person: str) -> int:
    cursor.execute("SELECT amount FROM savings WHERE person = ?", (person,))
    result = cursor.fetchone()
    return result[0] if result else 0

# Function to deposit savings
def deposit_savings(person: str, amount: int) -> None:
    cursor.execute("UPDATE savings SET amount = amount + ? WHERE person = ?", (amount, person))
    cursor.execute("INSERT INTO transactions (person, amount, type) VALUES (?, ?, ?)", (person, amount, "Deposit"))
    conn.commit()

# Function to withdraw savings
def withdraw_savings(person: str, amount: int) -> bool:
    cursor.execute("SELECT amount FROM savings WHERE person = ?", (person,))
    result = cursor.fetchone()
    if result and result[0] >= amount:
        cursor.execute("UPDATE savings SET amount = amount - ? WHERE person = ?", (amount, person))
        cursor.execute("INSERT INTO transactions (person, amount, type) VALUES (?, ?, ?)", (person, amount, "Withdraw"))
        conn.commit()
        return True
    return False

# Function to get transaction history
def get_transaction_history() -> str:
    history_text = "📜 Transaction History:\n"
    cursor.execute("SELECT person, amount, type FROM transactions")
    transactions are cursor.fetchall()
    for transaction in transactions:
        color = "🟢" if transaction[2] == "Deposit" else "🔴"
        history_text += f"{transaction[0]} | ₱{transaction[1]} | {color} {transaction[2]}\n"
    return history_text

def main() -> None:
    # Use your provided token
    updater = Updater("7317646358:AAHxZRBPP1jJTELkqyGFSp3GvL1Ulnjn034")

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
