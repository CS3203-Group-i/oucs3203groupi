def gapPreference(gap):
    """
    Validates if the given gap is:
    - an integer
    - between 0 and 1440 minutes
    - a multiple of 60 (i.e. full hours)
    """
    return isinstance(gap, int) and 0 <= gap <= 1440 and gap % 60 == 0