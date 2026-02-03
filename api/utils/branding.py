"""
Branding utilities for color contrast and accessibility.
"""
import re
from typing import Tuple


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def get_relative_luminance(rgb: Tuple[int, int, int]) -> float:
    """
    Calculate relative luminance for WCAG contrast calculations.
    https://www.w3.org/TR/WCAG20/#relativeluminancedef
    """
    r, g, b = [x / 255.0 for x in rgb]
    
    def adjust(c):
        if c <= 0.03928:
            return c / 12.92
        return ((c + 0.055) / 1.055) ** 2.4
    
    r = adjust(r)
    g = adjust(g)
    b = adjust(b)
    
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def get_contrast_ratio(color1: str, color2: str) -> float:
    """
    Calculate contrast ratio between two colors.
    Returns ratio from 1 (no contrast) to 21 (maximum contrast).
    """
    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)
    
    l1 = get_relative_luminance(rgb1)
    l2 = get_relative_luminance(rgb2)
    
    lighter = max(l1, l2)
    darker = min(l1, l2)
    
    return (lighter + 0.05) / (darker + 0.05)


def get_text_color_for_background(bg_color: str) -> str:
    """
    Determine whether to use dark or light text on a given background color.
    Returns '#FFFFFF' (white) or '#000000' (black) based on WCAG contrast requirements.
    """
    white_contrast = get_contrast_ratio(bg_color, '#FFFFFF')
    black_contrast = get_contrast_ratio(bg_color, '#000000')
    
    # Return the color with better contrast
    # WCAG AA requires 4.5:1 for normal text, 3:1 for large text
    return '#FFFFFF' if white_contrast > black_contrast else '#000000'


def lighten_color(hex_color: str, percent: float = 0.2) -> str:
    """
    Lighten a hex color by a percentage (0.0 to 1.0).
    """
    r, g, b = hex_to_rgb(hex_color)
    
    r = min(255, int(r + (255 - r) * percent))
    g = min(255, int(g + (255 - g) * percent))
    b = min(255, int(b + (255 - b) * percent))
    
    return f'#{r:02X}{g:02X}{b:02X}'


def darken_color(hex_color: str, percent: float = 0.2) -> str:
    """
    Darken a hex color by a percentage (0.0 to 1.0).
    """
    r, g, b = hex_to_rgb(hex_color)
    
    r = max(0, int(r * (1 - percent)))
    g = max(0, int(g * (1 - percent)))
    b = max(0, int(b * (1 - percent)))
    
    return f'#{r:02X}{g:02X}{b:02X}'


def validate_hex_color(color: str) -> bool:
    """Validate if string is a valid hex color."""
    return bool(re.match(r'^#[0-9A-Fa-f]{6}$', color))


def get_branding_css_vars(branding: dict) -> dict:
    """
    Generate CSS custom properties from branding configuration.
    Returns dict of CSS variable names and values with accessibility-safe colors.
    """
    primary = branding.get('primary_color', '#2196F3')
    secondary = branding.get('secondary_color', '#1976D2')
    accent = branding.get('accent_color', '#4CAF50')
    
    # Ensure valid hex colors
    if not validate_hex_color(primary):
        primary = '#2196F3'
    if secondary and not validate_hex_color(secondary):
        secondary = '#1976D2'
    if accent and not validate_hex_color(accent):
        accent = '#4CAF50'
    
    return {
        '--color-primary': primary,
        '--color-primary-light': lighten_color(primary, 0.2),
        '--color-primary-dark': darken_color(primary, 0.2),
        '--color-primary-text': get_text_color_for_background(primary),
        
        '--color-secondary': secondary or darken_color(primary, 0.15),
        '--color-secondary-text': get_text_color_for_background(secondary or darken_color(primary, 0.15)),
        
        '--color-accent': accent or '#4CAF50',
        '--color-accent-light': lighten_color(accent or '#4CAF50', 0.2),
        '--color-accent-dark': darken_color(accent or '#4CAF50', 0.2),
        '--color-accent-text': get_text_color_for_background(accent or '#4CAF50'),
    }
