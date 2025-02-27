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

@bot.command(name='help')
async def show_help(ctx):
    """Display help information for ESO Exchange Bot commands"""
    help_embed = discord.Embed(
        title="ESO Exchange Bot Commands",
        description="Manage ESO Crown and Gold Exchange Listings",
        color=discord.Color.blue()
    )
    
    help_embed.add_field(
        name="!esoaddlisting",
        value=(
            "Add a new exchange listing\n"
            "**Usage:** `!esoaddlisting [trader] [crowns] [gold] [time_info] [days_left]`\n"
            "**Example:** `!esoaddlisting Coizado 16000 16800000 \"12PM - 8PM EST\" 0`"
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

@bot.command(name='usage')
async def show_usage(ctx):
    """Display usage instructions for ESO Exchange Bot"""
    usage_embed = discord.Embed(
        title="ESO Exchange Bot Usage",
        description="How to use the ESO Exchange Bot",
        color=discord.Color.blue()
    )
    
    usage_embed.add_field(
        name="Getting Started",
        value=(
            "1. Invite the bot to your server\n"
            "2. Use the `!esoaddlisting` command to add a new exchange listing\n"
            "3. Use the `!esolistings` command to view all current exchange listings\n"
            "4. Use the `!esoremovelistings` command to remove a listing by trader name"
        ),
        inline=False
    )
    
    usage_embed.add_field(
        name="Tips and Tricks",
        value=(
            "Use the `!esoaddlisting` command to add multiple listings at once\n"
            "Use the `!esolistings` command to view listings in a specific category\n"
            "Use the `!esoremovelistings` command to remove multiple listings at once"
        ),
        inline=False
    )
    
    usage_embed.set_footer(text="ESO Exchange Bot - Helping traders connect!")
    
    await ctx.send(embed=usage_embed)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Application ID: {APPLICATION_ID}')

# Run the bot
bot.run(os.getenv('DISCORD_TOKEN'))
