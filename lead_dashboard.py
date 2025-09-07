#!/usr/bin/env python3
"""
Lead Nurturing Dashboard
Shows current status of all leads and nurturing activities
"""

import json
import csv
from datetime import datetime
from collections import Counter

def load_lead_data():
    """Load lead data from tracking file"""
    try:
        with open('lead_tracking.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def load_contacts():
    """Load contacts from CSV"""
    contacts = {}
    try:
        with open('contacts.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                contacts[row['to'].lower()] = {
                    'first_name': row['first_name'],
                    'company': row['company']
                }
    except FileNotFoundError:
        pass
    return contacts

def generate_dashboard():
    """Generate and display the lead dashboard"""
    tracking_data = load_lead_data()
    contacts = load_contacts()
    
    print("🎯 LEAD NURTURING DASHBOARD")
    print("=" * 50)
    
    # Overall stats
    total_leads = len(contacts)
    tracked_leads = len(tracking_data)
    
    print(f"📊 OVERVIEW")
    print(f"Total Leads: {total_leads}")
    print(f"Tracked Leads: {tracked_leads}")
    print(f"Tracking Coverage: {(tracked_leads/total_leads*100):.1f}%" if total_leads > 0 else "Tracking Coverage: 0%")
    
    # Status breakdown
    statuses = Counter()
    response_counts = Counter()
    lead_scores = []
    
    for email, data in tracking_data.items():
        statuses[data.get('status', 'new')] += 1
        response_counts[data.get('response_count', 0)] += 1
        lead_scores.append(data.get('lead_score', 0))
    
    print(f"\n📈 STATUS BREAKDOWN")
    for status, count in statuses.most_common():
        percentage = (count/tracked_leads*100) if tracked_leads > 0 else 0
        print(f"  {status.title()}: {count} ({percentage:.1f}%)")
    
    # Response stats
    total_responses = sum(data.get('response_count', 0) for data in tracking_data.values())
    responded_leads = sum(1 for data in tracking_data.values() if data.get('response_count', 0) > 0)
    
    print(f"\n💬 RESPONSE STATS")
    print(f"Total Responses: {total_responses}")
    print(f"Leads Who Responded: {responded_leads}")
    print(f"Response Rate: {(responded_leads/tracked_leads*100):.1f}%" if tracked_leads > 0 else "Response Rate: 0%")
    
    # Lead scoring
    if lead_scores:
        avg_score = sum(lead_scores) / len(lead_scores)
        max_score = max(lead_scores)
        min_score = min(lead_scores)
        
        print(f"\n⭐ LEAD SCORING")
        print(f"Average Score: {avg_score:.1f}")
        print(f"Highest Score: {max_score}")
        print(f"Lowest Score: {min_score}")
    
    # Top leads
    print(f"\n🏆 TOP LEADS BY SCORE")
    top_leads = sorted(tracking_data.items(), 
                      key=lambda x: x[1].get('lead_score', 0), 
                      reverse=True)[:10]
    
    for i, (email, data) in enumerate(top_leads, 1):
        contact_info = contacts.get(email, {})
        name = contact_info.get('first_name', 'Unknown')
        company = contact_info.get('company', 'Unknown')
        score = data.get('lead_score', 0)
        status = data.get('status', 'new')
        
        print(f"  {i:2d}. {name} at {company} - Score: {score} - Status: {status}")
    
    # Recent activity
    print(f"\n🕐 RECENT ACTIVITY")
    recent_activity = []
    
    for email, data in tracking_data.items():
        if data.get('last_contact'):
            try:
                last_contact = datetime.fromisoformat(data['last_contact'])
                contact_info = contacts.get(email, {})
                name = contact_info.get('first_name', 'Unknown')
                company = contact_info.get('company', 'Unknown')
                
                recent_activity.append({
                    'email': email,
                    'name': name,
                    'company': company,
                    'last_contact': last_contact,
                    'status': data.get('status', 'new')
                })
            except:
                continue
    
    recent_activity.sort(key=lambda x: x['last_contact'], reverse=True)
    
    for activity in recent_activity[:5]:
        days_ago = (datetime.now() - activity['last_contact']).days
        print(f"  {activity['name']} at {activity['company']} - {days_ago} days ago - {activity['status']}")
    
    print(f"\n" + "=" * 50)
    print(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    generate_dashboard()
