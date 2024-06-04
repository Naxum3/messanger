import unittest

from hamming import bits_to_text
from hamming import decode
from hamming import decode_text
from hamming import encode
from hamming import encode_text
from hamming import text_to_bits


class TestTextToBits(unittest.TestCase):
    def test(self):
        self.assertEqual(text_to_bits('a'), [0, 1, 1, 0, 0, 0, 0, 1])
        self.assertEqual(text_to_bits(''), [])
        self.assertEqual(text_to_bits('1'), [0, 0, 1, 1, 0, 0, 0, 1])


class TestBitsToText(unittest.TestCase):
    def test(self):
        self.assertEqual(bits_to_text([0, 1, 1, 0, 0, 0, 0, 1]), 'a')
        self.assertEqual(bits_to_text([]), '')
        self.assertEqual(bits_to_text([0, 0, 1, 1, 0, 0, 0, 1]), '1')


class TestEncode(unittest.TestCase):
    def test(self):
        self.assertEqual(encode([0, 0, 1, 1, 0, 0, 0, 1]), [1, 0, 0, 0, 0, 1, 1])


class TestDecode(unittest.TestCase):
    def test(self):
        self.assertEqual(decode([1, 0, 0, 0, 0, 1, 1]), [0, 0, 1, 1])


class TestEncodeText(unittest.TestCase):
    def test(self):
        self.assertEqual(encode_text("first"), "1100110110011011001100011001000111101010100001111100001100011111001100")
        self.assertEqual(encode_text(""), "")


class TestDecodeText(unittest.TestCase):
    def test(self):
        self.assertEqual(decode_text("1100110110011011001100011001000111101010100001111100001100011111001100"), "first")
        self.assertEqual(decode_text(""), "")
