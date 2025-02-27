# ESO Exchange Discord Bot

## Overview
A Discord bot designed for Elder Scrolls Online (ESO) traders to manage and track crown and gold exchange listings. This bot helps trading communities quickly share, view, and manage their current exchange offers, supporting time-sensitive and standard trading listings.

## Security Warning ⚠️
**IMPORTANT:** Never commit or share your `.env` file or bot token publicly. The token in this file provides full access to your Discord bot. If your token is exposed, immediately regenerate it in the Discord Developer Portal.

## Setup and Configuration

### Bot Permissions

#### Permission Integer

The permission integer `8` represents the "Administrator" permission, which grants full server access. 

Recommended Permissions:
- For most bots, use a more limited set of permissions
- Typical bot permissions include:
  * Send Messages: 2048
  * Read Message History: 65536
  * Use Slash Commands: 2097152

#### Generating Invite Link

To create an invite link with specific permissions:
1. Go to OAuth2 > URL Generator in Discord Developer Portal
2. Select bot scopes
3. Choose specific permissions
4. Copy the generated URL

### Discord Bot Intents

To run this bot, you need to enable specific intents in the Discord Developer Portal:

1. Go to [Discord Developer Portal](https://discord.com/developers/applications/)
2. Select your application
3. Navigate to the "Bot" section
4. Under "Privileged Gateway Intents", enable:
   - PRESENCE INTENT
   - SERVER MEMBERS INTENT
   - MESSAGE CONTENT INTENT

### Required Permissions

Ensure your bot has the following permissions:
- Send Messages
- Send Messages in Threads
- Use Slash Commands
- Use External Emojis

### Troubleshooting

If you encounter a `PrivilegedIntentsRequired` error, double-check that you have:
- Enabled all required intents
- Invited the bot to your server with the correct permissions
- Regenerated your bot token if necessary

### Troubleshooting Permissions

If your bot experiences permission issues:
- Verify bot role hierarchy
- Check channel-specific permissions
- Ensure bot has necessary intents enabled

## Setup
1. Create a Discord bot and get your token from the Discord Developer Portal
2. Replace the placeholder token in `.env` with your actual bot token
3. Install dependencies: `pip install -r requirements.txt`

## Commands
- `!esoaddlisting [trader] [crowns] [gold] [time_info] [days_left]`: Add a new exchange listing
- `!esolistings`: Show all current exchange listings
- `!esoremovelistings [trader]`: Remove a listing by trader name

## Example Usage
- Add a listing: `!esoaddlisting Coizado 16000 16800000 "12PM - 8PM EST" 0`
- View listings: `!esolistings`
- Remove a listing: `!esoremovelistings Coizado`
