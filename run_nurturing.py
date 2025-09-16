#!/usr/bin/env python3
"""
Simple script to run lead nurturing automation
Run this script daily or multiple times per day
"""

from lead_nurturer import LeadNurturer
import schedule
import time
import json

def run_nurturing():
    """Run the nurturing cycle"""
    print(f"🕐 {time.strftime('%Y-%m-%d %H:%M:%S')} - Starting nurturing cycle")
    
    try:
        nurturer = LeadNurturer()
        nurturer.run_nurturing_cycle()
    except Exception as e:
        print(f"❌ Error in nurturing cycle: {e}")

if __name__ == "__main__":
    # Load interval from config if available
    try:
        with open('nurturing_config.json', 'r') as f:
            cfg = json.load(f)
        interval_hours = int(cfg.get('automation', {}).get('check_responses_interval_hours', 4))
    except Exception:
        interval_hours = 4

    # Run immediately
    run_nurturing()
    
    # Schedule to run every N hours
    schedule.every(interval_hours).hours.do(run_nurturing)
    
    print("🤖 Lead nurturing automation started!")
    print(f"📅 Will run every {interval_hours} hours")
    print("⏹️  Press Ctrl+C to stop")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n🛑 Automation stopped")
