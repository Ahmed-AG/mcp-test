"""
Natural language query parser for calendar requests
Parses user queries and extracts intent and parameters
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union
import pytz
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)

class CalendarQueryParser:
    """Parse natural language queries about calendar events"""
    
    def __init__(self):
        self.default_timezone = pytz.timezone('UTC')
        
        # Try to detect system timezone
        try:
            import tzlocal
            self.default_timezone = tzlocal.get_localzone()
        except ImportError:
            logger.warning("tzlocal not available, using UTC as default timezone")
        
        # Define patterns for different query types
        self.patterns = {
            'today': [
                r'\btoday\b',
                r'\bthis\s+day\b',
                r'\bwhat.*today\b',
                r'\btoday.*schedule\b',
                r'\btoday.*events\b',
                r'\btoday.*appointments\b'
            ],
            'tomorrow': [
                r'\btomorrow\b',
                r'\bnext\s+day\b',
                r'\bwhat.*tomorrow\b',
                r'\btomorrow.*schedule\b',
                r'\btomorrow.*events\b',
                r'\btomorrow.*appointments\b'
            ],
            'yesterday': [
                r'\byesterday\b',
                r'\bprevious\s+day\b',
                r'\byesterday.*events\b'
            ],
            'this_week': [
                r'\bthis\s+week\b',
                r'\bthis\s+week.*events\b',
                r'\bthis\s+week.*schedule\b',
                r'\bweekly\s+schedule\b'
            ],
            'next_week': [
                r'\bnext\s+week\b',
                r'\bnext\s+week.*events\b',
                r'\bnext\s+week.*schedule\b'
            ],
            'upcoming': [
                r'\bupcoming\b',
                r'\bcoming\s+up\b',
                r'\bnext.*events\b',
                r'\bfuture.*events\b',
                r'\bwhat.*next\b'
            ],
            'specific_date': [
                r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # MM/DD/YYYY or MM-DD-YYYY
                r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',    # YYYY/MM/DD or YYYY-MM-DD
                r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}\b',
                r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{1,2}\b',
                r'\b\d{1,2}\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)\b',
                r'\b\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b'
            ]
        }
        
        # Days of the week patterns
        self.day_patterns = {
            'monday': [r'\bmonday\b', r'\bmon\b'],
            'tuesday': [r'\btuesday\b', r'\btue\b', r'\btues\b'],
            'wednesday': [r'\bwednesday\b', r'\bwed\b'],
            'thursday': [r'\bthursday\b', r'\bthu\b', r'\bthur\b', r'\bthurs\b'],
            'friday': [r'\bfriday\b', r'\bfri\b'],
            'saturday': [r'\bsaturday\b', r'\bsat\b'],
            'sunday': [r'\bsunday\b', r'\bsun\b']
        }
    
    def parse_query(self, query: str, timezone: Optional[str] = None) -> Dict[str, Any]:
        """Parse a natural language query and return structured information"""
        query_lower = query.lower()
        
        # Determine timezone
        tz = self._parse_timezone(timezone)
        now = datetime.now(tz)
        
        # Check for different query types
        if self._matches_patterns(query_lower, self.patterns['today']):
            return {
                'intent': 'specific_date',
                'date': now.replace(hour=0, minute=0, second=0, microsecond=0),
                'timezone': timezone,
                'original_query': query
            }
        
        elif self._matches_patterns(query_lower, self.patterns['tomorrow']):
            tomorrow = now + timedelta(days=1)
            return {
                'intent': 'specific_date',
                'date': tomorrow.replace(hour=0, minute=0, second=0, microsecond=0),
                'timezone': timezone,
                'original_query': query
            }
        
        elif self._matches_patterns(query_lower, self.patterns['yesterday']):
            yesterday = now - timedelta(days=1)
            return {
                'intent': 'specific_date',
                'date': yesterday.replace(hour=0, minute=0, second=0, microsecond=0),
                'timezone': timezone,
                'original_query': query
            }
        
        elif self._matches_patterns(query_lower, self.patterns['this_week']):
            # Calculate start and end of current week (Monday to Sunday)
            start_of_week = now - timedelta(days=now.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            return {
                'intent': 'date_range',
                'start_date': start_of_week.replace(hour=0, minute=0, second=0, microsecond=0),
                'end_date': end_of_week.replace(hour=23, minute=59, second=59, microsecond=999999),
                'timezone': timezone,
                'original_query': query
            }
        
        elif self._matches_patterns(query_lower, self.patterns['next_week']):
            # Calculate start and end of next week
            next_monday = now + timedelta(days=(7 - now.weekday()))
            next_sunday = next_monday + timedelta(days=6)
            return {
                'intent': 'date_range',
                'start_date': next_monday.replace(hour=0, minute=0, second=0, microsecond=0),
                'end_date': next_sunday.replace(hour=23, minute=59, second=59, microsecond=999999),
                'timezone': timezone,
                'original_query': query
            }
        
        elif self._matches_patterns(query_lower, self.patterns['upcoming']):
            # Extract number of days if mentioned
            days_ahead = self._extract_number_of_days(query_lower)
            max_results = self._extract_max_results(query_lower)
            
            return {
                'intent': 'upcoming_events',
                'days_ahead': days_ahead,
                'max_results': max_results,
                'timezone': timezone,
                'original_query': query
            }
        
        # Check for specific dates
        elif self._matches_patterns(query_lower, self.patterns['specific_date']):
            parsed_date = self._extract_specific_date(query, tz)
            if parsed_date:
                return {
                    'intent': 'specific_date',
                    'date': parsed_date,
                    'timezone': timezone,
                    'original_query': query
                }
        
        # Check for day of the week
        day_of_week = self._extract_day_of_week(query_lower)
        if day_of_week:
            target_date = self._get_next_weekday(now, day_of_week)
            return {
                'intent': 'specific_date',
                'date': target_date,
                'timezone': timezone,
                'original_query': query
            }
        
        # Default to upcoming events
        return {
            'intent': 'upcoming_events',
            'days_ahead': 7,
            'max_results': 10,
            'timezone': timezone,
            'original_query': query
        }
    
    def _parse_timezone(self, timezone_str: Optional[str]) -> Union[pytz.BaseTzInfo, Any]:
        """Parse timezone string and return timezone object"""
        if not timezone_str:
            return self.default_timezone
        
        try:
            return pytz.timezone(timezone_str)
        except pytz.exceptions.UnknownTimeZoneError:
            logger.warning(f"Unknown timezone: {timezone_str}, using default")
            return self.default_timezone
    
    def _matches_patterns(self, text: str, patterns: list) -> bool:
        """Check if text matches any of the given patterns"""
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _extract_number_of_days(self, text: str) -> int:
        """Extract number of days from query text"""
        # Look for patterns like "next 5 days", "next week" (7 days), etc.
        
        # Check for "next week" or "this week"
        if re.search(r'\bnext\s+week\b', text) or re.search(r'\bthis\s+week\b', text):
            return 7
        
        # Look for "next X days"
        match = re.search(r'\bnext\s+(\d+)\s+days?\b', text)
        if match:
            return int(match.group(1))
        
        # Look for "X days"
        match = re.search(r'\b(\d+)\s+days?\b', text)
        if match:
            return int(match.group(1))
        
        # Default
        return 7
    
    def _extract_max_results(self, text: str) -> int:
        """Extract maximum number of results from query text"""
        # Look for patterns like "show me 5 events", "first 10 appointments"
        
        match = re.search(r'\b(?:show|first|next)\s+(?:me\s+)?(\d+)\s+(?:events?|appointments?|meetings?)\b', text)
        if match:
            return min(int(match.group(1)), 50)  # Cap at 50
        
        # Default
        return 10
    
    def _extract_specific_date(self, text: str, timezone: pytz.BaseTzInfo) -> Optional[datetime]:
        """Extract a specific date from the query text"""
        # Try different date parsing approaches
        
        # Look for date patterns
        date_patterns = [
            r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',
            r'\b(\d{4}[/-]\d{1,2}[/-]\d{1,2})\b',
            r'\b((?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}(?:,?\s+\d{4})?)\b',
            r'\b((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{1,2}(?:,?\s+\d{4})?)\b',
            r'\b(\d{1,2}\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)(?:\s+\d{4})?)\b',
            r'\b(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)(?:\s+\d{4})?)\b'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                try:
                    # Parse the date
                    parsed_date = date_parser.parse(date_str)
                    
                    # If no year was specified, assume current year
                    if parsed_date.year == 1900:  # dateutil default
                        current_year = datetime.now(timezone).year
                        parsed_date = parsed_date.replace(year=current_year)
                    
                    # Localize to timezone
                    if parsed_date.tzinfo is None:
                        if hasattr(timezone, 'localize'):
                            parsed_date = timezone.localize(parsed_date)
                        else:
                            parsed_date = parsed_date.replace(tzinfo=timezone)
                    
                    return parsed_date.replace(hour=0, minute=0, second=0, microsecond=0)
                
                except (ValueError, OverflowError) as e:
                    logger.warning(f"Failed to parse date '{date_str}': {e}")
                    continue
        
        return None
    
    def _extract_day_of_week(self, text: str) -> Optional[str]:
        """Extract day of the week from query text"""
        for day, patterns in self.day_patterns.items():
            if self._matches_patterns(text, patterns):
                return day
        return None
    
    def _get_next_weekday(self, current_date: datetime, target_day: str) -> datetime:
        """Get the next occurrence of a specific weekday"""
        weekdays = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        target_weekday = weekdays.get(target_day.lower())
        if target_weekday is None:
            return current_date
        
        days_ahead = target_weekday - current_date.weekday()
        
        # If the target day is today or has passed this week, get next week's occurrence
        if days_ahead <= 0:
            days_ahead += 7
        
        target_date = current_date + timedelta(days=days_ahead)
        return target_date.replace(hour=0, minute=0, second=0, microsecond=0)
