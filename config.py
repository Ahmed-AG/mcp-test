"""
Configuration settings for the Calendar MCP Server
"""

import os
from typing import Optional

class Config:
    """Configuration management for the Calendar MCP Server"""
    
    def __init__(self):
        # Google Calendar API settings
        self.google_credentials_file = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
        self.google_token_file = os.getenv("GOOGLE_TOKEN_FILE", "token.json")
        self.google_scopes = ['https://www.googleapis.com/auth/calendar.readonly']
        
        # Server settings
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_file = os.getenv("LOG_FILE", "calendar_mcp.log")
        
        # Default query settings
        self.default_max_results = int(os.getenv("DEFAULT_MAX_RESULTS", "10"))
        self.default_days_ahead = int(os.getenv("DEFAULT_DAYS_AHEAD", "7"))
        self.default_timezone = os.getenv("DEFAULT_TIMEZONE", "UTC")
        
        # Feature flags
        self.enable_all_calendars = os.getenv("ENABLE_ALL_CALENDARS", "false").lower() == "true"
        self.enable_write_operations = os.getenv("ENABLE_WRITE_OPERATIONS", "false").lower() == "true"
        
        # OAuth settings
        self.oauth_redirect_port = int(os.getenv("OAUTH_REDIRECT_PORT", "0"))  # 0 = random port
        
    # Removed get_google_credentials_json and related validation
    def validate_config(self) -> bool:
        """Validate the configuration"""
        # Validate max results
        if self.default_max_results < 1 or self.default_max_results > 100:
            return False
        # Validate days ahead
        if self.default_days_ahead < 1 or self.default_days_ahead > 365:
            return False
        return True
    
    def __repr__(self):
        return f"Config(credentials_file={self.google_credentials_file}, max_results={self.default_max_results})"
