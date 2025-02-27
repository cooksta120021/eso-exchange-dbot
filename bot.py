import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Discord bot configuration
TOKEN = os.getenv('DISCORD_TOKEN')
APPLICATION_ID = os.getenv('DISCORD_APPLICATION_ID')
PUBLIC_KEY = os.getenv('DISCORD_PUBLIC_KEY')

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

class ExchangeListing:
    def __init__(self, trader, crowns, gold, time_info, days_left):
        self.trader = trader
        self.crowns = crowns
        self.gold = gold
        self.time_info = time_info
        self.days_left = days_left
    
    def __str__(self):
        return f"@{self.trader}: {self.crowns} Crowns for {self.gold} Gold | Time: {self.time_info} | Days Left: {self.days_left}"

class ExchangeManager:
    def __init__(self):
        self.listings = []
        self.listing_creation_state = {}
    
    def add_listing(self, listing):
        self.listings.append(listing)
    
    def remove_listing(self, trader):
        self.listings = [listing for listing in self.listings if listing.trader.lower() != trader.lower()]
    
    def get_listings(self):
        return self.listings

exchange_manager = ExchangeManager()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command(name='newlisting')
async def start_listing(ctx):
    """Start an interactive listing creation process"""
    # Initialize the listing creation state for this user
    exchange_manager.listing_creation_state[ctx.author.id] = {}
    
    # Start the interactive process
    await ctx.send("Let's create a new exchange listing! What's the trader's name?")

@bot.command(name='listings')
async def show_listings(ctx):
    """Show all current exchange listings"""
    if not exchange_manager.get_listings():
        await ctx.send("No current listings.")
        return
    
    listings_text = "\n".join(str(listing) for listing in exchange_manager.get_listings())
    await ctx.send(f"Current Listings:\n{listings_text}")

@bot.command(name='removelistings')
async def remove_listing(ctx, trader):
    """Remove a listing by trader name"""
    original_count = len(exchange_manager.get_listings())
    exchange_manager.remove_listing(trader)
    new_count = len(exchange_manager.get_listings())
    
    if original_count > new_count:
        await ctx.send(f"Removed listing(s) for trader: {trader}")
    else:
        await ctx.send(f"No listings found for trader: {trader}")

@bot.command(name='help')
async def show_help(ctx):
    """Display help information for ESO Exchange Bot commands"""
    help_embed = discord.Embed(
        title="ESO Exchange Bot Commands",
        description="Manage ESO Crown and Gold Exchange Listings",
        color=discord.Color.blue()
    )
    
    help_embed.add_field(
        name="!newlisting",
        value=(
            "Start an interactive listing creation process\n"
            "Guides you through adding a new exchange listing step by step"
        ),
        inline=False
    )
    
    help_embed.add_field(
        name="!listings",
        value=(
            "Show all current exchange listings\n"
            "**Usage:** `!listings`"
        ),
        inline=False
    )
    
    help_embed.add_field(
        name="!removelistings",
        value=(
            "Remove a listing by trader name\n"
            "**Usage:** `!removelistings [trader]`\n"
            "**Example:** `!removelistings Coizado`"
        ),
        inline=False
    )
    
    help_embed.add_field(
        name="Days Left Explanation",
        value=(
            "0: Normal store item\n"
            "Number > 0: Time-sensitive item with priority"
        ),
        inline=False
    )
    
    help_embed.set_footer(text="ESO Exchange Bot - Helping traders connect!")
    
    await ctx.send(embed=help_embed)

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Check if the message is part of the listing creation process
    if message.author.id in exchange_manager.listing_creation_state:
        state = exchange_manager.listing_creation_state[message.author.id]
        
        if 'trader' not in state:
            # First step: Get trader name
            state['trader'] = message.content.strip()
            await message.channel.send(f"Trader name set to {state['trader']}. How many crowns do you want to exchange?")
        
        elif 'crowns' not in state:
            # Second step: Get crown amount
            try:
                state['crowns'] = int(message.content.strip())
                await message.channel.send(f"Crown amount set to {state['crowns']}. How much gold are you offering?")
            except ValueError:
                await message.channel.send("Please enter a valid number of crowns.")
        
        elif 'gold' not in state:
            # Third step: Get gold amount
            try:
                state['gold'] = int(message.content.strip())
                await message.channel.send(f"Gold amount set to {state['gold']}. When are you available? (e.g., 'evenings', 'weekends')")
            except ValueError:
                await message.channel.send("Please enter a valid amount of gold.")
        
        elif 'time_info' not in state:
            # Fourth step: Get time availability
            state['time_info'] = message.content.strip()
            await message.channel.send(f"Availability set to {state['time_info']}. How many days left on the item? (0 for normal store item)")
        
        elif 'days_left' not in state:
            # Final step: Get days left
            try:
                state['days_left'] = int(message.content.strip())
                
                # Create and save the listing
                new_listing = ExchangeListing(
                    state['trader'], 
                    state['crowns'], 
                    state['gold'], 
                    state['time_info'], 
                    state['days_left']
                )
                exchange_manager.add_listing(new_listing)
                
                # Clear the state and confirm
                del exchange_manager.listing_creation_state[message.author.id]
                await message.channel.send(f"Listing created successfully!\n{new_listing}")
            except ValueError:
                await message.channel.send("Please enter a valid number of days.")
        
        return
    
    # Process other commands
    await bot.process_commands(message)

# Run the bot
bot.run(TOKEN)
