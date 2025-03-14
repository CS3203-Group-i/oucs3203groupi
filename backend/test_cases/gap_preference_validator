def gapPreference(time_gap):
    """
    Validates whether the given time gap is an acceptable integer value.

    Args:
        time_gap (int): The time gap in minutes.

    Returns:
        bool: True if the time gap is a valid integer between 0 and 1440 (inclusive), otherwise False.
    """

    # Check if time_gap is an integer and falls within the valid range (0 to 1440 minutes)
    if isinstance(time_gap, int) and 0 <= time_gap <= 1440:
        return True  # Valid time gap

    return False  # Invalid time gap (e.g., negative, non-integer, or over 24 hours)