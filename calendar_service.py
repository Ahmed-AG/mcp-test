"""
Google Calendar API service
Handles authentication and calendar operations
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import pytz
from dateutil import parser as date_parser

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

class GoogleCalendarService:
    """Service for interacting with Google Calendar API"""
    
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    
    def __init__(self):
        self.service = None
        self.credentials = None
        self.default_timezone = pytz.timezone('UTC')
        
        # Try to detect system timezone
        try:
            import tzlocal
            self.default_timezone = tzlocal.get_localzone()
        except ImportError:
            logger.warning("tzlocal not available, using UTC as default timezone")
    
    async def initialize(self):
        """Initialize the Google Calendar service"""
        await self._authenticate()
        
        if self.credentials:
            self.service = build('calendar', 'v3', credentials=self.credentials)
            logger.info("Google Calendar service initialized successfully")
        else:
            raise Exception("Failed to authenticate with Google Calendar API")
    
    async def _authenticate(self):
        """Authenticate with Google Calendar API"""
        creds = None
        
        # First try service account credentials
        service_account_key = os.getenv("GOOGLE_SERVICE_ACCOUNT_KEY")
        if service_account_key:
            try:
                service_account_info = json.loads(service_account_key)
                creds = ServiceCredentials.from_service_account_info(
                    service_account_info, scopes=self.SCOPES
                )
                logger.info("Successfully authenticated with service account")
                self.credentials = creds
                return
            except Exception as e:
                logger.warning(f"Service account authentication failed: {e}")
        
        # Try service account file
        if os.path.exists('service-account-key.json'):
            try:
                creds = ServiceCredentials.from_service_account_file(
                    'service-account-key.json', scopes=self.SCOPES
                )
                logger.info("Successfully authenticated with service account file")
                self.credentials = creds
                return
            except Exception as e:
                logger.warning(f"Service account file authentication failed: {e}")
        
        # Fallback to OAuth flow (existing code)
        # Check for existing token
        # (Removed support for GOOGLE_CREDENTIALS_JSON and credentials.json)
        
        self.credentials = creds
    
    def _parse_timezone(self, timezone_str: Optional[str]) -> Union[pytz.BaseTzInfo, Any]:
        """Parse timezone string and return timezone object"""
        if not timezone_str:
            return self.default_timezone
        
        try:
            return pytz.timezone(timezone_str)
        except pytz.exceptions.UnknownTimeZoneError:
            logger.warning(f"Unknown timezone: {timezone_str}, using default")
            return self.default_timezone
    
    def _format_datetime(self, dt_str: str, timezone: Optional[pytz.BaseTzInfo] = None) -> str:
        """Format datetime string for display"""
        try:
            # Parse the datetime
            if 'T' in dt_str:
                dt = date_parser.parse(dt_str)
            else:
                # All-day event
                return dt_str
            
            # Convert to specified timezone if provided
            if timezone and dt.tzinfo:
                dt = dt.astimezone(timezone)
            
            # Format for display
            return dt.strftime("%I:%M %p on %A, %B %d")
        except Exception as e:
            logger.warning(f"Failed to format datetime {dt_str}: {e}")
            return dt_str
    
    async def get_upcoming_events(self, max_results: int = 10, days_ahead: int = 7, timezone: Optional[str] = None, calendar_id: Optional[str] = None) -> List[Dict]:
        """Get upcoming calendar events"""
        if not self.service:
            raise Exception("Calendar service not initialized")

        try:
            # Calculate time range
            now = datetime.utcnow()
            time_max = now + timedelta(days=days_ahead)

            # Convert to RFC3339 format correctly
            def to_rfc3339(dt):
                if dt.tzinfo is not None:
                    return dt.isoformat()
                else:
                    return dt.isoformat() + 'Z'

            time_min = to_rfc3339(now)
            time_max = to_rfc3339(time_max)

            # Use provided calendar_id or default to 'primary'
            calendar_id = calendar_id or 'primary'
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            logger.debug(f"Raw Google Calendar API response (get_upcoming_events): {json.dumps(events_result, indent=2)}")

            events = events_result.get('items', [])

            # Format events
            formatted_events = []
            tz = self._parse_timezone(timezone)

            for event in events:
                formatted_event = self._format_event(event, tz)
                if formatted_event:
                    formatted_events.append(formatted_event)

            return formatted_events

        except HttpError as error:
            logger.error(f"Google Calendar API error: {error}")
            raise Exception(f"Failed to fetch calendar events: {error}")
    
    async def get_events_for_date(self, date: datetime, timezone: Optional[str] = None, calendar_id: Optional[str] = None) -> List[Dict]:
        """Get events for a specific date"""
        if not self.service:
            raise Exception("Calendar service not initialized")

        try:
            # Set time range for the specific date
            start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)

            # Convert to RFC3339 format correctly
            def to_rfc3339(dt):
                if dt.tzinfo is not None:
                    # If aware, use isoformat (includes offset)
                    return dt.isoformat()
                else:
                    # If naive, treat as UTC and add 'Z'
                    return dt.isoformat() + 'Z'

            time_min = to_rfc3339(start_of_day)
            time_max = to_rfc3339(end_of_day)

            calendar_id = calendar_id or 'primary'
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            logger.debug(f"Raw Google Calendar API response (get_events_for_date): {json.dumps(events_result, indent=2)}")

            events = events_result.get('items', [])

            # Format events
            formatted_events = []
            tz = self._parse_timezone(timezone)

            for event in events:
                formatted_event = self._format_event(event, tz)
                if formatted_event:
                    formatted_events.append(formatted_event)

            return formatted_events

        except HttpError as error:
            logger.error(f"Google Calendar API error: {error}")
            raise Exception(f"Failed to fetch events for date: {error}")
    
    async def get_events_in_range(self, start_date: datetime, end_date: datetime, timezone: Optional[str] = None, calendar_id: Optional[str] = None) -> List[Dict]:
        """Get events in a date range"""
        if not self.service:
            raise Exception("Calendar service not initialized")

        try:
            # Convert to RFC3339 format correctly
            def to_rfc3339(dt):
                if dt.tzinfo is not None:
                    return dt.isoformat()
                else:
                    return dt.isoformat() + 'Z'

            time_min = to_rfc3339(start_date)
            time_max = to_rfc3339(end_date)

            calendar_id = calendar_id or 'primary'
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=50,  # Reasonable limit for date ranges
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            logger.debug(f"Raw Google Calendar API response (get_events_in_range): {json.dumps(events_result, indent=2)}")

            events = events_result.get('items', [])

            # Format events
            formatted_events = []
            tz = self._parse_timezone(timezone)

            for event in events:
                formatted_event = self._format_event(event, tz)
                if formatted_event:
                    formatted_events.append(formatted_event)

            return formatted_events

        except HttpError as error:
            logger.error(f"Google Calendar API error: {error}")
            raise Exception(f"Failed to fetch events in range: {error}")
    
    async def check_availability(self, start_time: str, end_time: str, timezone: Optional[str] = None, calendar_id: Optional[str] = None) -> bool:
        """Check if a time slot is available"""
        if not self.service:
            raise Exception("Calendar service not initialized")
        
        try:
            # Parse the provided times
            start_dt = date_parser.parse(start_time)
            end_dt = date_parser.parse(end_time)
            
            # Convert to RFC3339 format
            time_min = start_dt.isoformat()
            time_max = end_dt.isoformat()
            
            # Add timezone if not present
            if not time_min.endswith('Z') and '+' not in time_min:
                time_min += 'Z'
            if not time_max.endswith('Z') and '+' not in time_max:
                time_max += 'Z'
            
            calendar_id = calendar_id or 'primary'
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True
            ).execute()
            
            events = events_result.get('items', [])
            
            # Check for conflicts
            for event in events:
                # Skip declined events
                attendees = event.get('attendees', [])
                user_response = None
                for attendee in attendees:
                    if attendee.get('self'):
                        user_response = attendee.get('responseStatus')
                        break
                
                if user_response == 'declined':
                    continue
                
                # Check if event overlaps with requested time
                event_start = event.get('start', {})
                event_end = event.get('end', {})
                
                if event_start.get('dateTime') and event_end.get('dateTime'):
                    return False  # There's a conflicting event
            
            return True  # No conflicts found
            
        except HttpError as error:
            logger.error(f"Google Calendar API error: {error}")
            raise Exception(f"Failed to check availability: {error}")
    
    async def get_conflicting_events(self, start_time: str, end_time: str, timezone: Optional[str] = None, calendar_id: Optional[str] = None) -> List[Dict]:
        """Get events that conflict with the specified time range"""
        if not self.service:
            raise Exception("Calendar service not initialized")
        
        try:
            # Parse the provided times
            start_dt = date_parser.parse(start_time)
            end_dt = date_parser.parse(end_time)
            
            # Convert to RFC3339 format
            time_min = start_dt.isoformat()
            time_max = end_dt.isoformat()
            
            # Add timezone if not present
            if not time_min.endswith('Z') and '+' not in time_min:
                time_min += 'Z'
            if not time_max.endswith('Z') and '+' not in time_max:
                time_max += 'Z'
            
            calendar_id = calendar_id or 'primary'
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Filter and format conflicting events
            conflicts = []
            tz = self._parse_timezone(timezone)
            
            for event in events:
                # Skip declined events
                attendees = event.get('attendees', [])
                user_response = None
                for attendee in attendees:
                    if attendee.get('self'):
                        user_response = attendee.get('responseStatus')
                        break
                
                if user_response == 'declined':
                    continue
                
                formatted_event = self._format_event(event, tz)
                if formatted_event:
                    conflicts.append(formatted_event)
            
            return conflicts
            
        except HttpError as error:
            logger.error(f"Google Calendar API error: {error}")
            raise Exception(f"Failed to get conflicting events: {error}")
    
    def _format_event(self, event: Dict, timezone: pytz.BaseTzInfo) -> Optional[Dict]:
        """Format a calendar event for response"""
        try:
            start = event.get('start', {})
            end = event.get('end', {})
            
            # Handle all-day events
            if start.get('date'):
                start_formatted = start['date']
                end_formatted = end.get('date', start['date'])
            elif start.get('dateTime'):
                start_formatted = self._format_datetime(start['dateTime'], timezone)
                end_formatted = self._format_datetime(end['dateTime'], timezone) if end.get('dateTime') else start_formatted
            else:
                return None
            
            return {
                'id': event.get('id'),
                'summary': event.get('summary', 'No title'),
                'description': event.get('description', ''),
                'location': event.get('location', ''),
                'start': start,
                'end': end,
                'start_formatted': start_formatted,
                'end_formatted': end_formatted,
                'status': event.get('status', ''),
                'html_link': event.get('htmlLink', ''),
                'attendees': event.get('attendees', [])
            }
        except Exception as e:
            logger.warning(f"Failed to format event: {e}")
            return None
