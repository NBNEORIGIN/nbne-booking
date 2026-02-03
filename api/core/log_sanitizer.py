import re
import logging
from typing import Any, Dict


class SensitiveDataFilter(logging.Filter):
    """
    Logging filter to sanitize sensitive data from log messages.
    
    Removes or masks:
    - Passwords
    - API keys
    - Tokens
    - Email addresses (optional)
    - Credit card numbers
    - Social security numbers
    - Database connection strings
    """
    
    # Patterns to detect and sanitize
    PATTERNS = {
        # Passwords in various formats
        'password': [
            (r'password["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)', r'password=***REDACTED***'),
            (r'"password":\s*"([^"]+)"', r'"password":"***REDACTED***"'),
            (r'pwd=([^&\s]+)', r'pwd=***REDACTED***'),
        ],
        # API keys and tokens
        'api_key': [
            (r'api[_-]?key["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,})', r'api_key=***REDACTED***'),
            (r'token["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_\-\.]{20,})', r'token=***REDACTED***'),
            (r'bearer\s+([a-zA-Z0-9_\-\.]{20,})', r'bearer ***REDACTED***'),
        ],
        # Database connection strings
        'db_connection': [
            (r'postgresql://([^:]+):([^@]+)@', r'postgresql://***:***@'),
            (r'mysql://([^:]+):([^@]+)@', r'mysql://***:***@'),
        ],
        # Credit card numbers (basic pattern)
        'credit_card': [
            (r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', r'****-****-****-****'),
        ],
        # Social security numbers (US format)
        'ssn': [
            (r'\b\d{3}-\d{2}-\d{4}\b', r'***-**-****'),
        ],
        # JWT tokens
        'jwt': [
            (r'eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+', r'***JWT_TOKEN***'),
        ],
    }
    
    def __init__(self, mask_emails: bool = False):
        """
        Initialize the filter.
        
        Args:
            mask_emails: If True, also mask email addresses in logs
        """
        super().__init__()
        self.mask_emails = mask_emails
        
        if mask_emails:
            self.PATTERNS['email'] = [
                (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', r'***@***.***'),
            ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter log record to sanitize sensitive data.
        
        Args:
            record: Log record to filter
            
        Returns:
            True (always allow the record, just sanitize it)
        """
        # Sanitize the message
        if isinstance(record.msg, str):
            record.msg = self.sanitize(record.msg)
        
        # Sanitize arguments
        if record.args:
            if isinstance(record.args, dict):
                record.args = {k: self.sanitize(str(v)) if isinstance(v, str) else v 
                              for k, v in record.args.items()}
            elif isinstance(record.args, tuple):
                record.args = tuple(self.sanitize(str(arg)) if isinstance(arg, str) else arg 
                                   for arg in record.args)
        
        return True
    
    def sanitize(self, text: str) -> str:
        """
        Sanitize sensitive data from text.
        
        Args:
            text: Text to sanitize
            
        Returns:
            Sanitized text
        """
        if not text:
            return text
        
        sanitized = text
        
        # Apply all patterns
        for category, patterns in self.PATTERNS.items():
            for pattern, replacement in patterns:
                sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
        
        return sanitized


def setup_sanitized_logging(mask_emails: bool = False):
    """
    Configure logging with sensitive data filtering.
    
    Args:
        mask_emails: If True, also mask email addresses in logs
    """
    # Get root logger
    root_logger = logging.getLogger()
    
    # Add sensitive data filter to all handlers
    sensitive_filter = SensitiveDataFilter(mask_emails=mask_emails)
    
    for handler in root_logger.handlers:
        handler.addFilter(sensitive_filter)
    
    # Also add to uvicorn loggers
    for logger_name in ['uvicorn', 'uvicorn.access', 'uvicorn.error']:
        logger = logging.getLogger(logger_name)
        for handler in logger.handlers:
            handler.addFilter(sensitive_filter)


def sanitize_dict(data: Dict[str, Any], sensitive_keys: set = None) -> Dict[str, Any]:
    """
    Sanitize sensitive keys in a dictionary.
    
    Useful for sanitizing request/response data before logging.
    
    Args:
        data: Dictionary to sanitize
        sensitive_keys: Set of keys to redact (default: password, token, api_key, secret)
        
    Returns:
        Sanitized dictionary
    """
    if sensitive_keys is None:
        sensitive_keys = {
            'password', 'pwd', 'passwd',
            'token', 'access_token', 'refresh_token',
            'api_key', 'apikey', 'api-key',
            'secret', 'secret_key',
            'authorization',
            'hashed_password',
        }
    
    sanitized = {}
    
    for key, value in data.items():
        # Check if key is sensitive (case-insensitive)
        if any(sensitive_key in key.lower() for sensitive_key in sensitive_keys):
            sanitized[key] = '***REDACTED***'
        elif isinstance(value, dict):
            # Recursively sanitize nested dictionaries
            sanitized[key] = sanitize_dict(value, sensitive_keys)
        elif isinstance(value, list):
            # Sanitize lists of dictionaries
            sanitized[key] = [
                sanitize_dict(item, sensitive_keys) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            sanitized[key] = value
    
    return sanitized
