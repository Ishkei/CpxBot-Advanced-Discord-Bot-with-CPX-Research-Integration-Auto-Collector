# CpxBot - CPX Research Integration

A Discord bot designed to automate CPX Research surveys and integrate with the Wyrecraft Discord server for cryptocurrency earnings.

## 🎯 Overview

CpxBot combines Discord bot functionality with CPX Research survey automation, allowing you to:
- Automate survey completion on CPX Research
- Earn cryptocurrency rewards (BTC, DOGE, LTC, SOL, etc.)
- Integrate with Discord gaming commands
- Withdraw earnings to Tip.cc or Lightning Network wallets

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.11+
- Discord account
- CPX Research account (linked to Discord)

### 2. Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run setup script
python setup_cpx_integration.py

# Configure environment variables
# Edit .env file with your credentials
```

### 3. Discord Setup
1. Join the Wyrecraft Discord: https://discord.gg/VXKfzW4B
2. Use `/setup` to create your character
3. Use `/offers` to access CPX Research surveys
4. Use `/withdraw` in the #🏛️・bank channel to cash out

## 📋 Configuration

### Environment Variables (.env)
```env
# Discord Bot Configuration
DISCORD_TOKEN=your_discord_bot_token_here
DISCORD_GUILD_ID=your_guild_id_here

# CPX Research Configuration (optional)
CPX_USERNAME=your_cpx_username_here
CPX_PASSWORD=your_cpx_password_here

# Optional: Google API for AI features
GOOGLE_API_KEY=your_google_api_key_here

# Optional: Tip.cc Integration
TIP_CC_WEBHOOK_URL=your_tip_cc_webhook_url_here
```

### CPX Research URL
Your personalized CPX Research URL:
```
https://offers.cpx-research.com/index.php?app_id=27806&ext_user_id=533055960609193994_1246050346233757798
```

## 🎮 Discord Commands

### CPX Research Commands
- `/offers` - Start CPX Research survey automation
- `/withdraw` - Withdraw earnings to crypto wallet
- `/cpx_status` - Check CPX Research configuration
- `/setup` - Set up your character

### Gaming Commands (from Wyrecraft)
- `/mine` - Mine for resources (every 15 minutes)
- `/fish` - Fish for resources (every 15 minutes)
- `/rob` - Rob for resources (every 15 minutes)
- `/shop` - Purchase gear to increase earnings
- `/sell` - Sell items for coins
- `/profile` - View your profile and balance

## 💰 Earning Methods

### 1. Survey Completion
- Use `/offers` to access CPX Research surveys
- Bot automatically completes surveys
- Earn cryptocurrency rewards

### 2. In-Game Activities
- **Mining**: Use `/mine` in #🏔️・mines
- **Fishing**: Use `/fish` in #🌊・lake  
- **Robbing**: Use `/rob` in #🏚️・alley
- **Chatting**: Chat in #🏰・chat for dust rewards

### 3. Inviting Friends
- Create invite links for friends
- Earn 5% of their survey earnings when they reach level 5

## 🏦 Withdrawal Process

1. **Earn Coins**: Complete surveys and in-game activities
2. **Check Balance**: Use `/profile` to see your earnings
3. **Withdraw**: Use `/withdraw` in #🏛️・bank channel
4. **Receive Crypto**: Get paid in BTC, DOGE, LTC, PEP, POL, SOL, TRX, WAXP, XLM, XNO, XRP

## 🤖 Bot Features

### Automated Survey Completion
- Intelligent form filling based on persona
- Handles multiple choice questions
- Navigates complex survey flows
- Maintains consistency across surveys

### Discord Integration
- Real-time status updates
- Embedded messages with survey progress
- Error handling and recovery
- Background task management

### Database Integration
- Tracks survey completion history
- Stores user balances and earnings
- Manages withdrawal requests
- Logs all activities

## 📁 Project Structure

```
CpxBot/
├── main.py                    # Main application entry point
├── config.yaml               # Configuration file
├── requirements.txt          # Python dependencies
├── setup_cpx_integration.py # CPX setup script
├── src/
│   ├── discord_bot/         # Discord bot modules
│   │   ├── commands/        # Command handlers
│   │   │   ├── cpx_commands.py    # CPX Research commands
│   │   │   ├── survey_commands.py # General survey commands
│   │   │   ├── gaming_commands.py # Gaming commands
│   │   │   └── tip_commands.py    # Tip.cc commands
│   │   ├── handlers/        # Event handlers
│   │   │   └── cpx_handler.py     # CPX Research handler
│   │   └── bot.py          # Main bot class
│   ├── web_scraper/        # Web scraping modules
│   │   └── cpx_scraper.py  # CPX Research scraper
│   └── utils/              # Utility modules
├── data/                   # Database files
├── logs/                   # Log files
└── tests/                  # Test files
```

## 🛠️ Usage

### Start the Bot
```bash
# Activate virtual environment (if using one)
source venv/bin/activate

# Run the bot
python main.py
```

### Test the Bot
```bash
# Run tests
python -m pytest tests/
```

## ⚠️ Important Notes

1. **Character Setup Required**: You must use `/setup` in Discord before earning
2. **Survey Availability**: Surveys may not always be available
3. **Rate Limiting**: Respect survey platform rate limits
4. **Account Security**: Keep your Discord account secure

## 🎯 Supported Cryptocurrencies

- Bitcoin (BTC)
- Dogecoin (DOGE)
- Litecoin (LTC)
- Pepe (PEP)
- Polygon (POL)
- Solana (SOL)
- Tron (TRX)
- Wax (WAXP)
- Stellar (XLM)
- Nano (XNO)
- Ripple (XRP)

## 🔧 Troubleshooting

### Common Issues

1. **"No Character" Error**
   - Use `/setup` in Discord to create your character

2. **Bot Won't Start**
   - Check dependencies: `pip install -r requirements.txt`
   - Verify environment variables in `.env`

3. **Survey Not Loading**
   - Check your internet connection
   - Verify the CPX Research URL is correct

4. **Discord Bot Not Responding**
   - Check DISCORD_TOKEN in `.env`
   - Verify bot has proper permissions

## 📞 Support

- Discord Server: https://discord.gg/VXKfzW4B
- Check the #guide channel for detailed instructions
- Use #offers channel for survey-related questions

## 🚀 Ready to Earn!

Your CpxBot is now configured and ready to start earning cryptocurrency through CPX Research surveys. Remember to:

1. ✅ Set up your Discord character
2. ✅ Join the Wyrecraft server
3. ✅ Start completing surveys
4. ✅ Withdraw your earnings

Happy earning! 🎉 