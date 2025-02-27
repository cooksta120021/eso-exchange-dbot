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
bot = commands.Bot(command_prefix='!eso', intents=intents)

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

    def add_listing(self, listing):
        self.listings.append(listing)

    def remove_listing(self, trader):
        self.listings = [l for l in self.listings if l.trader != trader]

    def get_listings(self):
        return self.listings

exchange_manager = ExchangeManager()

@bot.command(name='addlisting')
async def add_listing(ctx, trader, crowns: int, gold: int, time_info, days_left: int = 0):
    """Add a new exchange listing"""
    listing = ExchangeListing(trader, crowns, gold, time_info, days_left)
    exchange_manager.add_listing(listing)
    await ctx.send(f"Added listing: {listing}")

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

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Application ID: {APPLICATION_ID}')

# Run the bot
bot.run(os.getenv('DISCORD_TOKEN'))
