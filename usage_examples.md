# MCP Calendar Server Usage Examples

Your MCP server is now running and ready to answer questions about calendar appointments!

## Server Status
✅ **Server Running**: Authentication successful with Google Calendar API  
✅ **Service Account**: Using secure service account authentication  
✅ **MCP Protocol**: Ready to handle natural language queries  

## Available Tools

### 1. `query_calendar` - Natural Language Queries
Ask questions in plain English about your calendar:

**Examples:**
- "What's on my schedule today?"
- "Do I have any meetings tomorrow?"
- "Show me this week's appointments"
- "What events do I have on Friday?"
- "Am I busy next Monday?"

### 2. `get_upcoming_events` - Structured Event Retrieval
Get upcoming events with specific parameters:

**Parameters:**
- `max_results`: Number of events to return (1-50)
- `days_ahead`: How many days to look ahead (1-365)
- `timezone`: Optional timezone (e.g., "America/New_York")

### 3. `check_availability` - Time Slot Checking
Check if you're available during specific times:

**Parameters:**
- `start_time`: ISO format (e.g., "2025-08-12T14:00:00")
- `end_time`: ISO format (e.g., "2025-08-12T15:00:00")
- `timezone`: Optional timezone

## Calendar Access Note

**Important**: If you're getting "Bad Request" errors, you need to share your Google Calendar with the service account:

1. Open Google Calendar
2. Go to "Settings and Sharing" for your calendar
3. Under "Share with specific people", add the service account email
4. The email is in your service account JSON file as `client_email`
5. Give it "Make changes to events" or "See all event details" permission

## Integration

Your MCP server communicates via stdin/stdout using the Model Context Protocol. It's designed to work with:
- Claude Desktop
- Other MCP-compatible clients
- Custom integrations

## Testing

The server is currently running in the background and will respond to MCP protocol messages sent to its stdin.