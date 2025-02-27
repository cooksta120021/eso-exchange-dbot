import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Discord bot configuration
APPLICATION_ID = os.getenv('DISCORD_APPLICATION_ID')
PUBLIC_KEY = os.getenv('DISCORD_PUBLIC_KEY')

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!eso', intents=intents, help_command=None)

class ExchangeListing:
    def __init__(self, trader, crowns, gold, time_info, days_left):
        self.trader = trader
        self.crowns = crowns
        self.gold = gold
        self.time_info = time_info
        self.days_left = days_left

    def __str__(self):
        return (f"@Exchange @Broker {self.trader}/ "
                f"{self.crowns} Crowns/ {self.gold} Gold/ "
                f"(All {self.time_info}) ({self.days_left} Days Left)")

class ExchangeManager:
    def __init__(self):
        self.listings = []
        self.listing_creation_state = {}

    def add_listing(self, listing):
        self.listings.append(listing)

    def remove_listing(self, trader):
        self.listings = [l for l in self.listings if l.trader != trader]

    def get_listings(self):
        return self.listings

exchange_manager = ExchangeManager()

@bot.command(name='/newlisting')
async def start_listing(ctx):
    """Start an interactive listing creation process"""
    # Initialize the listing creation state for this user
    exchange_manager.listing_creation_state[ctx.author.id] = {}
    
    # Start the interactive process
    await ctx.send("Let's create a new exchange listing! What's the trader's name?")

@bot.event
async def on_message(message):
    # Ignore bot messages
    if message.author.bot:
        return
    
    # Check if the user is in the middle of creating a listing
    if message.author.id in exchange_manager.listing_creation_state:
        state = exchange_manager.listing_creation_state[message.author.id]
        
        # Guide the user through listing creation steps
        if 'trader' not in state:
            state['trader'] = message.content.strip()
            await message.channel.send(f"Trader set to {state['trader']}. How many Crowns are you offering?")
        
        elif 'crowns' not in state:
            try:
                state['crowns'] = int(message.content.strip())
                await message.channel.send(f"Crowns set to {state['crowns']}. How much Gold do you want in exchange?")
            except ValueError:
                await message.channel.send("Please enter a valid number of Crowns.")
        
        elif 'gold' not in state:
            try:
                state['gold'] = int(message.content.strip())
                await message.channel.send(f"Gold set to {state['gold']}. What are your available times? (e.g., '12PM - 8PM EST')")
            except ValueError:
                await message.channel.send("Please enter a valid amount of Gold.")
        
        elif 'time_info' not in state:
            state['time_info'] = message.content.strip()
            await message.channel.send(f"Time set to {state['time_info']}. How many days is this listing valid? (0 for normal listing)")
        
        elif 'days_left' not in state:
            try:
                state['days_left'] = int(message.content.strip())
                
                # Create the listing
                listing = ExchangeListing(
                    state['trader'], 
                    state['crowns'], 
                    state['gold'], 
                    state['time_info'], 
                    state['days_left']
                )
                
                # Add the listing
                exchange_manager.add_listing(listing)
                
                # Confirm the listing
                await message.channel.send(f"Listing created successfully!\n{listing}")
                
                # Clear the state
                del exchange_manager.listing_creation_state[message.author.id]
            
            except ValueError:
                await message.channel.send("Please enter a valid number of days.")
    
    # Process other commands
    await bot.process_commands(message)

@bot.command(name='listings')
async def show_listings(ctx):
    """Show all current exchange listings"""
    if not exchange_manager.get_listings():
        await ctx.send("No current listings.")
        return
    
    listings_text = "\n".join(str(listing) for listing in exchange_manager.get_listings())
    await ctx.send(f"Current Listings:\n{listings_text}")

@bot.command(name='removelisting')
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
        name="/newlisting",
        value=(
            "Start an interactive listing creation process\n"
            "Guides you through adding a new exchange listing step by step"
        ),
        inline=False
    )
    
    help_embed.add_field(
        name="!esolistings",
        value=(
            "Show all current exchange listings\n"
            "**Usage:** `!esolistings`"
        ),
        inline=False
    )
    
    help_embed.add_field(
        name="!esoremovelistings",
        value=(
            "Remove a listing by trader name\n"
            "**Usage:** `!esoremovelistings [trader]`\n"
            "**Example:** `!esoremovelistings Coizado`"
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
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Application ID: {APPLICATION_ID}')

# Run the bot
bot.run(os.getenv('DISCORD_TOKEN'))
