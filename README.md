# 🤖 Gmail MCP Agent - 24/7 Lead Nurturing System

A comprehensive, enterprise-grade lead nurturing system that automates Gmail outreach campaigns with intelligent follow-ups, response tracking, and 24/7 operation via MCP (Model Context Protocol) server.

## 🚀 Features

### ✅ **Automated Lead Nurturing**
- **24/7 Operation** - Runs continuously with Docker containerization
- **Intelligent Follow-ups** - Automatic sequences at 3 days and 7 days
- **Response Tracking** - Monitors Gmail for replies and categorizes them
- **Lead Scoring** - Tracks engagement and interest levels
- **Smart Responses** - Automatically responds to interested leads

### 📊 **MCP Server Architecture**
- **Remote Control** - Control system via MCP protocol
- **Real-time Monitoring** - Live status and performance tracking
- **Docker Deployment** - Production-ready containerization
- **Health Checks** - Automatic recovery and error handling
- **Scalable Design** - Ready for enterprise use

### 🎯 **Email Campaign Management**
- **CSV-based Lead Lists** - Easy contact management
- **Template System** - Jinja2-powered email personalization
- **Rate Limiting** - Respects Gmail API quotas
- **Resume Capability** - Continue from where you left off
- **Comprehensive Logging** - Complete audit trail

## 📁 Project Structure

```
├── send_from_csv.py          # Main Gmail sender script
├── lead_nurturer.py          # Automated nurturing system
├── mcp_server.py             # 24/7 MCP server
├── mcp_client.py             # Control interface
├── lead_dashboard.py         # Monitoring dashboard
├── run_nurturing.py          # Automation runner
├── contacts.csv              # Lead database (96 dental practices)
├── body.txt                  # Email template
├── credentials.json          # Gmail API credentials
├── nurturing_config.json     # System configuration
├── requirements.txt          # Python dependencies
├── Dockerfile               # Container configuration
├── docker-compose.yml       # Deployment setup
├── deploy.sh                # One-click deployment
└── DEPLOYMENT_GUIDE.md      # Complete setup guide
```

## 🛠️ Quick Start

### 1. **Clone and Setup**
```bash
git clone https://github.com/brandononchain/GMAIL-MCP-Agent.git
cd GMAIL-MCP-Agent
pip install -r requirements.txt
```

### 2. **Configure Gmail API**
- Get OAuth2 credentials from Google Cloud Console
- Save as `credentials.json`
- Update sender email in `nurturing_config.json`

### 3. **Deploy 24/7 System**
```bash
# Docker deployment (recommended)
./deploy.sh

# Or manual deployment
docker-compose up -d
```

### 4. **Start Nurturing**
```bash
# Using MCP client
python mcp_client.py start 4

# Or direct execution
python run_nurturing.py
```

## 🎮 Control Commands

### MCP Client Interface
```bash
# Start nurturing system (every 4 hours)
python mcp_client.py start 4

# Check system status
python mcp_client.py status

# Get lead report
python mcp_client.py report

# Send test email
python mcp_client.py test your-email@example.com

# View recent logs
python mcp_client.py logs 100

# Stop the system
python mcp_client.py stop
```

### Direct Scripts
```bash
# Run single nurturing cycle
python lead_nurturer.py

# View lead dashboard
python lead_dashboard.py

# Send emails from CSV
python send_from_csv.py contacts.csv --body_file body.txt
```

## 📊 Current Campaign

### **Dental Practice Outreach**
- **Target**: 96 dental practices in Chicago
- **Message**: AI lead follow-up system for dental practices
- **Follow-up Schedule**: 3 days and 7 days after initial contact
- **Expected Results**: 20-30% response rate, 10-15% conversion

### **Email Template**
```
Hi {{first_name}},

Did you know many dental practices lose 20–30% of new patient inquiries because follow-ups slip through the cracks?

We've built an AI agent that automatically follows up with every lead via SMS/email and books them straight into your calendar.

Clients typically see 5–9 extra appointments in the first 30 days.

Have time for 10-min demo call this week?

Thank you,
Brandon
Quantra Labs
```

## 🔧 Configuration

### Environment Variables
```env
# Gmail API Configuration
CREDENTIALS_FILE=credentials.json
TOKEN_FILE=token.json

# Nurturing Settings
PER_MINUTE=12
RESUME=false
LOG_FILE=send_log.csv

# MCP Server Settings
MCP_SERVER_PORT=8000
LOG_LEVEL=INFO
```

### Nurturing Configuration
```json
{
  "sender_email": "your-email@domain.com",
  "follow_up_schedule": {
    "followup_1_days": 3,
    "followup_2_days": 7
  },
  "automation": {
    "check_responses_interval_hours": 4,
    "auto_respond_to_interest": true
  }
}
```

## 📈 Performance Metrics

### Expected Results
- **Response Rate**: 20-30% from initial outreach
- **Follow-up Response**: 40-60% from follow-ups
- **Conversion Rate**: 10-15% to interested leads
- **Automation Coverage**: 80% of responses handled automatically
- **Uptime**: 99.9% with Docker restart policies

### Monitoring
- Real-time lead scoring and status tracking
- Response rate analytics and conversion metrics
- System health monitoring and error reporting
- Complete audit trail of all interactions

## 🚀 Deployment Options

### Docker (Recommended)
```bash
# One-click deployment
./deploy.sh

# Manual deployment
docker-compose up -d
```

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run nurturing system
python run_nurturing.py
```

### Production Server
```bash
# Systemd service
sudo cp lead-nurturing.service /etc/systemd/system/
sudo systemctl enable lead-nurturing
sudo systemctl start lead-nurturing
```

## 🔒 Security & Privacy

- **Local Data Storage** - All data remains on your server
- **OAuth2 Authentication** - Secure Gmail API access
- **No External Services** - No data sent to third parties
- **Encrypted Credentials** - Secure credential management
- **Audit Logging** - Complete activity tracking

## 📞 Support & Documentation

- **Deployment Guide**: `DEPLOYMENT_GUIDE.md`
- **Nurturing Guide**: `NURTURING_README.md`
- **Debug Report**: `DEBUG_REPORT.md`
- **Docker Setup**: `docker-compose.yml`

## 🎯 Use Cases

### **Sales Outreach**
- B2B lead generation and nurturing
- Automated follow-up sequences
- Response tracking and lead scoring

### **Marketing Campaigns**
- Email marketing automation
- A/B testing and optimization
- Performance analytics

### **Customer Success**
- Onboarding email sequences
- Renewal and upsell campaigns
- Customer feedback collection

## 📊 System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCP Client    │◄──►│   MCP Server     │◄──►│  Lead Nurturer  │
│  (Control)      │    │  (24/7 Service)  │    │  (Automation)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   Gmail API      │
                       │  (Email System)  │
                       └──────────────────┘
```

## 🏆 Enterprise Features

- **24/7 Operation** - Continuous automation
- **Scalable Architecture** - Handle thousands of leads
- **Professional Monitoring** - Real-time dashboards
- **Error Recovery** - Automatic failure handling
- **Audit Compliance** - Complete activity logging
- **Docker Deployment** - Production-ready containerization

---

**Ready to automate your lead nurturing?** 🚀

This system is production-ready and can handle enterprise-scale email campaigns with full automation, monitoring, and 24/7 operation.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

- **Author**: Brandon
- **Company**: Quantra Labs
- **Repository**: [GMAIL-MCP-Agent](https://github.com/brandononchain/GMAIL-MCP-Agent)