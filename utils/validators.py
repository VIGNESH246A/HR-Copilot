"""
Input validation utilities
"""
import re
from typing import Optional
from email_validator import validate_email, EmailNotValidError


def is_valid_email(email: str) -> bool:
    """Validate email address"""
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False


def is_valid_phone(phone: str) -> bool:
    """Validate phone number (basic validation)"""
    # Remove common separators
    phone_clean = re.sub(r'[\s\-\(\)\.]', '', phone)
    
    # Check if it's a valid phone number (10-15 digits)
    return bool(re.match(r'^\+?[1-9]\d{9,14}$', phone_clean))


def validate_date_format(date_str: str, format: str = "%Y-%m-%d") -> bool:
    """Validate date string format"""
    from datetime import datetime
    
    try:
        datetime.strptime(date_str, format)
        return True
    except ValueError:
        return False


def validate_file_extension(filename: str, allowed_extensions: list) -> bool:
    """Validate file extension"""
    import os
    
    ext = os.path.splitext(filename)[1].lower()
    return ext in allowed_extensions


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove any non-alphanumeric characters except . - _
    sanitized = re.sub(r'[^\w\s\-\.]', '', filename)
    # Replace spaces with underscores
    sanitized = re.sub(r'\s+', '_', sanitized)
    return sanitized


def validate_job_id(job_id: str) -> bool:
    """Validate job ID format"""
    return bool(re.match(r'^job_[\w\-]+$', job_id))


def validate_candidate_id(candidate_id: str) -> bool:
    """Validate candidate ID format"""
    return bool(re.match(r'^cand_[\w\-]+$', candidate_id))


def validate_salary_range(min_salary: Optional[float], max_salary: Optional[float]) -> bool:
    """Validate salary range"""
    if min_salary is None and max_salary is None:
        return True
    
    if min_salary and max_salary:
        return min_salary <= max_salary
    
    if min_salary:
        return min_salary > 0
    
    if max_salary:
        return max_salary > 0
    
    return True


def validate_experience_years(years: int) -> bool:
    """Validate years of experience"""
    return 0 <= years <= 50


def is_valid_url(url: str) -> bool:
    """Validate URL"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(url))