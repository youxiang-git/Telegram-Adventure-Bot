import logging
import constants_secrets
import openai
import requests
import re
from telegram import Bot, InlineKeyboardButton ,InlineKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (Application, CommandHandler, ContextTypes, CallbackQueryHandler,
                          ConversationHandler, MessageHandler, filters,)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

INPUT_PLAYER_NUM, INPUT_PLAYER_NAMES, GAME_START, GAME_IN_PROGRESS = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! I'm the game-master-bot for your new adventure!\n"
                                    "Send /cancel to end the game and stop talking to me at any time.\n")
    
    context.chat_data['player_num'] = {}
    context.chat_data['player_name'] = {}

    if update.effective_chat.type == "private":
        await update.message.reply_text("What do you want to call your character?\n")
        context.chat_data['player_num'] = 1
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

    context.chat_data['player_num'] = update.message.text
    await update.message.reply_text("So, there are {} adventurers. What are their character names?\n".format(context.chat_data['player_num']))

    return INPUT_PLAYER_NAMES

async def input_player_names(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print('inside input_player_names')
    user = update.message.from_user
    player_name = update.message.text

    if user.username not in context.chat_data['player_name']:
        context.chat_data['player_name'][user.username] = player_name
        await update.message.reply_text("Hi {}, welcome to the adventure!\n".format(player_name))
    else:
        await update.message.reply_text("Hey @{}, you already told me your adventurer's name is '{}'. Type /changename to change it.".format(user.username, context.chat_data['player_name'][user.username]))

    if len(context.chat_data['player_name']) != int(context.chat_data['player_num']):
        
        return INPUT_PLAYER_NAMES
    
    keyboard = [
        InlineKeyboardButton("Yes, let's go!", callback_data="Y"),
        InlineKeyboardButton("Maybe next time...", callback_data="N"),
    ]
    
    await update.message.reply_text("Shall we embark on with the adventure?", reply_markup=InlineKeyboardMarkup([keyboard]))
    return GAME_START

# async def 

async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    print(query)
    if query.data == "N":
        await update.callback_query.answer("Game cancelled. Goodbye!")
        return ConversationHandler.END
    
    print("game start")
    all_player_names = " ,".join(context.chat_data['player_name'].values())
    print('''I want you to act as a text based adventure game with {} people, named {}".
                                             I will type commands and you will reply with a description of what the player character sees. 
                                             I want you to only reply with the game output and nothing else. Do not write explanations. 
                                             Do not type commands unless instructed to do so. 
                                             Do not type any commands from the players.
                                             Do not make decisions for the players.
                                             Reply in the form of 'What do you do?' (Option 1) (Option 2) (Option 3)'''.format(context.chat_data['player_num'], all_player_names))
    
    reponse = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": '''I want you to act as a text based adventure game with {} people, named {}".
                                             I will type commands and you will reply with a description of what the player character sees. 
                                             I want you to only reply with the game output and nothing else. Do not write explanations. 
                                             Do not type commands unless instructed to do so. 
                                             Do not type any commands from the players.
                                             Do not make decisions for the players.
                                             Always reply with three options.
                                             Reply in the form of 'What do you do?' (Option 1 in here ) (Option 2 in here ) (Option 3 in here).
                                             Always place the text for the options within the brackets'''.format(context.chat_data['player_num'],all_player_names)},
            {"role": "user", "content": "Start the game!"}
        ],
        max_tokens=100
    )

    starting_scene = reponse.choices[0].message.content
    print(starting_scene)
    options = re.findall(r'\((.*?)\)', starting_scene)
    story = re.search(r'^(.*?)\(Option 1', starting_scene)
    print(options)

    keyboard = [
        [InlineKeyboardButton(options[0], callback_data=1)],
        [InlineKeyboardButton(options[1], callback_data=2)],
        [InlineKeyboardButton(options[2], callback_data=3)]
    ]

    await query.edit_message_text(story.group(1), reply_markup=InlineKeyboardMarkup(keyboard))
    

async def game_ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return

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
    game_start_handler = CallbackQueryHandler(start_game)
    # game_in_progress_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, game_ip)

    adventure_handler = ConversationHandler(
        entry_points=[start_handler],
        states={INPUT_PLAYER_NUM:  [input_player_num_handler],
                INPUT_PLAYER_NAMES: [input_player_names_handler],
                GAME_START: [game_start_handler]},
        fallbacks=[cancel_handler],
        per_user=False
        )
    
    application.add_handler(adventure_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
