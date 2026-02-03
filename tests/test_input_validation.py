import pytest
from api.core.input_validation import InputValidator, validate_input
from fastapi import HTTPException


def test_sanitize_html():
    """Test HTML sanitization."""
    validator = InputValidator()
    
    # Test basic HTML escaping
    assert validator.sanitize_html("<script>alert('xss')</script>") == "&lt;script&gt;alert('xss')&lt;/script&gt;"
    assert validator.sanitize_html("Hello & goodbye") == "Hello &amp; goodbye"
    assert validator.sanitize_html('Test "quotes"') == "Test &quot;quotes&quot;"
    assert validator.sanitize_html("Normal text") == "Normal text"


def test_validate_email():
    """Test email validation."""
    validator = InputValidator()
    
    # Valid emails
    assert validator.validate_email("test@example.com") == True
    assert validator.validate_email("user.name+tag@example.co.uk") == True
    
    # Invalid emails
    assert validator.validate_email("invalid") == False
    assert validator.validate_email("@example.com") == False
    assert validator.validate_email("test@") == False
    assert validator.validate_email("") == False


def test_validate_phone():
    """Test phone validation."""
    validator = InputValidator()
    
    # Valid phones
    assert validator.validate_phone("+44 20 1234 5678") == True
    assert validator.validate_phone("01234567890") == True
    assert validator.validate_phone("+1-555-123-4567") == True
    assert validator.validate_phone("") == True  # Optional
    
    # Invalid phones
    assert validator.validate_phone("abc") == False
    assert validator.validate_phone("123") == False  # Too short


def test_validate_slug():
    """Test slug validation."""
    validator = InputValidator()
    
    # Valid slugs
    assert validator.validate_slug("my-tenant") == True
    assert validator.validate_slug("tenant123") == True
    assert validator.validate_slug("a") == True
    
    # Invalid slugs
    assert validator.validate_slug("My-Tenant") == False  # Uppercase
    assert validator.validate_slug("my_tenant") == False  # Underscore
    assert validator.validate_slug("my tenant") == False  # Space
    assert validator.validate_slug("") == False


def test_validate_hex_color():
    """Test hex color validation."""
    validator = InputValidator()
    
    # Valid colors
    assert validator.validate_hex_color("#FF5722") == True
    assert validator.validate_hex_color("#000000") == True
    assert validator.validate_hex_color("#ffffff") == True
    
    # Invalid colors
    assert validator.validate_hex_color("FF5722") == False  # No #
    assert validator.validate_hex_color("#FF57") == False  # Too short
    assert validator.validate_hex_color("#GG5722") == False  # Invalid hex


def test_validate_url():
    """Test URL validation."""
    validator = InputValidator()
    
    # Valid URLs
    assert validator.validate_url("https://example.com") == True
    assert validator.validate_url("http://example.com/path") == True
    assert validator.validate_url("https://sub.example.com:8080/path?query=1") == True
    assert validator.validate_url("") == True  # Optional
    
    # Invalid URLs
    assert validator.validate_url("ftp://example.com") == False  # Not http/https
    assert validator.validate_url("javascript:alert(1)") == False
    assert validator.validate_url("//example.com") == False


def test_check_sql_injection():
    """Test SQL injection detection."""
    validator = InputValidator()
    
    # Suspicious patterns
    assert validator.check_sql_injection("SELECT * FROM users") == True
    assert validator.check_sql_injection("'; DROP TABLE users--") == True
    assert validator.check_sql_injection("1 OR 1=1") == True
    assert validator.check_sql_injection("admin'--") == True
    
    # Safe strings
    assert validator.check_sql_injection("Normal text") == False
    assert validator.check_sql_injection("user@example.com") == False


def test_check_xss():
    """Test XSS detection."""
    validator = InputValidator()
    
    # Suspicious patterns
    assert validator.check_xss("<script>alert('xss')</script>") == True
    assert validator.check_xss("javascript:alert(1)") == True
    assert validator.check_xss("<img onerror='alert(1)'>") == True
    assert validator.check_xss("<iframe src='evil.com'>") == True
    
    # Safe strings
    assert validator.check_xss("Normal text") == False
    assert validator.check_xss("Hello <world>") == False  # Not a script tag


def test_sanitize_filename():
    """Test filename sanitization."""
    validator = InputValidator()
    
    # Path traversal attempts
    assert validator.sanitize_filename("../../etc/passwd") == "etcpasswd"
    assert validator.sanitize_filename("..\\windows\\system32") == "windowssystem32"
    
    # Dangerous characters
    assert validator.sanitize_filename("file<>name.txt") == "filename.txt"
    assert validator.sanitize_filename("file|name.txt") == "filename.txt"
    
    # Normal filenames
    assert validator.sanitize_filename("document.pdf") == "document.pdf"
    assert validator.sanitize_filename("my-file-123.txt") == "my-file-123.txt"


def test_validate_string_length():
    """Test string length validation."""
    validator = InputValidator()
    
    assert validator.validate_string_length("test", 1, 10) == True
    assert validator.validate_string_length("", 0, 10) == True
    assert validator.validate_string_length("toolong", 1, 5) == False
    assert validator.validate_string_length("", 1, 10) == False  # Too short


def test_validate_integer_range():
    """Test integer range validation."""
    validator = InputValidator()
    
    assert validator.validate_integer_range(5, 0, 10) == True
    assert validator.validate_integer_range(0, 0, 10) == True
    assert validator.validate_integer_range(10, 0, 10) == True
    assert validator.validate_integer_range(-1, 0, 10) == False
    assert validator.validate_integer_range(11, 0, 10) == False


def test_sanitize_search_query():
    """Test search query sanitization."""
    validator = InputValidator()
    
    # Remove dangerous characters
    assert validator.sanitize_search_query("test'; DROP TABLE") == "test DROP TABLE"
    assert validator.sanitize_search_query("<script>alert(1)</script>") == "scriptalert(1)/script"
    
    # Normal queries
    assert validator.sanitize_search_query("search term") == "search term"
    assert validator.sanitize_search_query("  spaces  ") == "spaces"


def test_validate_input_email():
    """Test validate_input function with email."""
    # Valid email
    result = validate_input("test@example.com", "email", "email")
    assert result == "test@example.com"
    
    # Invalid email
    with pytest.raises(HTTPException) as exc_info:
        validate_input("invalid", "email", "email")
    assert exc_info.value.status_code == 400
    assert "email" in exc_info.value.detail.lower()


def test_validate_input_slug():
    """Test validate_input function with slug."""
    # Valid slug
    result = validate_input("my-tenant", "slug", "slug")
    assert result == "my-tenant"
    
    # Invalid slug
    with pytest.raises(HTTPException) as exc_info:
        validate_input("My_Tenant", "slug", "slug")
    assert exc_info.value.status_code == 400


def test_validate_input_sql_injection():
    """Test that SQL injection attempts are blocked."""
    with pytest.raises(HTTPException) as exc_info:
        validate_input("'; DROP TABLE users--", "notes", "length", max_length=1000)
    assert exc_info.value.status_code == 400
    assert "dangerous" in exc_info.value.detail.lower()


def test_validate_input_xss():
    """Test that XSS attempts are blocked."""
    with pytest.raises(HTTPException) as exc_info:
        validate_input("<script>alert('xss')</script>", "notes", "length", max_length=1000)
    assert exc_info.value.status_code == 400
    assert "dangerous" in exc_info.value.detail.lower()
