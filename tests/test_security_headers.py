import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_hsts_header():
    """Test that HSTS header is present."""
    response = client.get("/health")
    assert "Strict-Transport-Security" in response.headers
    assert "max-age=31536000" in response.headers["Strict-Transport-Security"]
    assert "includeSubDomains" in response.headers["Strict-Transport-Security"]


def test_x_content_type_options():
    """Test that X-Content-Type-Options header is present."""
    response = client.get("/health")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"


def test_x_frame_options():
    """Test that X-Frame-Options header is present."""
    response = client.get("/health")
    assert response.headers.get("X-Frame-Options") == "DENY"


def test_x_xss_protection():
    """Test that X-XSS-Protection header is present."""
    response = client.get("/health")
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"


def test_referrer_policy():
    """Test that Referrer-Policy header is present."""
    response = client.get("/health")
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"


def test_permissions_policy():
    """Test that Permissions-Policy header is present."""
    response = client.get("/health")
    assert "Permissions-Policy" in response.headers
    assert "geolocation=()" in response.headers["Permissions-Policy"]
    assert "camera=()" in response.headers["Permissions-Policy"]


def test_content_security_policy():
    """Test that Content-Security-Policy header is present."""
    response = client.get("/health")
    assert "Content-Security-Policy" in response.headers
    csp = response.headers["Content-Security-Policy"]
    
    # Check key directives
    assert "default-src 'self'" in csp
    assert "frame-ancestors 'none'" in csp
    assert "base-uri 'self'" in csp
    assert "form-action 'self'" in csp


def test_all_security_headers_on_all_endpoints():
    """Test that security headers are present on all endpoints."""
    endpoints = [
        "/health",
        "/api/v1/docs",
    ]
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        
        # All responses should have security headers
        assert "Strict-Transport-Security" in response.headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "Content-Security-Policy" in response.headers
