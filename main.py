import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
 
# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
# Configures the standard Python logger so you can see what the bot is doing
# in the terminal. Level INFO prints general activity; use DEBUG for verbose
# output while developing.
logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)
 
 
# ---------------------------------------------------------------------------
# /start  — greets the user when they first open the bot
# ---------------------------------------------------------------------------
# Every command handler receives two arguments:
#   update  — the incoming Telegram event (message, callback, etc.)
#   context — bot-level data and helper methods
#
# update.effective_user  gives us the User object (id, first_name, username…)
# update.message.reply_text()  sends a plain-text reply to the same chat
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"Hi {user.first_name}! 👋\n\n"
        "I'm your demo bot. Here's what I can do:\n"
        "/start  — show this welcome message\n"
        "/help   — get help\n"
        "/echo   — repeat back what you say\n"
        "/menu   — show an inline keyboard\n"
    )
 
 
# ---------------------------------------------------------------------------
# /help  — explains available commands to the user
# ---------------------------------------------------------------------------
# Identical structure to start(). Good practice is to keep help text in sync
# with the actual handlers registered at the bottom of this file.
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Available commands:\n\n"
        "/start — welcome message\n"
        "/help  — this message\n"
        "/echo  — I'll repeat whatever you type after the command\n"
        "/menu  — interactive button menu\n\n"
        "Or just send me any text and I'll echo it back!"
    )
 
 
# ---------------------------------------------------------------------------
# /echo  — repeats the arguments the user typed after the command
# ---------------------------------------------------------------------------
# context.args is a list of words after the command.
# Example: "/echo hello world"  →  context.args == ["hello", "world"]
# We join them back into a string with spaces.
# If the user typed /echo with nothing after it, we ask them to add text.
async def echo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:
        text = " ".join(context.args)
        await update.message.reply_text(f"You said: {text}")
    else:
        await update.message.reply_text("Usage: /echo <your message>")
 
 
# ---------------------------------------------------------------------------
# /menu  — sends a message with an inline keyboard attached
# ---------------------------------------------------------------------------
# InlineKeyboardButton takes a label (text) and a callback_data string.
# callback_data is the value sent back to the bot when the button is tapped —
# it's how we know which button was pressed in button_handler() below.
#
# InlineKeyboardMarkup accepts a list of rows; each row is a list of buttons.
# Here we have two rows: one with two buttons, one with one button.
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton("Option A", callback_data="option_a"),
            InlineKeyboardButton("Option B", callback_data="option_b"),
        ],
        [
            InlineKeyboardButton("Tell me a fact", callback_data="fact"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Pick an option:", reply_markup=reply_markup)
 
 
# ---------------------------------------------------------------------------
# button_handler  — responds when the user taps an inline keyboard button
# ---------------------------------------------------------------------------
# update.callback_query contains the button press event.
# query.answer() MUST be called first — it dismisses the loading spinner on
# the button. You can pass a string to show a brief toast notification.
#
# query.data is the callback_data string we set in InlineKeyboardButton above.
# query.edit_message_text() replaces the original message text in-place,
# which is neater than sending a separate reply.
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # acknowledge the button press
 
    responses = {
        "option_a": "You chose Option A! Great pick.",
        "option_b": "You chose Option B! Solid choice.",
        "fact":     "Honey never spoils — archaeologists found 3,000-year-old honey in Egyptian tombs.",
    }
 
    text = responses.get(query.data, "Unknown option.")
    await query.edit_message_text(text)
 
 
# ---------------------------------------------------------------------------
# handle_text  — catches any plain text message that isn't a command
# ---------------------------------------------------------------------------
# The filters.TEXT & ~filters.COMMAND filter means: text messages that do NOT
# start with a slash. Without ~filters.COMMAND, this handler would also fire
# on /start, /help, etc., which are handled by their own CommandHandlers.
#
# update.message.text  is the raw message string the user sent.
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text
    await update.message.reply_text(f"You wrote: {user_text}")
 
 
# ---------------------------------------------------------------------------
# error_handler  — global error catcher
# ---------------------------------------------------------------------------
# Any exception that bubbles up from a handler lands here.
# context.error holds the exception object.
# We log it with logger.error() so it appears in the terminal.
# exc_info=True prints the full Python traceback, helpful for debugging.
# In production you might also notify yourself via a separate alert chat.
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("An error occurred: %s", context.error, exc_info=True)
 
 
# ---------------------------------------------------------------------------
# main  — wires everything together and starts the bot
# ---------------------------------------------------------------------------
# Application.builder() constructs the bot client using your token.
# Each add_handler() call registers a handler with the dispatcher:
#   CommandHandler("start", start)  →  calls start() when /start is received
#   CallbackQueryHandler(button_handler)  →  handles all button presses
#   MessageHandler(filters…, handle_text)  →  catches plain text messages
#
# add_error_handler() attaches the global error catcher.
#
# application.run_polling() starts a long-poll loop: the bot repeatedly asks
# Telegram "any new updates?" and processes them. This is the simplest way to
# run a bot without needing a public server. For production, prefer webhooks.
def main() -> None:
    token = os.environ.get("8663909119:AAFJXHVHo6xy0k6bCuvaNu2qMZv6WzwOR98")
    if not token:
        raise ValueError("Set the BOT_TOKEN environment variable first.")
 
    application = Application.builder().token(token).build()
 
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("echo", echo_command))
    application.add_handler(CommandHandler("menu", menu))
 
    # Inline button handler
    application.add_handler(CallbackQueryHandler(button_handler))
 
    # Plain text handler (must come after command handlers)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
 
    # Global error handler
    application.add_error_handler(error_handler)
 
    logger.info("Bot is running. Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
 
 
if __name__ == "__main__":
    main()

