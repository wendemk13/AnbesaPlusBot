from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup,Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters,CallbackQueryHandler, ContextTypes
import logging
from pathlib import Path
from dotenv import load_dotenv
import os
import csv
import datetime
import pandas as pd
import glob

# Holds Telegram file_ids for subsequent sends
FILE_IDS = {}
# Holds raw file for first upload
FILE_CACHE = {}

THUMBNAILS = {
    "digital_access_steps_video": "./responses/thumbnails/Digital Access Thumbnail.jpeg",
    "blocked_customer_video": "./responses/thumbnails/unblocking on cbs.jpg",
    "Approve_of_Digital_Access_on_CBS_video": "./responses/thumbnails/cbs approval.jpg",
}

# document blocking
async def handle_document(update, context):
    if not update.message or not update.message.document:
        return
    # blocked_extensions
    blocked_extensions = ['.apk', '.exe', '.msi', '.bat', '.cmd','.sh']
    file_name = update.message.document.file_name
    if file_name and any(file_name.lower().endswith(ext) for ext in blocked_extensions):
        try:
            # 1. Get info before deleting
            username = update.effective_user.username or update.effective_user.first_name
            chat_id = update.effective_chat.id
            ext_found = next(ext for ext in blocked_extensions if file_name.lower().endswith(ext))
            # 2. Delete the forbidden file
            await update.message.delete()
            # 3. Send a message to the chat (Not a reply)
            clean_ext = ext_found.replace('.', '')
            await context.bot.send_message(
            chat_id=chat_id,
    text=f"""<b>🚫 SECURITY ALERT</b>
    
Sending <b>{clean_ext.upper()}</b> files is not allowed in this group for security reasons.

    <b>{clean_ext.upper()}</b> ፋይሎችን ወደ እዚህ ቡድን መላክ አይፈቀድም፡፡""",
    parse_mode="HTML"
)
            print(f"Blocked {ext_found} from {username}")
            
        except Exception as e:
            print(f"Error handling document: {e}")

# ===== STORAGE LOGIC =====
def save_report_to_file(name, phone, issue):
    os.makedirs("reports", exist_ok=True)
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Map issue names to clean filenames
    if "Phone" in issue:
        filename = f"reports/Already_Existed_Phone_{current_date}.csv"
    elif "Blocked" in issue:
        filename = f"reports/Blocked_Users_{current_date}.csv"
    elif "Automatically Returning to Login Screen" in issue:
        filename = f"reports/Automatically_Returning_to_Login_Screen_{current_date}.csv"
    else:
        filename = f"reports/General_Issues_{current_date}.csv"
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    row = [timestamp, name, phone]
    file_exists = os.path.isfile(filename)
    
    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Time", "Customer Name", "Phone Number"])
        writer.writerow(row)
    print(f"Logged to daily CSV: {filename}")

def format_for_storage(phone):
    raw_input = str(phone).strip()
    # Remove non-numeric characters for digit counting
    clean = ''.join(filter(str.isdigit, raw_input))
    # Rule 1: Starts with 09 or 07 (Must be exactly 10 digits)
    if raw_input.startswith("09") or raw_input.startswith("07"):
        if len(clean) == 10:
            return f"+251{clean[-9:]}"
    # Rule 2: Starts with +251 (Must be exactly 13 characters including '+')
    elif raw_input.startswith("+251"):
        if len(raw_input) == 13 and len(clean) == 12:
            return f"+251{clean[-9:]}"
    # Rule 3: Starts with 251 (Must be exactly 12 digits)
    elif raw_input.startswith("251"):
        if len(clean) == 12:
            return f"+251{clean[-9:]}"
    # If it doesn't match Rule 1, 2, or 3 exactly, it is rejected
    return None

def load_files():
    files_to_load = {
        "digital_ambassador_pdf": "./responses/Designation of Tech-Native.pdf",
        "digital_access_steps_video": "./responses/Digital Access Steps.mp4",
        "blocked_customer_video": "./responses/videos/Unlocking and Unblocking customer.mp4",
        "Approve_of_Digital_Access_on_CBS_video": "./responses/videos/Approval of Digital Access on CBS (Manual Review).mp4",

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

# normalize the phone number
def normalize_ethiopian_phone(phone):
    if not phone or pd.isna(phone):
        return ""
    clean_phone = ''.join(filter(str.isdigit, str(phone)))
    # Return the last 9 digits
    return clean_phone[-9:]

# Search function
def search_phone_in_reports(phone_number, category_prefix):
    file_pattern = f"solved/{category_prefix}*.csv"
    files = glob.glob(file_pattern)

    if not files:
        print(f"DEBUG: No files found for pattern: {file_pattern}")
        return []
    # Normalize the user input to 9 digits
    target = normalize_ethiopian_phone(phone_number)

    results = []
    for file in files:
        try:
            df = pd.read_csv(file, dtype=str)
            df.columns = [c.strip() for c in df.columns]
            
            # Now we compare normalized CSV vs normalized target (9 digits vs 9 digits)
            match = df[df['Phone Number'].apply(lambda x: normalize_ethiopian_phone(str(x))) == target]
            
            if not match.empty:
                for _, row in match.iterrows():
                    date_part = os.path.basename(file).split('_')[-1].replace('.csv', '')
                    results.append({
                        "date": date_part,
                        "status": "Fixed ✅"
                    })
        except Exception as e:
            print(f"Error reading {file}: {e}")
            
    return results

async def send_cached_file(update: Update, key: str, caption: str = "",parse_mode: str = None):
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
                caption=caption,
                parse_mode=parse_mode
            )
            FILE_IDS[key] = msg.document.file_id
        elif is_video:
            thumbnail_path = THUMBNAILS.get(key)
            if thumbnail_path and Path(thumbnail_path).exists():
                with open(thumbnail_path, "rb") as thumb:
                    msg = await update.message.reply_video(
                        video=FILE_CACHE[key],
                        caption=caption,
                        thumbnail=thumb,
                        supports_streaming=True,
                        parse_mode=parse_mode, 
            )
            else:
                msg = await update.message.reply_video(
                video=FILE_CACHE[key] if key not in FILE_IDS else FILE_IDS[key],
                caption=caption,
                supports_streaming=True,
                parse_mode=parse_mode,
        )
            FILE_IDS[key] = msg.video.file_id
        else:
            await update.message.reply_text("Unsupported file type.")
    else:
        # Reuse Telegram file_id — instant
        if is_pdf:
            await update.message.reply_document(
                document=FILE_IDS[key],
                caption=caption,
                parse_mode=parse_mode
            )
        elif is_video:
            await update.message.reply_video(
                video=FILE_IDS[key],
                caption=caption,
                supports_streaming=True,
                parse_mode=parse_mode
            )
        else:
            await update.message.reply_text("Unsupported file type.")

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
        ["Designation of Digital Ambassador at Branches"],
        ["❗️Announcements for Invalid Backoffice Requests"],
        ["Backoffice User Access Updates"],
        ["Digital Access Process"],
        ["Report Issue"],
        ["Digital Access Approval on CBS (Manual Review)"],
        ["How to unlock customer in the backoffice"],
        ["How to login to DBS backoffice"],
        ["What branches do when the customer is blocked"],
        ["ALREADY EXISTING PHONE NO"],
        ["How Anbesa Plus supports local language"],
        ["How to release trusted device"],
        ["How to search customer in DBS backoffice"],
        ["How Forgot password works"],
        ["⬇️ Download Anbesa Plus Application"],
        ["DBS End User Manual for Branches"],
        ["DBS Back Office / Portal User Access Request Form"],
        ["When OTP is not reaching to the customer's mobile"],
        ["Overlay Detected Avoid Entering Sensetive Information Error"],
        ["Reported And Fixed Issues"],

    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_app_download_menu():
    keyboard = [
        ["Android App Download Link"],
        ["Iphone App Download Link"],
        ["🏠 Main Menu"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Reported And Fixed Issues
def get_reported_and_fixed_issues_menu():
    keyboard = [
        ["Fixed Phone Number Already Exists Issues"],
        ["Fixed Blocked User/Account Issues"],
        ['"Fixed Automatically Returning to Login Screen Issues"'],
        ["🏠 Main Menu"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_issue_report_menu():
    keyboard = [
        ["Phone Number Already Exists"],
        ["Blocked User/Account"],
        ['"Automatically Returning to Login Screen"'], 
        ["🏠 Main Menu"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command with clean formatting and redirect support"""
    # 1. Capture the deep-link argument (if any)
    args = context.args 
    
    # 2. Check if user came from the "Report" link
    if args and "report" in args:
        await update.message.reply_text(
            "📝 *Issue Reporting Steps:*\n\n"
            "1️⃣ Select the specific *Issue Type* below.\n"
            "2️⃣ Enter the customer's *Full Name*.\n"
            "3️⃣ Enter the *Phone Number* to report.\n\n"
    
            "⚠️ *IMPORTANT WARNING* ⚠️\n\n"
            "Please check the menus below carefully. You must *only* report your issue "
            "if it matches one of the specific issues listed."
            "If your issue is not on the list, Do not report here.\n\n"
            "ከተዘረዘሩት ችግሮች ውስጥ የእርሶ ችግር የሚዛመድ ከሆነ ብቻ ሪፖርት ያድርጉ።\n"
            "ጉዳይዎ በዝርዝሩ ውስጥ ከሌለ፣ እባክዎን እዚህ ሪፖርት አያድርጉ።",
            reply_markup=get_issue_report_menu(),
            parse_mode="Markdown"
        )
        return
    
    # 3. Check if user came from the "Search" link (The Fix)
    if args and "search" in args:
        await update.message.reply_text(
            "📋 **Search Menu**\n\n"
            "Use this menu to check if a customer's issue has already been resolved. "
            "Please select the category that matches the customer's complaint:\n\n"
            "🔹 **How to search:**\n"
            "1️⃣ Choose a category from the buttons below.\n"
            "2️⃣ Enter the customer's phone number when prompted.\n",
            reply_markup=get_reported_and_fixed_issues_menu(),
            parse_mode="Markdown"
        )
        return

    # 4. Default Welcome Message (for regular /start)
    welcome_text = (
        "👋 **Welcome to AnbesaPlus Helper Bot!**\n\n"
        "This bot helps you resolve technical questions and report issues. "
        "Select an option from the menu below to begin."
    )
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
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
    return

# ===== BUTTON HANDLERS =====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all text messages, button clicks, and reporting states"""
    user_message = update.message.text
    # Get the current state
    state = context.user_data.get("state")

    # ==========================================
    #   PRIORITY COMMANDS & RESET BUTTONS
    # ==========================================
    # These always run first. If a user clicks a button, we stop any state.

    # Back to main
    if user_message == "🔙 Back" or user_message == "🏠 Main Menu":
        context.user_data.clear() # Reset everything
        await update.message.reply_text(
            "Return to Main menu",
            reply_markup=get_main_keyboard()
    )
        return
    
    # Report Issue
    elif user_message == "Report Issue":
        context.user_data.clear() # Kill any previous state
        # Check if the message is coming from a group
        if update.effective_chat.type in ["group", "supergroup"]:
            #  URL button to the bot's private chat The 'start=report' part acts as a deep link
            bot_username = (await context.bot.get_me()).username
            keyboard = [
                [InlineKeyboardButton("➡️ Start Reporting", url=f"https://t.me/{bot_username}?start=report")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
    "🛡️ *Privacy & Security Notice*\n\n"
    "To protect customer phone numbers and keep this group clean and organized, "
    "all reporting must be done in a *private chat* through the bot.\n\n"
    "የደንበኞችን መረጃ ለመጠበቅ እና ይህን Group ንፁህ እና የተደራጀ ለማድረግ ሁሉም ሪፖርት ከቦት ጋር በሚደረግ private chat መደረግ አለበት።\n\n"
    "Click the button below to start reporting.\n"
    "ሪፖርት ለማድረግ ከታች ያለውን Button ይጫኑ።",
    
    reply_markup=reply_markup,
    parse_mode="Markdown"
)
            return
        else:
            # If they are already in private chat, show the reporting menu
            context.user_data.clear()
            await update.message.reply_text("*Select Issue Type:\n\n*" 
             "⚠️ *IMPORTANT WARNING* ⚠️\n\n"
            "Please check the menus below carefully. You must *only* report your issue "
            "if it matches one of the specific issues listed."
            "If your issue is not on the list, Do not report here.\n\n"
            "ከተዘረዘሩት ችግሮች ውስጥ የእርሶ ችግር የሚዛመድ ከሆነ ብቻ ሪፖርት ያድርጉ።\n"
            "ጉዳይዎ በዝርዝሩ ውስጥ ከሌለ፣ እባክዎን እዚህ ሪፖርት አያድርጉ።",
            reply_markup=get_issue_report_menu(),
            parse_mode="Markdown")
            return
    
    # Reported And Fixed Issues Menu
    elif user_message == "Reported And Fixed Issues":
        # Check if the message is coming from a group
        if update.effective_chat.type in ["group", "supergroup"]:
            bot_username = (await context.bot.get_me()).username
            # We use 'start=search' as a deep link to tell the bot to open the search menu
            keyboard = [
                [InlineKeyboardButton("🔍 Open Search Menu", url=f"https://t.me/{bot_username}?start=search")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "🛡️ *Privacy & Security Notice*\n\n"
                "To protect customer privacy, searching for fixed issues must be done in a *private chat*.\n\n"
                "የደንበኞችን ደህንነት ለመጠበቅ፣ የተቀረፉ ችግሮችን ማረጋገጥ የሚቻለው በቦት በኩል በሚደረግ *private chat* ብቻ መሆን አለበት።\n\n"
                "Click the button below to start checking.\n"
                "ለማረጋገጥ ከታች ያለውን Button ይጫኑ።",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            return
        
        # If already in private chat, show the menu normally
        await update.message.reply_text(
            "📋 **Reported And Fixed Issues Searching Menu**",
            reply_markup=get_reported_and_fixed_issues_menu(),
            parse_mode="Markdown"
        )
        return

    # ==========================================
    #   Fixed Reported Issues Menus
    # ==========================================
    # Fixed Phone Number Already Exists Issues
    elif user_message == "Fixed Phone Number Already Exists Issues":
        context.user_data.clear() # Kill any previous state
        context.user_data["search_category"] = "Phone Number Already Exists"
        context.user_data["state"] = "WAITING_FOR_SEARCH"
    
        await update.message.reply_text(
        "🔍 **Search Customers phone number from *Resolved Phone Number Already Exists Issues* **\n\n"
       "Please enter only the customers phone number.\n"
       "እባክዎ የደንበኛውን ስልክ ቁጥር ያስገቡ።",
        parse_mode="Markdown"
    )
        return

    # Fixed Blocked User/Account Issues
    elif user_message == "Fixed Blocked User/Account Issues":
        context.user_data.clear() # Kill any previous state
        context.user_data["search_category"] = "Blocked_Users"
        context.user_data["state"] = "WAITING_FOR_SEARCH"
    
        await update.message.reply_text(
        "🔍 **Search Customers phone number from *Resolved Blocked User/Account Issues* **\n\n"
      "Please enter only the customers phone number.\n"
       "እባክዎ የደንበኛውን ስልክ ቁጥር ያስገቡ።",
            parse_mode="Markdown"
    )
        return

    # Fixed Automatically Returning to Login Screen Issues
    elif user_message == '"Fixed Automatically Returning to Login Screen Issues"':
        context.user_data.clear() # Kill any previous state
        context.user_data["search_category"] = "Automatic Return"
        context.user_data["state"] = "WAITING_FOR_SEARCH"
    
        await update.message.reply_text(
        "🔍 **Search Customers phone number from *Resolved Automatically Returning to Login Screen Issues* **\n\n"
        "Please enter only the customers phone number.\n"
        "እባክዎ የደንበኛውን ስልክ ቁጥር ያስገቡ።",
            parse_mode="Markdown"
        )
        return

    # ==========================================
    #   Report Issue Menus
    # ==========================================
    # Phone Number Already Exists issue reporting
    elif user_message == "Phone Number Already Exists":
        context.user_data["report_issue_type"] = "Phone Already Exists"
        context.user_data["state"] = "WAITING_FOR_NAME"
        await update.message.reply_text("*Existing Phone No Reporting...*", parse_mode="Markdown")
        await update.message.reply_text("Please enter the customer's **Full Name**:", parse_mode="Markdown")
        return
    # Phone Number Already Exists issue reporting
    elif user_message == "Blocked User/Account":
        context.user_data["report_issue_type"] = "User Blocked"
        context.user_data["state"] = "WAITING_FOR_NAME"
        await update.message.reply_text("*Account Blocked Reporting...*", parse_mode="Markdown")
        await update.message.reply_text("Please enter the customer's **Full Name**:", parse_mode="Markdown")
        return
    # Automatically Returning to Login Screen
    elif user_message == '"Automatically Returning to Login Screen"':
        context.user_data["report_issue_type"] = "Automatically Returning to Login Screen"
        context.user_data["state"] = "WAITING_FOR_NAME"
        await update.message.reply_text("*Automatically Returning to Login Screen Reporting...*", parse_mode="Markdown")
        await update.message.reply_text("Please enter the customer's **Full Name**:", parse_mode="Markdown")
        return

    # ==========================================
    # ACTIVE STATE MACHINE
    # ==========================================
    # This only runs if the user is in the middle of a report.
    if state == "WAITING_FOR_SEARCH":
        # This is the search logic you wanted to add here
        category = context.user_data.get("search_category", "General")
        
        # Normalize the search input (last 7 digits)
        target = normalize_ethiopian_phone(user_message)
        
        if len(target) < 7:
            await update.message.reply_text("⚠️ Please enter a valid number (at least 7-9 digits).")
            return

        found_data = search_phone_in_reports(user_message, category)
        
        if found_data:
            text = f"✅ **Record Found:**\n\n"
            for item in found_data:
                text += f"📱 **Phone:** 0{target}\n🚩 **Status:** {item['status']}\n\n"
        else:
            text = f"❌ No record found for `{user_message}`."

        # Inline button to search again
        keyboard = [[InlineKeyboardButton("🔍 Search Another", callback_data=f"search_{category}")]]
        
        # only clear the state so they can stay in this category if they want
        context.user_data["state"] = None
        
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    elif state == "WAITING_FOR_NAME":
        context.user_data["temp_name"] = user_message
        context.user_data["state"] = "WAITING_FOR_PHONE"
        await update.message.reply_text(
            f"Full Name recorded:    {user_message}\n\nNow, please enter the **Phone Number**:", 
            parse_mode="Markdown"
        )
        return

    elif state == "WAITING_FOR_PHONE":
        # 1. Get the data from context BEFORE clearing
        name = context.user_data.get("temp_name")
        issue = context.user_data.get("report_issue_type")
        
        # 2. Format the phone number to (+251)
        formatted_phone = format_for_storage(user_message)
        
        if not formatted_phone:
            await update.message.reply_text("❌ **Invalid Format.** Please use `09...`, `07...` or `+251...`")
            return
        
        # 3. Save to CSV and Clear state and temp data AFTER
        save_report_to_file(name, formatted_phone, issue)
        context.user_data.clear()
        
        await update.message.reply_text(
            f"🚀 **Issue Reported Successfully**\n\n"
            f"👤 **Full Name:** {name}\n"
            f"📱 **Phone:** `{formatted_phone}`\n"
            f"📝 **Type:** {issue}",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
        return

    # ==========================================
    #  Main Keybaord Menus
    # ==========================================
    # Digital Access Process
    if user_message == "Digital Access Process":
        response = """Digital Access Process
Video Tutorial: https://t.me/anbesaplus/2506
"""
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
        return
    
    # How to unlock customer in the backoffice
    elif user_message == "How to unlock customer in the backoffice":
        response = """Steps to unlock customer in the DBS Backoffice 
Video Tutorial: https://t.me/anbesaplus/2132
"""
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
        return

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
        return
    
    # How to login to DBS backoffice
    elif user_message == "How to login to DBS backoffice":
        response = """Steps to Log in to DBS Backoffice
Video Tutorial: https://t.me/anbesaplus/2252
"""
        
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
        return

    # Digital Access Approval on CBS (Manual Review)
    elif user_message == "Digital Access Approval on CBS (Manual Review)":
        caption = """Steps for Digital Access Approval on CBS (Manual Review)
"""
        await send_cached_file(update, "Approve_of_Digital_Access_on_CBS_video", caption=caption,parse_mode="Markdown")
        response_text = "Check the Video above."
        await update.message.reply_text(
            response_text,
            reply_markup=get_main_keyboard()
        )
        return

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
            response,
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
        return
    
    # What branches do when the customer is blocked
    elif user_message == "What branches do when the customer is blocked":
        caption = """
https://t.me/anbesaplus/12418

Branches need to know the difference between Blocked and Locked:
ቅርንጫፎች *በታገዷል* እና *በተቆልፏል* መካከል ያለውን ልዩነት ማወቅ አለባቸው።

- *⛔ Blocked*: Only Head Office (Third-Level Support) can fix this. When they unblock it, it applies to everyone at once—not just one customer.
*Blocked ማለት ታግዷል ሲሆን በዋናው መ/ቤት የሶስተኛ ደረጃ ድጋፍ ብቻ ነው መስተካከል የሚችለው። እገዳውን ሲያነሱት ለሁሉም በአንድ ጊዜ እንጂ ደንበኛ በደንበኛ አይደለም ስለዚህ ጥያቄያችሁን ልካችሁ እስኪስተካከል በትዕግስት ጠብቁ።*

- *🔓 Locked*: The branch can fix this themselves by unlocking it directly in the DBS back office system.
*Locked ​ማለት ተቆልፏል ሲሆን ቅርንጫፍ ላይ በቀጥታ DBS back office system በመጠቀም ማስተካከል ይቻላል።*

⚠️ Before sclaating the problem to the Head Office, branches should check if the customer is Blocked or Locked. If it's Blocked also make sure the status in the BackOffice system is also Blocked then try to reset it.

ችግሩን ወደ ዋናው መሥሪያ ቤት ከመላኩ በፊት ቅርንጫፍ ላይ በደንበኛው ስልክ የታገደ መሆኑን ማረጋገጥ አለባቸው። ከታገደ በBackOffice ሁኔታ መታገዱን ያረጋግጡ ከዚያም እንደገና ለማስጀመር ይሞክሩ።
"""
        await send_cached_file(update, "blocked_customer_video", caption=caption,parse_mode="Markdown")

    # How Anbesa Plus supports local language
    elif user_message == "How Anbesa Plus supports local language":
        response = """Anbesa Plus supports local language options in the app:
Video Tutorial: https://t.me/anbesaplus/1676
"""
    
        await update.message.reply_text(
            response,  parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
        return
    
    # How to release trusted device
    elif user_message == "How to release trusted device":
        response = """How to release trusted device
Video Tutorial: https://t.me/anbesaplus/2133
                """
        
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
        return
    
    # How to search customer in DBS backoffice
    elif user_message == "How to search customer in DBS backoffice":
        response = """How to search customer in DBS backoffice
Video tutorial: https://t.me/anbesaplus/2131"""
        
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
        return
    
    # How Forgot password works
    elif user_message == "How Forgot password works":
        response = """How Forgot password works
Video Tutorial: https://t.me/anbesaplus/1611."""
        
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
        return

    # Download Anbesa Plus Application
    elif user_message == "⬇️ Download Anbesa Plus Application":
        await update.message.reply_text(
            "Select your device type:",
        reply_markup=get_app_download_menu()
    )
        return

    # Android App Download link 
    elif user_message == "Android App Download Link":
        response = """🔗 Download the AnbesaPlus Android App from:
        https://downloads.anbesabank.com/ """
        
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
            # reply_markup=get_app_download_menu()

        )
        return
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
            # reply_markup=get_app_download_menu()

        )
        return

        # DBS End User Manual for Branches
    elif user_message == "DBS End User Manual for Branches":
        response = """Get the DBS End User Manual for Branches:
    https://t.me/anbesaplus/1199 """
        
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
        return
    
        # DBS Back Office / Portal User Access Request Form
    elif user_message == "DBS Back Office / Portal User Access Request Form":
        response = """Get DBS Back Office / Portal User Access Request Form:
    https://t.me/anbesaplus/3646 """
        
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
        return
    
    # Backoffice User Access Updates
    elif user_message == "Backoffice User Access Updates":
        response = """📢 Backoffice User Access Updates
Upto this week (19/February) the remaining branches who are not granted access DBS backoffice are the following:

1. Adi_daero
2. Adi Kelebes
3. Adishihu
4. Adwa
5. Agazian
6. Assosa
7. Assayta
8. Awlaelo
9. Aynalem
10. AyatNoah
11. Ayat_tafo
12. Berbere_tera
13. Beshale
14. Bethel
15. Boditi
16. Bolearabsa
17. CMC
18. Debre Tabor
18. Dera
20. Edagahamus
21. Edagakedam
22. Edagarebue
23. Furi
24. Ginbgebeya
25. Guroro
26. Ifb Kukufto
27. Kality
28. Kality_gumuruk
29. Kandearo
20. Karakore
31. Megenagn Athletderartu
32. Parlama
33. Seket
34. Selekleka
35. Semema
36. Shollagebeya
37. Teklehaimanot
38. Tuludimtu
39. Weyni
40. Wolkite

SMS has already been sent. Those who haven’t requested access yet must request it. If you requested this week, wait for notifications — we’ll send them soon. 
You are adviced to follow instructions. Use the request form we have shared to you. You can find it in this group or in the bot menu.
https://t.me/anbesaplus/3646
"""
        await update.message.reply_text(
            response,
            reply_markup=get_main_keyboard()
        )
        return
    
    # Announcements for Invalid Backoffice Requests
    elif user_message == "❗️Announcements for Invalid Backoffice Requests":
        response = """Upto this week (18/February)
Branches who submitted requests earlier but did not receive access:
ቀደም ሲል ጥያቄ አቅርባችሁ እስካሁን ፈቃድ (Access) ላልተሰጣችሁ ቅርንጫፎች፣ መዘግየቱ አብዛኛውን ጊዜ የሚፈጠረው ስህተት ከሆነ አሞላል የተያያዘ ነው። በመሆኑም በድጋሚ ጥያቄ ከማቅረባችሁ በፊት የሚከተሉትን ነጥቦች አረጋግጡ::

```
 1. Adi Mehameday            22. Keta
 2. Adiabum                  23. Mariam Quiha
 3. Adihaki Market           24. Maymekden
 4. Adisalem                 25. Meda agame
 5. Adwa                     26. MekanisaABO
 6. Agaro                    27. MEZBIR
 7. Ahferom                  28. Moyale
 8. Aradagiorgis             29. Sarbet
 9. Ardijeganu               30. sebeya
10. Atote                   31. Seket
11. Atsbi                   32. Semema
12. Aweday                  33. Semera
13. Berahle                 34. Shire Edaga
14. Boditi                  35. suhul shire
15. Endabaguna              36. Tana
16. Erdiseganu              37. Warabe
17. GojamBerenda            38. welwalo
18. Injibara                39. Wollosefer
19. kalamin                 40. Wuhalimat
20. Kality                  41. Yechila
21. Kality

```
Common reasons for delay or rejection:

 1️⃣ Some requests may not be processed if not forwarded by IT Support to digital technology, If you believe your request is delayed and you have not received any response in Help Desk. 
    please send, Branch name and ticket number to the following users: @tokeyj or @Fish\_dt
 
 2️⃣ Requests submitted without full name or complete user information.

 3️⃣ Submitting fewer than the required users or more than the allowed maximum
 
 4️⃣ Requests submitted without clear and readable round stamp
 
 5️⃣ Requests submitted for Branch Managers (these roles are not assigned Back Office access)
 
 6️⃣ Not using the official Anbesa Plus DBS Back Office Request Form

 7️⃣ Missing Branch Manager approval where required

*❗️ Reminder – Allowed Users per Branch:*

- Each branch may submit **only 2 users**: 1 CSO and 1 Accountant/ CSM
- Additionally, a branch may submit **1 Auditor**, only if the branch has an assigned auditor

"""
        await update.message.reply_text(
            response,  parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
        return
        
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
        return

    # ALREADY EXISTING PHONE NO
    elif user_message == "ALREADY EXISTING PHONE NO":
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
        return
    
    # Designation of Digital Ambassador at Branches
    elif user_message == "Designation of Digital Ambassador at Branches":
        caption='''Dear colleagues,
In accordance with the attached internal memo, please designate one representative for each branch. Kindly note that GRO has already completed this exercise at the district level and provided us with district-by-district lists.

While we have received responses from some branches, we now require a consolidated list covering all branches.

Your prompt cooperation in providing this information will be greatly appreciated.
'''
        await send_cached_file(update, "digital_ambassador_pdf", caption=caption,parse_mode="Markdown")
        return

    # Help command from keyboard
    elif user_message == "/help" or user_message.lower() == "help":
        await help_command(update, context)
        return
    
async def new_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome when bot is added to a group"""
    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            welcome_text = """AnbesaPlus Helper Bot has joined!
To start: Type /start or select from menu below"""
            await update.message.reply_text(
                welcome_text,
                reply_markup=get_main_keyboard()
            )
            logger.info(f"Bot added to group: {update.effective_chat.title}")
        return

# ===== ERROR HANDLER =====
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    logger.error(f"Update {update} caused error {context.error}")

async def handle_callback_query(update, context):
    query = update.callback_query
    # Acknowledge the click and Check if the button click starts with "search_"
    await query.answer()
    if query.data.startswith("search_"):
        # Extract the category (e.g., "Blocked_Users")
        category = query.data.replace("search_", "")
        # Update the bot's state to waits for a phone number
        context.user_data["search_category"] = category
        context.user_data["state"] = "WAITING_FOR_SEARCH"
        # Change the message to ask for the number
        await query.edit_message_text(
            text=f"🔍 **Search in {category.replace('_', ' ')}**\n\nPlease enter the **Phone Number** to check:",
            parse_mode="Markdown"
        )

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
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))    
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    # 4. Handle all text messages (button clicks)
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        handle_message
    ))
    # 5. Add error handler
    application.add_error_handler(error_handler)
    
    print("Bot is running...")
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