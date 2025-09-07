#!/usr/bin/env python3
"""
Advanced Lead Nurturing System for Gmail CSV Sender
Handles automated follow-ups, response tracking, and lead scoring
"""

import csv
import json
import os
import time
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from email.message import EmailMessage
import base64

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from jinja2 import Template

@dataclass
class Lead:
    email: str
    first_name: str
    company: str
    status: str = "new"  # new, contacted, responded, interested, not_interested, scheduled
    last_contact: Optional[datetime] = None
    response_count: int = 0
    follow_up_count: int = 0
    lead_score: int = 0
    notes: str = ""

class LeadNurturer:
    def __init__(self, credentials_path: str = "credentials.json", token_path: str = "token.json"):
        self.service = self._get_service(credentials_path, token_path)
        self.leads = self._load_leads()
        self.templates = self._load_templates()
        
    def _get_service(self, credentials_path: str, token_path: str):
        """Initialize Gmail service"""
        SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", 
                 "https://www.googleapis.com/auth/gmail.send"]
        
        creds = None
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(token_path, "w") as token:
                token.write(creds.to_json())
        
        return build("gmail", "v1", credentials=creds)
    
    def _load_leads(self) -> Dict[str, Lead]:
        """Load leads from CSV and tracking file"""
        leads = {}
        
        # Load from contacts.csv
        try:
            with open('contacts.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    email = row['to'].strip().lower()
                    leads[email] = Lead(
                        email=email,
                        first_name=row['first_name'],
                        company=row['company']
                    )
        except FileNotFoundError:
            print("contacts.csv not found")
        
        # Load tracking data
        try:
            with open('lead_tracking.json', 'r') as f:
                tracking_data = json.load(f)
                for email, data in tracking_data.items():
                    if email in leads:
                        leads[email].status = data.get('status', 'new')
                        leads[email].last_contact = datetime.fromisoformat(data['last_contact']) if data.get('last_contact') else None
                        leads[email].response_count = data.get('response_count', 0)
                        leads[email].follow_up_count = data.get('follow_up_count', 0)
                        leads[email].lead_score = data.get('lead_score', 0)
                        leads[email].notes = data.get('notes', '')
        except FileNotFoundError:
            print("No existing tracking data found")
        
        return leads
    
    def _save_leads(self):
        """Save lead tracking data"""
        tracking_data = {}
        for email, lead in self.leads.items():
            tracking_data[email] = {
                'status': lead.status,
                'last_contact': lead.last_contact.isoformat() if lead.last_contact else None,
                'response_count': lead.response_count,
                'follow_up_count': lead.follow_up_count,
                'lead_score': lead.lead_score,
                'notes': lead.notes
            }
        
        with open('lead_tracking.json', 'w') as f:
            json.dump(tracking_data, f, indent=2)
    
    def _load_templates(self) -> Dict[str, Template]:
        """Load email templates for different scenarios"""
        templates = {}
        
        # Initial outreach template
        templates['initial'] = Template("""
Hi {{first_name}},

Did you know many dental practices lose 20–30% of new patient inquiries because follow-ups slip through the cracks?

We've built an AI agent that automatically follows up with every lead via SMS/email and books them straight into your calendar.

Clients typically see 5–9 extra appointments in the first 30 days.

Have time for 10-min demo call this week?

Thank you,
Brandon
Quantra Labs
        """.strip())
        
        # Follow-up 1 (3 days later)
        templates['followup_1'] = Template("""
Hi {{first_name}},

Following up on my message about our AI lead follow-up system for dental practices.

I know you're busy, but this could be a game-changer for {{company}}.

Quick question: What's your biggest challenge with patient follow-ups right now?

Best,
Brandon
Quantra Labs
        """.strip())
        
        # Follow-up 2 (1 week later)
        templates['followup_2'] = Template("""
Hi {{first_name}},

I understand you might not be ready to discuss this right now.

Just wanted to share that Dr. Sarah Johnson at Smile Care Clinic increased her new patient bookings by 40% in the first month using our system.

If you're interested in a quick 5-minute demo, just reply with "demo" and I'll send you a calendar link.

No pressure - I'll stop following up after this.

Best,
Brandon
Quantra Labs
        """.strip())
        
        # Response to interest
        templates['interested'] = Template("""
Hi {{first_name}},

Great to hear from you! 

I'd love to show you how our AI system works. Here's a quick calendar link to book a 10-minute demo:

[Calendar Link]

Looking forward to showing you how this can help {{company}} capture more patients.

Best,
Brandon
Quantra Labs
        """.strip())
        
        return templates
    
    def check_for_responses(self):
        """Check Gmail for responses to our outreach"""
        try:
            # Search for recent emails
            query = "in:inbox newer_than:1d"
            results = self.service.users().messages().list(userId='me', q=query).execute()
            messages = results.get('messages', [])
            
            for message in messages:
                msg = self.service.users().messages().get(userId='me', id=message['id']).execute()
                headers = msg['payload'].get('headers', [])
                
                # Get sender email
                sender = None
                subject = None
                for header in headers:
                    if header['name'] == 'From':
                        sender = header['value']
                    elif header['name'] == 'Subject':
                        subject = header['value']
                
                if sender:
                    sender_email = re.search(r'<(.+?)>', sender)
                    if sender_email:
                        sender_email = sender_email.group(1).lower()
                    else:
                        sender_email = sender.lower()
                    
                    # Check if this is a response to our outreach
                    if sender_email in self.leads:
                        self._process_response(sender_email, subject, msg)
                        
        except Exception as e:
            print(f"Error checking responses: {e}")
    
    def _process_response(self, email: str, subject: str, message: dict):
        """Process a response from a lead"""
        lead = self.leads[email]
        lead.response_count += 1
        lead.last_contact = datetime.now()
        
        # Analyze response sentiment and keywords
        body = self._get_message_body(message)
        response_lower = body.lower()
        
        # Update lead score based on response
        if any(word in response_lower for word in ['interested', 'yes', 'demo', 'call', 'meeting']):
            lead.status = 'interested'
            lead.lead_score += 10
            self._send_automated_response(email, 'interested')
        elif any(word in response_lower for word in ['not interested', 'no thanks', 'stop', 'unsubscribe']):
            lead.status = 'not_interested'
            lead.lead_score -= 5
        else:
            lead.lead_score += 2
        
        # Add notes
        lead.notes += f"\n{datetime.now().strftime('%Y-%m-%d')}: Response received - {subject}"
        
        print(f"Processed response from {lead.first_name} at {lead.company}")
    
    def _get_message_body(self, message: dict) -> str:
        """Extract message body from Gmail message"""
        try:
            payload = message['payload']
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body']['data']
                        return base64.urlsafe_b64decode(data).decode('utf-8')
            else:
                if payload['mimeType'] == 'text/plain':
                    data = payload['body']['data']
                    return base64.urlsafe_b64decode(data).decode('utf-8')
        except Exception as e:
            print(f"Error extracting message body: {e}")
        return ""
    
    def _send_automated_response(self, email: str, template_type: str):
        """Send automated response based on template type"""
        lead = self.leads[email]
        template = self.templates[template_type]
        
        subject = "Re: AI Lead Follow-up System for Dental Practices"
        body = template.render(
            first_name=lead.first_name,
            company=lead.company
        )
        
        # Send email (using existing send_message function)
        try:
            msg = EmailMessage()
            msg["To"] = email
            msg["From"] = "brandon@quantralabs.com"  # Update with your email
            msg["Subject"] = subject
            msg.set_content(body)
            
            encoded = base64.urlsafe_b64encode(msg.as_bytes()).decode()
            self.service.users().messages().send(
                userId="me", 
                body={"raw": encoded}
            ).execute()
            
            print(f"Sent {template_type} response to {lead.first_name}")
        except Exception as e:
            print(f"Error sending response: {e}")
    
    def run_follow_up_sequence(self):
        """Run follow-up sequence for leads that need it"""
        now = datetime.now()
        
        for email, lead in self.leads.items():
            if lead.status in ['new', 'contacted'] and lead.last_contact:
                days_since_contact = (now - lead.last_contact).days
                
                # Follow-up 1: 3 days after initial contact
                if days_since_contact >= 3 and lead.follow_up_count == 0:
                    self._send_follow_up(email, 'followup_1')
                    lead.follow_up_count = 1
                    lead.last_contact = now
                
                # Follow-up 2: 7 days after initial contact
                elif days_since_contact >= 7 and lead.follow_up_count == 1:
                    self._send_follow_up(email, 'followup_2')
                    lead.follow_up_count = 2
                    lead.last_contact = now
                    lead.status = 'not_interested'  # Mark as not interested after final follow-up
    
    def _send_follow_up(self, email: str, template_type: str):
        """Send follow-up email"""
        lead = self.leads[email]
        template = self.templates[template_type]
        
        subject = "Following up - AI Lead Follow-up System"
        body = template.render(
            first_name=lead.first_name,
            company=lead.company
        )
        
        try:
            msg = EmailMessage()
            msg["To"] = email
            msg["From"] = "brandon@quantralabs.com"  # Update with your email
            msg["Subject"] = subject
            msg.set_content(body)
            
            encoded = base64.urlsafe_b64encode(msg.as_bytes()).decode()
            self.service.users().messages().send(
                userId="me", 
                body={"raw": encoded}
            ).execute()
            
            print(f"Sent {template_type} to {lead.first_name} at {lead.company}")
        except Exception as e:
            print(f"Error sending follow-up: {e}")
    
    def generate_lead_report(self):
        """Generate a lead nurturing report"""
        total_leads = len(self.leads)
        contacted = sum(1 for lead in self.leads.values() if lead.status != 'new')
        responded = sum(1 for lead in self.leads.values() if lead.response_count > 0)
        interested = sum(1 for lead in self.leads.values() if lead.status == 'interested')
        
        print(f"\n📊 LEAD NURTURING REPORT")
        print(f"Total Leads: {total_leads}")
        print(f"Contacted: {contacted}")
        print(f"Responded: {responded}")
        print(f"Interested: {interested}")
        print(f"Response Rate: {(responded/contacted*100):.1f}%" if contacted > 0 else "Response Rate: 0%")
        print(f"Interest Rate: {(interested/responded*100):.1f}%" if responded > 0 else "Interest Rate: 0%")
        
        # Top leads by score
        top_leads = sorted(self.leads.values(), key=lambda x: x.lead_score, reverse=True)[:5]
        print(f"\n🏆 TOP LEADS BY SCORE:")
        for lead in top_leads:
            print(f"  {lead.first_name} at {lead.company} - Score: {lead.lead_score}")
    
    def run_nurturing_cycle(self):
        """Run the complete nurturing cycle"""
        print("🔄 Starting lead nurturing cycle...")
        
        # Check for responses
        print("📧 Checking for responses...")
        self.check_for_responses()
        
        # Run follow-up sequence
        print("📤 Running follow-up sequence...")
        self.run_follow_up_sequence()
        
        # Save updated data
        self._save_leads()
        
        # Generate report
        self.generate_lead_report()
        
        print("✅ Nurturing cycle complete!")

if __name__ == "__main__":
    import os
    
    nurturer = LeadNurturer()
    nurturer.run_nurturing_cycle()
