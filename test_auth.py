#!/usr/bin/env python3
"""
Test Google Calendar authentication
"""

import asyncio
import sys
from calendar_service import GoogleCalendarService

async def test_auth():
    """Test Google Calendar authentication"""
    try:
        print("Testing Google Calendar authentication...")
        service = GoogleCalendarService()
        await service.initialize()
        
        print("✅ Authentication successful!")
        print("📅 Fetching a few upcoming events to test...")
        
        events = await service.get_upcoming_events(max_results=3, days_ahead=7)
        
        if events:
            print(f"Found {len(events)} events:")
            for event in events[:3]:
                print(f"  • {event.get('summary', 'No title')} - {event.get('start_formatted', 'No time')}")
        else:
            print("No upcoming events found (which is fine - authentication worked!)")
            
        return True
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_auth())
    sys.exit(0 if success else 1)