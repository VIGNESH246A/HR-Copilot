"""
Output formatting utilities
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
import json


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency amount"""
    if currency == "USD":
        return f"${amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"


def format_date(date: datetime, format: str = "%B %d, %Y") -> str:
    """Format date for display"""
    return date.strftime(format)


def format_datetime(dt: datetime, format: str = "%B %d, %Y at %I:%M %p") -> str:
    """Format datetime for display"""
    return dt.strftime(format)


def format_phone(phone: str) -> str:
    """Format phone number for display"""
    # Remove all non-digit characters
    digits = ''.join(filter(str.isdigit, phone))
    
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    else:
        return phone


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format percentage"""
    return f"{value:.{decimals}f}%"


def format_list_as_bullets(items: List[str]) -> str:
    """Format list as bullet points"""
    return "\n".join([f"• {item}" for item in items])


def format_list_as_numbered(items: List[str]) -> str:
    """Format list as numbered list"""
    return "\n".join([f"{i+1}. {item}" for i, item in enumerate(items)])


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_json_pretty(data: Dict[str, Any]) -> str:
    """Format JSON with indentation"""
    return json.dumps(data, indent=2, ensure_ascii=False)


def format_table(
    headers: List[str],
    rows: List[List[Any]],
    max_col_width: int = 30
) -> str:
    """Format data as ASCII table"""
    
    # Calculate column widths
    col_widths = [len(h) for h in headers]
    
    for row in rows:
        for i, cell in enumerate(row):
            cell_str = str(cell)
            if len(cell_str) > col_widths[i]:
                col_widths[i] = min(len(cell_str), max_col_width)
    
    # Create separator
    separator = "+" + "+".join(["-" * (w + 2) for w in col_widths]) + "+"
    
    # Format header
    header_row = "|" + "|".join([
        f" {h:<{col_widths[i]}} "
        for i, h in enumerate(headers)
    ]) + "|"
    
    # Format rows
    formatted_rows = []
    for row in rows:
        formatted_row = "|" + "|".join([
            f" {truncate_text(str(cell), col_widths[i]):<{col_widths[i]}} "
            for i, cell in enumerate(row)
        ]) + "|"
        formatted_rows.append(formatted_row)
    
    # Combine all parts
    table = "\n".join([
        separator,
        header_row,
        separator,
        *formatted_rows,
        separator
    ])
    
    return table


def format_duration(seconds: int) -> str:
    """Format duration in human-readable format"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"


def format_file_size(bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.1f} PB"


def format_status_badge(status: str) -> str:
    """Format status as badge with emoji"""
    status_emojis = {
        'new': '🆕',
        'screening': '🔍',
        'interview': '📅',
        'offer': '💼',
        'hired': '✅',
        'rejected': '❌',
        'draft': '📝',
        'active': '🟢',
        'paused': '⏸️',
        'closed': '🔒'
    }
    
    emoji = status_emojis.get(status.lower(), '•')
    return f"{emoji} {status.title()}"


def format_skills_list(skills: List[str], max_display: int = 10) -> str:
    """Format skills list for display"""
    if not skills:
        return "No skills listed"
    
    if len(skills) <= max_display:
        return ", ".join(skills)
    
    displayed = ", ".join(skills[:max_display])
    remaining = len(skills) - max_display
    return f"{displayed} +{remaining} more"