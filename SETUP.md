# 🚀 Quick Setup Guide

## 1. **Clone the Repository**
```bash
git clone https://github.com/brandononchain/GMAIL-MCP-Agent.git
cd GMAIL-MCP-Agent
```

## 2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

## 3. **Configure Gmail API**

### Get Google OAuth2 Credentials:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API
4. Create OAuth2 credentials (Desktop application)
5. Download the JSON file

### Setup Credentials:
```bash
# Copy your downloaded credentials file
cp /path/to/your/credentials.json ./credentials.json

# Or rename the example file and edit it
cp credentials.json.example credentials.json
# Edit credentials.json with your actual values
```

## 4. **Configure Environment**
```bash
# Copy the example environment file
cp env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

## 5. **Test the System**
```bash
# Test Gmail connection
python send_from_csv.py contacts.csv --body_file body.txt

# Start the nurturing system
python run_nurturing.py
```

## 6. **Deploy 24/7 (Optional)**
```bash
# Docker deployment
./deploy.sh

# Or manual Docker
docker-compose up -d
```

## 🔑 Required Files

After setup, you should have these files:
- `credentials.json` - Your Gmail API credentials
- `token.json` - Auto-generated OAuth token
- `.env` - Your environment configuration

## ⚠️ Security Notes

- **Never commit** `credentials.json`, `token.json`, or `.env` to Git
- These files are already in `.gitignore`
- Use `credentials.json.example` and `env.example` as templates

## 🎯 Ready to Go!

Your system is now ready to:
- Send automated emails to 96 dental practices
- Run 24/7 lead nurturing campaigns
- Track responses and manage follow-ups
- Scale to thousands of leads

See `README.md` for complete documentation and advanced features.
