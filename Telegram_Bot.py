from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from pathlib import Path
import logging
from dotenv import load_dotenv
import os


# Holds Telegram file_ids for subsequent sends
FILE_IDS = {}
# Holds raw bytes for first upload
FILE_CACHE = {}



def load_files():
    files_to_load = {
        "digital_ambassador_pdf": "./responses/Designation of Tech-Native.pdf",
        "digital_access_steps_video": "./responses/Digital Access Steps.mp4"
    }

    for key, path_str in files_to_load.items():
        path = Path(path_str)
        if path.exists():
            FILE_CACHE[key] = path.read_bytes()
            print(f"Loaded {key} into memory")
        else:
            print(f"File not found: {path}")

load_files()
load_dotenv()

# ===== BOT CONFIGURATION =====
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ===== SETUP LOGGING =====
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def send_cached_file(update: Update, key: str, caption: str = ""):
    """
    Sends a cached file (PDF, video, etc.) using Telegram file_id if available.
    """
    if key not in FILE_CACHE:
        await update.message.reply_text(f"File '{key}' not found in cache.")
        return

    # Determine if file is PDF or Video
    is_pdf = key.endswith("pdf")
    is_video = key.endswith("video") or key.endswith("mov")

    # First upload — store Telegram file_id
    if key not in FILE_IDS:
        if is_pdf:
            msg = await update.message.reply_document(
                document=FILE_CACHE[key],
                filename=f"{key}.pdf",
                caption=caption
            )
            FILE_IDS[key] = msg.document.file_id
        elif is_video:
            msg = await update.message.reply_video(
                video=FILE_CACHE[key],
                caption=caption,
                thumbnail=open("./responses/thumbnails/Digital Access Thumbnail.jpeg", "rb"),
                supports_streaming=True,
            )
            FILE_IDS[key] = msg.video.file_id

        else:
            await update.message.reply_text("Unsupported file type.")
    else:
        # Reuse Telegram file_id — instant
        if is_pdf:
            await update.message.reply_document(
                document=FILE_IDS[key],
                caption=caption
            )
        elif is_video:
            await update.message.reply_video(
                video=FILE_IDS[key],
                caption=caption
            )
        else:
            await update.message.reply_text("Unsupported file type.")


# ===== KEYBOARD DEFINITION =====
# def get_main_keyboard():
#     """Create the main menu keyboard with all your menu items"""
#     keyboard = [        
#         # ["🔥🔥 IMMEDIATE ALERT (አስቸኳይ መረጃ) 🔥🔥"],
#         ["Designation of Digital Ambassador"],
#         ["❗️Announcements for Invalid Backoffice Requests"],
#         ["Backoffice User Access Updates"],
#         ["Digital Access Process"],
#         ["How to unlock customer in the backoffice"],
#         ["How to login to DBS backoffice"],
#         ["What branches do when the customer is blocked"],
#         ["ALREADY EXISTING PHONE NO"],
#         ["How Anbesa Plus supports local language"],
#         ["How to release trusted device"],
#         ["How to search customer in DBS backoffice"],
#         ["How Forgot password works"],
#         ["Android App Download link"],
#         ["Iphone App Download Link"],
#         ["DBS End User Manual for Branches"],
#         ["DBS Back Office / Portal User Access Request Form"],
#         ["When OTP is not reaching to the customer's mobile"],
#         ["Overlay Detected Avoid Entering Sensetive Information Error"]

#     ]
#     return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# ===== KEYBOARD DEFINITION =====
def get_main_keyboard():
    """Create a more compact main menu keyboard"""
    keyboard = [
        ["🔥🔥 IMMEDIATE ALERT (አስቸኳይ መረጃ) 🔥🔥"],
        ["Designation of Digital Ambassador"],
        ["❗️Invalid Backoffice Requests","Backoffice Access Updates",],
        ["Digital Access Process", "Login to DBS Backoffice"],
        ["Blocked Customer", "Unlock Customer"],
        ["Existing Phone Number", "Overlay Detected Error"],
        [ "Unlock Trusted Device","Anbesa Plus local language"],
        ["Search Customer", "Forgot Password", "OTP Not Reaching"], 
        ["Android App Download", "Iphone App Download"], 
        ["DBS End User Manual", "DBS Access Request Form"]
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
        # await send_cached_file(update, "digital_access_steps_video", "Here are the Digital Access Steps")

        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
    
    # How to unlock customer in the backoffice
    elif user_message == "Unlock Customer":
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
🔥* To make the rollout process of Anbesa Plus Smooth and Successful, we have arranged Second Round online session for all branches. Branches are expected to dedicate atleast one person for this session.*

*Digital Ambassadors of each branch must attend the session.*

*የአንበሳ ፕላስ መተግብሪያን እና የአንበሳ ባንክን የዲጅታል የለወጥ ሂደት የተሳካ እንዲሆን ለማድረግ ለሁሉም ቅርንጫፎች ሁለተኛ ዙር የኦላይን የጥያቄ እና መልስ ክፍለ ጊዜ አዘጋጅተናል። ከቅርንጫፍ ቢያንስ አንድ ሰው እንዲሳተፍ ግዴታ ነው።*

*የእያንዳንዱ ቅርንጫፍ ዲጂታል አምባሳደሮች መሳተፍ አለባቸው።*

*🕧 ሰአት: ቅዳሜ ጠዋት 3:00*

🔥 Title:  A Request for Second Round Online Session

Anbesa Plus Rollout Second Round Online Session
Saturday, February 14, 2026
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
    elif user_message == "Login to DBS Backoffice":
        response = """Steps to Log in to DBS Backoffice
Video Tutorial: https://t.me/anbesaplus/2252
"""
        
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
    # Overlay Detected Avoid Entering Sensetive Information Error
    elif user_message == "Overlay Detected Error":
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
    elif user_message == "Blocked Customer":
        response = """
Branches need to know the difference between Blocked and Locked:
ቅርንጫፎች *በታገዷል* እና *በተቆልፏል* መካከል ያለውን ልዩነት ማወቅ አለባቸው።

- *⛔ Blocked*: Only Head Office (Third-Level Support) can fix this. When they unblock it, it applies to everyone at once—not just one customer.
*Blocked ማለት ታግዷል ሲሆን በዋናው መ/ቤት የሶስተኛ ደረጃ ድጋፍ ብቻ ነው መስተካከል የሚችለው። እገዳውን ሲያነሱት ለሁሉም በአንድ ጊዜ እንጂ ደንበኛ በደንበኛ አይደለም ስለዚህ ጥያቄያችሁን ልካችሁ እስኪስተካከል በትዕግስት ጠብቁ።*

- *🔓 Locked*: The branch can fix this themselves by unlocking it directly in the DBS back office system.
*Locked ​ማለት ተቆልፏል ሲሆን ቅርንጫፍ ላይ በቀጥታ DBS back office system በመጠቀም ማስተካከል ይቻላል።*

"""
        
        await update.message.reply_text(
            response,  parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
    
    # How Anbesa Plus supports local language
    elif user_message == "Anbesa Plus local language":
        response = """Anbesa Plus supports local language options in the app:
Video Tutorial: https://t.me/anbesaplus/1676
"""
    
        await update.message.reply_text(
            response,  parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
    
    # How to release trusted device
    elif user_message == "Unlock Trusted Device":
        response = """How to release trusted device
Video Tutorial: https://t.me/anbesaplus/2133
                """
        
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
    
    # How to search customer in DBS backoffice
    elif user_message == "Search Customer":
        response = """How to search customer in DBS backoffice
Video tutorial: https://t.me/anbesaplus/2131"""
        
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
    
    # How Forgot password works
    elif user_message == "Forgot Password":
        response = """How Forgot password works
Video Tutorial: https://t.me/anbesaplus/1611."""
        
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
    
    # Android App Download link 
    elif user_message == "Android App Download":
        response = """🔗 Download the AnbesaPlus Android App from:
        https://downloads.anbesabank.com/ """
        
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
    # Iphone App Download Link 
    elif user_message == "Iphone App Download":
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
    elif user_message == "DBS End User Manual":
        response = """Get the DBS End User Manual for Branches:
    https://t.me/anbesaplus/1199 """
        
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
    
    
        # DBS Back Office / Portal User Access Request Form
    elif user_message == "DBS Access Request Form":
        response = """Get DBS Back Office / Portal User Access Request Form:
    https://t.me/anbesaplus/3646 """
        
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
    # Backoffice User Access Updates
    elif user_message == "Backoffice Access Updates":
        response = """📢 Backoffice User Access Updates
Upto this week (11/February) the remaining branches who are not granted access DBS backoffice are the following:

1  Abaymado
2  Adihageray
3  Adihawsi
4  Arbaminch
5  Athlete_Haile
6  Ayder
7  Bonga
8  Gerji
9  Gijet
10  Gofa_Gebriel
11  Goro
12  Hadnet
13  Hayahulet
14  Horaarsedi
15  Hossaena
16  Jerer
17  Jinka
18  k.Weyane
19  May_Tsebri
20  Metema_Yohanes
21  Mizan_Aman
22  Momona
23  Sekota
24  Sengatera
25  Wajirat

SMS has already been sent. Those who haven’t requested access yet must request it. If you requested this week, wait for notifications — we’ll send them soon. 
You are adviced to follow instructions. Use the request form we have shared to you. You can find it in this group or in the bot menu.
https://t.me/anbesaplus/3646
"""
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
    # Announcements for Invalid Backoffice Requests
    elif user_message == "❗️Invalid Backoffice Requests":
        response = """Upto this week (11/February) Branches who submitted requests earlier but did not receive access:
ቀደም ሲል ጥያቄ አቅርባችሁ እስካሁን ፈቃድ (Access) ላልተሰጣችሁ ቅርንጫፎች፣ መዘግየቱ አብዛኛውን ጊዜ የሚፈጠረው ስህተት ከሆነ አሞላል የተያያዘ ነው። በመሆኑም በድጋሚ ጥያቄ ከማቅረባችሁ በፊት የሚከተሉትን ነጥቦች አረጋግጡ::

```
1  24Stadium        24  Guroro
2  Adi Mehameday    25  Hamiday
3  Adihaki Market   26  Kalamin
4  Adisalem         27  Kan daero
5  Adishih          28  Kelkel debri
6  Adwa             29  Keta
7  AfricaGodana     30  Kisadgaba
8  Aradagiorgis     31  Mariam Quiha
9  Ardijeganu       32  Maymekden
10 Atote            33  Meda agame
11 Atsbi            34  MekanisaAbo
12 Aweday           35  MEZBIR
13 Ayat Tafo        36  Midre hayelom
14 Berahle          37  Sarbet
15 Bethel           38  Shalla
16 Debre tabor      39  Shire Edaga
17 Dera             40  Suhul shire
18 Edagahamus       41  Tana
19 Endabaguna       42  Welwalo
20 Furi             43  Wenbeta
21 Gerhusrnay       44  Wollosefer
22 GojamBerenda     45  Yechila
23 Gotera

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
    elif user_message == "OTP Not Reaching":
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
# ALREADY EXISTING PHONE NO
    elif user_message == "Existing Phone Number":
        response = """
When a customer’s status shows *“ALREADY EXISTING PHONE NO”*, it means they tried to set up Digital Access but didn’t finish, for different reasons. First Branches must check if the phone number is in the DBS backoffice. If it doesn’t exist in the DBS backoffice , follow these steps

- 	If the customer forgot their password, they cannot fix it themselves. They must wait for us to reset it so they can start fresh.

- 	To reset, Third-Level Support (IT–Digital Banking) checks whether the customer has already clicked “Forgot Password” and been disabled.

- 	So, the customer must first initiate *“Forgot Password.”*

- 	After that, they need to wait until IT–Digital Banking completes the reset. This is done for all affected customers at once, not individually.

⚠️ Note: IT–Digital Banking usually performs this reset at least twice a week.

"""
        await context.bot.send_message(
    chat_id=update.effective_chat.id, 
    text=response,parse_mode="Markdown",
    reply_markup=get_main_keyboard()
)

        # await update.message.reply_text(
        #     response,
        #     reply_markup=get_main_keyboard()
        # )


        
    # # Designation of Digital Ambassador
    # elif user_message == "Designation of Digital Ambassador":
    #     await update.message.reply_document(
    #     document=PDF_CACHE["digital_ambassador"],
    #     filename="designation_digital_ambassador.pdf",
    #     caption="Designation of Digital Ambassador",
    #     reply_markup=get_main_keyboard()
    # )

    # Designation of Digital Ambassador
    elif user_message == "Designation of Digital Ambassador":
        await send_cached_file(update, "digital_ambassador_pdf", "Designation of Digital Ambassador")


    # elif user_message == "Designation of Digital Ambassador":
    #     # First upload
    #     if "digital_ambassador" not in PDF_FILE_IDS:
    #         msg = await update.message.reply_document(
    #         document=PDF_CACHE["digital_ambassador"],
    #         filename="designation_digital_ambassador.pdf",
    #         caption="Designation of Digital Ambassador",
    #         reply_markup=get_main_keyboard()
    #         )
    #         PDF_FILE_IDS["digital_ambassador"] = msg.document.file_id
    #     else:
    #         # Reuse Telegram file_id
    #         await update.message.reply_document(
    #         document=PDF_FILE_IDS["digital_ambassador"],
    #         caption="Designation of Digital Ambassador",
    #         reply_markup=get_main_keyboard()
    #     )


    # # Log the file_id for later use
    # print("Telegram file_id:", msg.document.file_id)



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