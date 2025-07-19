from rest_framework.response import Response

def validate_max_lengths(data, limits):
    """
    Validates that fields in `data` do not exceed max lengths defined in `limits`.
    Returns (True, None) if all valid, else (False, Response).
    """
    for field, limit in limits.items():
        val = data.get(field, '')
        if val and len(str(val)) > limit:
            return False, Response({
                'status': False,
                'message': f"{field.capitalize()} must not exceed {limit} characters."
            })
    return True, None
