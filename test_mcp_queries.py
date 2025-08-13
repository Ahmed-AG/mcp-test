#!/usr/bin/env python3
"""
Test MCP server queries to demonstrate functionality
"""

import asyncio
import json
from mcp_server import CalendarMCPServer

async def test_mcp_queries():
    """Test different MCP query types"""
    print("🧪 Testing MCP Calendar Server Queries")
    print("=" * 50)
    
    # Initialize the MCP server
    server = CalendarMCPServer()
    await server.calendar_service.initialize()
    
    # Test queries
    test_cases = [
        {
            "name": "Natural Language Query - Today",
            "tool": "query_calendar",
            "args": {"query": "What's on my schedule today?"}
        },
        {
            "name": "Natural Language Query - This Week", 
            "tool": "query_calendar",
            "args": {"query": "Show me this week's appointments"}
        },
        {
            "name": "Get Upcoming Events",
            "tool": "get_upcoming_events", 
            "args": {"max_results": 5, "days_ahead": 14}
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📋 {test_case['name']}")
        print("-" * 30)
        
        try:
            # Call the appropriate handler
            if test_case['tool'] == 'query_calendar':
                result = await server._handle_calendar_query(test_case['args'])
            elif test_case['tool'] == 'get_upcoming_events':
                result = await server._handle_upcoming_events(test_case['args'])
            else:
                continue
                
            # Print the result
            for content in result:
                print(content.text)
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n✅ MCP Server testing completed!")

if __name__ == "__main__":
    asyncio.run(test_mcp_queries())