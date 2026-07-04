import logging
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from templates import TEMPLATES

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

CHOOSING_TEMPLATE, COLLECTING = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    keyboard = [
        [InlineKeyboardButton(t["label"], callback_data=key)]
        for key, t in TEMPLATES.items()
    ]
    await update.message.reply_text(
        "👋 Welcome to Business Card Maker!\n\nPick a template to get started:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return CHOOSING_TEMPLATE


async def template_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    template_key = query.data

    if template_key not in TEMPLATES:
        await query.edit_message_text("Something went wrong, please /start again.")
        return ConversationHandler.END

    context.user_data["template"] = template_key
    context.user_data["field_index"] = 0
    context.user_data["field_data"] = {}

    template = TEMPLATES[template_key]
    await query.edit_message_text(
        f"Great choice: {template['label']}\n\nLet's fill in the details."
    )

    first_prompt = template["fields"][0][1]
    await query.message.reply_text(first_prompt)
    return COLLECTING


async def collect_field(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    template_key = context.user_data.get("template")
    if template_key is None:
        await update.message.reply_text("Please send /start to begin.")
        return ConversationHandler.END

    template = TEMPLATES[template_key]
    idx = context.user_data["field_index"]
    field_key, _ = template["fields"][idx]

    answer = update.message.text.strip()
    context.user_data["field_data"][field_key] = answer

    idx += 1
    context.user_data["field_index"] = idx

    if idx < len(template["fields"]):
        next_prompt = template["fields"][idx][1]
        await update.message.reply_text(next_prompt)
        return COLLECTING

    # All fields collected -> render the final card
    card_text = template["render"](context.user_data["field_data"])
    await update.message.reply_text(f"✅ Here's your business card:\n\n{card_text}")
    await update.message.reply_text(
        "Send /start to make another card (you'll pick a template again)."
    )
    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text("Cancelled. Send /start to begin again.")
    return ConversationHandler.END


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🪪 Business Card Maker\n\n"
        "/start - choose a template and build a card\n"
        "/cancel - stop the current card\n"
        "/help - show this message"
    )


def main() -> None:
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "BOT_TOKEN environment variable is not set. "
            "Get a token from @BotFather and set it before starting the bot."
        )

    application = Application.builder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_TEMPLATE: [CallbackQueryHandler(template_chosen)],
            COLLECTING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, collect_field)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))

    logger.info("Bot starting (polling)...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
