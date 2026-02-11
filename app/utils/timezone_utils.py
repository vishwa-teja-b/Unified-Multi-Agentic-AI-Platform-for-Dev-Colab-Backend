"""
Timezone utility functions for team formation.
Calculates timezone differences and filters candidates.
"""
from datetime import datetime
from typing import List, Dict, Any
import pytz

# Common timezone mappings (IANA timezone names)
TIMEZONE_OFFSETS = {
    "IST": "Asia/Kolkata",      # India Standard Time, UTC+5:30
    "PST": "America/Los_Angeles", # Pacific Standard Time, UTC-8
    "EST": "America/New_York",   # Eastern Standard Time, UTC-5
    "GMT": "Europe/London",      # Greenwich Mean Time, UTC+0
    "CET": "Europe/Paris",       # Central European Time, UTC+1
    "JST": "Asia/Tokyo",         # Japan Standard Time, UTC+9
    "AEST": "Australia/Sydney",  # Australian Eastern, UTC+10
    "SGT": "Asia/Singapore",     # Singapore Time, UTC+8
    "GST": "Asia/Dubai",         # Gulf Standard Time, UTC+4
}


def get_utc_offset_hours(timezone_str: str) -> float:
    """
    Get the UTC offset in hours for a given timezone.
    
    Args:
        timezone_str: Timezone string like "IST", "PST", or "Asia/Kolkata"
    
    Returns:
        Float representing hours offset from UTC (e.g., 5.5 for IST)
    
    Example:
        >>> get_utc_offset_hours("IST")
        5.5
        >>> get_utc_offset_hours("PST")
        -8.0
    """
    # Convert short codes to IANA format
    if timezone_str in TIMEZONE_OFFSETS:
        timezone_str = TIMEZONE_OFFSETS[timezone_str]
    
    try:
        tz = pytz.timezone(timezone_str)
        now = datetime.now(pytz.UTC)
        offset = tz.utcoffset(now)
        return offset.total_seconds() / 3600  # Convert to hours
    except Exception:
        return 0.0  # Default to UTC if timezone is invalid


def calculate_timezone_difference(tz1: str, tz2: str) -> float:
    """
    Calculate the absolute hour difference between two timezones.
    
    Args:
        tz1: First timezone (e.g., "IST")
        tz2: Second timezone (e.g., "PST")
    
    Returns:
        Absolute hour difference between the two timezones
    
    Example:
        >>> calculate_timezone_difference("IST", "IST")
        0.0
        >>> calculate_timezone_difference("IST", "PST")
        13.5  # IST is +5:30, PST is -8, difference = 13.5 hours
    """
    offset1 = get_utc_offset_hours(tz1)
    offset2 = get_utc_offset_hours(tz2)
    return abs(offset1 - offset2)


def get_timezone_compatibility_score(tz1: str, tz2: str, max_diff: float = 4.0) -> float:
    """
    Calculate a compatibility score between 0 and 1 based on timezone difference.
    
    Args:
        tz1: First timezone
        tz2: Second timezone
        max_diff: Maximum acceptable hour difference (default: 4 hours)
    
    Returns:
        Score between 0.0 (incompatible) and 1.0 (same timezone)
    
    Example:
        >>> get_timezone_compatibility_score("IST", "IST")
        1.0
        >>> get_timezone_compatibility_score("IST", "GST")  # 1.5 hour diff
        0.625
        >>> get_timezone_compatibility_score("IST", "PST")  # 13.5 hour diff
        0.0
    """
    diff = calculate_timezone_difference(tz1, tz2)
    
    if diff > max_diff:
        return 0.0  # Incompatible
    
    # Linear score: 0 diff = 1.0, max_diff = 0.0
    return 1.0 - (diff / max_diff)


def filter_candidates_by_timezone(
    candidates: List[Dict[str, Any]], 
    owner_timezone: str,
    max_hour_difference: float = 4.0
) -> List[Dict[str, Any]]:
    """
    Filter candidates who are within the acceptable timezone difference.
    Also adds timezone_score and timezone_diff to each candidate.
    
    Args:
        candidates: List of candidate dictionaries
        owner_timezone: The project owner's timezone
        max_hour_difference: Maximum acceptable hour difference
    
    Returns:
        Filtered list of candidates with timezone_score added
    
    Example:
        >>> candidates = [
        ...     {"name": "Priya", "timezone": "IST"},
        ...     {"name": "John", "timezone": "PST"},
        ... ]
        >>> filtered = filter_candidates_by_timezone(candidates, "IST", max_diff=4)
        >>> len(filtered)  # Only Priya passes
        1
    """
    filtered_candidates = []
    
    for candidate in candidates:
        candidate_tz = candidate.get("timezone", "UTC")
        
        # Calculate difference
        tz_diff = calculate_timezone_difference(owner_timezone, candidate_tz)
        
        # Calculate score
        tz_score = get_timezone_compatibility_score(owner_timezone, candidate_tz, max_hour_difference)
        
        # Add timezone info to candidate
        candidate["timezone_diff"] = tz_diff
        candidate["timezone_score"] = tz_score
        
        # Only include if within acceptable range
        if tz_diff <= max_hour_difference:
            filtered_candidates.append(candidate)
    
    return filtered_candidates


def get_timezone_label(tz_diff: float) -> str:
    """
    Get a human-readable label for timezone compatibility.
    
    Example:
        >>> get_timezone_label(0)
        "Excellent"
        >>> get_timezone_label(2)
        "Good"
        >>> get_timezone_label(4)
        "Fair"
        >>> get_timezone_label(6)
        "Poor"
    """
    if tz_diff <= 1:
        return "Excellent"
    elif tz_diff <= 2:
        return "Good"
    elif tz_diff <= 4:
        return "Fair"
    else:
        return "Poor"