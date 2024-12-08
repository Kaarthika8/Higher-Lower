import discord
from discord.ext import commands
import random

# Intents and bot setup
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Game variables
number_to_guess = None
leaderboard = {}
active_game = False
last_player = None
total_attempts = 0
max_attempts = 20  # Maximum number of attempts for the game (combined guesses from all players)

@bot.event
async def on_ready():
    print(f'Bot is ready as {bot.user}')

@bot.command(name='start')
async def start_game(ctx):
    global number_to_guess, active_game, total_attempts
    if active_game:
        await ctx.send("A game is already in progress! Finish it before starting a new one.")
        return

    number_to_guess = random.randint(1, 50000)
    active_game = True
    total_attempts = 0  # Reset the total attempts for the new game
    await ctx.send("🎮 The Higher Lower game has started! I've picked a number between 1 and 50,000. Start guessing!")
    print(f"Picked number: {number_to_guess}")  # For debugging purposes.

@bot.command(name='guess')
async def guess_number(ctx, *, guess: str):
    global number_to_guess, active_game, leaderboard, last_player, total_attempts, max_attempts

    if not active_game:
        await ctx.send("There's no active game right now. Start one using `!start`. But don't worry, a new game will start soon!")
        return

    # Check if the maximum number of attempts has been reached
    if total_attempts >= max_attempts:
        await ctx.send("The game has ended. No more attempts can be made. A new game will start soon.")
        return

    # Validate input: ensure it is an integer
    if not guess.isdigit():
        await ctx.send(f"{ctx.author.mention}, please enter a valid integer.")
        return

    guess = int(guess)  # Convert to integer after validation

    if not (1 <= guess <= 50000):
        await ctx.send(f"{ctx.author.mention}, your guess must be between 1 and 50,000.")
        return

    # Check for consecutive guesses by the same player
    if last_player == ctx.author.id:
        # Deduct 2 points as a penalty for guessing consecutively
        if ctx.author.name in leaderboard:
            leaderboard[ctx.author.name] -= 2  # Deduct 2 points
        else:
            leaderboard[ctx.author.name] = -2  # Set initial points to -2 if player is new
        
        await ctx.send(f"{ctx.author.mention}, you cannot guess consecutively! You've been penalized -2 points.")
        return  # Do not count this guess toward total attempts

    # Update last player
    last_player = ctx.author.id

    # Update total attempts and calculate bonus points
    total_attempts += 1
    bonus_points = max_attempts - total_attempts  # 19 points for first guess, 18 for second, etc.

    # Process the guess
    if guess < number_to_guess:
        await ctx.send(f"{ctx.author.mention}, Higher! Try again.")
    elif guess > number_to_guess:
        await ctx.send(f"{ctx.author.mention}, Lower! Try again.")
    else:
        # Player guessed correctly
        total_points = 10 + bonus_points  # 10 points for the correct guess + bonus points
        await ctx.send(f"🎉 {ctx.author.mention} guessed it right! The number was {number_to_guess}. You earn {total_points} points!")
        
        if ctx.author.name not in leaderboard:
            leaderboard[ctx.author.name] = 0
        leaderboard[ctx.author.name] += total_points  # Add the total points to the leaderboard

        # Reset the game variables for the new round
        active_game = False  # End the game after the correct guess
        number_to_guess = None  # Reset the number to guess
        last_player = None  # Reset the last player
        
        await ctx.send("The game has ended. A new game is starting...")

        # Start a new round automatically
        await start_game(ctx)  # Automatically starts the next round after the game ends

    # Save the leaderboard after every guess
    save_leaderboard()

@bot.command(name='leaderboard')
async def show_leaderboard(ctx):
    if not leaderboard:
        await ctx.send("The leaderboard is empty. Play a game to earn points!")
        return

    sorted_leaderboard = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)
    leaderboard_message = "\n".join([f"{name}: {points} points" for name, points in sorted_leaderboard])
    await ctx.send(f"🏆 **Leaderboard:**\n{leaderboard_message}")

@bot.command(name='stop')
async def stop_game(ctx):
    global active_game, number_to_guess

    if not active_game:
        await ctx.send("There's no active game to stop.")
        return

    active_game = False
    number_to_guess = None
    await ctx.send("The current game has been stopped. Use `!start` to begin a new one.")

def save_leaderboard():
    # Function to save the leaderboard to a file or database (optional)
    pass

# Run the bot
bot.run('DISCORD_TOKEN')
