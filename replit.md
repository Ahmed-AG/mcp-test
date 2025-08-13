# Google Calendar MCP Server

## Overview

This project is a Model Context Protocol (MCP) server that provides natural language interface to Google Calendar API. It allows users to query their calendar events using conversational language like "What's on my schedule today?" or "Do I have any meetings tomorrow?". The system acts as a bridge between MCP clients and Google Calendar, parsing natural language queries and returning structured calendar information with timezone support and flexible time range handling.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Components

**MCP Server Layer (`mcp_server.py`)**
- Implements the Model Context Protocol server interface
- Handles client communication through stdio
- Routes calendar queries to appropriate service handlers
- Registers available tools and manages the MCP protocol lifecycle

**Calendar Service Layer (`calendar_service.py`)**
- Manages Google Calendar API authentication using OAuth2
- Handles Google API credentials and token management
- Provides calendar data retrieval operations
- Manages timezone conversions and date formatting

**Query Parser (`query_parser.py`)**
- Processes natural language queries about calendar events
- Uses regex patterns to identify query intent (today, tomorrow, specific dates)
- Extracts temporal information and converts to API parameters
- Supports flexible date parsing and timezone handling

**Configuration Management (`config.py`)**
- Centralizes environment variable handling
- Manages API credentials and server settings
- Provides configuration validation
- Handles feature flags for different operational modes

### Authentication Architecture

**OAuth2 Flow**
- Uses Google OAuth2 for secure API access
- Supports both credential file and environment variable configuration
- Implements token refresh mechanisms
- Maintains readonly access scope for security

**Credential Management**
- Primary: `credentials.json` file in project directory
- Fallback: `GOOGLE_CREDENTIALS_JSON` environment variable
- Token persistence through `token.json` for session management

### Data Processing Pipeline

**Query Processing Flow**
1. Natural language input received via MCP protocol
2. Query parser extracts intent and temporal parameters
3. Calendar service converts parameters to Google API calls
4. Results formatted and returned through MCP response

**Timezone Handling**
- Automatic system timezone detection using `tzlocal`
- UTC fallback for compatibility
- Timezone conversion for accurate event timing
- Support for user-specified timezone overrides

### Integration Patterns

**Google API Integration**
- Uses official Google Client Libraries
- Implements proper error handling and retry logic
- Follows Google API quotas and rate limiting
- Readonly calendar access for security

**MCP Protocol Implementation**
- Standard MCP server setup with stdio transport
- Tool registration for calendar query capabilities
- Structured input/output schema definitions
- Async/await pattern for non-blocking operations

## External Dependencies

### Google Services
- **Google Calendar API**: Primary data source for calendar events
- **Google OAuth2**: Authentication and authorization
- **Google Cloud Console**: Project and API management

### Python Libraries
- **google-auth & google-auth-oauthlib**: Google authentication
- **google-api-python-client**: Google API client library
- **mcp**: Model Context Protocol implementation
- **python-dateutil**: Advanced date parsing capabilities
- **pytz**: Timezone handling and conversions
- **tzlocal**: System timezone detection

### Development Tools
- **asyncio**: Asynchronous programming support
- **logging**: Application logging and debugging
- **json**: Configuration and data serialization
- **re**: Regular expressions for query parsing