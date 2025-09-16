#!/usr/bin/env python3
"""
MCP Server for Lead Nurturing System
Provides remote control and monitoring of the 24/7 lead nurturing automation
"""

import asyncio
import json
import logging
import os
import signal
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

# Import our lead nurturing system
from lead_nurturer import LeadNurturer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ServerState:
    """Server state management"""
    is_running: bool = False
    last_run: Optional[datetime] = None
    total_runs: int = 0
    error_count: int = 0
    nurturer: Optional[LeadNurturer] = None

class LeadNurturingMCPServer:
    """MCP Server for Lead Nurturing System"""
    
    def __init__(self):
        self.server = Server("lead-nurturing-server")
        self.state = ServerState()
        self.setup_handlers()
        self.setup_signal_handlers()
        
    def setup_handlers(self):
        """Setup MCP server handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List available tools"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="start_nurturing",
                        description="Start the lead nurturing automation system",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "interval_hours": {
                                    "type": "integer",
                                    "description": "Hours between nurturing cycles (default: 4)",
                                    "default": 4
                                }
                            }
                        }
                    ),
                    Tool(
                        name="stop_nurturing",
                        description="Stop the lead nurturing automation system",
                        inputSchema={
                            "type": "object",
                            "properties": {}
                        }
                    ),
                    Tool(
                        name="run_single_cycle",
                        description="Run a single nurturing cycle immediately",
                        inputSchema={
                            "type": "object",
                            "properties": {}
                        }
                    ),
                    Tool(
                        name="get_status",
                        description="Get current system status and statistics",
                        inputSchema={
                            "type": "object",
                            "properties": {}
                        }
                    ),
                    Tool(
                        name="get_lead_report",
                        description="Get detailed lead nurturing report",
                        inputSchema={
                            "type": "object",
                            "properties": {}
                        }
                    ),
                    Tool(
                        name="update_config",
                        description="Update nurturing configuration",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "config": {
                                    "type": "object",
                                    "description": "Configuration updates"
                                }
                            }
                        }
                    ),
                    Tool(
                        name="send_test_email",
                        description="Send a test email to verify system",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "email": {
                                    "type": "string",
                                    "description": "Email address to send test to"
                                }
                            }
                        }
                    ),
                    Tool(
                        name="get_logs",
                        description="Get recent system logs",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "lines": {
                                    "type": "integer",
                                    "description": "Number of log lines to retrieve (default: 50)",
                                    "default": 50
                                }
                            }
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls"""
            try:
                if name == "start_nurturing":
                    return await self.start_nurturing(arguments)
                elif name == "stop_nurturing":
                    return await self.stop_nurturing(arguments)
                elif name == "run_single_cycle":
                    return await self.run_single_cycle(arguments)
                elif name == "get_status":
                    return await self.get_status(arguments)
                elif name == "get_lead_report":
                    return await self.get_lead_report(arguments)
                elif name == "update_config":
                    return await self.update_config(arguments)
                elif name == "send_test_email":
                    return await self.send_test_email(arguments)
                elif name == "get_logs":
                    return await self.get_logs(arguments)
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"Unknown tool: {name}")]
                    )
            except Exception as e:
                logger.error(f"Error handling tool {name}: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")]
                )
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down gracefully...")
            self.stop_nurturing({})
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def start_nurturing(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Start the nurturing automation"""
        try:
            if self.state.is_running:
                return CallToolResult(
                    content=[TextContent(type="text", text="Nurturing system is already running")]
                )
            
            interval_hours = arguments.get("interval_hours", 4)
            
            # Initialize nurturer
            self.state.nurturer = LeadNurturer()
            self.state.is_running = True
            
            # Start background task
            asyncio.create_task(self._nurturing_loop(interval_hours))
            
            logger.info(f"Started nurturing system with {interval_hours}h interval")
            
            return CallToolResult(
                content=[TextContent(
                    type="text", 
                    text=f"✅ Lead nurturing system started successfully!\n"
                         f"🕐 Running every {interval_hours} hours\n"
                         f"📊 Monitoring {len(self.state.nurturer.leads)} leads"
                )]
            )
            
        except Exception as e:
            logger.error(f"Error starting nurturing: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ Error starting system: {str(e)}")]
            )
    
    async def stop_nurturing(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Stop the nurturing automation"""
        try:
            self.state.is_running = False
            
            if self.state.nurturer:
                self.state.nurturer._save_leads()
            
            logger.info("Stopped nurturing system")
            
            return CallToolResult(
                content=[TextContent(
                    type="text", 
                    text="🛑 Lead nurturing system stopped successfully"
                )]
            )
            
        except Exception as e:
            logger.error(f"Error stopping nurturing: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ Error stopping system: {str(e)}")]
            )
    
    async def run_single_cycle(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Run a single nurturing cycle"""
        try:
            if not self.state.nurturer:
                self.state.nurturer = LeadNurturer()
            
            # Run the cycle
            self.state.nurturer.run_nurturing_cycle()
            self.state.total_runs += 1
            self.state.last_run = datetime.now()
            
            logger.info("Completed single nurturing cycle")
            
            return CallToolResult(
                content=[TextContent(
                    type="text", 
                    text="✅ Single nurturing cycle completed successfully!"
                )]
            )
            
        except Exception as e:
            self.state.error_count += 1
            logger.error(f"Error in single cycle: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ Error in cycle: {str(e)}")]
            )
    
    async def get_status(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Get system status"""
        try:
            status_text = f"""
🤖 **LEAD NURTURING SYSTEM STATUS**

🔄 **System Status**: {'🟢 Running' if self.state.is_running else '🔴 Stopped'}
📅 **Last Run**: {self.state.last_run.strftime('%Y-%m-%d %H:%M:%S') if self.state.last_run else 'Never'}
🔢 **Total Runs**: {self.state.total_runs}
❌ **Error Count**: {self.state.error_count}

📊 **Lead Statistics**:
"""
            
            if self.state.nurturer:
                leads = self.state.nurturer.leads
                total_leads = len(leads)
                contacted = sum(1 for lead in leads.values() if lead.status != 'new')
                responded = sum(1 for lead in leads.values() if lead.response_count > 0)
                interested = sum(1 for lead in leads.values() if lead.status == 'interested')

                response_rate_text = "N/A"
                if contacted > 0:
                    response_rate_text = f"{(responded / contacted * 100):.1f}%"

                status_text += f"""
• Total Leads: {total_leads}
• Contacted: {contacted}
• Responded: {responded}
• Interested: {interested}
• Response Rate: {response_rate_text}
"""
            else:
                status_text += "• No nurturer initialized"
            
            return CallToolResult(
                content=[TextContent(type="text", text=status_text)]
            )
            
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ Error getting status: {str(e)}")]
            )
    
    async def get_lead_report(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Get detailed lead report"""
        try:
            if not self.state.nurturer:
                self.state.nurturer = LeadNurturer()
            
            # Capture the report output
            import io
            import contextlib
            
            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                self.state.nurturer.generate_lead_report()
            
            report_text = f.getvalue()
            
            return CallToolResult(
                content=[TextContent(type="text", text=report_text)]
            )
            
        except Exception as e:
            logger.error(f"Error getting lead report: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ Error getting report: {str(e)}")]
            )
    
    async def update_config(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Update configuration"""
        try:
            config_updates = arguments.get("config", {})
            
            # Load existing config
            try:
                with open('nurturing_config.json', 'r') as f:
                    config = json.load(f)
            except FileNotFoundError:
                config = {}
            
            # Update config
            config.update(config_updates)
            
            # Save config
            with open('nurturing_config.json', 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Updated configuration: {config_updates}")
            
            # Hot-reload config into running nurturer
            try:
                if self.state.nurturer:
                    self.state.nurturer.reload_config(config)
            except Exception as e:
                logger.warning(f"Failed to hot-reload config into nurturer: {e}")

            return CallToolResult(
                content=[TextContent(
                    type="text", 
                    text=f"✅ Configuration updated successfully!\n"
                         f"Updated: {list(config_updates.keys())}"
                )]
            )
            
        except Exception as e:
            logger.error(f"Error updating config: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ Error updating config: {str(e)}")]
            )
    
    async def send_test_email(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Send test email"""
        try:
            test_email = arguments.get("email")
            if not test_email:
                return CallToolResult(
                    content=[TextContent(type="text", text="❌ Email address required")]
                )
            
            if not self.state.nurturer:
                self.state.nurturer = LeadNurturer()
            
            # Send test email
            test_subject = "Test Email - Lead Nurturing System"
            test_body = f"""
This is a test email from your Lead Nurturing System.

System Status: {'Running' if self.state.is_running else 'Stopped'}
Last Run: {self.state.last_run.strftime('%Y-%m-%d %H:%M:%S') if self.state.last_run else 'Never'}
Total Runs: {self.state.total_runs}

If you receive this email, your system is working correctly!

Best regards,
Lead Nurturing System
            """.strip()
            
            # Create and send email
            from email.message import EmailMessage
            import base64
            
            msg = EmailMessage()
            msg["To"] = test_email
            try:
                with open('nurturing_config.json', 'r') as f:
                    cfg = json.load(f)
                sender_email = cfg.get('sender_email')
                sender_name = cfg.get('sender_name') or ''
            except Exception:
                sender_email = None
                sender_name = ''

            fallback_email = self.state.nurturer.service.users().getProfile(userId="me").execute().get("emailAddress")
            from_header = sender_email or fallback_email
            msg["From"] = f"{sender_name} <{from_header}>" if sender_name else from_header
            msg["Subject"] = test_subject
            msg.set_content(test_body)
            
            encoded = base64.urlsafe_b64encode(msg.as_bytes()).decode()
            self.state.nurturer.service.users().messages().send(
                userId="me", 
                body={"raw": encoded}
            ).execute()
            
            logger.info(f"Sent test email to {test_email}")
            
            return CallToolResult(
                content=[TextContent(
                    type="text", 
                    text=f"✅ Test email sent successfully to {test_email}"
                )]
            )
            
        except Exception as e:
            logger.error(f"Error sending test email: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ Error sending test email: {str(e)}")]
            )
    
    async def get_logs(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Get recent logs"""
        try:
            lines = arguments.get("lines", 50)
            
            try:
                with open('mcp_server.log', 'r') as f:
                    log_lines = f.readlines()
                    recent_logs = log_lines[-lines:] if len(log_lines) > lines else log_lines
                    
                log_text = "".join(recent_logs)
                
                return CallToolResult(
                    content=[TextContent(
                        type="text", 
                        text=f"📋 **Recent Logs (Last {len(recent_logs)} lines):**\n\n```\n{log_text}\n```"
                    )]
                )
                
            except FileNotFoundError:
                return CallToolResult(
                    content=[TextContent(type="text", text="No log file found")]
                )
                
        except Exception as e:
            logger.error(f"Error getting logs: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ Error getting logs: {str(e)}")]
            )
    
    async def _nurturing_loop(self, interval_hours: int):
        """Background nurturing loop"""
        while self.state.is_running:
            try:
                logger.info("Starting nurturing cycle...")
                
                if not self.state.nurturer:
                    self.state.nurturer = LeadNurturer()
                
                self.state.nurturer.run_nurturing_cycle()
                self.state.total_runs += 1
                self.state.last_run = datetime.now()
                
                logger.info(f"Nurturing cycle completed. Next run in {interval_hours} hours.")
                
                # Wait for next cycle
                await asyncio.sleep(interval_hours * 3600)
                
            except Exception as e:
                self.state.error_count += 1
                logger.error(f"Error in nurturing loop: {e}")
                # Exponential backoff up to 30 minutes
                backoff_seconds = min(1800, 60 * (2 ** min(self.state.error_count, 5)))
                await asyncio.sleep(backoff_seconds)
    
    async def run(self):
        """Run the MCP server"""
        logger.info("Starting Lead Nurturing MCP Server...")
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="lead-nurturing-server",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None,
                    ),
                ),
            )

async def main():
    """Main entry point"""
    server = LeadNurturingMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
