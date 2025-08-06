# Complete Webhook and Bot Profile Setup Guide

## 🎯 **Overview**

This guide will help you set up:
1. **Multiple Discord webhooks** for different notification types
2. **Bot profile description and commands** that appear when users click your bot

## 🔗 **Part 1: Multiple Webhook Setup**

### **Step 1: Create Discord Channels**

Create these 5 channels in your Discord server:

1. **#survey-notifications** - Survey completion alerts
2. **#earnings-updates** - Earnings notifications  
3. **#error-logs** - Error reports
4. **#system-status** - Bot startup/shutdown
5. **#withdrawal-confirmations** - Withdrawal confirmations

### **Step 2: Create Webhooks**

For each channel:
1. **Right-click** the channel
2. **Select "Edit Channel"**
3. **Go to "Integrations" tab**
4. **Click "Create Webhook"**
5. **Name it** appropriately (e.g., "Survey Bot - Surveys")
6. **Copy the Webhook URL**

### **Step 3: Configure Environment Variables**

Edit your `.env` file and add:

```env
# Discord Webhooks
DISCORD_WEBHOOK_SURVEYS=https://discord.com/api/webhooks/YOUR_SURVEY_WEBHOOK_ID/YOUR_SURVEY_WEBHOOK_TOKEN
DISCORD_WEBHOOK_EARNINGS=https://discord.com/api/webhooks/YOUR_EARNINGS_WEBHOOK_ID/YOUR_EARNINGS_WEBHOOK_TOKEN
DISCORD_WEBHOOK_ERRORS=https://discord.com/api/webhooks/YOUR_ERRORS_WEBHOOK_ID/YOUR_ERRORS_WEBHOOK_TOKEN
DISCORD_WEBHOOK_SYSTEM=https://discord.com/api/webhooks/YOUR_SYSTEM_WEBHOOK_ID/YOUR_SYSTEM_WEBHOOK_TOKEN
DISCORD_WEBHOOK_WITHDRAWALS=https://discord.com/api/webhooks/YOUR_WITHDRAWAL_WEBHOOK_ID/YOUR_WITHDRAWAL_WEBHOOK_TOKEN
```

### **Step 4: Test Webhooks**

Run the setup script:
```bash
python3 setup_multiple_webhooks.py
```

## 🤖 **Part 2: Bot Profile Setup**

### **Step 1: Go to Discord Developer Portal**

1. Visit [Discord Developer Portal](https://discord.com/developers/applications)
2. Sign in with your Discord account
3. Select your bot application

### **Step 2: Set Bot Description**

1. **Go to "Bot" section**
2. **Scroll to "Bot Profile"**
3. **Add Description:**
   ```
   Automated survey completion bot with CPX Research integration. 
   Earn money by completing surveys automatically! Features include:
   • Automated survey completion
   • Real-time earnings tracking
   • Discord notifications
   • Withdrawal system
   • Role-based access control
   ```

### **Step 3: Add Slash Commands**

1. **Go to "Commands" section**
2. **Click "New Command"**
3. **Add these commands:**

| Command | Description | Options |
|---------|-------------|---------|
| `/survey` | Check survey bot status | None |
| `/start` | Start a new survey | None |
| `/earnings` | Check current earnings | None |
| `/withdraw` | Withdraw earnings | `amount` (Number, Required) |
| `/help` | Show all commands | None |
| `/assign` | Assign gamer role | None |
| `/remove` | Remove gamer role | None |
| `/secret` | Secret command (requires role) | None |
| `/poll` | Create a poll | `question` (String, Required) |
| `/status` | Bot system status | None |

### **Step 4: Set Bot Permissions**

1. **Go to "OAuth2" → "URL Generator"**
2. **Select scopes:** `bot`, `applications.commands`
3. **Select permissions:**
   - Send Messages
   - Use Slash Commands
   - Manage Messages
   - Embed Links
   - Add Reactions
   - Read Message History

## 📋 **What You'll Get**

### **Webhook Notifications:**

1. **Survey Completions** (`#survey-notifications`)
   - When surveys are finished
   - Earnings amount
   - Duration taken

2. **Earnings Updates** (`#earnings-updates`)
   - New earnings from surveys
   - Total earnings balance
   - Source of earnings

3. **Error Reports** (`#error-logs`)
   - System errors
   - Survey failures
   - Database issues

4. **System Status** (`#system-status`)
   - Bot startup/shutdown
   - User actions
   - System events

5. **Withdrawal Confirmations** (`#withdrawal-confirmations`)
   - Withdrawal amounts
   - Transaction IDs
   - Payment method

### **Bot Profile Features:**

When users click on your bot, they'll see:

**Name:** SurveyBot
**Description:** Automated survey completion bot with CPX Research integration...

**Commands:**
- `/survey` - Check survey bot status
- `/start` - Start a new survey
- `/earnings` - Check current earnings
- `/withdraw` - Withdraw earnings
- `/help` - Show all commands

## 🚀 **Quick Setup Commands**

```bash
# 1. Run webhook setup
python3 setup_multiple_webhooks.py

# 2. Test webhooks
python3 setup_webhook.py

# 3. Start your bot
python3 main.py
```

## 🎯 **Benefits**

### **Multiple Webhooks:**
- ✅ **Organized notifications** by type
- ✅ **Easy to manage** different channels
- ✅ **Professional appearance** with embeds
- ✅ **Error tracking** and debugging
- ✅ **Real-time updates** for all activities

### **Bot Profile:**
- ✅ **Professional appearance** when users click your bot
- ✅ **Clear description** of what your bot does
- ✅ **Slash commands** appear in profile
- ✅ **Easy discovery** of bot features
- ✅ **Trust building** with users

## 📝 **Example Notifications**

### **Survey Completion:**
```
🎉 Survey Completed!
Successfully completed CPX Research Survey #12345
💰 Earnings: $2.50
⏱️ Duration: 15 minutes
```

### **Earnings Update:**
```
💰 Earnings Update
New earnings from Survey
💵 Amount Earned: $1.75
🏦 Total Earnings: $45.25
```

### **Withdrawal Confirmation:**
```
💸 Withdrawal Confirmed
Withdrawal processed successfully
💰 Amount: $10.00
🏦 Method: tip.cc wallet
🆔 Transaction ID: TXN_123456_1234567890
```

Your bot will now have professional notifications and a great profile! 🎉 