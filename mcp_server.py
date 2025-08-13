"""
MCP Server implementation for Google Calendar
Handles MCP protocol communication and routes requests to calendar service
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
import mcp.server.stdio
from mcp import types
from mcp.server import Server

from calendar_service import GoogleCalendarService
from query_parser import CalendarQueryParser
from config import Config

logger = logging.getLogger(__name__)

class CalendarMCPServer:
    """MCP Server for Google Calendar integration"""
    
    def __init__(self):
        self.server = Server("google-calendar-mcp")
        self.calendar_service = GoogleCalendarService()
        self.query_parser = CalendarQueryParser()
        self.config = Config()
        
        # Register MCP handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register MCP protocol handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> List[types.Tool]:
            """List available calendar tools"""
            logger.info("Received MCP request: list_tools")
            tools = [
                types.Tool(
                    name="query_calendar",
                    description="Query Google Calendar for appointments and events using natural language",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Natural language query about calendar events (e.g., 'What's on my schedule today?', 'Do I have any meetings tomorrow?', 'Show me this week's appointments')"
                            },
                            "timezone": {
                                "type": "string",
                                "description": "Optional timezone for the query (e.g., 'America/New_York'). Defaults to system timezone.",
                                "default": None
                            },
                            "calendar_id": {
                                "type": "string",
                                "description": "Optional calendar ID or email address to query. Defaults to 'primary'.",
                                "default": "primary"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="get_upcoming_events",
                    description="Get upcoming calendar events within a specified time range",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of events to return",
                                "default": 10,
                                "minimum": 1,
                                "maximum": 50
                            },
                            "days_ahead": {
                                "type": "integer",
                                "description": "Number of days ahead to search for events",
                                "default": 7,
                                "minimum": 1,
                                "maximum": 365
                            },
                            "timezone": {
                                "type": "string",
                                "description": "Timezone for the results",
                                "default": None
                            },
                            "calendar_id": {
                                "type": "string",
                                "description": "Optional calendar ID or email address to query. Defaults to 'primary'.",
                                "default": "primary"
                            }
                        },
                        "required": []
                    }
                ),
                types.Tool(
                    name="check_availability",
                    description="Check if a specific time slot is available in the calendar",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "start_time": {
                                "type": "string",
                                "description": "Start time in ISO format (e.g., '2025-08-12T14:00:00')"
                            },
                            "end_time": {
                                "type": "string",
                                "description": "End time in ISO format (e.g., '2025-08-12T15:00:00')"
                            },
                            "timezone": {
                                "type": "string",
                                "description": "Timezone for the time slot check",
                                "default": None
                            },
                            "calendar_id": {
                                "type": "string",
                                "description": "Optional calendar ID or email address to query. Defaults to 'primary'.",
                                "default": "primary"
                            }
                        },
                        "required": ["start_time", "end_time"]
                    }
                )
            ]
            logger.debug(f"Sending MCP response: list_tools: {json.dumps([tool.__dict__ for tool in tools], indent=2, default=str)}")
            return tools
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Handle tool calls"""
            logger.info(f"Received MCP request: call_tool: name={name}, arguments={json.dumps(arguments, indent=2, default=str)}")
            try:
                if name == "query_calendar":
                    response = await self._handle_calendar_query(arguments)
                elif name == "get_upcoming_events":
                    response = await self._handle_upcoming_events(arguments)
                elif name == "check_availability":
                    response = await self._handle_availability_check(arguments)
                else:
                    response = [types.TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]
                # Log the full response sent to the client
                logger.debug(f"Sending MCP response: call_tool: name={name}, response={json.dumps([r.__dict__ for r in response], indent=2, default=str)}")
                return response
            except Exception as e:
                logger.error(f"Error handling tool call {name}: {e}")
                error_response = [types.TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
                logger.debug(f"Sending MCP error response: call_tool: name={name}, response={json.dumps([r.__dict__ for r in error_response], indent=2, default=str)}")
                return error_response
    
    async def _handle_calendar_query(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle natural language calendar queries"""
        query = arguments.get("query", "")
        timezone = arguments.get("timezone")

        if not query:
            return [types.TextContent(
                type="text",
                text="Error: Query cannot be empty"
            )]

        # Parse the natural language query
        parsed_query = self.query_parser.parse_query(query, timezone)

        # Execute the query based on parsed intent
        if parsed_query["intent"] == "upcoming_events":
            events = await self.calendar_service.get_upcoming_events(
                max_results=parsed_query.get("max_results", 10),
                days_ahead=parsed_query.get("days_ahead", 7),
                timezone=parsed_query.get("timezone"),
                calendar_id=arguments.get("calendar_id")
            )
        elif parsed_query["intent"] == "specific_date":
            events = await self.calendar_service.get_events_for_date(
                date=parsed_query["date"],
                timezone=parsed_query.get("timezone"),
                calendar_id=arguments.get("calendar_id")
            )
        elif parsed_query["intent"] == "date_range":
            events = await self.calendar_service.get_events_in_range(
                start_date=parsed_query["start_date"],
                end_date=parsed_query["end_date"],
                timezone=parsed_query.get("timezone"),
                calendar_id=arguments.get("calendar_id")
            )
        else:
            return [types.TextContent(
                type="text",
                text=f"Sorry, I couldn't understand your query: '{query}'. Try asking about today's schedule, upcoming events, or specific dates."
            )]

        # Format the response
        response_text = self._format_events_response(events, query, parsed_query)

        # Log the full response returned to the MCP client
        import json
        logging.getLogger(__name__).debug(f"Tool response (calendar_query): {json.dumps({'events': events, 'response_text': response_text}, indent=2, default=str)}")

        return [types.TextContent(
            type="text",
            text=response_text
        )]
    
    async def _handle_upcoming_events(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle upcoming events requests"""
        max_results = arguments.get("max_results", 10)
        days_ahead = arguments.get("days_ahead", 7)
        timezone = arguments.get("timezone")

        events = await self.calendar_service.get_upcoming_events(
            max_results=max_results,
            days_ahead=days_ahead,
            timezone=timezone,
            calendar_id=arguments.get("calendar_id")
        )

        if not events:
            response_text = f"No upcoming events found in the next {days_ahead} days."
        else:
            response_text = f"Upcoming Events (next {days_ahead} days):\n\n"
            for event in events:
                response_text += self._format_single_event(event) + "\n"

        # Log the full response returned to the MCP client
        import json
        logging.getLogger(__name__).debug(f"Tool response (upcoming_events): {json.dumps({'events': events, 'response_text': response_text}, indent=2, default=str)}")

        return [types.TextContent(
            type="text",
            text=response_text
        )]
    
    async def _handle_availability_check(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle availability check requests"""
        start_time = arguments.get("start_time")
        end_time = arguments.get("end_time")
        timezone = arguments.get("timezone")

        if not start_time or not end_time:
            return [types.TextContent(
                type="text",
                text="Error: Both start_time and end_time are required"
            )]

        is_available = await self.calendar_service.check_availability(
            start_time=str(start_time),
            end_time=str(end_time),
            timezone=timezone,
            calendar_id=arguments.get("calendar_id")
        )

        response_data = {
            'is_available': is_available,
            'start_time': start_time,
            'end_time': end_time
        }

        if is_available:
            response_text = f"✅ You are available from {start_time} to {end_time}"
        else:
            response_text = f"❌ You have conflicts during {start_time} to {end_time}"

            # Get conflicting events
            conflicts = await self.calendar_service.get_conflicting_events(
                start_time=str(start_time),
                end_time=str(end_time),
                timezone=timezone,
                calendar_id=arguments.get("calendar_id")
            )

            response_data['conflicts'] = conflicts

            if conflicts:
                response_text += "\n\nConflicting events:"
                for event in conflicts:
                    response_text += f"\n• {self._format_single_event(event)}"

        response_data['response_text'] = response_text

        # Log the full response returned to the MCP client
        import json
        logging.getLogger(__name__).debug(f"Tool response (availability_check): {json.dumps(response_data, indent=2, default=str)}")

        return [types.TextContent(
            type="text",
            text=response_text
        )]
    
    def _format_events_response(self, events: List[Dict], original_query: str, parsed_query: Dict) -> str:
        """Format events into a readable response"""
        if not events:
            return "No events found for your query."
        
        intent = parsed_query.get("intent", "")
        
        if intent == "specific_date":
            date_str = parsed_query.get("date", "").strftime("%A, %B %d, %Y")
            response = f"Schedule for {date_str}:\n\n"
        elif intent == "date_range":
            start_str = parsed_query.get("start_date", "").strftime("%B %d")
            end_str = parsed_query.get("end_date", "").strftime("%B %d, %Y")
            response = f"Events from {start_str} to {end_str}:\n\n"
        else:
            response = f"Calendar events for '{original_query}':\n\n"
        
        for event in events:
            response += self._format_single_event(event) + "\n"
        
        return response
    
    def _format_single_event(self, event: Dict) -> str:
        """Format a single event for display"""
        title = event.get("summary", "No title")
        start = event.get("start_formatted", "No start time")
        end = event.get("end_formatted", "No end time")
        location = event.get("location", "")
        description = event.get("description", "")
        
        formatted = f"📅 {title}\n"
        formatted += f"⏰ {start}"
        
        if end and end != start:
            formatted += f" - {end}"
        
        if location:
            formatted += f"\n📍 {location}"
        
        if description and len(description) < 100:
            formatted += f"\n📝 {description}"
        
        return formatted
    
    async def run(self):
        """Run the MCP server"""
        logger.info("Starting MCP server...")
        
        # Initialize calendar service
        await self.calendar_service.initialize()
        
        # Run the server
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )
