"""Core implementation for URL-safe Base64 encoding and decoding.

The standard library's base64 module provides ``urlsafe_b64encode`` and
``urlsafe_b64decode``. However, those functions operate on the padded
alphabet (``-`` and ``_`` replace ``+`` and ``/``, but ``=`` padding is still
emitted). Many URL-safe contexts (JWT, some query parameters, filenames)
require the padding to be omitted entirely. This module wraps those
functions to strip padding on encode and restore it on decode, while also
accepting already-padded input for decode.
"""

from __future__ import annotations

import base64
import binascii
from typing import Union


def encode(data: bytes) -> str:
    """Encode bytes using the URL-safe Base64 alphabet with no padding.

    Args:
        data: The bytes to encode.

    Returns:
        A string containing the unpadded URL-safe Base64 representation.

    Raises:
        TypeError: If ``data`` is not bytes-like.

    Why this choice: We deliberately return ``str`` rather than ``bytes``
    because Base64 text is conventionally handled as ASCII text in Python 3,
    and callers typically need to embed it in URLs, JSON, or headers.
    """
    # base64.urlsafe_b64encode accepts any bytes-like object and returns bytes.
    # We decode to ASCII str and strip all '=' padding characters.
    encoded = base64.urlsafe_b64encode(data)
    return encoded.decode("ascii").rstrip("=")


def decode(data: Union[str, bytes]) -> bytes:
    """Decode URL-safe Base64 text, accepting padded or unpadded input.

    Args:
        data: The Base64 text to decode. May be a ``str`` or ASCII ``bytes``.
            Both the standard URL-safe alphabet (``-`` and ``_``) and the
            normal Base64 alphabet (``+`` and ``/``) are accepted, because
            the underlying ``urlsafe_b64decode`` maps both. Padding is
            optional; missing padding is restored before decoding.

    Returns:
        The decoded bytes.

    Raises:
        TypeError: If ``data`` is neither ``str`` nor bytes-like.
        binascii.Error: If the input contains invalid Base64 characters or
            has an invalid length after padding restoration.

    Why accept both alphabets: The URL-safe variant is often produced by
    other tools that may or may not use the URL-safe alphabet. Accepting
    both costs nothing and makes the decoder more forgiving in practice.
    """
    if isinstance(data, str):
        # Encode to ASCII bytes; non-ASCII characters will raise UnicodeEncodeError
        # which is a subclass of ValueError. We let it propagate.
        raw = data.encode("ascii")
    else:
        # Assume bytes-like. Passing a non-bytes-like will raise TypeError from
        # base64 module, which is acceptable.
        raw = data  # type: ignore[assignment]

    # Strip whitespace that may have been introduced by copying/pasting.
    # This is not part of the Base64 alphabet, so it is safe to remove.
    raw = raw.strip()

    # If the input is already padded, use it as-is; otherwise add the
    # necessary '=' padding to make the length a multiple of 4.
    # Note: base64.urlsafe_b64decode requires padding unless the input length
    # is already a multiple of 4. We compute the required padding and add it.
    # We use a local variable to avoid modifying the input object.
    padded = raw
    remainder = len(padded) % 4
    if remainder != 0:
        padded = padded + b"=" * (4 - remainder)

    # urlsafe_b64decode accepts both URL-safe and standard alphabets and
    # handles the mapping internally. It raises binascii.Error for invalid
    # input, which we let propagate.
    try:
        return base64.urlsafe_b64decode(padded)
    except (binascii.Error, ValueError) as exc:
        # Re-raise as binascii.Error for a consistent exception type.
        # The standard library may raise either depending on the specific
        # failure, but binascii.Error is the documented type for bad Base64.
        raise binascii.Error(f"Invalid Base64 input: {exc}") from exc
