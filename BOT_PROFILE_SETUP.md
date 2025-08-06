# Discord Bot Profile Setup Guide

## 🎯 **How to Add Description and Commands to Your Bot Profile**

### **Step 1: Go to Discord Developer Portal**

1. Visit [Discord Developer Portal](https://discord.com/developers/applications)
2. Sign in with your Discord account
3. Select your bot application

### **Step 2: Set Bot Description**

1. **Go to "Bot" section** in the left sidebar
2. **Scroll down to "Bot Profile"**
3. **Add Description:**
   ```
   Create your own communities with our awesome server templates. Build your own kingdom.
   ```
   Or customize it to:
   ```
   Automated survey completion bot with CPX Research integration. 
   Earn money by completing surveys automatically!
   ```

### **Step 3: Add Slash Commands**

1. **Go to "Commands" section** in the left sidebar
2. **Click "New Command"**
3. **Add these commands:**

#### **Command 1: Survey Status**
- **Name:** `survey`
- **Description:** `Check survey bot status and earnings`
- **Options:** None

#### **Command 2: Start Survey**
- **Name:** `start`
- **Description:** `Start a new survey`
- **Options:** None

#### **Command 3: Earnings**
- **Name:** `earnings`
- **Description:** `Check your current earnings`
- **Options:** None

#### **Command 4: Withdraw**
- **Name:** `withdraw`
- **Description:** `Withdraw your earnings`
- **Options:** 
  - **Name:** `amount`
  - **Description:** `Amount to withdraw`
  - **Type:** `Number`
  - **Required:** `True`

#### **Command 5: Help**
- **Name:** `help`
- **Description:** `Show all available commands`
- **Options:** None

### **Step 4: Update Bot Application**

1. **Go to "General Information"**
2. **Update Application Name** (if needed)
3. **Add Application Description:**
   ```
   Survey Bot - Automated CPX Research survey completion with Discord integration
   ```

### **Step 5: Set Bot Permissions**

1. **Go to "OAuth2" → "URL Generator"**
2. **Select scopes:** `bot`, `applications.commands`
3. **Select permissions:**
   - Send Messages
   - Use Slash Commands
   - Manage Messages
   - Embed Links
   - Add Reactions
   - Read Message History

### **Step 6: Update Invite Link**

1. **Copy the generated OAuth2 URL**
2. **Use this URL to invite your bot** with the new permissions

## 📋 **Complete Bot Profile Configuration**

### **Bot Description:**
```
Automated survey completion bot with CPX Research integration. 
Earn money by completing surveys automatically! Features include:
• Automated survey completion
• Real-time earnings tracking
• Discord notifications
• Withdrawal system
• Role-based access control
```

### **Slash Commands to Add:**

1. **`/survey`** - Check survey bot status
2. **`/start`** - Start a new survey
3. **`/earnings`** - Check current earnings
4. **`/withdraw`** - Withdraw earnings
5. **`/help`** - Show all commands
6. **`/assign`** - Assign gamer role
7. **`/remove`** - Remove gamer role
8. **`/secret`** - Secret command (requires role)
9. **`/poll`** - Create a poll
10. **`/status`** - Bot system status

## 🎨 **Bot Avatar and Branding**

### **Recommended Bot Avatar:**
- Use a survey-related icon
- Or a robot/automation icon
- Size: 512x512 pixels
- Format: PNG or JPG

### **Bot Username:**
- **SurveyBot** or **CPX Bot**
- Make it memorable and descriptive

## 🔧 **Integration with Your Code**

The bot will automatically use these slash commands when configured in the Developer Portal. The commands will appear in the bot's profile when users click on it.

## 📝 **Example Bot Profile**

When users click on your bot, they'll see:

**Name:** SurveyBot
**Description:** Automated survey completion bot with CPX Research integration. Earn money by completing surveys automatically!

**Commands:**
- `/survey` - Check survey bot status
- `/start` - Start a new survey  
- `/earnings` - Check current earnings
- `/withdraw` - Withdraw earnings
- `/help` - Show all commands

This makes your bot look professional and users will know exactly what it does! 🎉 