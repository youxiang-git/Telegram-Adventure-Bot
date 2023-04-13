import logging
import constants_secrets
import openai
import requests
from telegram import Bot ,InlineKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (Application, CommandHandler, ContextTypes,
                          ConversationHandler, MessageHandler, filters)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

INPUT_PLAYER_NUM, INPUT_PLAYER_NAMES, GAME_IN_PROGRESS = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! I'm the game-master-bot for your new adventure!\n"
                                    "Send /cancel to end the game and stop talking to me at any time.\n")
    
    context.user_data['player_num'] = {}
    context.user_data['player_name'] = {}

    if update.effective_chat.type == "private":
        await update.message.reply_text("What do you want to call your character?\n")
        context.user_data['player_num'] = 1
        return INPUT_PLAYER_NAMES
    
    await update.message.reply_text("How many adventurers are there?\n")
    return INPUT_PLAYER_NUM

async def input_player_num(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print('inside input_player_num')
    print(update.message.text)
    print(update.message.text.isnumeric())
    if not update.message.text.isnumeric():
        await update.message.reply_text("Please enter a number!")
        return INPUT_PLAYER_NUM

    context.user_data['player_num'] = update.message.text
    await update.message.reply_text("So, there are {} adventurers. What are their character names?\n".format(context.user_data['player_num']))

    return INPUT_PLAYER_NAMES

async def input_player_names(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print('inside input_player_names')
    user = update.message.from_user
    player_name = update.message.text

    if user.username not in context.user_data['player_name']:
        context.user_data['player_name'][user.username] = player_name
        await update.message.reply_text("Hi {}, welcome to the adventure!\n".format(player_name))
    else:
        await update.message.reply_text("Hey @{}, you already told me your adventurer's name is '{}'. Type /changename to change it.".format(user.username, context.user_data['player_name'][user.username]))

    if len(context.user_data['player_name']) != int(context.user_data['player_num']):
        
        return INPUT_PLAYER_NAMES
    
    await update.message.reply_text("Let's get on with the adventure!")
    return GAME_IN_PROGRESS

async def game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("game start")
    reponse = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        prompt="Start an adventure game with {} players, give me 3 options per move.".format(context.user_data['player_num']),
        max_tokens=50
    )
    update.message.reply_text(reponse.choices[0].text)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Game cancelled. Goodbye!", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    openai.api_key = constants_secrets.OPENAI_API_KEY
    application = Application.builder().token(constants_secrets.TELEGRAM_API_KEY).build()
    start_handler = CommandHandler("start", start)
    cancel_handler = CommandHandler("cancel", cancel)
    input_player_names_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, input_player_names)
    input_player_num_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, input_player_num)
    game_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, game)

    adventure_handler = ConversationHandler(
        entry_points=[start_handler],
        states={INPUT_PLAYER_NUM:  [input_player_num_handler],
                INPUT_PLAYER_NAMES: [input_player_names_handler],
                GAME_IN_PROGRESS: [game_handler]},
        fallbacks=[cancel_handler])
    
    application.add_handler(adventure_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
