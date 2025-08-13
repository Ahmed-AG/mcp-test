#!/usr/bin/env python3
"""
Manual driver to test MCP server tool connectivity with Google Calendar
"""
import asyncio
import logging
from mcp_server import CalendarMCPServer

async def test_tools():
    server = CalendarMCPServer()
    await server.calendar_service.initialize()

    calendar_id = "ahmed.aviata@gmail.com"  # Change to your desired calendar

    print("\n--- Testing query_calendar ---")
    args = {"query": "What's on my schedule today?", "calendar_id": calendar_id}
    result = await server._handle_calendar_query(args)
    for content in result:
        print(content.text)

    print("\n--- Testing get_upcoming_events ---")
    args = {"max_results": 5, "days_ahead": 14, "calendar_id": calendar_id}
    result = await server._handle_upcoming_events(args)
    for content in result:
        print(content.text)

    print("\n--- Testing check_availability ---")
    args = {
        "start_time": "2025-08-12T14:00:00",
        "end_time": "2025-08-12T15:00:00",
        "calendar_id": calendar_id
    }
    result = await server._handle_availability_check(args)
    for content in result:
        print(content.text)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(test_tools())
