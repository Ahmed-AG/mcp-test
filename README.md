# Google Calendar MCP Server

An MCP (Model Context Protocol) server that connects to Google Calendar API to answer natural language questions about appointments and events.

## Features

- **Natural Language Queries**: Ask questions like "What's on my schedule today?" or "Do I have any meetings tomorrow?"
- **Flexible Time Ranges**: Query events for specific dates, date ranges, or upcoming periods
- **Availability Checking**: Check if specific time slots are free or conflicted
- **Timezone Support**: Handle different timezones for accurate scheduling
- **Structured Responses**: Get formatted, easy-to-read calendar information

## Setup

### 1. Google Calendar API Setup

**Option A: Service Account (Recommended - No OAuth redirects needed)**

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google Calendar API
4. Go to "APIs & Services" > "Credentials"
5. Click "Create Credentials" > "Service Account"
6. Create the service account and download the JSON key file
7. **Important**: Share your Google Calendar with the service account email address (found in the JSON file as `client_email`)

**Option B: OAuth 2.0 (Traditional method)**

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google Calendar API
4. Create credentials (OAuth 2.0 client ID) for a desktop application
5. Download the credentials JSON file

### 2. Configuration

**For Service Account:**
1. Copy the service account JSON file to `service-account-key.json`, OR
2. Set as environment variable:
   ```bash
   export GOOGLE_SERVICE_ACCOUNT_KEY='{"type": "service_account", ...}'
   ```

**For OAuth 2.0:**
1. Copy the downloaded credentials file to `credentials.json`, OR
2. Set as environment variable:
   ```bash
   export GOOGLE_CREDENTIALS_JSON='{"installed": {...}}'
   ```

### 3. Installation

Install required dependencies:
```bash
pip install google-auth google-auth-oauthlib google-api-python-client mcp python-dateutil pytz
