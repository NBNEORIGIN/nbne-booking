import pytest
import logging
from api.core.log_sanitizer import SensitiveDataFilter, sanitize_dict


def test_sanitize_password():
    """Test that passwords are sanitized."""
    filter = SensitiveDataFilter()
    
    # Various password formats
    assert '***REDACTED***' in filter.sanitize('password=secret123')
    assert '***REDACTED***' in filter.sanitize('password: secret123')
    assert '***REDACTED***' in filter.sanitize('"password":"secret123"')
    assert '***REDACTED***' in filter.sanitize('pwd=secret123')


def test_sanitize_api_key():
    """Test that API keys are sanitized."""
    filter = SensitiveDataFilter()
    
    assert '***REDACTED***' in filter.sanitize('api_key=sk_live_1234567890abcdef')
    assert '***REDACTED***' in filter.sanitize('api-key: pk_test_abcdefghijklmnop')
    assert '***REDACTED***' in filter.sanitize('apikey=1234567890abcdefghij')


def test_sanitize_token():
    """Test that tokens are sanitized."""
    filter = SensitiveDataFilter()
    
    assert '***REDACTED***' in filter.sanitize('token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9')
    assert '***REDACTED***' in filter.sanitize('bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U')


def test_sanitize_db_connection():
    """Test that database connection strings are sanitized."""
    filter = SensitiveDataFilter()
    
    result = filter.sanitize('postgresql://user:password@localhost:5432/db')
    assert 'password' not in result
    assert '***:***@' in result
    
    result = filter.sanitize('mysql://admin:secret@db.example.com/mydb')
    assert 'secret' not in result
    assert '***:***@' in result


def test_sanitize_credit_card():
    """Test that credit card numbers are sanitized."""
    filter = SensitiveDataFilter()
    
    assert '****-****-****-****' in filter.sanitize('Card: 4532-1234-5678-9010')
    assert '****-****-****-****' in filter.sanitize('Card: 4532 1234 5678 9010')
    assert '****-****-****-****' in filter.sanitize('Card: 4532123456789010')


def test_sanitize_ssn():
    """Test that social security numbers are sanitized."""
    filter = SensitiveDataFilter()
    
    assert '***-**-****' in filter.sanitize('SSN: 123-45-6789')


def test_sanitize_jwt():
    """Test that JWT tokens are sanitized."""
    filter = SensitiveDataFilter()
    
    jwt = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'
    result = filter.sanitize(f'Token: {jwt}')
    assert '***JWT_TOKEN***' in result
    assert 'eyJ' not in result


def test_sanitize_email_optional():
    """Test that email sanitization is optional."""
    # Without email masking
    filter_no_mask = SensitiveDataFilter(mask_emails=False)
    result = filter_no_mask.sanitize('Contact: user@example.com')
    assert 'user@example.com' in result
    
    # With email masking
    filter_mask = SensitiveDataFilter(mask_emails=True)
    result = filter_mask.sanitize('Contact: user@example.com')
    assert '***@***.***' in result
    assert 'user@example.com' not in result


def test_logging_filter():
    """Test that the filter works with logging."""
    # Create logger with filter
    logger = logging.getLogger('test_logger')
    logger.setLevel(logging.INFO)
    
    # Add handler with filter
    handler = logging.StreamHandler()
    handler.addFilter(SensitiveDataFilter())
    logger.addHandler(handler)
    
    # Create log record
    record = logger.makeRecord(
        'test_logger',
        logging.INFO,
        __file__,
        1,
        'User login with password=secret123',
        (),
        None
    )
    
    # Apply filter
    handler.filter(record)
    
    # Check that password was sanitized
    assert 'secret123' not in record.msg
    assert '***REDACTED***' in record.msg


def test_sanitize_dict_basic():
    """Test dictionary sanitization."""
    data = {
        'username': 'john',
        'password': 'secret123',
        'email': 'john@example.com'
    }
    
    result = sanitize_dict(data)
    
    assert result['username'] == 'john'
    assert result['password'] == '***REDACTED***'
    assert result['email'] == 'john@example.com'


def test_sanitize_dict_nested():
    """Test nested dictionary sanitization."""
    data = {
        'user': {
            'name': 'john',
            'credentials': {
                'password': 'secret123',
                'api_key': 'sk_live_1234567890'
            }
        }
    }
    
    result = sanitize_dict(data)
    
    assert result['user']['name'] == 'john'
    assert result['user']['credentials']['password'] == '***REDACTED***'
    assert result['user']['credentials']['api_key'] == '***REDACTED***'


def test_sanitize_dict_list():
    """Test dictionary with list sanitization."""
    data = {
        'users': [
            {'name': 'john', 'password': 'secret1'},
            {'name': 'jane', 'password': 'secret2'}
        ]
    }
    
    result = sanitize_dict(data)
    
    assert result['users'][0]['name'] == 'john'
    assert result['users'][0]['password'] == '***REDACTED***'
    assert result['users'][1]['name'] == 'jane'
    assert result['users'][1]['password'] == '***REDACTED***'


def test_sanitize_dict_custom_keys():
    """Test dictionary sanitization with custom sensitive keys."""
    data = {
        'username': 'john',
        'custom_secret': 'sensitive_data'
    }
    
    result = sanitize_dict(data, sensitive_keys={'custom_secret'})
    
    assert result['username'] == 'john'
    assert result['custom_secret'] == '***REDACTED***'


def test_sanitize_preserves_non_sensitive():
    """Test that non-sensitive data is preserved."""
    filter = SensitiveDataFilter()
    
    text = 'User john logged in from 192.168.1.1 at 2026-02-03 10:00:00'
    result = filter.sanitize(text)
    
    # Should be unchanged
    assert result == text


def test_sanitize_multiple_patterns():
    """Test that multiple sensitive patterns in one string are all sanitized."""
    filter = SensitiveDataFilter()
    
    text = 'Login with password=secret123 and api_key=sk_live_abcdefghij'
    result = filter.sanitize(text)
    
    assert 'secret123' not in result
    assert 'sk_live_abcdefghij' not in result
    assert '***REDACTED***' in result
