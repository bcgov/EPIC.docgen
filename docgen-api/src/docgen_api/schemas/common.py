"""Some common validation functions"""
import base64

from marshmallow.exceptions import ValidationError


def is_base64(value):
    """Check if the value is valid base64."""
    try:
        base64.b64decode(value)
        return True
    except Exception:
        raise ValidationError("template_content must be a valid base64 encoded string")