# base64-url-safe-encoder

Encodes bytes to URL-safe Base64 with no padding, and decodes both padded and unpadded input.

## Usage

```python
from base64_url_safe_encoder import encode, decode

text = encode(b"hello, world")
print(text)  # aGVsbG8sIHdvcmxk

original = decode(text)
print(original)  # b"hello, world"
```

The `encode` function returns a `str`. The `decode` function accepts either `str` or `bytes` and returns `bytes`. Both the URL-safe alphabet (`-` and `_`) and the standard Base64 alphabet (`+` and `/`) are accepted when decoding.

## Why this library exists

Python's standard `base64.urlsafe_b64encode` still emits `=` padding characters. Many URL-safe contexts, such as JSON Web Tokens (JWTs) and some query parameters, require that padding to be omitted. This library wraps the standard functions to always produce unpadded output and to accept both padded and unpadded input when decoding.

## Edge cases

Decoding input with invalid Base64 characters raises a `binascii.Error`. Leading and trailing whitespace in the input string is stripped before decoding. Non-ASCII characters in a `str` input raise a `UnicodeEncodeError`.
