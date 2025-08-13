#!/usr/bin/env python3
"""
MCP Server for Google Calendar API
Main entry point for the MCP server that handles calendar queries
"""

import asyncio
import logging
import os
import sys
from mcp_server import CalendarMCPServer

# Configure logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),
        logging.FileHandler('calendar_mcp.log')
    ]
)
logging.getLogger().setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)

async def main():
    """Main entry point for the MCP server"""
    try:
        # Initialize the MCP server
        server = CalendarMCPServer()
        
        # Start the server
        logger.info("Starting Calendar MCP Server...")
        await server.run()
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
