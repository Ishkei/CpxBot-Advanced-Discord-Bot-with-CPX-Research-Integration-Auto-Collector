# CpxBot Setup Guide

This guide will help you set up and configure CpxBot for automated survey completion and Discord integration.

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd CpxBot
   ```

2. **Run the setup script**
   ```bash
   python setup.py
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the bot**
   - Edit `.env` with your credentials
   - Edit `config.yaml` with your server settings

5. **Run the bot**
   ```bash
   python main.py
   ```

## 📋 Prerequisites

### Discord Bot Setup

1. **Create a Discord Application**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Click "New Application"
   - Give it a name (e.g., "CpxBot")

2. **Create a Bot**
   - Go to the "Bot" section
   - Click "Add Bot"
   - Copy the bot token

3. **Set Bot Permissions**
   - Go to "OAuth2" > "URL Generator"
   - Select scopes: `bot`, `applications.commands`
   - Select permissions:
     - Send Messages
     - Read Message History
     - Use Slash Commands
     - Embed Links
     - Attach Files

4. **Invite Bot to Server**
   - Use the generated URL to invite the bot to your server
   - Note the server (guild) ID

### CPX Research Account

1. **Create CPX Research Account**
   - Go to [CPX Research](https://offers.cpx-research.com)
   - Sign up for an account
   - Complete your profile

2. **Get Your Credentials**
   - Username/email
   - Password
   - Note your user ID from the URL

## ⚙️ Configuration

### Environment Variables (.env)

Edit the `.env` file with your actual credentials:

```env
# Discord Configuration
DISCORD_TOKEN=your_discord_bot_token_here
DISCORD_GUILD_ID=your_guild_id_here
DISCORD_WEBHOOK_URL=your_discord_webhook_url_here

# CPX Research Configuration
CPX_USERNAME=your_cpx_username_here
CPX_PASSWORD=your_cpx_password_here

# Tip.cc Auto-collector Integration
TIP_CC_WEBHOOK_URL=your_tip_cc_webhook_url_here

# Database Configuration
DATABASE_URL=sqlite:///data/survey_bot.db

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/survey_bot.log
```

### Configuration File (config.yaml)

Edit `config.yaml` with your server settings:

```yaml
# Discord Configuration
discord:
  token: ${DISCORD_TOKEN}
  guild_id: ${DISCORD_GUILD_ID}
  prefix: "!"

# Channel Configuration
channels:
  airdrops: "airdrops"
  mines: "mines"
  lakes: "lakes"
  alley: "alley"
  stash: "stash"
  nexus: "nexus"
  arena: "arena"
  shop: "shop"
  bank: "bank"
```

## 🎮 Discord Commands

The bot supports all the gaming commands from your Discord server:

### Survey Commands
- `!survey status` - Check survey status
- `!survey start` - Start a new survey
- `!earnings` - Check earnings
- `!withdraw [amount]` - Withdraw funds

### Gaming Commands
- `!setup` - Character setup
- `!profile [@user]` - View profile
- `!mine` - Start mining
- `!fish` - Start fishing
- `!rob` - Start robbing
- `!shop` - View shop
- `!craft` - Craft items
- `!enchant` - Enchant gear
- And many more...

### Tip Commands
- `!tip @user amount` - Tip a user
- `!rain [amount]` - Tip active members
- `!balance` - Check tip.cc balance
- `!auto-collect status` - Auto-collector status

## 🔧 Features

### Survey Automation
- **Automatic Survey Detection**: Finds available surveys on CPX Research
- **Smart Survey Selection**: Prioritizes high-paying, short-duration surveys
- **Automated Completion**: Intelligently answers survey questions
- **Earnings Tracking**: Tracks all earnings and statistics

### Discord Integration
- **Multi-Channel Support**: Works across all your gaming channels
- **Gaming Commands**: Full integration with your Discord server's gaming system
- **Real-time Notifications**: Get notified of survey completions and earnings

### Tip.cc Auto-Collector
- **Automatic Tip Collection**: Collects tips from tip.cc automatically
- **Webhook Integration**: Sends notifications to Discord
- **Configurable Settings**: Set collection intervals and minimum amounts

### Web Scraping
- **Stealth Mode**: Uses advanced techniques to avoid detection
- **Human-like Behavior**: Random delays and realistic interactions
- **Error Handling**: Robust error handling and retry mechanisms

## 🛠️ Advanced Configuration

### Survey Settings

Edit the survey settings in `config.yaml`:

```yaml
cpx_research:
  survey_settings:
    min_earnings: 0.10  # Minimum earnings to accept
    max_time: 30        # Maximum time in minutes
    auto_accept: true   # Automatically accept surveys
    random_delays: true # Add random delays
```

### Auto-Collector Settings

```yaml
auto_collection:
  enabled: true
  collection_interval: 300  # seconds
  min_tip_amount: 0.01
```

### Web Scraping Settings

```yaml
web_scraper:
  headless: true
  timeout: 30
  retry_attempts: 3
```

## 🔍 Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check if the bot token is correct
   - Verify the bot has proper permissions
   - Check if the bot is in the correct server

2. **Survey automation not working**
   - Verify CPX Research credentials
   - Check if Chrome/ChromeDriver is installed
   - Review the logs for errors

3. **Auto-collector not working**
   - Check if tip.cc webhook URL is correct
   - Verify auto-collection is enabled
   - Check collection interval settings

### Logs

Check the logs for detailed information:

```bash
tail -f logs/survey_bot.log
```

### Testing

Run the test suite to verify everything is working:

```bash
python tests/test_basic.py
```

## 📊 Monitoring

### Database

The bot uses SQLite to store:
- Survey completion history
- Earnings data
- Tip collection logs
- Bot statistics

### Statistics

Track your bot's performance:
- Total earnings
- Surveys completed
- Tips collected
- Uptime statistics

## 🔒 Security

### Best Practices

1. **Never commit sensitive data**
   - Keep `.env` file in `.gitignore`
   - Use environment variables for secrets

2. **Regular updates**
   - Keep dependencies updated
   - Monitor for security patches

3. **Monitoring**
   - Review logs regularly
   - Monitor for unusual activity

## 📈 Performance Optimization

### Survey Completion

- **Parallel Processing**: Run multiple surveys simultaneously
- **Smart Scheduling**: Optimize survey selection based on earnings/time ratio
- **Caching**: Cache survey data to reduce API calls

### Discord Integration

- **Rate Limiting**: Respect Discord's rate limits
- **Efficient Commands**: Optimize command processing
- **Background Tasks**: Run heavy operations in background

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For support:
1. Check the logs for error messages
2. Review the troubleshooting section
3. Open an issue on GitHub
4. Contact the development team

## 📄 License

This project is licensed under the MIT License.

---

**Happy Surveying! 🎉** 