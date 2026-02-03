from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging
from dotenv import load_dotenv
import os

load_dotenv()

# ===== BOT CONFIGURATION =====
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ===== SETUP LOGGING =====
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===== KEYBOARD DEFINITION =====
def get_main_keyboard():
    """Create the main menu keyboard with all your menu items"""
    keyboard = [
        ["Digital Access Process"],
        ["How to unlock customer in the backoffice"],
        ["How to login to DBS backoffice"],
        ["What branches do when the customer is blocked"],
        ["How Anbesa Plus supports local language"],
        ["How to release trusted device"],
        ["How to search customer in DBS backoffice"],
        ["How Forgot password works"],
        ["Android App Download link"],
        ["DBS End User Manual for Branches"],
        ["DBS Back Office / Portal User Access Request Form"],
        ["Backoffice User Access Updates"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ===== COMMAND HANDLERS =====
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - show welcome message"""
    welcome_text = """Welcome to AnbesaPlus Helper!
I'm here to help with common questions about:
- Digital Access Process
- Unlocking Anbesa Plus users
- Releasing trusted devices
- Android App Download
- And more!
Select an option below:"""
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_keyboard()
    )
    logger.info(f"User {update.effective_user.id} started the bot")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """Available Commands:
/start - Show welcome message with keyboard
/help - Show this help message

Select an option from the keyboard below for specific help:"""
    
    await update.message.reply_text(
        help_text,
        reply_markup=get_main_keyboard()
    )

# ===== BUTTON HANDLERS =====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all text messages and button clicks"""
    user_message = update.message.text
    
    # Digital Access Process
    if user_message == "Digital Access Process":
        response = """Digital Access Process
Video Tutorial: https://t.me/anbesaplus/2506
"""
        
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
    
    # How to unlock customer in the backoffice
    elif user_message == "How to unlock customer in the backoffice":
        response = """Steps to unlock customer in the DBS Backoffice 
Video Tutorial: https://t.me/anbesaplus/2132
"""
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
    
    # How to login to DBS backoffice
    elif user_message == "How to login to DBS backoffice":
        response = """Steps to Log in to DBS Backoffice
Video Tutorial: https://t.me/anbesaplus/2252
"""
        
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
    
    # What branches do when the customer is blocked
    elif user_message == "What branches do when the customer is blocked":
        response = """Trusted Device can only be removed at the Backoffice.
"""
        
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
    
    # How Anbesa Plus supports local language
    elif user_message == "How Anbesa Plus supports local language":
        response = """Anbesa Plus supports local language options in the app:
Video Tutorial: https://t.me/anbesaplus/1676
"""
    
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
    
    # How to release trusted device
    elif user_message == "How to release trusted device":
        response = """How to release trusted device
Video Tutorial: https://t.me/anbesaplus/2133
                """
        
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
    
    # How to search customer in DBS backoffice
    elif user_message == "How to search customer in DBS backoffice":
        response = """How to search customer in DBS backoffice
Video tutorial: https://t.me/anbesaplus/2131"""
        
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
    
    # How Forgot password works
    elif user_message == "How Forgot password works":
        response = """How Forgot password works
Video Tutorial: https://t.me/anbesaplus/1611."""
        
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
    
    # Android App Download link 
    elif user_message == "Android App Download link":
        response = """🔗 Download the AnbesaPlus Android App from:
        https://downloads.anbesabank.com/ """
        
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )

        # DBS End User Manual for Branches
    elif user_message == "DBS End User Manual for Branches":
        response = """Get the DBS End User Manual for Branches:
    https://t.me/anbesaplus/1199 """
        
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
    
    
        # DBS Back Office / Portal User Access Request Form
    elif user_message == "DBS Back Office / Portal User Access Request Form":
        response = """Get DBS Back Office / Portal User Access Request Form:
    https://t.me/anbesaplus/3646 """
        
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
    # Backoffice User Access Updates
    elif user_message == "Backoffice User Access Updates":
        response = """Information on Updates to Backoffice User Access
    https://t.me/anbesaplus/3900"""
        
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )

    # Help command from keyboard
    elif user_message == "/help" or user_message.lower() == "help":
        await help_command(update, context)
    
    else:
        # If message not recognized, show keyboard
        await update.message.reply_text(
            "Please select an option from the menu below:",
            reply_markup=get_main_keyboard()
        )

async def new_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome when bot is added to a group"""
    for member in update.message.new_chat_members:
        if member.id == context.bot.id:  # If the new member is our bot
            welcome_text = """AnbesaPlus Helper Bot has joined!
To start: Type /start or select from menu below"""
            
            await update.message.reply_text(
                welcome_text,
                reply_markup=get_main_keyboard()
            )
            logger.info(f"Bot added to group: {update.effective_chat.title}")

# ===== ERROR HANDLER =====
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    logger.error(f"Update {update} caused error {context.error}")

# ===== MAIN FUNCTION =====
def main():
    """Start the bot"""
    print("=" * 50)
    print("STARTING AnbesaPLUS HELPER BOT")
    print("=" * 50)
    
    # 1. Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # 2. Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # 3. Handle when bot is added to group
    application.add_handler(MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS, 
        new_chat_members
    ))
    
    # 4. Handle all text messages (button clicks)
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        handle_message
    ))
    
    # 5. Add error handler
    application.add_error_handler(error_handler)
    
    # 6. Start polling
    print("Bot is running...")
    print("Add me to your Telegram group!")
    print("=" * 50)
    application.run_polling(allowed_updates=Update.ALL_TYPES)

# ===== START THE BOT =====
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Error: {e}")