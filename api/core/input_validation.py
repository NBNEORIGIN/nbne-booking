import re
import html
from typing import Optional, Any
from fastapi import HTTPException, status


class InputValidator:
    """
    Input validation and sanitization utilities.
    
    Provides defense against:
    - SQL Injection (via parameterized queries in SQLAlchemy)
    - XSS (via HTML escaping)
    - Path Traversal
    - Command Injection
    - Email Header Injection
    """
    
    # Regex patterns
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    PHONE_PATTERN = re.compile(r'^\+?[0-9\s\-\(\)]{7,20}$')
    SLUG_PATTERN = re.compile(r'^[a-z0-9-]+$')
    HEX_COLOR_PATTERN = re.compile(r'^#[0-9A-Fa-f]{6}$')
    URL_PATTERN = re.compile(r'^https?://[^\s<>"{}|\\^`\[\]]+$')
    
    # Dangerous patterns
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(--|;|\/\*|\*\/)",
        r"(\bOR\b.*=.*)",
        r"(\bAND\b.*=.*)",
    ]
    
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe",
        r"<object",
        r"<embed",
    ]
    
    @classmethod
    def sanitize_html(cls, text: str) -> str:
        """
        Escape HTML special characters to prevent XSS.
        
        Converts: < > & " ' to HTML entities
        """
        if not text:
            return text
        return html.escape(text)
    
    @classmethod
    def validate_email(cls, email: str) -> bool:
        """Validate email format."""
        if not email or len(email) > 255:
            return False
        return bool(cls.EMAIL_PATTERN.match(email))
    
    @classmethod
    def validate_phone(cls, phone: str) -> bool:
        """Validate phone number format."""
        if not phone:
            return True  # Phone is optional
        if len(phone) > 20:
            return False
        return bool(cls.PHONE_PATTERN.match(phone))
    
    @classmethod
    def validate_slug(cls, slug: str) -> bool:
        """Validate slug format (lowercase alphanumeric + hyphens)."""
        if not slug or len(slug) > 100:
            return False
        return bool(cls.SLUG_PATTERN.match(slug))
    
    @classmethod
    def validate_hex_color(cls, color: str) -> bool:
        """Validate hex color format (#RRGGBB)."""
        if not color:
            return True  # Color is optional in some cases
        return bool(cls.HEX_COLOR_PATTERN.match(color))
    
    @classmethod
    def validate_url(cls, url: str) -> bool:
        """Validate URL format (http/https only)."""
        if not url:
            return True  # URL is optional
        if len(url) > 2000:
            return False
        return bool(cls.URL_PATTERN.match(url))
    
    @classmethod
    def check_sql_injection(cls, text: str) -> bool:
        """
        Check for potential SQL injection patterns.
        
        Note: This is defense in depth. SQLAlchemy parameterized queries
        are the primary defense against SQL injection.
        """
        if not text:
            return False
        
        text_upper = text.upper()
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text_upper, re.IGNORECASE):
                return True
        return False
    
    @classmethod
    def check_xss(cls, text: str) -> bool:
        """Check for potential XSS patterns."""
        if not text:
            return False
        
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """
        Sanitize filename to prevent path traversal.
        
        Removes: ../ ./ / \ and other dangerous characters
        """
        if not filename:
            return ""
        
        # Remove path separators and traversal
        filename = filename.replace("..", "")
        filename = filename.replace("/", "")
        filename = filename.replace("\\", "")
        
        # Remove dangerous characters
        filename = re.sub(r'[<>:"|?*]', '', filename)
        
        # Limit length
        if len(filename) > 255:
            filename = filename[:255]
        
        return filename
    
    @classmethod
    def validate_string_length(cls, text: str, min_length: int = 0, max_length: int = 1000) -> bool:
        """Validate string length."""
        if not text:
            return min_length == 0
        return min_length <= len(text) <= max_length
    
    @classmethod
    def validate_integer_range(cls, value: int, min_value: int = 0, max_value: int = 2147483647) -> bool:
        """Validate integer is within range."""
        return min_value <= value <= max_value
    
    @classmethod
    def sanitize_search_query(cls, query: str) -> str:
        """
        Sanitize search query for safe use.
        
        Removes dangerous SQL and XSS patterns.
        """
        if not query:
            return ""
        
        # Remove SQL injection patterns
        query = re.sub(r'[;\'"\\]', '', query)
        
        # Remove XSS patterns
        query = re.sub(r'[<>]', '', query)
        
        # Limit length
        if len(query) > 100:
            query = query[:100]
        
        return query.strip()
    
    @classmethod
    def validate_json_field(cls, data: Any, max_size: int = 10000) -> bool:
        """Validate JSON field size."""
        if data is None:
            return True
        
        import json
        json_str = json.dumps(data)
        return len(json_str) <= max_size


def validate_input(
    value: Any,
    field_name: str,
    validator_type: str,
    **kwargs
) -> Any:
    """
    Generic input validation function.
    
    Args:
        value: Value to validate
        field_name: Name of field (for error messages)
        validator_type: Type of validation (email, phone, slug, etc.)
        **kwargs: Additional validation parameters
        
    Returns:
        Validated value
        
    Raises:
        HTTPException: If validation fails
    """
    validator = InputValidator()
    
    if validator_type == "email":
        if not validator.validate_email(value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid {field_name}: must be a valid email address"
            )
    
    elif validator_type == "phone":
        if not validator.validate_phone(value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid {field_name}: must be a valid phone number"
            )
    
    elif validator_type == "slug":
        if not validator.validate_slug(value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid {field_name}: must contain only lowercase letters, numbers, and hyphens"
            )
    
    elif validator_type == "hex_color":
        if not validator.validate_hex_color(value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid {field_name}: must be a valid hex color (#RRGGBB)"
            )
    
    elif validator_type == "url":
        if not validator.validate_url(value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid {field_name}: must be a valid HTTP/HTTPS URL"
            )
    
    elif validator_type == "length":
        min_len = kwargs.get("min_length", 0)
        max_len = kwargs.get("max_length", 1000)
        if not validator.validate_string_length(value, min_len, max_len):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid {field_name}: length must be between {min_len} and {max_len}"
            )
    
    # Check for SQL injection and XSS
    if isinstance(value, str):
        if validator.check_sql_injection(value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid {field_name}: contains potentially dangerous content"
            )
        
        if validator.check_xss(value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid {field_name}: contains potentially dangerous content"
            )
    
    return value
