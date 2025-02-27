import os
import discord
from discord.ui import View, Button, Modal, TextInput
from discord.ext import commands
from dotenv import load_dotenv
import pytz

# Load environment variables
load_dotenv()

# Discord bot configuration
TOKEN = os.getenv('DISCORD_TOKEN')
APPLICATION_ID = os.getenv('DISCORD_APPLICATION_ID')
PUBLIC_KEY = os.getenv('DISCORD_PUBLIC_KEY')

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Predefined list of timezones
AVAILABLE_TIMEZONES = sorted(pytz.all_timezones)

class ExchangeListing:
    def __init__(self, buyer_name, crowns, gold_per_crown, item, time_sensitive_days, 
                 days_available, time_available, timezone):
        self.buyer_name = buyer_name
        self.crowns = int(crowns)
        self.gold_per_crown = float(gold_per_crown)
        self.item = item
        self.time_sensitive_days = int(time_sensitive_days)
        self.days_available = days_available
        self.time_available = time_available
        self.timezone = timezone
        
        # Calculate total gold
        self.total_gold = int(self.crowns * self.gold_per_crown)
    
    def __str__(self):
        """
        Create a copy-pastable listing format
        """
        return (
            f"@{self.buyer_name}|"
            f"{self.gold_per_crown}|"
            f"{self.crowns}|"
            f"{self.item}|"
            f"{self.time_sensitive_days}|"
            f"{self.days_available}|"
            f"{self.time_available}|"
            f"{self.timezone}|"
            f"{self.total_gold}"
        )
    
    @classmethod
    def from_string(cls, listing_string):
        """
        Reconstruct a listing from a copy-pasted string
        """
        parts = listing_string.split('|')
        if len(parts) != 9:
            raise ValueError("Invalid listing format")
        
        # Remove @ from buyer name if present
        buyer_name = parts[0].lstrip('@')
        
        return cls(
            buyer_name=buyer_name,
            crowns=parts[2],
            gold_per_crown=parts[1],
            item=parts[3],
            time_sensitive_days=parts[4],
            days_available=parts[5],
            time_available=parts[6],
            timezone=parts[7]
        )

class ExchangeManager:
    def __init__(self):
        self.listings = []
        self.listing_creation_state = {}
        self.timezone_selection_state = {}
    
    def add_listing(self, listing):
        self.listings.append(listing)
    
    def remove_listing(self, buyer_name):
        self.listings = [listing for listing in self.listings if listing.buyer_name.lower() != buyer_name.lower()]
    
    def get_listings(self):
        return self.listings

exchange_manager = ExchangeManager()

class ListingCreationModal(Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.buyer_name = TextInput(
            label="Buyer Name",
            placeholder="Enter your name",
            style=discord.TextStyle.short,
            required=True
        )
        self.add_item(self.buyer_name)
        
        self.gold_per_crown = TextInput(
            label="Exchange Rate (Gold per Crown)",
            placeholder="How many gold per crown?",
            style=discord.TextStyle.short,
            required=True
        )
        self.add_item(self.gold_per_crown)
        
        self.crowns = TextInput(
            label="Crown Amount",
            placeholder="How many crowns do you want to exchange?",
            style=discord.TextStyle.short,
            required=True
        )
        self.add_item(self.crowns)
        
        self.item = TextInput(
            label="Item",
            placeholder="What item are you trading?",
            style=discord.TextStyle.short,
            required=True
        )
        self.add_item(self.item)
        
        self.time_sensitive_days = TextInput(
            label="Time Sensitive Days",
            placeholder="Days at time of listing (0 if not time-sensitive)",
            style=discord.TextStyle.short,
            required=True
        )
        self.add_item(self.time_sensitive_days)
        
        self.days_available = TextInput(
            label="Days Available",
            placeholder="Which days are you available?",
            style=discord.TextStyle.short,
            required=True
        )
        self.add_item(self.days_available)
        
        self.time_available = TextInput(
            label="Time Available",
            placeholder="What times are you available?",
            style=discord.TextStyle.short,
            required=True
        )
        self.add_item(self.time_available)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Create timezone selection view
            timezone_view = TimezoneSelectionView(
                buyer_name=self.buyer_name.value,
                crowns=self.crowns.value,
                gold_per_crown=self.gold_per_crown.value,
                item=self.item.value,
                time_sensitive_days=self.time_sensitive_days.value,
                days_available=self.days_available.value,
                time_available=self.time_available.value
            )
            
            await interaction.response.send_message(
                "Select your timezone:", 
                view=timezone_view, 
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)

class TimezoneSelectionView(View):
    def __init__(self, buyer_name, crowns, gold_per_crown, item, 
                 time_sensitive_days, days_available, time_available):
        super().__init__()
        self.buyer_name = buyer_name
        self.crowns = crowns
        self.gold_per_crown = gold_per_crown
        self.item = item
        self.time_sensitive_days = time_sensitive_days
        self.days_available = days_available
        self.time_available = time_available
        
        # Dynamically create timezone buttons
        timezone_groups = [AVAILABLE_TIMEZONES[i:i+25] for i in range(0, len(AVAILABLE_TIMEZONES), 25)]
        
        for group in timezone_groups[:4]:  # Limit to first 4 groups to avoid Discord's button limit
            group_view = View()
            for tz in group:
                button = Button(label=tz, style=discord.ButtonStyle.primary)
                button.callback = self.create_timezone_callback(tz)
                group_view.add_item(button)
            self.add_item(group_view)

    def create_timezone_callback(self, timezone):
        async def callback(interaction: discord.Interaction):
            try:
                # Create the listing
                new_listing = ExchangeListing(
                    buyer_name=self.buyer_name,
                    crowns=self.crowns,
                    gold_per_crown=self.gold_per_crown,
                    item=self.item,
                    time_sensitive_days=self.time_sensitive_days,
                    days_available=self.days_available,
                    time_available=self.time_available,
                    timezone=timezone
                )
                
                # Add the listing to the exchange manager
                exchange_manager.add_listing(new_listing)
                
                # Send confirmation
                await interaction.response.send_message(
                    f"Listing created successfully!\n{new_listing}", 
                    ephemeral=True
                )
            except Exception as e:
                await interaction.response.send_message(f"Error creating listing: {e}", ephemeral=True)
        return callback

@bot.command(name='newlisting')
async def start_listing(ctx):
    """Start an interactive listing creation process using a modal"""
    modal = ListingCreationModal(title="Create ESO Exchange Listing")
    await ctx.interaction.response.send_modal(modal)

@bot.command(name='listings')
async def show_listings(ctx):
    """Show all current exchange listings"""
    if not exchange_manager.get_listings():
        await ctx.send("No current listings.")
        return
    
    listings_text = "\n".join(str(listing) for listing in exchange_manager.get_listings())
    await ctx.send(f"Current Listings:\n{listings_text}")

@bot.command(name='removelistings')
async def remove_listing(ctx, buyer_name):
    """Remove a listing by buyer name"""
    original_count = len(exchange_manager.get_listings())
    exchange_manager.remove_listing(buyer_name)
    new_count = len(exchange_manager.get_listings())
    
    if original_count > new_count:
        await ctx.send(f"Removed listing(s) for buyer: {buyer_name}")
    else:
        await ctx.send(f"No listings found for buyer: {buyer_name}")

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
            "Remove a listing by buyer name\n"
            "**Usage:** `!removelistings [buyer]`\n"
            "**Example:** `!removelistings Coizado`"
        ),
        inline=False
    )
    
    help_embed.set_footer(text="ESO Exchange Bot - Helping traders connect!")
    
    await ctx.send(embed=help_embed)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Process other commands
    await bot.process_commands(message)

# Run the bot
bot.run(TOKEN)
