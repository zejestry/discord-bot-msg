import discord
from discord.ext import commands, tasks
import random
import os

# Set up intents
intents = discord.Intents.default()
intents.message_content = True

# Load words from the external file
def load_words():
    if os.path.exists("words.txt"):
        with open("words.txt", "r") as f:
            return [line.strip() for line in f.readlines()]
    return []

# Create the bot with a default prefix
default_prefix = "!"
bot = commands.Bot(command_prefix=default_prefix, intents=intents)

# Variables for the msg feature
msg_user = None
time_interval = 10  # Default interval in seconds
greeting_message = "Hi! I'm here to send you some reminders"
shuffled_words = load_words()  # Load words from the file
message_history = []  # To store message history
msg_enabled = True  # To control if msg messages are enabled
shuffle_enabled = False  # Shuffle words flag
words_list = shuffled_words  # Set words_list from loaded words

# Store the current prefix
current_prefix = default_prefix

@bot.command(name="setprefix")
async def setprefix(ctx, new_prefix: str):
    """Sets a new command prefix."""
    global current_prefix
    current_prefix = new_prefix
    await ctx.send(f"Command prefix has been changed to: `{current_prefix}`")

@bot.command(name="sendmsg")
async def sendmsg(ctx):
    """Starts sending msg messages via DM to the user."""
    global msg_user, shuffled_words, message_history
    msg_user = ctx.author
    shuffled_words = random.sample(words_list, len(words_list)) if shuffle_enabled else words_list.copy()  # Shuffle words if enabled
    
    # Send the greeting message
    await msg_user.send(greeting_message)
    
    # Start the task to send msg messages
    await ctx.send(f"I’ll start sending msg messages to your DMs, {msg_user.mention}! ")
    send_msg_message.change_interval(seconds=time_interval)
    send_msg_message.start()

@bot.command(name="stopmsg")
async def stopmsg(ctx):
    """Stops the msg message loop."""
    global msg_user
    msg_user = None
    send_msg_message.stop()
    await ctx.send(f"Msg messages have been stopped, {ctx.author.mention}.")

@bot.command(name="settime")
async def settime(ctx, seconds: int):
    """Sets the interval time for sending msg messages."""
    global time_interval
    time_interval = seconds
    await ctx.send(f"The interval for msg messages is now set to every {time_interval} seconds, {ctx.author.mention}.")
    if send_msg_message.is_running():
        send_msg_message.change_interval(seconds=time_interval)

@bot.command(name="setgreeting")
async def setgreeting(ctx, *, message: str):
    """Sets a custom greeting message."""
    global greeting_message
    greeting_message = message
    await ctx.send(f"Greeting message has been updated, {ctx.author.mention}!")

@bot.command(name="history")
async def history(ctx):
    """Displays the history of msg messages sent to the user."""
    if message_history:
        history_message = "\n".join(message_history)
        embed = discord.Embed(title="Msg Message History", description=history_message, color=discord.Color.purple())
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"No msg messages have been sent yet, {ctx.author.mention}.")

@bot.command(name="togglemsg")
async def togglemsg(ctx):
    """Toggles the sending of msg messages on and off."""
    global msg_enabled
    msg_enabled = not msg_enabled
    status = "enabled" if msg_enabled else "disabled"
    await ctx.send(f"Msg messages have been {status}, {ctx.author.mention}.")

@bot.command(name="listwords")
async def listwords(ctx):
    """Lists all the available msg words."""
    words_message = "\n".join(words_list)
    embed = discord.Embed(title="Available Msg Words", description=words_message, color=discord.Color.blue())
    await ctx.send(embed=embed)

@bot.command(name="reactmsg")
async def reactmsg(ctx, emoji: str):
    """React to the latest msg message with an emoji."""
    if message_history:
        message_to_react = message_history[-1]
        await ctx.send(f"Reacting to the last message: {message_to_react}")
        await msg_user.send(message_to_react)  # Send the last message again to react
        await ctx.send(f"{emoji} added as a reaction to the latest message!")
    else:
        await ctx.send(f"No messages to react to, {ctx.author.mention}.")

@bot.command(name="panel")
async def panel(ctx):
    """Displays the command panel with available commands."""
    commands_list = """
    **Available Commands:**
    !sendmsg - Start receiving msg messages.
    !stopmsg - Stop receiving msg messages.
    !settime <seconds> - Set the interval time for msg messages.
    !setgreeting <message> - Set a custom greeting message.
    !history - View the history of msg messages sent.
    !togglemsg - Toggle msg messages on or off.
    !listwords - List available msg words.
    !reactmsg <emoji> - React to the latest msg message.
    !panel - Show this command panel.
    !setprefix <new_prefix> - Change the command prefix.
    !purgemessages - Delete all msg messages sent in DMs.
    """
    embed = discord.Embed(title="Command Panel", description=commands_list, color=discord.Color.green())
    await ctx.send(embed=embed)

@bot.command(name="purgemessages")
async def purgemessages(ctx):
    """Deletes all msg messages sent in DMs to the user."""
    global message_history
    message_history.clear()  # Clear the message history
    await ctx.send("All msg messages sent in DMs have been deleted.")

@bot.command(name="shuffle")
async def shuffle(ctx):
    """Toggles the shuffling of words on or off."""
    global shuffle_enabled
    shuffle_enabled = not shuffle_enabled
    status = "enabled" if shuffle_enabled else "disabled"
    await ctx.send(f"Shuffling of words has been {status}, {ctx.author.mention}.")

# Msg message function to send each word one by one in shuffled order
@tasks.loop(seconds=10)  # Default interval for sending messages
async def send_msg_message():
    global shuffled_words, msg_user, msg_enabled, shuffle_enabled
    if msg_user and msg_enabled:
        # If shuffling is enabled, shuffle words
        if shuffle_enabled:
            shuffled_words = random.sample(words_list, len(words_list))
        # If the list is empty, reshuffle
        if not shuffled_words:
            shuffled_words = random.sample(words_list, len(words_list))
        # Send one word and remove it from the list
        word_to_send = shuffled_words.pop(0)
        message_history.append(word_to_send)  # Save message to history
        await msg_user.send(word_to_send)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# Run the bot (replace YOUR_BOT_TOKEN with your bot token)
bot.run("YOUR_BOT_TOKEN")

