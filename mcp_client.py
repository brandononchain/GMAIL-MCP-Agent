#!/usr/bin/env python3
"""
MCP Client for Lead Nurturing System
Provides a simple interface to control the 24/7 lead nurturing server
"""

import asyncio
import json
import sys
from typing import Dict, Any

from mcp.client import Client
from mcp.client.stdio import stdio_client

class LeadNurturingClient:
    """Client for interacting with the Lead Nurturing MCP Server"""
    
    def __init__(self):
        self.client = Client("lead-nurturing-client")
    
    async def connect(self):
        """Connect to the MCP server"""
        async with stdio_client() as (read, write):
            await self.client.connect(read, write)
            return self.client
    
    async def start_nurturing(self, interval_hours: int = 4):
        """Start the nurturing system"""
        result = await self.client.call_tool(
            "start_nurturing",
            {"interval_hours": interval_hours}
        )
        return result.content[0].text
    
    async def stop_nurturing(self):
        """Stop the nurturing system"""
        result = await self.client.call_tool("stop_nurturing", {})
        return result.content[0].text
    
    async def run_single_cycle(self):
        """Run a single nurturing cycle"""
        result = await self.client.call_tool("run_single_cycle", {})
        return result.content[0].text
    
    async def get_status(self):
        """Get system status"""
        result = await self.client.call_tool("get_status", {})
        return result.content[0].text
    
    async def get_lead_report(self):
        """Get lead report"""
        result = await self.client.call_tool("get_lead_report", {})
        return result.content[0].text
    
    async def send_test_email(self, email: str):
        """Send test email"""
        result = await self.client.call_tool("send_test_email", {"email": email})
        return result.content[0].text
    
    async def get_logs(self, lines: int = 50):
        """Get recent logs"""
        result = await self.client.call_tool("get_logs", {"lines": lines})
        return result.content[0].text

async def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        print("""
🤖 Lead Nurturing MCP Client

Usage: python mcp_client.py <command> [arguments]

Commands:
  start [hours]     - Start nurturing system (default: 4 hours interval)
  stop             - Stop nurturing system
  cycle            - Run single nurturing cycle
  status           - Get system status
  report           - Get lead report
  test <email>     - Send test email
  logs [lines]     - Get recent logs (default: 50 lines)

Examples:
  python mcp_client.py start 6
  python mcp_client.py status
  python mcp_client.py test your-email@example.com
        """)
        return
    
    command = sys.argv[1]
    client = LeadNurturingClient()
    
    try:
        await client.connect()
        
        if command == "start":
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 4
            result = await client.start_nurturing(interval)
            print(result)
            
        elif command == "stop":
            result = await client.stop_nurturing()
            print(result)
            
        elif command == "cycle":
            result = await client.run_single_cycle()
            print(result)
            
        elif command == "status":
            result = await client.get_status()
            print(result)
            
        elif command == "report":
            result = await client.get_lead_report()
            print(result)
            
        elif command == "test":
            if len(sys.argv) < 3:
                print("❌ Email address required for test command")
                return
            email = sys.argv[2]
            result = await client.send_test_email(email)
            print(result)
            
        elif command == "logs":
            lines = int(sys.argv[2]) if len(sys.argv) > 2 else 50
            result = await client.get_logs(lines)
            print(result)
            
        else:
            print(f"❌ Unknown command: {command}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
