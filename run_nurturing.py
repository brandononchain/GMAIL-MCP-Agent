#!/usr/bin/env python3
"""
Simple script to run lead nurturing automation
Run this script daily or multiple times per day
"""

from lead_nurturer import LeadNurturer
import schedule
import time

def run_nurturing():
    """Run the nurturing cycle"""
    print(f"🕐 {time.strftime('%Y-%m-%d %H:%M:%S')} - Starting nurturing cycle")
    
    try:
        nurturer = LeadNurturer()
        nurturer.run_nurturing_cycle()
    except Exception as e:
        print(f"❌ Error in nurturing cycle: {e}")

if __name__ == "__main__":
    # Run immediately
    run_nurturing()
    
    # Schedule to run every 4 hours
    schedule.every(4).hours.do(run_nurturing)
    
    print("🤖 Lead nurturing automation started!")
    print("📅 Will run every 4 hours")
    print("⏹️  Press Ctrl+C to stop")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n🛑 Automation stopped")
