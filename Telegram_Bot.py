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
        # ["🔥🔥 IMMEDIATE ALERT (አስቸኳይ መረጃ) 🔥🔥"],
                ["❗️Announcements for Invalid Backoffice Requests"],
        ["Backoffice User Access Updates"],
        ["Digital Access Process"],
        ["How to unlock customer in the backoffice"],
        ["How to login to DBS backoffice"],
        ["What branches do when the customer is blocked"],
        ["How Anbesa Plus supports local language"],
        ["How to release trusted device"],
        ["How to search customer in DBS backoffice"],
        ["How Forgot password works"],
        ["Android App Download link"],
        ["Iphone App Download Link"],
        ["DBS End User Manual for Branches"],
        ["DBS Back Office / Portal User Access Request Form"],
        ["When OTP is not reaching to the customer's mobile"],
        ["Overlay Detected Avoid Entering Sensetive Information Error"]

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

            # How to unlock customer in the backoffice
    elif user_message == "🔥🔥 IMMEDIATE ALERT (አስቸኳይ መረጃ) 🔥🔥":
        response = """
🔥* To make the rollout process of Anbesa Plus smooth and Successful, we have arranged online session for all branches. Branches are expected to dedicate atleast one person for this session.*

*የአንበሳ ፕላስ መተግብሪያን እና የአንበሳ ባንክን የዲጅታል የለወጥ ሂደት የተሳካ እንዲሆን ለማድረግ ለሁሉም ቅርንጫፎች የኦላይን የጥያቄ እና መልስ ክፍለ ጊዜ አዘጋጅተናል። ከቅርንጫፍ ቢያንስ አንድ ሰው እንዲሳተፍ ግዴታ ነው።*

*🕧 ሰአት: ጠዋት 3:00*

🔥 Title:  A Request for Online Session

Anbesa Plus Rollout Online Session
Saturday, February 7, 2026
9:00 AM  |  (UTC+03:00) Nairobi  |  2 hrs 30 mins

Meeting number (access code):  * 2554 485 2539*
Meeting password:   *MB@ab1*
*
When it's time, click the link below.
https://anbesabank.webex.com/anbesabank/j.php?MTID=mb87517a0b86da76cd320a073a946fce9  *
"""
        await update.message.reply_text(
            response,   
             parse_mode="Markdown",
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
    # Overlay Detected Avoid Entering Sensetive Information Error
    elif user_message == "Overlay Detected Avoid Entering Sensetive Information Error":
        response = """This error occurs when your device detected an app on top of Anbesa Plus—for example, a screen recorder or any app that can display over other apps. This is a security measure to protect sensitive information like passwords, PINs, or payment details.

*ይህ የሚያጋጥመው ስልክዎ በአንበሳ ፕላስ መተግበሪያ ላይ ተጨማሪ ሌላ መተግበሪያ ሲያገኝ ሲሆን ለምሳሌ Screen Recorder ወይም ሌሎች መተግበሪያዎች ሊሆኑ ይችላሉ።ይህም የይለፍ ቃላት(Password)፣ ፒን(Pin) ወይም ሌሎች የክፍያ ዝርዝሮች እና ሚስጥራዊነት ያላቸውን መረጃዎች ለመጠበቅ የተደረገ የደህንነት እርምጃ ነው።*


 Steps to Fix This Overlay Warning

1️⃣ ⚙️ Open Settings on your phone.

2️⃣ 📱 Go to Apps.

3️⃣  ⋮  Tap the three dots at the top-right → select Special app access.

4️⃣  Choose Display over other apps (sometimes called Draw over other apps or Appear on top).

Look for apps that may create overlays:
Example: Screen recorders, Floating widgets or notepads, Screen dimming apps

5️⃣ Temporarily disable these apps.

🔙 Go back to Anbesa Plus and try again

💡 Tip: After finishing your sensitive actions, you can re-enable any apps you need.
"""
        
        await update.message.reply_text(
            response,        parse_mode="Markdown",

            reply_markup=get_main_keyboard()
        )
    
    # What branches do when the customer is blocked
    elif user_message == "What branches do when the customer is blocked":
        response = """
Branches need to understand that “Blocked” and “Locked” are not the same.

-   If the status shows “Blocked”, only Third-Level Support at Head Office can fix it. When they unblock it, it is done for everyone at once, not customer by customer.

-   If the status shows “Locked”, then the branch itself can unlock it directly in the DBS back office system.
"""
        
        await update.message.reply_text(
            response,  parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
    
    # How Anbesa Plus supports local language
    elif user_message == "How Anbesa Plus supports local language":
        response = """Anbesa Plus supports local language options in the app:
Video Tutorial: https://t.me/anbesaplus/1676
"""
    
        await update.message.reply_text(
            response,  parse_mode="Markdown",
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
    # Iphone App Download Link 
    elif user_message == "Iphone App Download Link":
        response = """
❗️❗️ *These steps are temporary until the production app is officially released on the App Store.* ❗️❗️

Steps to Download TestFlight and Install Anbesa Plus.

1. Open the App Store on your Iphone.

2. Search for *TestFlight* in the search bar.

3. Download and install TestFlight.
	Authenticate if needed (Face ID, Touch ID, or Apple ID password).

4. Once TestFlight is installed.

5. Open the link below to download Anbesa Plus.

6. Tap *Install* in TestFlight to download Anbesa Plus.

7. Open Anbesa Plus from TestFlight and start using it.

🔗 Download the AnbesaPlus Iphone App from:
        https://testflight.apple.com/join/Mz5erFuA """
        
        await update.message.reply_text(
            response,   parse_mode="Markdown",
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
        response = """📢 Backoffice User Access Updates
Upto this week (09/February) the remaining branches who are not granted access DBS backoffice are the following:

1. Afdera
2. Decheto
3. Dego
4. Gurdshola
5. Hayaarat Akababi
6. Hayahulet
7. Jomo
8. Kazanchis
9. Nigiste Saba
10. Selekleka
11. Wajatmuga
12. Weyni
13. Wukro

SMS has already been sent. Those who haven’t requested access yet must request it. If you requested this week, wait for notifications — we’ll send them soon. 
You are adviced to follow instructions. Use the request form we have shared to you. You can find it in this group or in the bot menu.
https://t.me/anbesaplus/3646
"""
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
    # Announcements for Invalid Backoffice Requests
    elif user_message == "❗️Announcements for Invalid Backoffice Requests":
        response = """Branches who submitted requests earlier but did not receive access:
ቀደም ሲል ጥያቄ አቅርባችሁ እስካሁን ፈቃድ (Access) ላልተሰጣችሁ ቅርንጫፎች፣ መዘግየቱ አብዛኛውን ጊዜ የሚፈጠረው ስህተት ከሆነ አሞላል የተያያዘ ነው። በመሆኑም በድጋሚ ጥያቄ ከማቅረባችሁ በፊት የሚከተሉትን ነጥቦች አረጋግጡ::

```
1  24Stadium        24  Guroro
2  Adi Mehameday    25  Hamiday
3  Adihaki Market   26  Jinka
4  Adisalem         27  Kalamin
5  Adishih          28  Kan daero
6  Adwa             29  Kelkel debri
7  AfricaGodana     30  Keta
8  Aradagiorgis     31  Kisadgaba
9  Ardijeganu       32  Mariam Quiha
10 Atote            33  Maymekden
11 Atsbi            34  Meda agame
12 Aweday           35  MekanisaAbo
13 Ayat Tafo        36  MEZBIR
14 Berahle          37  Midre hayelom
15 Bethel           38  Sarbet
16 Debre tabor      39  Shalla
17 Dera             40  Shire Edaga
18 Edagahamus       41  Suhul shire
19 Endabaguna       42  Tana
20 Furi             43  Welwalo
21 Gerhusrnay       44  Wenbeta
22 GojamBerenda     45  Wollosefer
23 Gotera           46  Yechila

```
Common reasons for delay or rejection:

 1️⃣ Requests submitted without full name or complete user information

 2️⃣ Submitting fewer than the required users or more than the allowed maximum

 3️⃣ Requests submitted without clear and readable round stamp

 4️⃣ Requests submitted for Branch Managers (these roles are not assigned Back Office access)

 5️⃣ Not using the official Anbesa Plus DBS Back Office Request Form

 6️⃣ Missing Branch Manager approval where required

*❗️ Reminder – Allowed Users per Branch:*

- Each branch may submit **only 2 users**: 1 CSO and 1 Accountant/ CSM
- Additionally, a branch may submit **1 Auditor**, only if the branch has an assigned auditor

"""
        await update.message.reply_text(
            response,  parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
        
# When OTP is not reaching to the customer's mobile
    elif user_message == "When OTP is not reaching to the customer's mobile":
        response = """
📱 When OTP is not reaching the customer's mobile

1️⃣ Verify SMS reception

Confirm if the customer receives SMS from any sender.

2️⃣ Check sender-specific blocking

If other SMS are received, verify whether messages from Anbesabank / LIB / 8803 are blocked on the customer’s device.

If blocked, unblock immediately.

3️⃣ Ensure phone accessibility

If not blocked, confirm the customer’s phone is reachable for both calls and SMS (network coverage, SIM active, not in airplane mode).

4️⃣ Validate head office SMS service

If all above checks pass, confirm whether SMS service is temporarily stopped at the Head Office.

⚠️ Note: This occurs in <2% of cases, so check steps 1–3 first.
"""
        await context.bot.send_message(
    chat_id=update.effective_chat.id, 
    text=response,
    reply_markup=get_main_keyboard()
)

        # await update.message.reply_text(
        #     response,
        #     reply_markup=get_main_keyboard()
        # )



    # Help command from keyboard
    elif user_message == "/help" or user_message.lower() == "help":
        await help_command(update, context)
    
    # else:
    #     # If message not recognized, show keyboard
    #     await update.message.reply_text(
    #         "Please select an option from the menu below:",
    #         reply_markup=get_main_keyboard()
    #     )

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