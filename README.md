# Survey Bot with CPX Research Integration

An advanced Discord bot that automates survey completion on CPX Research. This bot combines survey automation with Discord integration for seamless survey management.

## 🌟 Features

### Core Features
- **Survey Automation**: Automatically completes surveys on CPX Research website
- **Discord Integration**: Responds to commands in Discord channels
- **Web Scraping**: Intelligent survey detection and completion
- **Data Management**: Tracks survey completion and earnings
- **Firefox Automation**: Uses Firefox browser for survey completion

### Advanced Features
- **Smart Survey Selection**: Prioritizes surveys by earnings and completion rate
- **Anti-Detection**: Human-like behavior simulation during survey completion
- **Earnings Tracking**: Comprehensive tracking of all earnings and withdrawals
- **Database Storage**: SQLite database for persistent data storage
- **Logging System**: Detailed logging for monitoring and debugging

### Survey Commands
The bot supports survey-related commands:
- `!survey status` - Check current survey status
- `!survey start` - Start a new survey
- `!survey earnings` - Check current earnings
- `!survey list` - List available surveys
- `!earnings` - Quick earnings check
- `!withdraw [amount]` - Withdraw earnings to tip.cc wallet

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Chrome browser (for web scraping)
- Discord bot token
- CPX Research account

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd survey_bot_project
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Discord token and other settings
   ```

4. **Configure the bot**
   - Edit `config.yaml` with your Discord server settings
   - Add your CPX Research credentials
   - Configure channel permissions

5. **Run the bot**
   ```bash
   python main.py
   ```

## 📋 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Discord Configuration
DISCORD_TOKEN=your_discord_bot_token_here
DISCORD_GUILD_ID=your_guild_id_here
DISCORD_WEBHOOK_URL=your_discord_webhook_url_here

# CPX Research Configuration
CPX_USERNAME=your_cpx_username_here
CPX_PASSWORD=your_cpx_password_here
CPX_URL=https://offers.cpx-research.com/index.php?app_id=27806&ext_user_id=533055960609193994_1246050346233757798&secure_hash=49069f12991d2283f61a52dc967dff9f&subid_1=&subid_2=&cpx_message_id=K05VejRYcUJsQUw2ZGFYOUkzaEc0bHJCU3BBOElJSEVoRzFJSForNUo1MD0=

# Discord Webhook (Optional)
DISCORD_WEBHOOK_URL=your_discord_webhook_url_here

# Database Configuration
DATABASE_URL=sqlite:///data/survey_bot.db

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/survey_bot.log

# Security Settings
ENCRYPTION_KEY=your_encryption_key_here

# Web Scraping Settings
SELENIUM_HEADLESS=true
BROWSER_TIMEOUT=30
MAX_RETRY_ATTEMPTS=3

# Survey Bot Settings
MIN_EARNINGS_THRESHOLD=0.10
MAX_SURVEY_TIME=30
AUTO_ACCEPT_SURVEYS=true
RANDOM_DELAYS=true

# Auto-Collection Settings
AUTO_COLLECTION_ENABLED=true
COLLECTION_INTERVAL=300
MIN_TIP_AMOUNT=0.01
```

### Discord Bot Setup

1. Create a Discord application at https://discord.com/developers/applications
2. Add a bot to your application
3. Get the bot token and add it to `.env`
4. Invite the bot to your server with appropriate permissions:
   - Send Messages
   - Embed Links
   - Attach Files
   - Read Message History
   - Use Slash Commands

### CPX Research Integration

- Configure your CPX Research account credentials
- Set up survey completion preferences
- Configure earning thresholds and auto-withdrawal

## 🎮 Discord Commands

### Survey Commands
- `!survey status` - Check current survey status
- `!survey start` - Start a new survey
- `!survey earnings` - Check current earnings
- `!survey list` - List available surveys
- `!earnings` - Quick earnings check
- `!withdraw [amount]` - Withdraw earnings to tip.cc wallet

## 🔧 Auto-collector Features

### Tip Detection
The bot automatically detects tips in Discord messages using patterns like:
- `$1.50`, `$5`, `$10.00`
- `1.50 USD`, `5 USD`
- `tip 1.50`, `tip $5`
- `1.50 tip`, `$5 tip`
- `+1.50`, `+$5`

### Collection Settings
- **Minimum Amount**: Set minimum tip amount to collect
- **Collection Interval**: How often to scan for tips
- **Channel Filtering**: Only collect from specific channels
- **Notifications**: Discord webhook notifications for collections

### Smart Features
- **Pattern Recognition**: Detects various tip formats
- **Channel Validation**: Only collects from appropriate channels
- **User Notifications**: Confirms tip collection to sender
- **Database Logging**: Tracks all collection activity

## 📊 Survey Automation

### Survey Selection
- **Earnings Priority**: Automatically selects highest-paying surveys
- **Time Filtering**: Avoids surveys that take too long
- **Rating Consideration**: Prefers surveys with good ratings
- **Category Targeting**: Focuses on preferred survey categories

### Completion Features
- **Smart Answering**: Answers questions based on type
- **Human-like Delays**: Random delays to appear natural
- **Progress Tracking**: Monitors survey completion progress
- **Error Handling**: Graceful handling of survey errors

### Survey Types Supported
- **Rating Questions**: Scale and star ratings
- **Multiple Choice**: Radio buttons and checkboxes
- **Text Input**: Open-ended questions
- **Ranking Questions**: Drag and drop rankings

## 🗄️ Database Schema

### Tables
- **surveys**: Survey completion records
- **earnings**: All earning transactions
- **tips**: Tip collection records
- **bot_stats**: Bot statistics and settings
- **auto_collector_logs**: Auto-collection activity

### Data Tracking
- Survey completion history
- Earnings by source and date
- Tip collection statistics
- Bot performance metrics
- User interaction logs

## 🔒 Security Features

- **Environment Variables**: Secure credential storage
- **Rate Limiting**: Prevents API abuse
- **Error Handling**: Graceful error recovery
- **Logging**: Comprehensive activity logging
- **Database Encryption**: Secure data storage

## 📈 Monitoring and Analytics

### Logging
- **File Rotation**: Automatic log file management
- **Error Tracking**: Detailed error logging
- **Performance Metrics**: Bot performance monitoring
- **User Activity**: Command usage tracking

### Statistics
- Survey completion rates
- Earnings tracking
- Tip collection statistics
- Bot uptime and performance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## ⚠️ Disclaimer

This bot is for educational purposes only. Users are responsible for:
- Complying with Discord's Terms of Service
- Following CPX Research's terms and conditions
- Respecting tip.cc's usage policies
- Ensuring proper bot permissions and setup

## 🆘 Support

For support, please:
1. Check the documentation
2. Review the logs in `logs/survey_bot.log`
3. Open an issue on GitHub
4. Contact the development team

## 🔄 Updates

### Recent Updates
- Added tip.cc auto-collector integration
- Enhanced survey automation features
- Improved error handling and logging
- Added comprehensive gaming commands
- Implemented database persistence

### Planned Features
- Advanced survey filtering
- Machine learning for better answers
- Mobile app integration
- Advanced analytics dashboard
- Multi-platform support

---

**Happy Surveying and Tip Collecting! 🎉** 