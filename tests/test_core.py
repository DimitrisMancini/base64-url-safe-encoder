"""Tests for the URL-safe Base64 encoder."""

import binascii
import unittest

from base64_url_safe_encoder import decode, encode


class TestEncode(unittest.TestCase):
    def test_empty_bytes(self):
        self.assertEqual(encode(b""), "")

    def test_simple_ascii(self):
        self.assertEqual(encode(b"hello"), "aGVsbG8")

    def test_bytes_with_padding_required(self):
        # "foobar" -> "Zm9vYmFy" with one '=' padding in standard encoding.
        # URL-safe unpadded should strip that '='.
        self.assertEqual(encode(b"foobar"), "Zm9vYmFy")

    def test_bytes_with_two_padding_chars(self):
        # "foob" -> "Zm9vYg==" in standard encoding.
        self.assertEqual(encode(b"foob"), "Zm9vYg")

    def test_non_ascii_bytes(self):
        # 0xFF, 0xFE, 0xFD
        self.assertEqual(encode(b"\xff\xfe\xfd"), "__79")

    def test_url_safe_alphabet_used(self):
        # Bytes that produce '+' and '/' in standard Base64.
        # 0xFB, 0xFF -> standard "+/8=", URL-safe "-_8"
        self.assertEqual(encode(b"\xfb\xff"), "-_8")

    def test_type_error_on_non_bytes(self):
        with self.assertRaises(TypeError):
            encode("not bytes")  # type: ignore[arg-type]


class TestDecode(unittest.TestCase):
    def test_empty_string(self):
        self.assertEqual(decode(""), b"")

    def test_simple_ascii(self):
        self.assertEqual(decode("aGVsbG8"), b"hello")

    def test_unpadded_input(self):
        self.assertEqual(decode("Zm9vYmFy"), b"foobar")

    def test_padded_input(self):
        self.assertEqual(decode("Zm9vYmFy="), b"foobar")

    def test_url_safe_alphabet(self):
        self.assertEqual(decode("-_8"), b"\xfb\xff")

    def test_standard_alphabet_also_accepted(self):
        # We accept standard Base64 as a convenience.
        self.assertEqual(decode("+/8="), b"\xfb\xff")

    def test_bytes_input(self):
        self.assertEqual(decode(b"aGVsbG8"), b"hello")

    def test_whitespace_is_stripped(self):
        self.assertEqual(decode("  aGVsbG8  "), b"hello")

    def test_invalid_character_raises_error(self):
        with self.assertRaises(binascii.Error):
            decode("aGVsbG8$")

    def test_invalid_length_raises_error(self):
        # After padding restoration, this length is invalid.
        with self.assertRaises(binascii.Error):
            decode("a")


if __name__ == "__main__":
    unittest.main()
