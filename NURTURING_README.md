# 🤖 Lead Nurturing & Automation System

A comprehensive system for automating lead nurturing, response tracking, and follow-up sequences for your dental practice outreach campaign.

## 🚀 Features

### ✅ Automated Lead Nurturing
- **Follow-up Sequences**: Automatic follow-ups at 3 days and 7 days
- **Response Tracking**: Monitors Gmail for replies and categorizes them
- **Lead Scoring**: Tracks engagement and interest levels
- **Smart Responses**: Automatically responds to interested leads

### 📊 Lead Management
- **Status Tracking**: new → contacted → responded → interested/not_interested
- **Response Analysis**: Parses email content for sentiment and keywords
- **Lead Scoring**: Points system based on engagement
- **Activity Logging**: Complete history of all interactions

### 🎯 Email Templates
- **Initial Outreach**: Your main dental practice message
- **Follow-up 1**: 3-day follow-up with engagement question
- **Follow-up 2**: 7-day final follow-up with social proof
- **Interest Response**: Automatic response to interested leads

## 📁 Files Created

- `lead_nurturer.py` - Main nurturing system
- `run_nurturing.py` - Automation runner
- `lead_dashboard.py` - Lead monitoring dashboard
- `nurturing_config.json` - Configuration settings
- `lead_tracking.json` - Lead data storage (auto-created)

## 🛠️ Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Settings**:
   - Update `nurturing_config.json` with your email and preferences
   - Set your sender email in the config

3. **Run Initial Setup**:
   ```bash
   python lead_nurturer.py
   ```

## 🎮 Usage

### Manual Nurturing Cycle
```bash
python lead_nurturer.py
```

### Automated Nurturing (Every 4 Hours)
```bash
python run_nurturing.py
```

### View Lead Dashboard
```bash
python lead_dashboard.py
```

## 📈 How It Works

### 1. Response Monitoring
- Checks Gmail every 4 hours for new responses
- Analyzes email content for interest keywords
- Updates lead status and scores automatically

### 2. Follow-up Sequences
- **Day 0**: Initial outreach email sent
- **Day 3**: First follow-up with engagement question
- **Day 7**: Final follow-up with social proof
- **After Day 7**: Lead marked as "not_interested"

### 3. Lead Scoring System
- **+10 points**: Response received
- **+5 points**: Interest expressed
- **+2 points**: Any response
- **-5 points**: Not interested
- **-1 point**: Each follow-up sent

### 4. Automated Responses
- **Interested leads**: Automatic response with calendar link
- **Not interested**: No further follow-ups
- **Neutral responses**: Continue nurturing sequence

## 📊 Dashboard Features

The dashboard shows:
- Total leads and tracking coverage
- Status breakdown (new, contacted, responded, interested)
- Response rates and statistics
- Top leads by score
- Recent activity timeline

## ⚙️ Configuration

Edit `nurturing_config.json` to customize:

```json
{
  "sender_email": "your-email@domain.com",
  "follow_up_schedule": {
    "followup_1_days": 3,
    "followup_2_days": 7
  },
  "response_keywords": {
    "interested": ["interested", "yes", "demo"],
    "not_interested": ["not interested", "no thanks"]
  }
}
```

## 🔄 Automation Schedule

- **Response Checking**: Every 4 hours
- **Follow-up Sending**: Based on last contact date
- **Data Saving**: After each cycle
- **Report Generation**: After each cycle

## 📱 Monitoring

Run the dashboard anytime to see:
```bash
python lead_dashboard.py
```

## 🎯 Best Practices

1. **Run Daily**: Execute the nurturing cycle at least once per day
2. **Monitor Responses**: Check the dashboard regularly
3. **Customize Templates**: Adjust email templates for your industry
4. **Review Scores**: Focus on high-scoring leads
5. **Update Keywords**: Refine response detection keywords

## 🚨 Important Notes

- **Gmail API Limits**: Respect Gmail's rate limits
- **Email Authentication**: Ensure your sender email is properly configured
- **Data Backup**: The system auto-saves to `lead_tracking.json`
- **Privacy**: All data is stored locally

## 🔧 Troubleshooting

- **No responses detected**: Check Gmail API permissions
- **Follow-ups not sending**: Verify sender email configuration
- **Dashboard empty**: Run the nurturing cycle first
- **Import errors**: Install all dependencies from requirements.txt

## 📈 Expected Results

With proper setup, you should see:
- **20-30% response rate** from initial outreach
- **40-60% response rate** from follow-ups
- **10-15% conversion rate** to interested leads
- **Automated handling** of 80% of responses

---

**Ready to nurture your leads? Run `python lead_nurturer.py` to get started!** 🚀
